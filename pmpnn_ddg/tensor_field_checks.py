"""Validation helpers for recovered ProteinMPNN-DDG tensor fields."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

import numpy as np

from pmpnn_ddg.extraction import V3_TENSOR_FIELDS


SCHEMA_FIELDNAMES = [
    "field",
    "target_shape",
    "generated_shape",
    "shape_match",
    "generated_finite_numeric",
    "max_abs_diff_vs_target",
]


def is_true(value: Any) -> bool:
    """Interpret bools and TSV-loaded bool strings consistently."""

    if isinstance(value, bool):
        return value
    return str(value) == "True"


def write_tsv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    """Write dictionaries to TSV with stable string conversion."""

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


def array_shape(value: Any) -> str:
    """Return a compact shape string for saved or generated tensor-like values."""

    if isinstance(value, list) and value and isinstance(value[0], str):
        return f"list[{len(value)}]"
    return "x".join(str(dim) for dim in np.asarray(value).shape)


def finite_numeric(value: Any) -> str:
    """Return whether a tensor-like value is numeric and finite."""

    if isinstance(value, list) and value and isinstance(value[0], str):
        return "not_numeric"
    arr = np.asarray(value)
    if arr.dtype.kind not in "biufc":
        return "not_numeric"
    return str(bool(np.isfinite(arr).all()))


def max_abs_difference(left: Any, right: Any) -> str:
    """Return a diagnostic max absolute difference for shape-matched values."""

    if isinstance(left, list) and left and isinstance(left[0], str):
        return "NA"
    left_arr = np.asarray(left)
    right_arr = np.asarray(right)
    if left_arr.shape != right_arr.shape:
        return "shape_mismatch"
    if left_arr.dtype.kind not in "biufc" or right_arr.dtype.kind not in "biufc":
        return "NA"
    return f"{float(np.max(np.abs(left_arr - right_arr))):.8g}"


def schema_rows(
    target_entry: dict[str, Any],
    generated_fields: dict[str, Any],
) -> list[dict[str, Any]]:
    """Compare target and generated direct V3 tensor-field schemas."""

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


def all_shapes_match(rows: list[dict[str, Any]]) -> bool:
    """Return True when every direct V3 tensor field has the expected shape."""

    return all(is_true(row["shape_match"]) for row in rows)


def all_generated_numeric_finite(rows: list[dict[str, Any]]) -> bool:
    """Return True when every generated numeric field contains finite values."""

    return all(row["generated_finite_numeric"] in {"True", "not_numeric"} for row in rows)


def failed_fields(rows: list[dict[str, Any]]) -> str:
    """Return a compact comma-separated list of failed field names."""

    failed = [
        str(row["field"])
        for row in rows
        if not is_true(row["shape_match"])
        or row["generated_finite_numeric"] not in {"True", "not_numeric"}
    ]
    return ",".join(failed) if failed else "NA"
