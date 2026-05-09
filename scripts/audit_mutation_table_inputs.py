#!/usr/bin/env python3
"""Audit mutation/DDG table snapshots against the target V3 pickle records.

This checks the first reproducibility edge only:

    mutation/DDG input table -> initial two_level_dict mut/ddg records

It intentionally does not run ProteinMPNN, read PDB/PSSM files, or inspect
engineered features. The goal is to verify that the local table snapshots
recreate the same protein keys, mutation labels, DDG values, and entry order
that are already present in the 2022 V3 PMPNN pickle targets.
"""

from __future__ import annotations

import argparse
import csv
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from fingerprint_v3_pickles import PICKLE_SOURCE_DIR, WORKSPACE_ROOT, load_pickle_with_audit


INPUT_DIR = WORKSPACE_ROOT / "reproduction_inputs" / "mutation_ddg_tables"
DEFAULT_OUTPUT_DIR = WORKSPACE_ROOT / "pickle_analysis" / "mutation_table_audit" / "tables"


@dataclass(frozen=True)
class DatasetConfig:
    dataset: str
    table_path: Path
    target_pickle: Path
    table_kind: str


@dataclass(frozen=True)
class ParsedTable:
    records_by_protein: dict[str, list[dict[str, Any]]]
    rows_read: int
    rows_used: int


DATASETS = {
    "S_2648": DatasetConfig(
        dataset="S_2648",
        table_path=INPUT_DIR / "S_2648" / "S2648.txt",
        target_pickle=PICKLE_SOURCE_DIR / "S_2648_pmppn_info_dict_V3.pickle",
        table_kind="premps",
    ),
    "S_921": DatasetConfig(
        dataset="S_921",
        table_path=INPUT_DIR / "S_921" / "S921.txt",
        target_pickle=PICKLE_SOURCE_DIR / "S_921_pmppn_info_dict_V3.pickle",
        table_kind="premps",
    ),
    "S_669": DatasetConfig(
        dataset="S_669",
        table_path=INPUT_DIR / "S_669" / "Data_s669_with_predictions.csv",
        target_pickle=PICKLE_SOURCE_DIR / "S_669_pmppn_info_dict_V3.pickle",
        table_kind="s669_csv",
    ),
    "Ssym": DatasetConfig(
        dataset="Ssym",
        table_path=INPUT_DIR / "Ssym" / "Ssym.txt",
        target_pickle=PICKLE_SOURCE_DIR / "Ssym_pmppn_info_dict_V3.pickle",
        table_kind="ssym_forward_only",
    ),
}


def write_tsv(path: Path, rows: Iterable[dict[str, Any]], fieldnames: list[str]) -> None:
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
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def mutation_label_from_table_value(value: str) -> str:
    """Match the notebook label logic: wild + numeric position + mutant."""

    text = str(value).strip()
    match = re.search(r"-?\d+", text)
    if not match:
        raise ValueError(f"Could not parse mutation position from {value!r}")
    return f"{text[0]}{int(match.group(0))}{text[-1]}"


def add_record(
    records_by_protein: dict[str, list[dict[str, Any]]],
    protein_key: str,
    mutation: str,
    ddg: str,
) -> None:
    records_by_protein.setdefault(protein_key, []).append(
        {
            "mut": mutation_label_from_table_value(mutation),
            "ddg": float(ddg),
        }
    )


def parse_premps_table(path: Path, forward_only: bool = False) -> ParsedTable:
    records: dict[str, list[dict[str, Any]]] = {}
    rows_read = 0
    rows_used = 0

    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        for row in reader:
            rows_read += 1
            if forward_only and "forward" not in str(row.get("Label", "")):
                continue
            protein_key = f"{row['PDB Id'].lower()}{row['Mutated Chain']}"
            add_record(records, protein_key, row["Mutation_PDB"], row["DDGexp"])
            rows_used += 1

    return ParsedTable(records, rows_read, rows_used)


def parse_s669_csv(path: Path) -> ParsedTable:
    records: dict[str, list[dict[str, Any]]] = {}
    rows_read = 0

    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            rows_read += 1
            protein_and_chain = str(row["Protein"])
            protein_key = f"{protein_and_chain[:-1].lower()}{protein_and_chain[-1]}"
            add_record(records, protein_key, row["PDB_Mut"], row["DDG_checked_dir"])

    return ParsedTable(records, rows_read, rows_read)


def parse_table(config: DatasetConfig) -> ParsedTable:
    if config.table_kind == "premps":
        return parse_premps_table(config.table_path)
    if config.table_kind == "ssym_forward_only":
        return parse_premps_table(config.table_path, forward_only=True)
    if config.table_kind == "s669_csv":
        return parse_s669_csv(config.table_path)
    raise ValueError(f"Unhandled table kind: {config.table_kind}")


def target_mut_ddg_records(path: Path) -> dict[str, list[dict[str, Any]]]:
    obj, _globals_seen = load_pickle_with_audit(path)
    if not isinstance(obj, dict):
        raise TypeError(f"Expected top-level dict in {path}, found {type(obj).__name__}")

    records: dict[str, list[dict[str, Any]]] = {}
    for protein_key, entries in obj.items():
        if not isinstance(entries, list):
            raise TypeError(f"Expected list entries for {protein_key!r}")
        records[str(protein_key)] = [
            {
                "mut": entry.get("mut"),
                "ddg": float(entry.get("ddg")),
            }
            for entry in entries
            if isinstance(entry, dict)
        ]
    return records


def flatten(records: dict[str, list[dict[str, Any]]]) -> list[tuple[str, int, str, float]]:
    flat: list[tuple[str, int, str, float]] = []
    for protein_key, entries in records.items():
        for entry_index, entry in enumerate(entries):
            flat.append((protein_key, entry_index, str(entry["mut"]), float(entry["ddg"])))
    return flat


def ddg_matches(left: float, right: float, tolerance: float) -> bool:
    if math.isnan(left) or math.isnan(right):
        return math.isnan(left) and math.isnan(right)
    if tolerance == 0:
        return left == right
    return abs(left - right) <= tolerance


def first_flat_difference(
    target_flat: list[tuple[str, int, str, float]],
    generated_flat: list[tuple[str, int, str, float]],
    tolerance: float,
) -> tuple[int, str] | None:
    for index, (target_item, generated_item) in enumerate(zip(target_flat, generated_flat)):
        if target_item[:3] != generated_item[:3]:
            return index, "protein/mutation order differs"
        if not ddg_matches(target_item[3], generated_item[3], tolerance):
            return index, "DDG value differs"
    if len(target_flat) != len(generated_flat):
        return min(len(target_flat), len(generated_flat)), "flat record count differs"
    return None


def compare_dataset(
    config: DatasetConfig,
    tolerance: float,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    parsed = parse_table(config)
    target = target_mut_ddg_records(config.target_pickle)
    generated = parsed.records_by_protein

    target_keys = list(target)
    generated_keys = list(generated)
    target_key_set = set(target)
    generated_key_set = set(generated)
    differences: list[dict[str, Any]] = []

    for protein_key in sorted(target_key_set - generated_key_set):
        differences.append(
            {
                "dataset": config.dataset,
                "check": "protein_missing_from_generated",
                "protein_key": protein_key,
                "entry_index": "",
                "target_mut": "",
                "generated_mut": "",
                "target_ddg": "",
                "generated_ddg": "",
                "abs_ddg_diff": "",
                "note": "protein key exists in target V3 pickle but not parsed table",
            }
        )

    for protein_key in sorted(generated_key_set - target_key_set):
        differences.append(
            {
                "dataset": config.dataset,
                "check": "protein_extra_in_generated",
                "protein_key": protein_key,
                "entry_index": "",
                "target_mut": "",
                "generated_mut": "",
                "target_ddg": "",
                "generated_ddg": "",
                "abs_ddg_diff": "",
                "note": "protein key exists in parsed table but not target V3 pickle",
            }
        )

    mut_mismatch_count = 0
    ddg_mismatch_count = 0
    entry_count_mismatch_count = 0

    for protein_key in target_keys:
        if protein_key not in generated:
            continue
        target_entries = target[protein_key]
        generated_entries = generated[protein_key]
        if len(target_entries) != len(generated_entries):
            entry_count_mismatch_count += 1
            differences.append(
                {
                    "dataset": config.dataset,
                    "check": "entry_count_mismatch",
                    "protein_key": protein_key,
                    "entry_index": "",
                    "target_mut": "",
                    "generated_mut": "",
                    "target_ddg": len(target_entries),
                    "generated_ddg": len(generated_entries),
                    "abs_ddg_diff": "",
                    "note": "entry count differs for this protein key",
                }
            )

        for entry_index, (target_entry, generated_entry) in enumerate(
            zip(target_entries, generated_entries)
        ):
            target_ddg = float(target_entry["ddg"])
            generated_ddg = float(generated_entry["ddg"])
            if target_entry["mut"] != generated_entry["mut"]:
                mut_mismatch_count += 1
                differences.append(
                    {
                        "dataset": config.dataset,
                        "check": "mutation_label_mismatch",
                        "protein_key": protein_key,
                        "entry_index": entry_index,
                        "target_mut": target_entry["mut"],
                        "generated_mut": generated_entry["mut"],
                        "target_ddg": target_ddg,
                        "generated_ddg": generated_ddg,
                        "abs_ddg_diff": abs(target_ddg - generated_ddg),
                        "note": "same protein and entry index, different mutation label",
                    }
                )
            if not ddg_matches(target_ddg, generated_ddg, tolerance):
                ddg_mismatch_count += 1
                differences.append(
                    {
                        "dataset": config.dataset,
                        "check": "ddg_mismatch",
                        "protein_key": protein_key,
                        "entry_index": entry_index,
                        "target_mut": target_entry["mut"],
                        "generated_mut": generated_entry["mut"],
                        "target_ddg": target_ddg,
                        "generated_ddg": generated_ddg,
                        "abs_ddg_diff": abs(target_ddg - generated_ddg),
                        "note": "same protein and entry index, different DDG value",
                    }
                )

    target_flat = flatten(target)
    generated_flat = flatten(generated)
    first_order_difference = first_flat_difference(target_flat, generated_flat, tolerance)
    if first_order_difference is not None:
        flat_index, note = first_order_difference
        differences.append(
            {
                "dataset": config.dataset,
                "check": "first_flat_order_difference",
                "protein_key": "",
                "entry_index": flat_index,
                "target_mut": target_flat[flat_index][2] if flat_index < len(target_flat) else "",
                "generated_mut": (
                    generated_flat[flat_index][2] if flat_index < len(generated_flat) else ""
                ),
                "target_ddg": target_flat[flat_index][3] if flat_index < len(target_flat) else "",
                "generated_ddg": (
                    generated_flat[flat_index][3] if flat_index < len(generated_flat) else ""
                ),
                "abs_ddg_diff": "",
                "note": note,
            }
        )

    summary = {
        "dataset": config.dataset,
        "table_path": str(config.table_path.relative_to(WORKSPACE_ROOT)),
        "target_pickle": str(config.target_pickle.relative_to(WORKSPACE_ROOT)),
        "table_kind": config.table_kind,
        "float_tolerance": tolerance,
        "input_rows_read": parsed.rows_read,
        "input_rows_used": parsed.rows_used,
        "target_protein_count": len(target),
        "generated_protein_count": len(generated),
        "target_entry_count": len(target_flat),
        "generated_entry_count": len(generated_flat),
        "protein_key_set_match": target_key_set == generated_key_set,
        "protein_order_match": target_keys == generated_keys,
        "flat_record_order_match": first_order_difference is None,
        "entry_count_mismatch_count": entry_count_mismatch_count,
        "mutation_label_mismatch_count": mut_mismatch_count,
        "ddg_mismatch_count": ddg_mismatch_count,
        "missing_protein_count": len(target_key_set - generated_key_set),
        "extra_protein_count": len(generated_key_set - target_key_set),
        "mut_ddg_match_with_tolerance": not differences,
    }
    return summary, differences


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit local mutation/DDG snapshots against V3 pickle mut/ddg records."
    )
    parser.add_argument(
        "--dataset",
        action="append",
        choices=sorted(DATASETS),
        help="Dataset to audit. Repeat to audit multiple datasets. Default: all.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for TSV outputs.",
    )
    parser.add_argument(
        "--float-tolerance",
        type=float,
        default=1e-12,
        help=(
            "Absolute tolerance for DDG comparison. Default: 1e-12 to ignore "
            "decimal-to-binary float round-trip noise; use 0 for exact float equality."
        ),
    )
    parser.add_argument(
        "--fail-on-mismatch",
        action="store_true",
        help="Exit with status 1 if any audited dataset has a mismatch.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    datasets = args.dataset or sorted(DATASETS)

    summary_rows: list[dict[str, Any]] = []
    difference_rows: list[dict[str, Any]] = []

    for dataset in datasets:
        summary, differences = compare_dataset(DATASETS[dataset], args.float_tolerance)
        summary_rows.append(summary)
        difference_rows.extend(differences)

    write_tsv(
        args.output_dir / "mutation_table_audit_summary.tsv",
        summary_rows,
        [
            "dataset",
            "table_path",
            "target_pickle",
            "table_kind",
            "float_tolerance",
            "input_rows_read",
            "input_rows_used",
            "target_protein_count",
            "generated_protein_count",
            "target_entry_count",
            "generated_entry_count",
            "protein_key_set_match",
            "protein_order_match",
            "flat_record_order_match",
            "entry_count_mismatch_count",
            "mutation_label_mismatch_count",
            "ddg_mismatch_count",
            "missing_protein_count",
            "extra_protein_count",
            "mut_ddg_match_with_tolerance",
        ],
    )
    write_tsv(
        args.output_dir / "mutation_table_audit_differences.tsv",
        difference_rows,
        [
            "dataset",
            "check",
            "protein_key",
            "entry_index",
            "target_mut",
            "generated_mut",
            "target_ddg",
            "generated_ddg",
            "abs_ddg_diff",
            "note",
        ],
    )

    print(f"Wrote {args.output_dir / 'mutation_table_audit_summary.tsv'}")
    print(f"Wrote {args.output_dir / 'mutation_table_audit_differences.tsv'}")
    mismatched = [row["dataset"] for row in summary_rows if not row["mut_ddg_match_with_tolerance"]]
    if mismatched:
        print(f"Datasets with mutation-table mismatches: {', '.join(mismatched)}")
        return 1 if args.fail_on_mismatch else 0
    print("All audited mutation tables match target V3 mut/ddg records within tolerance.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
