#!/usr/bin/env python3
"""Summarize value-level mismatches from the Ssym tensor-extraction run.

The all-entry tensor experiment writes one row per mutation and direct V3 tensor
field. This helper aggregates those rows by field so we can distinguish schema
success from value-level recovery.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from statistics import median
from typing import Any


WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT_TSV = (
    WORKSPACE_ROOT
    / "manuscript_codebase_mapping"
    / "tensor_extraction_codeblock_recovery"
    / "ssym_all_entries_tensor_extraction"
    / "tables"
    / "ssym_all_entries_field_schema_compare.tsv"
)
DEFAULT_OUTPUT_TSV = DEFAULT_INPUT_TSV.with_name(
    "ssym_tensor_value_mismatch_summary.tsv"
)
DEFAULT_OUTPUT_JSON = (
    WORKSPACE_ROOT
    / "manuscript_codebase_mapping"
    / "tensor_extraction_codeblock_recovery"
    / "ssym_all_entries_tensor_extraction"
    / "json"
    / "ssym_tensor_value_mismatch_summary.json"
)

SUMMARY_FIELDS = [
    "field",
    "row_count",
    "numeric_row_count",
    "exact_zero_count",
    "allclose_1e-6_count",
    "max_abs_diff",
    "median_abs_diff",
]


def load_rows(path: Path) -> list[dict[str, str]]:
    """Load the tensor field comparison TSV."""

    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def parse_diff(value: str) -> float | None:
    """Parse a numeric max-difference field, returning None for nonnumeric rows."""

    if value in {"", "NA", "shape_mismatch"}:
        return None
    return float(value)


def summarize_rows(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    """Aggregate mismatch statistics by V3 tensor field."""

    by_field: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        by_field.setdefault(row["field"], []).append(row)

    summary_rows: list[dict[str, Any]] = []
    for field, field_rows in by_field.items():
        diffs = [
            diff
            for diff in (
                parse_diff(row["max_abs_diff_vs_target"]) for row in field_rows
            )
            if diff is not None
        ]
        if diffs:
            exact_zero_count: int | str = sum(diff == 0.0 for diff in diffs)
            allclose_count: int | str = sum(diff <= 1e-6 for diff in diffs)
            max_abs_diff: float | str = max(diffs)
            median_abs_diff: float | str = median(diffs)
        else:
            exact_zero_count = "NA"
            allclose_count = "NA"
            max_abs_diff = "NA"
            median_abs_diff = "NA"

        summary_rows.append(
            {
                "field": field,
                "row_count": len(field_rows),
                "numeric_row_count": len(diffs),
                "exact_zero_count": exact_zero_count,
                "allclose_1e-6_count": allclose_count,
                "max_abs_diff": max_abs_diff,
                "median_abs_diff": median_abs_diff,
            }
        )
    return summary_rows


def write_tsv(path: Path, rows: list[dict[str, Any]]) -> None:
    """Write summary rows as TSV."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            delimiter="\t",
            fieldnames=SUMMARY_FIELDS,
            lineterminator="\n",
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-tsv", type=Path, default=DEFAULT_INPUT_TSV)
    parser.add_argument("--output-tsv", type=Path, default=DEFAULT_OUTPUT_TSV)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    args = parser.parse_args()

    rows = load_rows(args.input_tsv)
    summary_rows = summarize_rows(rows)
    write_tsv(args.output_tsv, summary_rows)

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(
        json.dumps({"field_summaries": summary_rows}, indent=2),
        encoding="utf-8",
    )
    print(json.dumps({"field_summaries": summary_rows}, indent=2))


if __name__ == "__main__":
    main()
