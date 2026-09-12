#!/usr/bin/env python3
"""Diagnose Ssym V3 direct-tensor mismatch on a small slice.

Compares three extraction modes against saved V3 pickle entries:

A) baseline: current recovered path with per-mutation seed reset
B) continuous_rng: seed once; no per-mutation seed reset
C) replay_neighbors: force saved top_15_neighbor_indices into the neighbor loop

This does not claim any mode is the historical algorithm; it measures whether
RNG continuity or neighbor-identity replay improves value-level match rates.
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

from proteinmpnn_ddg_recovery.recovered_v6v2 import (  # noqa: E402
    DEFAULT_SSYM_PDB_DIR,
    V3_TENSOR_FIELDS,
    build_residue_index_map,
    extract_mutation_tensor_fields,
    load_runtime,
    load_single_chain_protein,
)
from proteinmpnn_ddg_recovery.tensor_field_checks import (  # noqa: E402
    max_abs_difference,
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
    / "reproduction_runs"
    / "latest"
    / "v3_ssym_slice_diagnostics"
)

MODES = ("baseline", "continuous_rng", "replay_neighbors")
KEY_FIELDS = [
    "log_prob",
    "top_15_neighbor_indices",
    "top_10_neighbor_indices",
    "top_5_neighbor_indices",
    "top_15_closest_neighbor_indices",
    "top_10_closest_neighbor_indices",
    "top_15_attention_weights",
    "w_n_log_prob",
    "m_n_log_prob",
    "neighbor_w_message_vector_coming_from_center",
    "neighbor_m_message_vector_coming_from_center",
    "neighbor_w_neighbor_embedding",
    "neighbor_m_neighbor_embedding",
]


def load_pickle(path: Path) -> dict[str, list[dict[str, Any]]]:
    with path.open("rb") as handle:
        return pickle.load(handle)


def as_int_list(value: Any) -> list[int]:
    return [int(x) for x in np.asarray(value).tolist()]


def field_match(target: Any, generated: Any, atol: float = 1e-6) -> dict[str, Any]:
    if isinstance(target, list) and target and isinstance(target[0], str):
        exact = list(target) == list(generated)
        return {
            "exact_match": exact,
            "allclose_1e-6": exact,
            "max_abs_diff": "NA",
            "set_overlap": "NA",
            "ordered_prefix_match": "NA",
        }

    target_arr = np.asarray(target)
    generated_arr = np.asarray(generated)
    if target_arr.shape != generated_arr.shape:
        return {
            "exact_match": False,
            "allclose_1e-6": False,
            "max_abs_diff": "shape_mismatch",
            "set_overlap": "NA",
            "ordered_prefix_match": "NA",
        }

    if np.issubdtype(target_arr.dtype, np.integer) or target_arr.dtype == object:
        exact = bool(np.array_equal(target_arr, generated_arr))
        target_list = as_int_list(target_arr)
        generated_list = as_int_list(generated_arr)
        set_overlap = len(set(target_list) & set(generated_list))
        ordered = sum(1 for a, b in zip(target_list, generated_list) if a == b)
        return {
            "exact_match": exact,
            "allclose_1e-6": exact,
            "max_abs_diff": "0" if exact else max_abs_difference(target_arr, generated_arr),
            "set_overlap": set_overlap,
            "ordered_prefix_match": ordered,
        }

    diff = float(np.max(np.abs(target_arr.astype(np.float64) - generated_arr.astype(np.float64))))
    exact = diff == 0.0
    close = bool(np.allclose(target_arr, generated_arr, atol=atol, rtol=atol))
    return {
        "exact_match": exact,
        "allclose_1e-6": close,
        "max_abs_diff": f"{diff:.8g}",
        "set_overlap": "NA",
        "ordered_prefix_match": "NA",
    }


def select_entries(
    target: dict[str, list[dict[str, Any]]],
    limit: int,
    protein_key: str | None,
) -> list[tuple[int, str, dict[str, Any]]]:
    selected: list[tuple[int, str, dict[str, Any]]] = []
    global_index = 0
    for key, entries in target.items():
        if protein_key is not None and key != protein_key:
            global_index += len(entries)
            continue
        for entry in entries:
            selected.append((global_index, key, entry))
            global_index += 1
            if len(selected) >= limit:
                return selected
    return selected


def extract_for_mode(
    mode: str,
    runtime: Any,
    protein: dict[str, Any],
    protein_key: str,
    mutation_label: str,
    sequence_index: int,
    target_entry: dict[str, Any],
    seed: int,
    global_index: int,
    continuous_seeded: dict[str, bool],
) -> dict[str, Any]:
    if mode == "baseline":
        torch.manual_seed(seed + global_index)
        np.random.seed((seed + global_index) % (2**32))
        override = None
    elif mode == "continuous_rng":
        if not continuous_seeded.get("done"):
            torch.manual_seed(seed)
            np.random.seed(seed % (2**32))
            continuous_seeded["done"] = True
        override = None
    elif mode == "replay_neighbors":
        torch.manual_seed(seed + global_index)
        np.random.seed((seed + global_index) % (2**32))
        override = as_int_list(target_entry["top_15_neighbor_indices"])
    else:
        raise ValueError(mode)

    extracted = extract_mutation_tensor_fields(
        runtime,
        protein,
        protein_key,
        mutation_label,
        sequence_index,
        neighbor_indices_override=override,
    )
    return extracted.fields


def summarize_mode(rows: list[dict[str, Any]], mode: str, n_entries: int) -> dict[str, Any]:
    by_field: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        if row["mode"] != mode:
            continue
        by_field.setdefault(row["field"], []).append(row)

    field_summary = {}
    for field, field_rows in by_field.items():
        exact = sum(1 for r in field_rows if r["exact_match"] == "True")
        close = sum(1 for r in field_rows if r["allclose_1e-6"] == "True")
        field_summary[field] = {
            "exact_matches": exact,
            "allclose_1e-6_matches": close,
            "n": len(field_rows),
            "exact_rate": exact / len(field_rows) if field_rows else 0.0,
            "allclose_rate": close / len(field_rows) if field_rows else 0.0,
        }
    return {
        "mode": mode,
        "n_entries": n_entries,
        "fields": field_summary,
        "top15_neighbor_exact": field_summary.get("top_15_neighbor_indices", {}).get(
            "exact_matches", 0
        ),
        "closest15_exact": field_summary.get("top_15_closest_neighbor_indices", {}).get(
            "exact_matches", 0
        ),
        "log_prob_allclose": field_summary.get("log_prob", {}).get("allclose_1e-6_matches", 0),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target-pickle", type=Path, default=DEFAULT_TARGET_PICKLE)
    parser.add_argument("--pdb-dir", type=Path, default=DEFAULT_SSYM_PDB_DIR)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--protein-key", default=None)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    target = load_pickle(args.target_pickle)
    selected = select_entries(target, args.limit, args.protein_key)
    output_dir = args.output_dir
    table_dir = output_dir / "tables"
    json_dir = output_dir / "json"
    table_dir.mkdir(parents=True, exist_ok=True)
    json_dir.mkdir(parents=True, exist_ok=True)

    runtime = load_runtime(device=args.device)
    protein_cache: dict[str, tuple[dict[str, Any], dict[str, int]]] = {}

    detail_rows: list[dict[str, Any]] = []
    entry_rows: list[dict[str, Any]] = []

    for mode in MODES:
        continuous_seeded = {"done": False}
        print(f"=== mode={mode} entries={len(selected)} ===", flush=True)
        for ordinal, (global_index, protein_key, target_entry) in enumerate(selected, start=1):
            mutation_label = str(target_entry["mut"])
            start = time.perf_counter()
            if protein_key not in protein_cache:
                chain_id = protein_key[-1]
                pdb_path = args.pdb_dir / f"{protein_key}.pdb"
                residue_map = build_residue_index_map(pdb_path, chain_id)
                protein = load_single_chain_protein(runtime, pdb_path, chain_id)
                protein_cache[protein_key] = (protein, residue_map)
            protein, residue_map = protein_cache[protein_key]
            sequence_index = residue_map[mutation_label[:-1]]

            fields = extract_for_mode(
                mode=mode,
                runtime=runtime,
                protein=protein,
                protein_key=protein_key,
                mutation_label=mutation_label,
                sequence_index=sequence_index,
                target_entry=target_entry,
                seed=args.seed,
                global_index=global_index,
                continuous_seeded=continuous_seeded,
            )

            exact_fields = 0
            close_fields = 0
            for field in V3_TENSOR_FIELDS:
                stats = field_match(target_entry.get(field), fields.get(field))
                exact_fields += int(stats["exact_match"])
                close_fields += int(stats["allclose_1e-6"])
                detail_rows.append(
                    {
                        "mode": mode,
                        "protein_key": protein_key,
                        "mutation_label": mutation_label,
                        "global_index": global_index,
                        "field": field,
                        "exact_match": str(stats["exact_match"]),
                        "allclose_1e-6": str(stats["allclose_1e-6"]),
                        "max_abs_diff": stats["max_abs_diff"],
                        "set_overlap": stats["set_overlap"],
                        "ordered_prefix_match": stats["ordered_prefix_match"],
                    }
                )

            entry_rows.append(
                {
                    "mode": mode,
                    "protein_key": protein_key,
                    "mutation_label": mutation_label,
                    "global_index": global_index,
                    "exact_field_matches": exact_fields,
                    "allclose_field_matches": close_fields,
                    "n_fields": len(V3_TENSOR_FIELDS),
                    "elapsed_seconds": f"{time.perf_counter() - start:.3f}",
                }
            )
            print(
                f"[{ordinal}/{len(selected)}] {mode} {protein_key} {mutation_label} "
                f"exact_fields={exact_fields}/{len(V3_TENSOR_FIELDS)}",
                flush=True,
            )

    write_tsv(
        table_dir / "mode_field_comparisons.tsv",
        detail_rows,
        [
            "mode",
            "protein_key",
            "mutation_label",
            "global_index",
            "field",
            "exact_match",
            "allclose_1e-6",
            "max_abs_diff",
            "set_overlap",
            "ordered_prefix_match",
        ],
    )
    write_tsv(
        table_dir / "mode_entry_summary.tsv",
        entry_rows,
        [
            "mode",
            "protein_key",
            "mutation_label",
            "global_index",
            "exact_field_matches",
            "allclose_field_matches",
            "n_fields",
            "elapsed_seconds",
        ],
    )

    mode_summaries = {
        mode: summarize_mode(detail_rows, mode, len(selected)) for mode in MODES
    }

    comparison_rows = []
    for field in KEY_FIELDS:
        row = {"field": field}
        for mode in MODES:
            info = mode_summaries[mode]["fields"].get(field, {})
            row[f"{mode}_exact"] = info.get("exact_matches", 0)
            row[f"{mode}_allclose"] = info.get("allclose_1e-6_matches", 0)
            row[f"{mode}_n"] = info.get("n", 0)
        comparison_rows.append(row)
    write_tsv(
        table_dir / "mode_vs_baseline_key_fields.tsv",
        comparison_rows,
        [
            "field",
            "baseline_exact",
            "baseline_allclose",
            "baseline_n",
            "continuous_rng_exact",
            "continuous_rng_allclose",
            "continuous_rng_n",
            "replay_neighbors_exact",
            "replay_neighbors_allclose",
            "replay_neighbors_n",
        ],
    )

    summary = {
        "limit": args.limit,
        "seed": args.seed,
        "device": args.device,
        "selected_entries": [
            {"global_index": gi, "protein_key": pk, "mutation_label": str(e["mut"])}
            for gi, pk, e in selected
        ],
        "modes": mode_summaries,
        "headline": {
            mode: {
                "top15_neighbor_exact": mode_summaries[mode]["top15_neighbor_exact"],
                "closest15_exact": mode_summaries[mode]["closest15_exact"],
                "log_prob_allclose": mode_summaries[mode]["log_prob_allclose"],
                "n_entries": len(selected),
            }
            for mode in MODES
        },
    }
    (json_dir / "v3_slice_diagnostic_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    lines = [
        "# Ssym V3 Slice RNG / Neighbor-Replay Diagnostics",
        "",
        f"Entries: `{len(selected)}` (limit={args.limit}, seed={args.seed}, device={args.device})",
        "",
        "## Headline Match Counts",
        "",
        "| Mode | top_15_neighbor exact | closest15 exact | log_prob allclose@1e-6 |",
        "| --- | --- | --- | --- |",
    ]
    for mode in MODES:
        h = summary["headline"][mode]
        lines.append(
            f"| `{mode}` | {h['top15_neighbor_exact']}/{h['n_entries']} | "
            f"{h['closest15_exact']}/{h['n_entries']} | "
            f"{h['log_prob_allclose']}/{h['n_entries']} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation Guardrails",
            "",
            "- `continuous_rng` tests notebook-style continuous RNG consumption.",
            "- `replay_neighbors` forces saved attended-neighbor identities into the",
            "  neighbor loop; it is a diagnostic, not historical proof.",
            "- Closest-neighbor geometry matching without attended-neighbor/log_prob",
            "  matching remains the known V3 blocker pattern.",
            "",
            "## Files",
            "",
            "- `tables/mode_field_comparisons.tsv`",
            "- `tables/mode_entry_summary.tsv`",
            "- `tables/mode_vs_baseline_key_fields.tsv`",
            "- `json/v3_slice_diagnostic_summary.json`",
            "",
        ]
    )
    (output_dir / "README.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(summary["headline"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
