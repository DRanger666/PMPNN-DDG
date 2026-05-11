#!/usr/bin/env python3
"""Inspect historical feature-combination model pickle artifacts.

The two large model pickles may preserve trained RF/ML models that explain
manuscript-era result generation. This script loads them one at a time,
summarizes their structure, extracts estimator metadata, and writes compact
JSON/TSV/Markdown reports.

This script intentionally does not modify the copied evidence files.
"""

from __future__ import annotations

import csv
import gc
import json
import math
import pickle
import statistics
import sys
import warnings
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

try:
    import numpy as np
except Exception:  # pragma: no cover - optional at import time
    np = None  # type: ignore[assignment]


WORKSPACE = Path(__file__).resolve().parents[1]
EVIDENCE_ROOT = (
    WORKSPACE
    / "drive_evidence_copy"
    / "sajidahmedprotres_drive"
    / "Protein_MPNN_Digging"
)
OUTPUT_DIR = WORKSPACE / "code_inventory_analysis" / "feature_combo_pickle_inspection"

MODEL_PICKLES = [
    "feature_combo_model_dict.pickle",
    "S_669_feature_combo_model_dict.pickle",
]

CONTEXT_PICKLES = [
    "feature_combo_result_dict.pickle",
    "S_669_feature_combo_result_dict.pickle",
    "incremental_feature_result_dict.pickle",
    "list_incremental_feature_result_dict.pickle",
    "res_dict.pickle",
]

RESULT_ENTRY_PICKLES = {
    "feature_combo_result_dict.pickle",
    "S_669_feature_combo_result_dict.pickle",
    "incremental_feature_result_dict.pickle",
    "list_incremental_feature_result_dict.pickle",
}

IMPORTANT_PARAM_NAMES = [
    "n_estimators",
    "criterion",
    "max_depth",
    "max_features",
    "min_samples_leaf",
    "min_samples_split",
    "bootstrap",
    "oob_score",
    "random_state",
    "n_jobs",
]


def write_tsv(path: Path, rows: Iterable[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fields,
            delimiter="\t",
            extrasaction="ignore",
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def rel_workspace(path: Path) -> str:
    return path.relative_to(WORKSPACE).as_posix()


def type_name(value: Any) -> str:
    cls = value.__class__
    return f"{cls.__module__}.{cls.__name__}"


def safe_repr(value: Any, max_len: int = 200) -> str:
    try:
        text = repr(value)
    except Exception as exc:
        text = f"<repr failed: {exc!r}>"
    if len(text) > max_len:
        return text[: max_len - 3] + "..."
    return text


def json_safe(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, bool)):
        return value
    if isinstance(value, float):
        if math.isfinite(value):
            return value
        return repr(value)
    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(v) for v in value]
    if np is not None and isinstance(value, np.ndarray):
        return {
            "type": "numpy.ndarray",
            "shape": list(value.shape),
            "dtype": str(value.dtype),
        }
    if hasattr(value, "item"):
        try:
            return json_safe(value.item())
        except Exception:
            pass
    return safe_repr(value)


def load_pickle(path: Path) -> tuple[Any, dict[str, Any]]:
    captured_warnings: list[str] = []
    with warnings.catch_warnings(record=True) as records:
        warnings.simplefilter("always")
        with path.open("rb") as handle:
            obj = pickle.load(handle)
        for record in records:
            captured_warnings.append(str(record.message))
    warning_counts = Counter(captured_warnings)
    warning_summary = {
        "count": len(captured_warnings),
        "unique_count": len(warning_counts),
        "unique_preview": [
            {"message": message, "count": count}
            for message, count in warning_counts.most_common(20)
        ],
    }
    return obj, warning_summary


def is_estimator(value: Any) -> bool:
    return callable(getattr(value, "predict", None)) and callable(getattr(value, "get_params", None))


def limited_sequence_summary(values: Iterable[Any], limit: int = 20) -> list[str]:
    out: list[str] = []
    for idx, value in enumerate(values):
        if idx >= limit:
            break
        out.append(safe_repr(value))
    return out


def summarize_object_shape(value: Any, max_key_preview: int = 20) -> dict[str, Any]:
    summary: dict[str, Any] = {
        "type": type_name(value),
    }
    if isinstance(value, dict):
        summary["len"] = len(value)
        summary["key_type_counts"] = dict(Counter(type_name(k) for k in value.keys()))
        summary["value_type_counts"] = dict(Counter(type_name(v) for v in value.values()))
        summary["key_preview"] = limited_sequence_summary(value.keys(), max_key_preview)
    elif isinstance(value, (list, tuple)):
        summary["len"] = len(value)
        summary["item_type_counts"] = dict(Counter(type_name(v) for v in value))
        summary["item_preview"] = limited_sequence_summary(value, max_key_preview)
    else:
        if hasattr(value, "shape"):
            summary["shape"] = list(getattr(value, "shape"))
        if hasattr(value, "dtype"):
            summary["dtype"] = str(getattr(value, "dtype"))
        summary["repr"] = safe_repr(value)
    return summary


def find_estimators(value: Any, path: str = "root", depth: int = 0, max_depth: int = 5) -> list[tuple[str, Any]]:
    if is_estimator(value):
        return [(path, value)]
    if depth >= max_depth:
        return []

    found: list[tuple[str, Any]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            found.extend(find_estimators(child, f"{path}[{safe_repr(key, 80)}]", depth + 1, max_depth))
    elif isinstance(value, (list, tuple)):
        for idx, child in enumerate(value):
            found.extend(find_estimators(child, f"{path}[{idx}]", depth + 1, max_depth))
    return found


def numeric_array_stats(value: Any, top_n: int = 10) -> dict[str, Any]:
    if np is None:
        return {}
    arr = np.asarray(value)
    if arr.size == 0:
        return {"shape": list(arr.shape), "dtype": str(arr.dtype), "size": 0}
    flat = arr.astype(float, copy=False).ravel()
    order = np.argsort(flat)[::-1][:top_n]
    return {
        "shape": list(arr.shape),
        "dtype": str(arr.dtype),
        "size": int(arr.size),
        "sum": float(np.nansum(flat)),
        "min": float(np.nanmin(flat)),
        "max": float(np.nanmax(flat)),
        "mean": float(np.nanmean(flat)),
        "top_indices": [int(i) for i in order.tolist()],
        "top_values": [float(flat[i]) for i in order.tolist()],
    }


def tree_stats(model: Any) -> dict[str, Any]:
    estimators = getattr(model, "estimators_", None)
    if estimators is None:
        return {}
    try:
        estimator_list = list(estimators)
    except TypeError:
        return {"estimators_repr": safe_repr(estimators)}
    node_counts: list[int] = []
    max_depths: list[int] = []
    for estimator in estimator_list:
        tree = getattr(estimator, "tree_", None)
        if tree is None:
            continue
        node_counts.append(int(getattr(tree, "node_count", 0)))
        max_depths.append(int(getattr(tree, "max_depth", 0)))
    stats: dict[str, Any] = {"estimators_len": len(estimator_list)}
    if node_counts:
        stats.update(
            {
                "tree_node_count_min": min(node_counts),
                "tree_node_count_max": max(node_counts),
                "tree_node_count_mean": statistics.mean(node_counts),
                "tree_max_depth_min": min(max_depths),
                "tree_max_depth_max": max(max_depths),
                "tree_max_depth_mean": statistics.mean(max_depths),
            }
        )
    return stats


def estimator_summary(model: Any) -> dict[str, Any]:
    summary: dict[str, Any] = {
        "model_class": type_name(model),
        "repr": safe_repr(model, 500),
    }
    try:
        params = model.get_params(deep=False)
        summary["important_params"] = {
            name: json_safe(params.get(name))
            for name in IMPORTANT_PARAM_NAMES
            if name in params
        }
    except Exception as exc:
        summary["get_params_error"] = repr(exc)

    for attr in ["n_features_in_", "n_outputs_", "classes_", "n_classes_"]:
        if hasattr(model, attr):
            summary[attr] = json_safe(getattr(model, attr))

    if hasattr(model, "feature_importances_"):
        try:
            summary["feature_importances"] = numeric_array_stats(getattr(model, "feature_importances_"))
        except Exception as exc:
            summary["feature_importances_error"] = repr(exc)

    summary["tree_stats"] = tree_stats(model)
    fitted_attrs = sorted(name for name in dir(model) if name.endswith("_") and not name.startswith("__"))
    summary["fitted_attrs"] = fitted_attrs[:80]
    return summary


def top_level_entry_rows(filename: str, obj: Any) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    if not isinstance(obj, dict):
        for model_path, model in find_estimators(obj):
            summary = estimator_summary(model)
            rows.append(model_row(filename, "", "", type_name(obj), model_path, summary))
        return rows

    for key, value in obj.items():
        estimators = find_estimators(value, "value")
        if not estimators and is_estimator(value):
            estimators = [("value", value)]
        for model_path, model in estimators:
            summary = estimator_summary(model)
            rows.append(
                model_row(
                    filename,
                    safe_repr(key, 250),
                    type_name(key),
                    type_name(value),
                    model_path,
                    summary,
                )
            )
    return rows


def is_numeric_scalar(value: Any) -> bool:
    if isinstance(value, bool):
        return False
    if isinstance(value, (int, float)):
        return True
    if np is not None and isinstance(value, np.generic):
        return np.issubdtype(value.dtype, np.number)
    return False


def flatten_numeric_result_rows(
    filename: str,
    value: Any,
    path: str = "root",
    depth: int = 0,
    max_depth: int = 8,
) -> list[dict[str, object]]:
    if is_numeric_scalar(value):
        return [
            {
                "pickle_file": filename,
                "result_path": path,
                "value": float(value),
            }
        ]
    if depth >= max_depth:
        return []

    rows: list[dict[str, object]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            rows.extend(
                flatten_numeric_result_rows(
                    filename,
                    child,
                    f"{path}.{safe_repr(key, 120)}",
                    depth + 1,
                    max_depth,
                )
            )
    elif isinstance(value, (list, tuple)):
        for idx, child in enumerate(value):
            rows.extend(
                flatten_numeric_result_rows(
                    filename,
                    child,
                    f"{path}[{idx}]",
                    depth + 1,
                    max_depth,
                )
            )
    return rows


def model_row(
    filename: str,
    top_key_repr: str,
    top_key_type: str,
    top_value_type: str,
    model_path: str,
    summary: dict[str, Any],
) -> dict[str, object]:
    params = summary.get("important_params", {})
    fi = summary.get("feature_importances", {})
    trees = summary.get("tree_stats", {})
    return {
        "pickle_file": filename,
        "top_key_repr": top_key_repr,
        "top_key_type": top_key_type,
        "top_value_type": top_value_type,
        "model_path": model_path,
        "model_class": summary.get("model_class", ""),
        "n_estimators": params.get("n_estimators", ""),
        "random_state": params.get("random_state", ""),
        "max_depth": params.get("max_depth", ""),
        "max_features": params.get("max_features", ""),
        "n_features_in_": summary.get("n_features_in_", ""),
        "feature_importances_shape": fi.get("shape", ""),
        "feature_importances_sum": fi.get("sum", ""),
        "feature_importances_top_indices": fi.get("top_indices", ""),
        "feature_importances_top_values": fi.get("top_values", ""),
        "estimators_len": trees.get("estimators_len", ""),
        "tree_node_count_mean": trees.get("tree_node_count_mean", ""),
        "tree_max_depth_mean": trees.get("tree_max_depth_mean", ""),
    }


def process_pickle(filename: str) -> dict[str, Any]:
    path = EVIDENCE_ROOT / filename
    if not path.exists():
        return {
            "filename": filename,
            "exists": False,
            "path": rel_workspace(path),
        }

    try:
        obj, warning_summary = load_pickle(path)
    except Exception as exc:
        return {
            "filename": filename,
            "exists": True,
            "path": rel_workspace(path),
            "size_bytes": path.stat().st_size,
            "mtime_utc": datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat(),
            "load_error": repr(exc),
            "runtime_note": (
                "This pickle could not be loaded in the current Python/scikit-learn "
                "runtime. Use a compatibility runtime before treating this as a "
                "content-level failure."
            ),
            "model_entry_count": 0,
            "model_class_counts": {},
            "model_rows": [],
        }

    summary: dict[str, Any] = {
        "filename": filename,
        "exists": True,
        "path": rel_workspace(path),
        "size_bytes": path.stat().st_size,
        "mtime_utc": datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat(),
        "load_warning_summary": warning_summary,
        "top_level_shape": summarize_object_shape(obj),
    }

    model_rows = top_level_entry_rows(filename, obj)
    summary["model_entry_count"] = len(model_rows)
    summary["model_class_counts"] = dict(Counter(str(row["model_class"]) for row in model_rows))
    summary["model_rows"] = model_rows
    summary["numeric_result_rows"] = (
        flatten_numeric_result_rows(filename, obj) if filename in RESULT_ENTRY_PICKLES else []
    )

    if isinstance(obj, dict):
        value_type_counts = Counter(type_name(v) for v in obj.values())
        summary["top_level_value_type_counts"] = dict(value_type_counts)
        summary["top_level_key_repr_preview"] = limited_sequence_summary(obj.keys(), 30)

    del obj
    gc.collect()
    return summary


def write_markdown(all_summaries: list[dict[str, Any]], model_rows: list[dict[str, object]]) -> None:
    try:
        import sklearn

        sklearn_version = sklearn.__version__
    except Exception:
        sklearn_version = "not importable"

    lines = [
        "# Feature-Combination Pickle Inspection",
        "",
        f"Generated at: `{datetime.now(timezone.utc).isoformat()}`",
        f"Runtime: Python `{sys.version.split()[0]}`, scikit-learn `{sklearn_version}`, NumPy `{getattr(np, '__version__', 'not importable')}`.",
        "",
        "This report inspects the large historical model pickles and nearby result-summary pickles in `Protein_MPNN_Digging`.",
        "",
        "## Model Pickles",
        "",
    ]

    for summary in all_summaries:
        filename = summary["filename"]
        if filename not in MODEL_PICKLES:
            continue
        if not summary.get("exists"):
            lines.append(f"- `{filename}`: missing")
            continue
        if summary.get("load_error"):
            lines.append(f"- `{filename}`: load failed under this runtime: `{summary['load_error']}`")
            continue
        shape = summary.get("top_level_shape", {})
        lines.append(
            f"- `{filename}`: top-level `{shape.get('type')}`, len `{shape.get('len', '')}`, "
            f"model entries `{summary.get('model_entry_count')}`, size `{summary.get('size_bytes')}` bytes"
        )
        numeric_rows = summary.get("numeric_result_rows", [])
        if numeric_rows:
            lines.append(f"  - Numeric result rows extracted: `{len(numeric_rows)}`")
        class_counts = summary.get("model_class_counts", {})
        for model_class, count in sorted(class_counts.items()):
            lines.append(f"  - `{model_class}`: `{count}` entries")
        warning_summary = summary.get("load_warning_summary", {})
        warning_count = warning_summary.get("count", 0) if isinstance(warning_summary, dict) else 0
        if warning_count:
            lines.append(f"  - Load warnings: `{warning_count}` total, `{warning_summary.get('unique_count')}` unique")

    lines.extend(["", "## Context Result Pickles", ""])
    for summary in all_summaries:
        filename = summary["filename"]
        if filename not in CONTEXT_PICKLES:
            continue
        if not summary.get("exists"):
            lines.append(f"- `{filename}`: missing")
            continue
        if summary.get("load_error"):
            lines.append(f"- `{filename}`: load failed under this runtime: `{summary['load_error']}`")
            continue
        shape = summary.get("top_level_shape", {})
        lines.append(
            f"- `{filename}`: top-level `{shape.get('type')}`, len `{shape.get('len', '')}`, "
            f"model entries `{summary.get('model_entry_count')}`, size `{summary.get('size_bytes')}` bytes"
        )
        numeric_rows = summary.get("numeric_result_rows", [])
        if numeric_rows:
            lines.append(f"  - Numeric result rows extracted: `{len(numeric_rows)}`")

    lines.extend(
        [
            "",
            "## Interpretation Guardrails",
            "",
            "- A saved model pickle can explain historical evaluation only if a notebook or code path loads it for prediction/evaluation.",
            "- If the manuscript numbers were produced by training models inside a notebook, these pickles may be saved byproducts rather than the direct source of the manuscript table.",
            "- The model metadata here is therefore evidence for possible reuse, not by itself proof of manuscript-number provenance.",
            "",
            "## Generated Files",
            "",
            "- `feature_combo_pickle_summary.json`",
            "- `feature_combo_model_entries.tsv`",
            "- `feature_combo_result_entries.tsv`",
            "- `README.md`",
            "",
        ]
    )
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "README.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    all_filenames = MODEL_PICKLES + CONTEXT_PICKLES
    summaries: list[dict[str, Any]] = []
    model_rows: list[dict[str, object]] = []
    result_rows: list[dict[str, object]] = []
    for filename in all_filenames:
        summary = process_pickle(filename)
        summaries.append(summary)
        model_rows.extend(summary.get("model_rows", []))
        result_rows.extend(summary.get("numeric_result_rows", []))

    json_path = OUTPUT_DIR / "feature_combo_pickle_summary.json"
    summaries_for_json = []
    for summary in summaries:
        compact = dict(summary)
        compact.pop("model_rows", None)
        compact.pop("numeric_result_rows", None)
        summaries_for_json.append(compact)
    json_path.write_text(json.dumps(json_safe(summaries_for_json), indent=2, sort_keys=True), encoding="utf-8")

    write_tsv(
        OUTPUT_DIR / "feature_combo_model_entries.tsv",
        model_rows,
        [
            "pickle_file",
            "top_key_repr",
            "top_key_type",
            "top_value_type",
            "model_path",
            "model_class",
            "n_estimators",
            "random_state",
            "max_depth",
            "max_features",
            "n_features_in_",
            "feature_importances_shape",
            "feature_importances_sum",
            "feature_importances_top_indices",
            "feature_importances_top_values",
            "estimators_len",
            "tree_node_count_mean",
            "tree_max_depth_mean",
        ],
    )
    write_tsv(
        OUTPUT_DIR / "feature_combo_result_entries.tsv",
        result_rows,
        [
            "pickle_file",
            "result_path",
            "value",
        ],
    )
    write_markdown(summaries, model_rows)


if __name__ == "__main__":
    main()
