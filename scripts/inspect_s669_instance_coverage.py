#!/usr/bin/env python3
"""Inspect S_669 V3 instance-level feature coverage.

This script reads only workspace-local copied pickle evidence. It checks which
S_669 mutation entries contain the fields required by the RF feature-matrix
assembly code in ``Quick_Dirty_MPNN_ML_V2_VGRAPHS_V1.ipynb.py.txt`` and reports
what remains on the entries that lack ProteinMPNN-derived feature records.
"""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

from fingerprint_v3_pickles import (
    EXPECTED_GENERATOR_FIELDS,
    PICKLE_SOURCE_DIR,
    WORKSPACE_ROOT,
    iter_entry_dicts,
    load_pickle_with_audit,
    normalize_protein_key,
    type_name,
)


ANALYSIS_DIR = WORKSPACE_ROOT / "pickle_analysis" / "s669_instance_coverage"
TABLE_DIR = ANALYSIS_DIR / "tables"

S669_V3 = PICKLE_SOURCE_DIR / "S_669_pmppn_info_dict_V3.pickle"
S669_FULL_FEATURE = PICKLE_SOURCE_DIR / "S_669_full_feature_dict.pickle"

PSSM_FIELDS = {
    "wild_pssm",
    "alternate_pssm",
}

RF_ASSEMBLY_REQUIRED_FIELDS = {
    "ddg",
    "center_mut_wild_energy",
    "center_entropy",
    "V2_backward_weighted_neighbor_energy_changes",
    "weighted_neighbor_forward_KL",
    "V2_backward_weighted_neighbor_backward_KL",
    "wild_pssm",
    "alternate_pssm",
    "V2_backward_weighted_neighbor_entropy_changes",
    "center_neighbor_weight_check_w_m",
    "neighbor_embedding_change_m_w",
    "neighbor_embedding_change_m_w_raw",
    "neighbor_message_change_m_w_raw",
    "neighbor_w_neighbor_embedding",
    "neighbor_m_neighbor_embedding",
    "neighbor_w_message_vector_coming_from_center",
    "neighbor_m_message_vector_coming_from_center",
}


def write_tsv(path: Path, rows: Iterable[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def compact_value_summary(value: Any) -> str:
    if value.__class__.__module__.startswith("numpy") and value.__class__.__name__ == "ndarray":
        return f"ndarray shape={list(value.shape)} dtype={value.dtype}"
    if isinstance(value, list):
        child_types = Counter(type_name(item) for item in value[:20])
        return f"list length={len(value)} child_types={dict(child_types.most_common())}"
    if isinstance(value, tuple):
        child_types = Counter(type_name(item) for item in value[:20])
        return f"tuple length={len(value)} child_types={dict(child_types.most_common())}"
    return type_name(value)


def entry_id(protein_key: str, entry: dict[Any, Any], entry_index: int) -> tuple[str, str, int, str]:
    return (
        str(protein_key),
        normalize_protein_key(str(protein_key)),
        entry_index,
        str(entry.get("mut", "")),
    )


def build_full_feature_lookup(full_feature_obj: Any) -> dict[tuple[str, int, str], dict[Any, Any]]:
    lookup: dict[tuple[str, int, str], dict[Any, Any]] = {}
    for protein_key, entry_index, entry in iter_entry_dicts(full_feature_obj):
        _, normalized, _, mut = entry_id(protein_key, entry, entry_index)
        lookup[(normalized, entry_index, mut)] = entry
    return lookup


def main() -> None:
    TABLE_DIR.mkdir(parents=True, exist_ok=True)

    v3_obj, _ = load_pickle_with_audit(S669_V3)
    full_feature_obj, _ = load_pickle_with_audit(S669_FULL_FEATURE)
    full_feature_lookup = build_full_feature_lookup(full_feature_obj)

    entry_rows: list[dict[str, Any]] = []
    field_rows: list[dict[str, Any]] = []
    protein_summary: dict[str, Counter[str]] = defaultdict(Counter)

    for protein_key, entry_index, entry in iter_entry_dicts(v3_obj):
        protein, normalized, _, mut = entry_id(protein_key, entry, entry_index)
        fields = {str(key) for key in entry}
        missing_pmpnn = sorted(EXPECTED_GENERATOR_FIELDS - fields)
        missing_rf = sorted(RF_ASSEMBLY_REQUIRED_FIELDS - fields)
        missing_pssm = sorted(PSSM_FIELDS - fields)
        has_pmpnn_record = not missing_pmpnn
        has_rf_required_fields = not missing_rf
        has_pssm_fields = not missing_pssm

        protein_summary[protein]["entry_count"] += 1
        protein_summary[protein]["pmpnn_record_count"] += int(has_pmpnn_record)
        protein_summary[protein]["rf_required_count"] += int(has_rf_required_fields)
        protein_summary[protein]["pssm_count"] += int(has_pssm_fields)

        full_feature_entry = full_feature_lookup.get((normalized, entry_index, mut))
        full_feature_fields = (
            sorted(str(key) for key in full_feature_entry)
            if isinstance(full_feature_entry, dict)
            else []
        )

        entry_rows.append(
            {
                "protein_key": protein,
                "normalized_protein_key": normalized,
                "entry_index": entry_index,
                "mut": mut,
                "ddg": entry.get("ddg", ""),
                "has_pmpnn_feature_record": has_pmpnn_record,
                "has_rf_assembly_required_fields": has_rf_required_fields,
                "has_pssm_fields_in_v3": has_pssm_fields,
                "missing_pmpnn_fields": json.dumps(missing_pmpnn),
                "missing_rf_assembly_fields": json.dumps(missing_rf),
                "missing_pssm_fields_in_v3": json.dumps(missing_pssm),
                "v3_field_count": len(fields),
                "v3_fields": json.dumps(sorted(fields)),
                "matched_full_feature_entry": isinstance(full_feature_entry, dict),
                "full_feature_field_count": len(full_feature_fields),
                "full_feature_fields": json.dumps(full_feature_fields),
            }
        )

        if normalized == "3dv0i":
            for key in sorted(fields):
                field_rows.append(
                    {
                        "protein_key": protein,
                        "entry_index": entry_index,
                        "mut": mut,
                        "field": key,
                        "value_summary": compact_value_summary(entry[key]),
                    }
                )

    summary_rows: list[dict[str, Any]] = []
    for protein_key, counts in sorted(protein_summary.items()):
        entry_count = counts["entry_count"]
        summary_rows.append(
            {
                "protein_key": protein_key,
                "entry_count": entry_count,
                "pmpnn_feature_record_count": counts["pmpnn_record_count"],
                "rf_assembly_required_count": counts["rf_required_count"],
                "pssm_field_count": counts["pssm_count"],
                "missing_pmpnn_feature_record_count": entry_count - counts["pmpnn_record_count"],
                "missing_rf_assembly_required_count": entry_count - counts["rf_required_count"],
                "missing_pssm_field_count": entry_count - counts["pssm_count"],
            }
        )

    write_tsv(
        TABLE_DIR / "s669_v3_entry_feature_completeness.tsv",
        entry_rows,
        [
            "protein_key",
            "normalized_protein_key",
            "entry_index",
            "mut",
            "ddg",
            "has_pmpnn_feature_record",
            "has_rf_assembly_required_fields",
            "has_pssm_fields_in_v3",
            "missing_pmpnn_fields",
            "missing_rf_assembly_fields",
            "missing_pssm_fields_in_v3",
            "v3_field_count",
            "v3_fields",
            "matched_full_feature_entry",
            "full_feature_field_count",
            "full_feature_fields",
        ],
    )
    write_tsv(
        TABLE_DIR / "s669_v3_feature_completeness_by_protein.tsv",
        summary_rows,
        [
            "protein_key",
            "entry_count",
            "pmpnn_feature_record_count",
            "rf_assembly_required_count",
            "pssm_field_count",
            "missing_pmpnn_feature_record_count",
            "missing_rf_assembly_required_count",
            "missing_pssm_field_count",
        ],
    )
    write_tsv(
        TABLE_DIR / "s669_3dv0i_v3_remaining_fields.tsv",
        field_rows,
        ["protein_key", "entry_index", "mut", "field", "value_summary"],
    )


if __name__ == "__main__":
    main()
