#!/usr/bin/env python3
"""Run the Ssym all-entry Set 1 tensor-extraction experiment.

This experiment validates only the direct ProteinMPNN-derived tensor fields in
the saved Ssym V3 pickle. It does not construct engineered/PSSM features and it
does not claim full V3 pickle reproduction.
"""

from __future__ import annotations

import argparse
import csv
import json
import pickle
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
import torch

WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from proteinmpnn_ddg.recovered_v6v2 import (
    DEFAULT_SSYM_PDB_DIR,
    build_residue_index_map,
    extract_mutation_tensor_fields,
    load_runtime,
    load_single_chain_protein,
)
from proteinmpnn_ddg.tensor_field_checks import (
    SCHEMA_FIELDNAMES,
    all_generated_numeric_finite,
    all_shapes_match,
    failed_fields,
    schema_rows,
    write_tsv,
)


DEFAULT_TARGET_PICKLE = (
    WORKSPACE_ROOT
    / "drive_evidence_copy"
    / "sajidahmedprotres_drive"
    / "Protein_MPNN_Digging"
    / "Ssym_pmppn_info_dict_V3.pickle"
)
DEFAULT_OUTPUT_DIR = (
    WORKSPACE_ROOT
    / "manuscript_codebase_mapping"
    / "tensor_extraction_codeblock_recovery"
    / "ssym_all_entries_tensor_extraction"
)

MUTATION_FIELDNAMES = [
    "protein_key",
    "mutation_label",
    "sequence_index",
    "status",
    "all_shapes_match",
    "all_generated_numeric_finite",
    "failed_fields",
    "error_type",
    "error_message",
    "elapsed_seconds",
]
FIELD_FIELDNAMES = [
    "protein_key",
    "mutation_label",
    "sequence_index",
    *SCHEMA_FIELDNAMES,
]


def load_pickle(path: Path) -> dict[str, list[dict[str, Any]]]:
    with path.open("rb") as handle:
        return pickle.load(handle)


def load_existing_tsv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def drop_entry_rows(
    mutation_rows: list[dict[str, Any]],
    field_rows: list[dict[str, Any]],
    protein_key: str,
    mutation_label: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    mutation_rows = [
        row
        for row in mutation_rows
        if not (
            row.get("protein_key") == protein_key
            and row.get("mutation_label") == mutation_label
        )
    ]
    field_rows = [
        row
        for row in field_rows
        if not (
            row.get("protein_key") == protein_key
            and row.get("mutation_label") == mutation_label
        )
    ]
    return mutation_rows, field_rows


def runtime_summary(runtime: Any) -> dict[str, Any]:
    return {
        "utils_path": str(runtime.utils_path.relative_to(WORKSPACE_ROOT)),
        "checkpoint_path": str(runtime.checkpoint_path.relative_to(WORKSPACE_ROOT)),
        "device": str(runtime.device),
        "num_edges": int(runtime.checkpoint["num_edges"]),
    }


def target_entries(
    target: dict[str, list[dict[str, Any]]],
    protein_key_filter: str | None,
    limit: int | None,
) -> list[tuple[int, str, dict[str, Any]]]:
    selected: list[tuple[int, str, dict[str, Any]]] = []
    global_index = 0
    for protein_key, entries in target.items():
        if protein_key_filter is not None and protein_key != protein_key_filter:
            global_index += len(entries)
            continue
        for entry in entries:
            selected.append((global_index, protein_key, entry))
            global_index += 1
            if limit is not None and len(selected) >= limit:
                return selected
    return selected


def write_report(
    output_dir: Path,
    summary: dict[str, Any],
) -> None:
    lines = [
        "# Ssym All-Entry Tensor Extraction Experiment",
        "",
        "Scope: all saved Ssym V3 mutation entries, direct ProteinMPNN-derived",
        "tensor fields only. This experiment does not stitch engineered/PSSM",
        "features and does not claim full V3 pickle reproduction.",
        "",
        "## Result",
        "",
        f"- Target mutation entries: `{summary['target_entry_count']}`",
        f"- Successful entries: `{summary['ok_entry_count']}`",
        f"- Schema failures: `{summary['schema_failure_count']}`",
        f"- Runtime errors: `{summary['error_count']}`",
        f"- All selected entries passed: `{summary['all_selected_entries_passed']}`",
        "",
        "## Runtime",
        "",
        f"- Utils source: `{summary['runtime']['utils_path']}`",
        f"- Checkpoint: `{summary['runtime']['checkpoint_path']}`",
        f"- Device: `{summary['runtime']['device']}`",
        f"- Number of ProteinMPNN edges: `{summary['runtime']['num_edges']}`",
        f"- Seed base: `{summary['seed']}`",
        "",
        "## Tables",
        "",
        "- `tables/ssym_all_entries_mutation_status.tsv`",
        "- `tables/ssym_all_entries_field_schema_compare.tsv`",
        "- `json/ssym_all_entries_tensor_extraction_summary.json`",
        "",
        "## Boundary",
        "",
        "Passing this experiment means the recovered Set 1 scaffold traverses the",
        "complete selected Ssym V3 direct tensor-field surface without shape or",
        "finite-numeric failures. It does not yet validate engineered features.",
        "",
    ]
    (output_dir / "SSYM_ALL_ENTRIES_TENSOR_EXTRACTION_EXPERIMENT.md").write_text(
        "\n".join(lines),
        encoding="utf-8",
    )


def build_summary(
    selected: list[tuple[int, str, dict[str, Any]]],
    mutation_rows: list[dict[str, Any]],
    seed: int,
    runtime_info: dict[str, Any],
) -> dict[str, Any]:
    selected_keys = {(protein_key, str(entry["mut"])) for _, protein_key, entry in selected}
    selected_rows = [
        row
        for row in mutation_rows
        if (row.get("protein_key"), row.get("mutation_label")) in selected_keys
    ]
    ok_rows = [row for row in selected_rows if row.get("status") == "ok"]
    schema_failure_rows = [
        row for row in selected_rows if row.get("status") == "schema_failure"
    ]
    error_rows = [row for row in selected_rows if row.get("status") == "error"]

    by_protein: dict[str, dict[str, int]] = {}
    for _, protein_key, _entry in selected:
        by_protein.setdefault(
            protein_key,
            {"target_entries": 0, "ok": 0, "schema_failure": 0, "error": 0},
        )
        by_protein[protein_key]["target_entries"] += 1
    for row in selected_rows:
        protein_key = str(row.get("protein_key"))
        status = str(row.get("status"))
        if protein_key not in by_protein:
            continue
        if status in {"ok", "schema_failure", "error"}:
            by_protein[protein_key][status] += 1

    return {
        "target_entry_count": len(selected),
        "processed_entry_count": len(selected_rows),
        "ok_entry_count": len(ok_rows),
        "schema_failure_count": len(schema_failure_rows),
        "error_count": len(error_rows),
        "all_selected_entries_passed": len(ok_rows) == len(selected)
        and not schema_failure_rows
        and not error_rows,
        "seed": seed,
        "runtime": runtime_info,
        "by_protein": by_protein,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target-pickle", type=Path, default=DEFAULT_TARGET_PICKLE)
    parser.add_argument("--pdb-dir", type=Path, default=DEFAULT_SSYM_PDB_DIR)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--protein-key", default=None)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()

    target = load_pickle(args.target_pickle)
    selected = target_entries(target, args.protein_key, args.limit)
    output_dir = args.output_dir
    table_dir = output_dir / "tables"
    json_dir = output_dir / "json"
    mutation_status_path = table_dir / "ssym_all_entries_mutation_status.tsv"
    field_schema_path = table_dir / "ssym_all_entries_field_schema_compare.tsv"

    mutation_rows: list[dict[str, Any]] = []
    field_rows: list[dict[str, Any]] = []
    completed_ok: set[tuple[str, str]] = set()
    if args.resume:
        mutation_rows = load_existing_tsv(mutation_status_path)
        field_rows = load_existing_tsv(field_schema_path)
        completed_ok = {
            (str(row["protein_key"]), str(row["mutation_label"]))
            for row in mutation_rows
            if row.get("status") == "ok"
        }

    runtime = load_runtime(device=args.device)
    protein_cache: dict[str, tuple[dict[str, Any], dict[str, int]]] = {}
    runtime_info = runtime_summary(runtime)

    table_dir.mkdir(parents=True, exist_ok=True)
    json_dir.mkdir(parents=True, exist_ok=True)

    for ordinal, (global_index, protein_key, target_entry) in enumerate(selected, start=1):
        mutation_label = str(target_entry["mut"])
        entry_key = (protein_key, mutation_label)
        if entry_key in completed_ok:
            print(f"[{ordinal}/{len(selected)}] skip ok {protein_key} {mutation_label}", flush=True)
            continue

        mutation_rows, field_rows = drop_entry_rows(
            mutation_rows,
            field_rows,
            protein_key,
            mutation_label,
        )
        start = time.perf_counter()
        try:
            torch.manual_seed(args.seed + global_index)
            np.random.seed((args.seed + global_index) % (2**32))

            if protein_key not in protein_cache:
                chain_id = protein_key[-1]
                pdb_path = args.pdb_dir / f"{protein_key}.pdb"
                residue_map = build_residue_index_map(pdb_path, chain_id)
                protein = load_single_chain_protein(runtime, pdb_path, chain_id)
                protein_cache[protein_key] = (protein, residue_map)

            protein, residue_map = protein_cache[protein_key]
            sequence_index = residue_map[mutation_label[:-1]]
            extracted = extract_mutation_tensor_fields(
                runtime,
                protein,
                protein_key,
                mutation_label,
                sequence_index,
            )
            rows = schema_rows(target_entry, extracted.fields)
            shapes_ok = all_shapes_match(rows)
            finite_ok = all_generated_numeric_finite(rows)
            status = "ok" if shapes_ok and finite_ok else "schema_failure"

            for row in rows:
                field_rows.append(
                    {
                        "protein_key": protein_key,
                        "mutation_label": mutation_label,
                        "sequence_index": sequence_index,
                        **row,
                    }
                )
            mutation_rows.append(
                {
                    "protein_key": protein_key,
                    "mutation_label": mutation_label,
                    "sequence_index": sequence_index,
                    "status": status,
                    "all_shapes_match": shapes_ok,
                    "all_generated_numeric_finite": finite_ok,
                    "failed_fields": failed_fields(rows),
                    "error_type": "NA",
                    "error_message": "NA",
                    "elapsed_seconds": f"{time.perf_counter() - start:.3f}",
                }
            )
            print(
                f"[{ordinal}/{len(selected)}] {status} {protein_key} {mutation_label}",
                flush=True,
            )
        except Exception as exc:  # noqa: BLE001 - record all per-entry failures.
            mutation_rows.append(
                {
                    "protein_key": protein_key,
                    "mutation_label": mutation_label,
                    "sequence_index": "NA",
                    "status": "error",
                    "all_shapes_match": False,
                    "all_generated_numeric_finite": False,
                    "failed_fields": "NA",
                    "error_type": type(exc).__name__,
                    "error_message": str(exc),
                    "elapsed_seconds": f"{time.perf_counter() - start:.3f}",
                }
            )
            print(
                f"[{ordinal}/{len(selected)}] error {protein_key} {mutation_label}: {type(exc).__name__}: {exc}",
                flush=True,
            )

        write_tsv(mutation_status_path, mutation_rows, MUTATION_FIELDNAMES)
        write_tsv(field_schema_path, field_rows, FIELD_FIELDNAMES)

    summary = build_summary(selected, mutation_rows, args.seed, runtime_info)
    (json_dir / "ssym_all_entries_tensor_extraction_summary.json").write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )
    write_report(output_dir, summary)
    print(json.dumps(summary, indent=2))

    if not summary["all_selected_entries_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
