#!/usr/bin/env python3
"""Run the Ssym engineered/PSSM feature-reconstruction experiment.

This is the Set 2 experiment after direct tensor-field recovery. It starts from
the saved Ssym V3 pickle entries, recomputes the engineered and PSSM fields from
their direct tensor fields plus local PSSM files, and compares the reconstructed
values against the same saved V3 entries.

It does not rerun ProteinMPNN tensor extraction and it does not write a new V3
pickle. That boundary keeps this experiment focused on the feature-construction
segment only.
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

WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from proteinmpnn_ddg_recovery.engineered_features import (  # noqa: E402
    DEFAULT_SSYM_PSSM_DIR,
    V3_ENGINEERED_AND_PSSM_FIELDS,
    compute_v3_engineered_and_pssm_features,
)
from proteinmpnn_ddg_recovery.recovered_v6v2 import (  # noqa: E402
    DEFAULT_SSYM_PDB_DIR,
    build_residue_index_map,
)
from proteinmpnn_ddg_recovery.tensor_field_checks import write_tsv  # noqa: E402


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
    / "engineered_feature_recovery"
    / "ssym_engineered_pssm_feature_reconstruction"
)

FIELD_COMPARISON_FIELDNAMES = [
    "protein_key",
    "mutation_label",
    "sequence_index",
    "field",
    "target_shape",
    "reconstructed_shape",
    "shape_match",
    "exact_equal",
    "allclose_atol_1e-6_rtol_1e-6",
    "max_abs_diff",
    "target_dtype",
    "reconstructed_dtype",
]
MUTATION_STATUS_FIELDNAMES = [
    "protein_key",
    "mutation_label",
    "sequence_index",
    "status",
    "failed_fields",
    "max_abs_diff",
    "error_type",
    "error_message",
]


def load_pickle(path: Path) -> dict[str, list[dict[str, Any]]]:
    with path.open("rb") as handle:
        return pickle.load(handle)


def target_entries(
    target: dict[str, list[dict[str, Any]]],
    protein_key_filter: str | None,
    limit: int | None,
) -> list[tuple[str, dict[str, Any]]]:
    selected: list[tuple[str, dict[str, Any]]] = []
    for protein_key, entries in target.items():
        if protein_key_filter is not None and protein_key != protein_key_filter:
            continue
        for entry in entries:
            selected.append((protein_key, entry))
            if limit is not None and len(selected) >= limit:
                return selected
    return selected


def array_shape(value: Any) -> str:
    shape = np.asarray(value).shape
    return "scalar" if shape == () else "x".join(str(dim) for dim in shape)


def max_abs_difference(left: Any, right: Any) -> str:
    left_arr = np.asarray(left)
    right_arr = np.asarray(right)
    if left_arr.shape != right_arr.shape:
        return "shape_mismatch"
    if left_arr.dtype.kind not in "biufc" or right_arr.dtype.kind not in "biufc":
        return "NA"
    if left_arr.shape == ():
        return f"{float(abs(left_arr.item() - right_arr.item())):.12g}"
    return f"{float(np.max(np.abs(left_arr - right_arr))):.12g}"


def field_comparison_rows(
    protein_key: str,
    mutation_label: str,
    sequence_index: int,
    target_entry: dict[str, Any],
    reconstructed: dict[str, Any],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for field in V3_ENGINEERED_AND_PSSM_FIELDS:
        target_value = target_entry[field]
        reconstructed_value = reconstructed[field]
        target_array = np.asarray(target_value)
        reconstructed_array = np.asarray(reconstructed_value)
        shape_match = target_array.shape == reconstructed_array.shape
        exact_equal = shape_match and bool(np.array_equal(target_array, reconstructed_array))
        allclose = (
            shape_match
            and target_array.dtype.kind in "biufc"
            and reconstructed_array.dtype.kind in "biufc"
            and bool(np.allclose(target_array, reconstructed_array, atol=1e-6, rtol=1e-6))
        )
        rows.append(
            {
                "protein_key": protein_key,
                "mutation_label": mutation_label,
                "sequence_index": sequence_index,
                "field": field,
                "target_shape": array_shape(target_value),
                "reconstructed_shape": array_shape(reconstructed_value),
                "shape_match": shape_match,
                "exact_equal": exact_equal,
                "allclose_atol_1e-6_rtol_1e-6": allclose,
                "max_abs_diff": max_abs_difference(target_value, reconstructed_value),
                "target_dtype": str(target_array.dtype),
                "reconstructed_dtype": str(reconstructed_array.dtype),
            }
        )
    return rows


def mutation_status_row(
    protein_key: str,
    mutation_label: str,
    sequence_index: int,
    rows: list[dict[str, Any]],
) -> dict[str, Any]:
    failed_fields = [
        str(row["field"])
        for row in rows
        if str(row["allclose_atol_1e-6_rtol_1e-6"]) != "True"
    ]
    numeric_diffs = []
    for row in rows:
        value = str(row["max_abs_diff"])
        if value not in {"NA", "shape_mismatch"}:
            numeric_diffs.append(float(value))
    return {
        "protein_key": protein_key,
        "mutation_label": mutation_label,
        "sequence_index": sequence_index,
        "status": "ok" if not failed_fields else "mismatch",
        "failed_fields": ",".join(failed_fields) if failed_fields else "NA",
        "max_abs_diff": max(numeric_diffs) if numeric_diffs else "NA",
        "error_type": "NA",
        "error_message": "NA",
    }


def error_status_row(
    protein_key: str,
    mutation_label: str,
    error: Exception,
) -> dict[str, Any]:
    return {
        "protein_key": protein_key,
        "mutation_label": mutation_label,
        "sequence_index": "NA",
        "status": "error",
        "failed_fields": "NA",
        "max_abs_diff": "NA",
        "error_type": type(error).__name__,
        "error_message": str(error),
    }


def build_summary(
    selected_count: int,
    mutation_rows: list[dict[str, Any]],
    field_rows: list[dict[str, Any]],
    target_pickle: Path,
    pdb_dir: Path,
    pssm_dir: Path,
) -> dict[str, Any]:
    ok_rows = [row for row in mutation_rows if row["status"] == "ok"]
    mismatch_rows = [row for row in mutation_rows if row["status"] == "mismatch"]
    error_rows = [row for row in mutation_rows if row["status"] == "error"]
    mismatched_field_counts: dict[str, int] = {}
    exact_match_count = 0
    allclose_count = 0
    for row in field_rows:
        if str(row["exact_equal"]) == "True":
            exact_match_count += 1
        if str(row["allclose_atol_1e-6_rtol_1e-6"]) == "True":
            allclose_count += 1
        else:
            field = str(row["field"])
            mismatched_field_counts[field] = mismatched_field_counts.get(field, 0) + 1

    max_abs_diff = "NA"
    numeric_diffs = [
        float(str(row["max_abs_diff"]))
        for row in field_rows
        if str(row["max_abs_diff"]) not in {"NA", "shape_mismatch"}
    ]
    if numeric_diffs:
        max_abs_diff = max(numeric_diffs)

    return {
        "target_entry_count": selected_count,
        "processed_entry_count": len(mutation_rows),
        "ok_entry_count": len(ok_rows),
        "mismatch_entry_count": len(mismatch_rows),
        "error_entry_count": len(error_rows),
        "field_comparison_count": len(field_rows),
        "exact_field_match_count": exact_match_count,
        "allclose_field_match_count": allclose_count,
        "all_entries_passed": (
            len(ok_rows) == selected_count and not mismatch_rows and not error_rows
        ),
        "mismatched_field_counts": mismatched_field_counts,
        "max_abs_diff": max_abs_diff,
        "target_pickle": str(target_pickle.relative_to(WORKSPACE_ROOT)),
        "pdb_dir": str(pdb_dir.relative_to(WORKSPACE_ROOT)),
        "pssm_dir": str(pssm_dir.relative_to(WORKSPACE_ROOT)),
        "field_order": V3_ENGINEERED_AND_PSSM_FIELDS,
    }


def write_report(output_dir: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# Ssym Engineered/PSSM Feature Reconstruction",
        "",
        "Scope: recompute the saved Ssym V3 engineered and PSSM fields from",
        "the saved direct tensor fields plus the copied local Ssym PSSM files.",
        "This is the feature-construction segment only; it does not rerun",
        "ProteinMPNN tensor extraction and does not write a replacement pickle.",
        "",
        "## Result",
        "",
        f"- Target mutation entries: `{summary['target_entry_count']}`",
        f"- Successful entries: `{summary['ok_entry_count']}`",
        f"- Mismatch entries: `{summary['mismatch_entry_count']}`",
        f"- Runtime errors: `{summary['error_entry_count']}`",
        f"- Field comparisons: `{summary['field_comparison_count']}`",
        f"- Exact field matches: `{summary['exact_field_match_count']}`",
        f"- Allclose field matches at `atol=1e-6, rtol=1e-6`: "
        f"`{summary['allclose_field_match_count']}`",
        f"- All selected entries passed: `{summary['all_entries_passed']}`",
        f"- Maximum absolute difference: `{summary['max_abs_diff']}`",
        "",
        "## Inputs",
        "",
        f"- Target pickle: `{summary['target_pickle']}`",
        f"- PDB directory used for residue-index mapping: `{summary['pdb_dir']}`",
        f"- PSSM directory: `{summary['pssm_dir']}`",
        "",
        "## Important Recovery Detail",
        "",
        "The old notebook stores message-norm ratio weights as one-element arrays.",
        "For several weighted neighbor scalar features, NumPy therefore broadcasts",
        "a `(15,)` value vector against a `(15, 1)` weight vector. The recovery",
        "module preserves that behavior because flattening the weights changes the",
        "saved V3 values.",
        "",
        "## Tables",
        "",
        "- `tables/ssym_engineered_pssm_mutation_status.tsv`",
        "- `tables/ssym_engineered_pssm_field_compare.tsv`",
        "- `json/ssym_engineered_pssm_feature_reconstruction_summary.json`",
        "",
    ]
    if summary["mismatched_field_counts"]:
        lines.extend(["## Mismatched Fields", ""])
        for field, count in sorted(summary["mismatched_field_counts"].items()):
            lines.append(f"- `{field}`: `{count}`")
        lines.append("")

    (output_dir / "SSYM_ENGINEERED_PSSM_FEATURE_RECONSTRUCTION.md").write_text(
        "\n".join(lines),
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target-pickle", type=Path, default=DEFAULT_TARGET_PICKLE)
    parser.add_argument("--pdb-dir", type=Path, default=DEFAULT_SSYM_PDB_DIR)
    parser.add_argument("--pssm-dir", type=Path, default=DEFAULT_SSYM_PSSM_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--protein-key", default=None)
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    target = load_pickle(args.target_pickle)
    selected = target_entries(target, args.protein_key, args.limit)
    residue_maps: dict[str, dict[str, int]] = {}
    mutation_rows: list[dict[str, Any]] = []
    field_rows: list[dict[str, Any]] = []

    for protein_key, entry in selected:
        mutation_label = str(entry["mut"])
        try:
            if protein_key not in residue_maps:
                residue_maps[protein_key] = build_residue_index_map(
                    args.pdb_dir / f"{protein_key}.pdb",
                    protein_key[-1],
                )
            sequence_index = residue_maps[protein_key][mutation_label[:-1]]
            reconstructed = compute_v3_engineered_and_pssm_features(
                protein_key,
                entry,
                sequence_index,
                args.pssm_dir,
            )
            rows = field_comparison_rows(
                protein_key,
                mutation_label,
                sequence_index,
                entry,
                reconstructed,
            )
            field_rows.extend(rows)
            mutation_rows.append(
                mutation_status_row(protein_key, mutation_label, sequence_index, rows)
            )
        except Exception as error:  # noqa: BLE001 - experiment table should capture all failures.
            mutation_rows.append(error_status_row(protein_key, mutation_label, error))

    output_dir = args.output_dir
    table_dir = output_dir / "tables"
    json_dir = output_dir / "json"
    table_dir.mkdir(parents=True, exist_ok=True)
    json_dir.mkdir(parents=True, exist_ok=True)

    write_tsv(
        table_dir / "ssym_engineered_pssm_mutation_status.tsv",
        mutation_rows,
        MUTATION_STATUS_FIELDNAMES,
    )
    write_tsv(
        table_dir / "ssym_engineered_pssm_field_compare.tsv",
        field_rows,
        FIELD_COMPARISON_FIELDNAMES,
    )

    summary = build_summary(
        len(selected),
        mutation_rows,
        field_rows,
        args.target_pickle,
        args.pdb_dir,
        args.pssm_dir,
    )
    (json_dir / "ssym_engineered_pssm_feature_reconstruction_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_report(output_dir, summary)

    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
