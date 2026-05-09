#!/usr/bin/env python3
"""Run one Ssym V6_V2 tensor-extraction smoke test.

This is not a full V3 pickle reproduction script. It only checks that the
recovered V6_V2 ProteinMPNN tensor-extraction module can regenerate the direct
ProteinMPNN-derived tensor-field schema for one saved Ssym V3 mutation entry.
"""

from __future__ import annotations

import argparse
import csv
import json
import pickle
import sys
from pathlib import Path
from typing import Any

import numpy as np
import torch

WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from proteinmpnn_ddg.recovered_v6v2 import (
    DEFAULT_SSYM_PDB_DIR,
    V3_TENSOR_FIELDS,
    build_residue_index_map,
    extract_mutation_tensor_fields,
    load_runtime,
    load_single_chain_protein,
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
    / "ssym_smoke_test"
)


def write_tsv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            delimiter="\t",
            fieldnames=fieldnames,
            lineterminator="\n",
        )
        writer.writeheader()
        for row in rows:
            cleaned = {}
            for field in fieldnames:
                value = str(row.get(field, "NA")).rstrip()
                cleaned[field] = value if value else "NA"
            writer.writerow(cleaned)


def load_target_entry(
    pickle_path: Path,
    protein_key: str | None,
    mutation_label: str | None,
) -> tuple[str, dict[str, Any]]:
    with pickle_path.open("rb") as handle:
        obj = pickle.load(handle)

    if protein_key is not None:
        entries = obj[protein_key]
    else:
        protein_key = next(iter(obj))
        entries = obj[protein_key]

    if mutation_label is None:
        return protein_key, entries[0]

    for entry in entries:
        if entry.get("mut") == mutation_label:
            return protein_key, entry
    raise ValueError(f"Mutation {mutation_label!r} not found under {protein_key!r}")


def array_shape(value: Any) -> str:
    if isinstance(value, list) and value and isinstance(value[0], str):
        return f"list[{len(value)}]"
    return "x".join(str(dim) for dim in np.asarray(value).shape)


def finite_numeric(value: Any) -> str:
    if isinstance(value, list) and value and isinstance(value[0], str):
        return "not_numeric"
    arr = np.asarray(value)
    if arr.dtype.kind not in "biufc":
        return "not_numeric"
    return str(bool(np.isfinite(arr).all()))


def max_abs_difference(left: Any, right: Any) -> str:
    if isinstance(left, list) and left and isinstance(left[0], str):
        return "NA"
    left_arr = np.asarray(left)
    right_arr = np.asarray(right)
    if left_arr.shape != right_arr.shape:
        return "shape_mismatch"
    if left_arr.dtype.kind not in "biufc" or right_arr.dtype.kind not in "biufc":
        return "NA"
    return f"{float(np.max(np.abs(left_arr - right_arr))):.8g}"


def schema_rows(target_entry: dict[str, Any], generated_fields: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for field in V3_TENSOR_FIELDS:
        target_value = target_entry.get(field)
        generated_value = generated_fields.get(field)
        target_shape = array_shape(target_value) if target_value is not None else "missing"
        generated_shape = array_shape(generated_value) if generated_value is not None else "missing"
        rows.append(
            {
                "field": field,
                "target_shape": target_shape,
                "generated_shape": generated_shape,
                "shape_match": target_shape == generated_shape,
                "generated_finite_numeric": finite_numeric(generated_value),
                "max_abs_diff_vs_target": (
                    max_abs_difference(target_value, generated_value)
                    if target_value is not None and generated_value is not None
                    else "NA"
                ),
            }
        )
    return rows


def write_report(
    output_dir: Path,
    protein_key: str,
    mutation_label: str,
    sequence_index: int,
    rows: list[dict[str, Any]],
    runtime_summary: dict[str, Any],
) -> None:
    all_shapes_match = all(bool(row["shape_match"]) for row in rows)
    all_numeric_finite = all(
        row["generated_finite_numeric"] in {"True", "not_numeric"} for row in rows
    )
    lines = [
        "# Ssym Tensor Extraction Smoke Test",
        "",
        "Scope: one-entry smoke test for the recovered V6_V2 ProteinMPNN tensor",
        "extraction module. This does not stitch engineered/PSSM features and does",
        "not claim full V3 pickle reproduction.",
        "",
        "## Target",
        "",
        f"- Protein key: `{protein_key}`",
        f"- Mutation: `{mutation_label}`",
        f"- Zero-based sequence index from PDB residue map: `{sequence_index}`",
        "",
        "## Result",
        "",
        f"- All V3 tensor-field shapes match target entry: `{all_shapes_match}`",
        f"- All generated numeric tensors are finite: `{all_numeric_finite}`",
        "- Numeric values are recorded as diagnostics only. Exact equality is not",
        "  expected at this stage because the historical RNG state and runtime stack",
        "  are not recovered.",
        "",
        "## Runtime",
        "",
        f"- Utils source: `{runtime_summary['utils_path']}`",
        f"- Checkpoint: `{runtime_summary['checkpoint_path']}`",
        f"- Device: `{runtime_summary['device']}`",
        f"- Number of ProteinMPNN edges: `{runtime_summary['num_edges']}`",
        "",
        "## Tables",
        "",
        "- `tables/ssym_tensor_field_schema_compare.tsv`",
        "- `json/ssym_tensor_extraction_smoke_summary.json`",
        "",
    ]
    (output_dir / "SSYM_TENSOR_EXTRACTION_SMOKE_TEST.md").write_text(
        "\n".join(lines),
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target-pickle", type=Path, default=DEFAULT_TARGET_PICKLE)
    parser.add_argument("--pdb-dir", type=Path, default=DEFAULT_SSYM_PDB_DIR)
    parser.add_argument("--protein-key", default="1amqA")
    parser.add_argument("--mutation-label", default="C191Y")
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    np.random.seed(args.seed)
    torch.manual_seed(args.seed)

    runtime = load_runtime(device=args.device)
    protein_key, target_entry = load_target_entry(
        args.target_pickle,
        args.protein_key,
        args.mutation_label,
    )
    mutation_label = str(target_entry["mut"])
    chain_id = protein_key[-1]
    pdb_path = args.pdb_dir / f"{protein_key}.pdb"

    residue_map = build_residue_index_map(pdb_path, chain_id)
    mutation_residue_key = mutation_label[:-1]
    sequence_index = residue_map[mutation_residue_key]
    protein = load_single_chain_protein(runtime, pdb_path, chain_id)
    extracted = extract_mutation_tensor_fields(
        runtime,
        protein,
        protein_key,
        mutation_label,
        sequence_index,
    )

    rows = schema_rows(target_entry, extracted.fields)
    output_dir = args.output_dir
    table_dir = output_dir / "tables"
    json_dir = output_dir / "json"
    table_dir.mkdir(parents=True, exist_ok=True)
    json_dir.mkdir(parents=True, exist_ok=True)

    write_tsv(
        table_dir / "ssym_tensor_field_schema_compare.tsv",
        rows,
        [
            "field",
            "target_shape",
            "generated_shape",
            "shape_match",
            "generated_finite_numeric",
            "max_abs_diff_vs_target",
        ],
    )

    summary = {
        "protein_key": protein_key,
        "mutation_label": mutation_label,
        "sequence_index": sequence_index,
        "seed": args.seed,
        "all_shapes_match": all(bool(row["shape_match"]) for row in rows),
        "all_generated_numeric_finite": all(
            row["generated_finite_numeric"] in {"True", "not_numeric"} for row in rows
        ),
        "runtime": {
            "utils_path": str(runtime.utils_path.relative_to(WORKSPACE_ROOT)),
            "checkpoint_path": str(runtime.checkpoint_path.relative_to(WORKSPACE_ROOT)),
            "device": str(runtime.device),
            "num_edges": int(runtime.checkpoint["num_edges"]),
        },
    }
    (json_dir / "ssym_tensor_extraction_smoke_summary.json").write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )
    write_report(output_dir, protein_key, mutation_label, sequence_index, rows, summary["runtime"])

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
