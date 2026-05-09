#!/usr/bin/env python3
"""Compare two pickle files by the Python values they contain.

This is meant for V3 PMPNN pickle reproduction checks. It deliberately avoids
byte-level pickle comparison because two pickle byte streams can differ while
storing the same object values.

The report is path-based and value-based:

- dict keys and list lengths are compared structurally;
- NumPy arrays are compared by shape, dtype, and element values;
- scalar mismatches include both values;
- each difference row includes the protein key, mutation index, and mutation
  label when the compared object has the V3 ``protein -> list[entry]`` shape.
"""

from __future__ import annotations

import argparse
import csv
import math
import re
from collections import Counter
from pathlib import Path
from typing import Any

from fingerprint_v3_pickles import WORKSPACE_ROOT, load_pickle_with_audit, safe_repr


DEFAULT_OUTPUT_DIR = WORKSPACE_ROOT / "pickle_analysis" / "value_level_pickle_comparison"
SUMMARY_FIELDS = [
    "target_pickle",
    "candidate_pickle",
    "output_prefix",
    "float_tolerance",
    "relative_tolerance",
    "max_differences",
    "difference_count",
    "difference_limit_reached",
    "status_counts",
    "target_type",
    "candidate_type",
]
DIFFERENCE_FIELDS = [
    "path",
    "protein_key",
    "mutation_index",
    "mutation_label",
    "field",
    "status",
    "target_summary",
    "candidate_summary",
    "details",
]


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
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def is_numpy_array(value: Any) -> bool:
    return (
        value.__class__.__module__.startswith("numpy")
        and value.__class__.__name__ == "ndarray"
    )


def is_numpy_scalar(value: Any) -> bool:
    return value.__class__.__module__.startswith("numpy") and not is_numpy_array(value)


def normalize_scalar(value: Any) -> Any:
    if is_numpy_scalar(value):
        return value.item()
    return value


def type_name(value: Any) -> str:
    cls = value.__class__
    return f"{cls.__module__}.{cls.__name__}"


def path_to_text(path: tuple[Any, ...]) -> str:
    if not path:
        return "<root>"
    text = ""
    for segment in path:
        if isinstance(segment, int):
            text += f"[{segment}]"
        else:
            key = str(segment)
            if text:
                text += "."
            text += key
    return text


def value_summary(value: Any) -> str:
    value = normalize_scalar(value)
    if is_numpy_array(value):
        return f"ndarray shape={list(value.shape)} dtype={value.dtype}"
    if isinstance(value, dict):
        return f"dict keys={len(value)}"
    if isinstance(value, list):
        return f"list length={len(value)}"
    if isinstance(value, tuple):
        return f"tuple length={len(value)}"
    return f"{type_name(value)} {safe_repr(value, 100)}"


def first_protein_and_index(path: tuple[Any, ...]) -> tuple[str, int | None]:
    protein_key = ""
    mutation_index: int | None = None
    if path and isinstance(path[0], str):
        protein_key = path[0]
    for segment in path[1:]:
        if isinstance(segment, int):
            mutation_index = segment
            break
    return protein_key, mutation_index


def field_from_path(path: tuple[Any, ...]) -> str:
    if not path:
        return "<root>"
    return str(path[-1])


def mutation_label_at(root: Any, protein_key: str, mutation_index: int | None) -> str:
    if not protein_key or mutation_index is None:
        return ""
    try:
        entry = root[protein_key][mutation_index]
    except (KeyError, IndexError, TypeError):
        return ""
    if isinstance(entry, dict):
        return str(entry.get("mut", ""))
    return ""


def numeric_scalars_match(left: Any, right: Any, atol: float, rtol: float) -> bool:
    left = normalize_scalar(left)
    right = normalize_scalar(right)
    if isinstance(left, float) or isinstance(right, float):
        left_float = float(left)
        right_float = float(right)
        if math.isnan(left_float) or math.isnan(right_float):
            return math.isnan(left_float) and math.isnan(right_float)
        if atol == 0 and rtol == 0:
            return left_float == right_float
        return math.isclose(left_float, right_float, abs_tol=atol, rel_tol=rtol)
    return left == right


def arrays_match(left: Any, right: Any, atol: float, rtol: float) -> tuple[bool, str]:
    import numpy as np

    if left.shape != right.shape:
        return False, f"shape {list(left.shape)} != {list(right.shape)}"
    if left.dtype != right.dtype:
        return False, f"dtype {left.dtype} != {right.dtype}"
    if left.size == 0:
        return True, ""

    if np.issubdtype(left.dtype, np.number) and np.issubdtype(right.dtype, np.number):
        if atol == 0 and rtol == 0:
            equal_mask = left == right
            if np.issubdtype(left.dtype, np.floating):
                equal_mask = equal_mask | (np.isnan(left) & np.isnan(right))
        else:
            equal_mask = np.isclose(left, right, atol=atol, rtol=rtol, equal_nan=True)
        if bool(np.all(equal_mask)):
            return True, ""
        diff = np.abs(left.astype(float) - right.astype(float))
        finite_diff = diff[np.isfinite(diff)]
        max_abs = float(np.max(finite_diff)) if finite_diff.size else "nan_or_inf_only"
        return False, f"differing_elements={int(left.size - np.sum(equal_mask))}; max_abs_diff={max_abs}"

    if np.array_equal(left, right, equal_nan=True):
        return True, ""
    return False, "array values differ"


class DifferenceRecorder:
    def __init__(self, target_root: Any, candidate_root: Any, max_differences: int):
        self.target_root = target_root
        self.candidate_root = candidate_root
        self.max_differences = max_differences
        self.rows: list[dict[str, Any]] = []
        self.limit_reached = False

    def add(
        self,
        path: tuple[Any, ...],
        status: str,
        target_value: Any,
        candidate_value: Any,
        details: str = "",
    ) -> None:
        if len(self.rows) >= self.max_differences:
            self.limit_reached = True
            return
        protein_key, mutation_index = first_protein_and_index(path)
        mutation_label = mutation_label_at(self.target_root, protein_key, mutation_index)
        if not mutation_label:
            mutation_label = mutation_label_at(self.candidate_root, protein_key, mutation_index)
        self.rows.append(
            {
                "path": path_to_text(path),
                "protein_key": protein_key,
                "mutation_index": "" if mutation_index is None else mutation_index,
                "mutation_label": mutation_label,
                "field": field_from_path(path),
                "status": status,
                "target_summary": value_summary(target_value),
                "candidate_summary": value_summary(candidate_value),
                "details": details,
            }
        )


def compare_values(
    target: Any,
    candidate: Any,
    path: tuple[Any, ...],
    recorder: DifferenceRecorder,
    atol: float,
    rtol: float,
) -> None:
    if recorder.limit_reached:
        return

    target = normalize_scalar(target)
    candidate = normalize_scalar(candidate)

    if is_numpy_array(target) or is_numpy_array(candidate):
        if not (is_numpy_array(target) and is_numpy_array(candidate)):
            recorder.add(path, "type_mismatch", target, candidate, "one side is a NumPy array")
            return
        matched, details = arrays_match(target, candidate, atol, rtol)
        if not matched:
            recorder.add(path, "array_mismatch", target, candidate, details)
        return

    if type(target) is not type(candidate):
        recorder.add(path, "type_mismatch", target, candidate)
        return

    if isinstance(target, dict):
        target_keys = list(target)
        candidate_keys = list(candidate)
        target_key_set = set(target_keys)
        candidate_key_set = set(candidate_keys)

        if target_keys != candidate_keys:
            recorder.add(
                path,
                "dict_key_order_mismatch",
                target_keys[:10],
                candidate_keys[:10],
                "first 10 keys shown",
            )
        for key in target_keys:
            if key not in candidate:
                recorder.add(path + (key,), "dict_key_missing_from_candidate", target[key], "")
        for key in candidate_keys:
            if key not in target:
                recorder.add(path + (key,), "dict_key_extra_in_candidate", "", candidate[key])
        for key in target_keys:
            if key in candidate_key_set:
                compare_values(target[key], candidate[key], path + (key,), recorder, atol, rtol)
        return

    if isinstance(target, (list, tuple)):
        if len(target) != len(candidate):
            recorder.add(path, "sequence_length_mismatch", target, candidate)
        for index, (target_item, candidate_item) in enumerate(zip(target, candidate)):
            compare_values(target_item, candidate_item, path + (index,), recorder, atol, rtol)
        return

    if isinstance(target, (int, float, str, bool, type(None))):
        if isinstance(target, (int, float)) or isinstance(candidate, (int, float)):
            if not numeric_scalars_match(target, candidate, atol, rtol):
                recorder.add(path, "scalar_mismatch", target, candidate)
        elif target != candidate:
            recorder.add(path, "scalar_mismatch", target, candidate)
        return

    if target != candidate:
        recorder.add(path, "value_mismatch", target, candidate)


def safe_output_prefix(target: Path, candidate: Path, requested: str | None) -> str:
    if requested:
        return requested
    raw = f"{target.stem}__vs__{candidate.stem}"
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", raw)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Value-level comparison for pickle files.")
    parser.add_argument("--target", type=Path, required=True, help="Reference pickle path.")
    parser.add_argument("--candidate", type=Path, required=True, help="Regenerated or candidate pickle path.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--output-prefix", help="Prefix for TSV output filenames.")
    parser.add_argument(
        "--float-tolerance",
        type=float,
        default=0.0,
        help="Absolute tolerance for numeric scalar and array comparisons.",
    )
    parser.add_argument(
        "--relative-tolerance",
        type=float,
        default=0.0,
        help="Relative tolerance for numeric scalar and array comparisons.",
    )
    parser.add_argument(
        "--max-differences",
        type=int,
        default=50_000,
        help="Maximum number of difference rows to write before truncating.",
    )
    parser.add_argument(
        "--fail-on-difference",
        action="store_true",
        help="Exit with status 1 if differences are found.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    target, _target_globals = load_pickle_with_audit(args.target)
    candidate, _candidate_globals = load_pickle_with_audit(args.candidate)

    recorder = DifferenceRecorder(target, candidate, args.max_differences)
    compare_values(
        target,
        candidate,
        (),
        recorder,
        args.float_tolerance,
        args.relative_tolerance,
    )

    output_prefix = safe_output_prefix(args.target, args.candidate, args.output_prefix)
    status_counts = Counter(row["status"] for row in recorder.rows)
    summary_row = {
        "target_pickle": str(args.target),
        "candidate_pickle": str(args.candidate),
        "output_prefix": output_prefix,
        "float_tolerance": args.float_tolerance,
        "relative_tolerance": args.relative_tolerance,
        "max_differences": args.max_differences,
        "difference_count": len(recorder.rows),
        "difference_limit_reached": recorder.limit_reached,
        "status_counts": dict(status_counts),
        "target_type": type_name(target),
        "candidate_type": type_name(candidate),
    }

    summary_path = args.output_dir / f"{output_prefix}_summary.tsv"
    differences_path = args.output_dir / f"{output_prefix}_differences.tsv"
    write_tsv(summary_path, [summary_row], SUMMARY_FIELDS)
    write_tsv(differences_path, recorder.rows, DIFFERENCE_FIELDS)

    print(f"Wrote {summary_path}")
    print(f"Wrote {differences_path}")
    if recorder.rows:
        print(f"Found {len(recorder.rows)} value-level differences.")
        return 1 if args.fail_on_difference else 0
    print("No value-level differences found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
