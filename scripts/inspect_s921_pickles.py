#!/usr/bin/env python3
"""Conservatively inspect copied S_921 pickle artifacts.

This script is intentionally evidence-oriented:

1. It only reads the copied local analysis inputs under
   ``pickle_analysis/S_921_target_pickles``.
2. It scans pickle opcodes/globals before loading.
3. It loads files one by one with a restricted, logging unpickler.
4. It writes compact TSV/JSON summaries rather than raw object dumps.

The goal is to recover what the S_921 artifacts contain and how they connect
to the old manuscript/code trail, without executing notebooks or modifying the
primary copied Drive evidence.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import math
import pickle
import pickletools
import statistics
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
INPUT_DIR = WORKSPACE_ROOT / "pickle_analysis" / "S_921_target_pickles"
TABLE_DIR = WORKSPACE_ROOT / "pickle_analysis" / "tables"
JSON_DIR = WORKSPACE_ROOT / "pickle_analysis" / "json"

EXPECTED_PICKLES = [
    "S_921_full_feature_dict.pickle",
    "S_921_pmppn_info_dict.pickle",
    "S_921_pmppn_info_dict_V2.pickle",
    "S_921_pmppn_info_dict_V3.pickle",
]

MAX_REPRESENTATIVE_LEAF_ROWS = 20_000

ARTIFACT_CONTEXT = {
    "S_921_full_feature_dict.pickle": {
        "artifact_role": "early assembled feature dictionary",
        "known_notebook_links": (
            "Consumed by Quick_Dirty_MPNN_ML.ipynb and "
            "Quick_Dirty_MPNN_ML_V2.ipynb; older feature-combination era."
        ),
        "manuscript_relevance": (
            "Candidate precursor for early feature tests, before the V2/V3 "
            "ProteinMPNN intermediate dictionaries used by final A-H mapping."
        ),
    },
    "S_921_pmppn_info_dict.pickle": {
        "artifact_role": "first S_921 ProteinMPNN intermediate info dictionary",
        "known_notebook_links": (
            "Associated with S_921 feature-extraction notebook lineage around "
            "ProteinMPNNTesting_V6.ipynb."
        ),
        "manuscript_relevance": (
            "Early S_921 extraction state; useful for reconstructing how the "
            "feature schema evolved before manuscript-level runs."
        ),
    },
    "S_921_pmppn_info_dict_V2.pickle": {
        "artifact_role": "V2 S_921 ProteinMPNN intermediate info dictionary",
        "known_notebook_links": (
            "Consumed by Quick_Dirty_MPNN_ML_V2_V2.ipynb and mentioned by the "
            "S921_ProteinMPNNTesting_V6_V2.ipynb lineage."
        ),
        "manuscript_relevance": (
            "Intermediate V2 feature-generation state; helps explain changes "
            "between early full-feature dictionaries and final V3 ML inputs."
        ),
    },
    "S_921_pmppn_info_dict_V3.pickle": {
        "artifact_role": "final V3 S_921 ProteinMPNN intermediate info dictionary",
        "known_notebook_links": (
            "Consumed by Quick_Dirty_MPNN_ML_V2_V3.ipynb and "
            "Quick_Dirty_MPNN_ML_V2_VGRAPHS_V1.ipynb."
        ),
        "manuscript_relevance": (
            "Highest-priority S_921 artifact for final manuscript table/figure "
            "provenance and A-H feature mapping."
        ),
    },
}

ALLOWED_MODULE_PREFIXES = (
    "builtins",
    "__builtin__",
    "collections",
    "copyreg",
    "numpy",
    "numpy.core",
    "numpy._core",
    "pandas",
    "scipy.sparse",
)


@dataclass(frozen=True)
class FileRecord:
    filename: str
    path: Path
    size_bytes: int
    mtime_iso: str
    sha256: str


class RestrictedLoggingUnpickler(pickle.Unpickler):
    """Unpickler that records globals and blocks unexpected module imports."""

    def __init__(self, file: io.BufferedReader):
        super().__init__(file)
        self.resolved_globals: set[str] = set()

    def find_class(self, module: str, name: str) -> Any:
        full_name = f"{module}.{name}"
        self.resolved_globals.add(full_name)
        if not module.startswith(ALLOWED_MODULE_PREFIXES):
            raise pickle.UnpicklingError(
                f"Blocked global {full_name!r}; update allowlist only after review."
            )
        return super().find_class(module, name)


def ensure_dirs() -> None:
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    JSON_DIR.mkdir(parents=True, exist_ok=True)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def iso_mtime(path: Path) -> str:
    return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat()


def collect_file_records() -> list[FileRecord]:
    records: list[FileRecord] = []
    missing: list[str] = []
    for filename in EXPECTED_PICKLES:
        path = INPUT_DIR / filename
        if not path.exists():
            missing.append(filename)
            continue
        stat = path.stat()
        records.append(
            FileRecord(
                filename=filename,
                path=path,
                size_bytes=stat.st_size,
                mtime_iso=iso_mtime(path),
                sha256=sha256_file(path),
            )
        )
    if missing:
        raise FileNotFoundError(f"Missing expected copied pickle(s): {missing}")
    return records


def static_pickle_global_scan(path: Path) -> dict[str, Any]:
    """Scan pickle opcodes without constructing the stored Python object."""

    opcode_counts: Counter[str] = Counter()
    globals_seen: Counter[str] = Counter()
    stack_global_count = 0
    protocol_versions: set[int] = set()
    opcode_total = 0

    with path.open("rb") as handle:
        for opcode, arg, _pos in pickletools.genops(handle):
            opcode_total += 1
            opcode_counts[opcode.name] += 1
            if opcode.name == "PROTO" and isinstance(arg, int):
                protocol_versions.add(arg)
            elif opcode.name == "GLOBAL" and isinstance(arg, str):
                globals_seen[arg.replace(" ", ".")] += 1
            elif opcode.name == "STACK_GLOBAL":
                stack_global_count += 1

    return {
        "opcode_total": opcode_total,
        "protocol_versions": sorted(protocol_versions),
        "opcode_counts": dict(opcode_counts.most_common()),
        "globals_seen": dict(globals_seen.most_common()),
        "stack_global_count": stack_global_count,
    }


def load_pickle_with_audit(path: Path) -> tuple[Any, list[str]]:
    with path.open("rb") as handle:
        unpickler = RestrictedLoggingUnpickler(handle)
        obj = unpickler.load()
        return obj, sorted(unpickler.resolved_globals)


def safe_repr(value: Any, max_len: int = 120) -> str:
    text = repr(value)
    if len(text) <= max_len:
        return text
    return text[: max_len - 3] + "..."


def type_name(value: Any) -> str:
    cls = value.__class__
    return f"{cls.__module__}.{cls.__name__}"


def is_numpy_array(value: Any) -> bool:
    return value.__class__.__module__.startswith("numpy") and value.__class__.__name__ == "ndarray"


def is_numpy_scalar(value: Any) -> bool:
    return value.__class__.__module__.startswith("numpy") and not is_numpy_array(value)


def summarize_scalar(value: Any) -> str:
    if isinstance(value, float):
        if math.isnan(value):
            return "nan"
        if math.isinf(value):
            return "inf" if value > 0 else "-inf"
        return f"{value:.6g}"
    return safe_repr(value, 80)


def array_stats(value: Any) -> dict[str, Any]:
    import numpy as np

    arr = value
    stats: dict[str, Any] = {
        "shape": list(arr.shape),
        "dtype": str(arr.dtype),
        "size": int(arr.size),
        "ndim": int(arr.ndim),
    }
    if arr.size == 0:
        return stats
    if np.issubdtype(arr.dtype, np.number):
        flat = arr.reshape(-1)
        finite = flat[np.isfinite(flat)]
        stats["nan_count"] = int(np.isnan(flat).sum()) if np.issubdtype(arr.dtype, np.floating) else 0
        if finite.size:
            stats["finite_min"] = float(np.min(finite))
            stats["finite_max"] = float(np.max(finite))
            stats["finite_mean"] = float(np.mean(finite))
            stats["finite_std"] = float(np.std(finite))
    else:
        sample = [safe_repr(x, 40) for x in arr.reshape(-1)[:5]]
        stats["sample"] = sample
    return stats


def path_to_text(path_parts: list[str]) -> str:
    return "root" + "".join(path_parts)


def normalized_path(path_parts: list[str]) -> str:
    normalized: list[str] = []
    entry_replaced = False
    for part in path_parts:
        if part.startswith("[") and not entry_replaced:
            normalized.append("[<entry>]")
            entry_replaced = True
        elif part.startswith("[") and part[1:-1].isdigit():
            normalized.append("[<idx>]")
        else:
            normalized.append(part)
    return "root" + "".join(normalized)


def key_token(key: Any) -> str:
    return f"[{safe_repr(key, 60)}]"


def summarize_top_level(obj: Any) -> dict[str, Any]:
    summary: dict[str, Any] = {"type": type_name(obj)}
    if isinstance(obj, dict):
        keys = list(obj.keys())
        child_types = Counter(type_name(v) for v in obj.values())
        summary.update(
            {
                "kind": "dict",
                "key_count": len(keys),
                "key_type_counts": dict(Counter(type_name(k) for k in keys).most_common()),
                "sample_keys": [safe_repr(k, 80) for k in keys[:12]],
                "child_type_counts": dict(child_types.most_common()),
            }
        )
        if keys and all(isinstance(obj[k], dict) for k in keys[: min(50, len(keys))]):
            child_key_sets = []
            child_key_counter: Counter[str] = Counter()
            child_key_count_values: list[int] = []
            for key in keys:
                child = obj[key]
                if not isinstance(child, dict):
                    continue
                child_keys = [safe_repr(k, 80) for k in child.keys()]
                child_key_sets.append(tuple(child_keys))
                child_key_counter.update(child_keys)
                child_key_count_values.append(len(child_keys))
            summary["dict_child_count"] = len(child_key_count_values)
            summary["child_key_count_min"] = min(child_key_count_values) if child_key_count_values else None
            summary["child_key_count_max"] = max(child_key_count_values) if child_key_count_values else None
            summary["child_key_count_median"] = (
                statistics.median(child_key_count_values) if child_key_count_values else None
            )
            summary["child_key_union_count"] = len(child_key_counter)
            summary["child_key_union_sample"] = [k for k, _ in child_key_counter.most_common(30)]
            summary["uniform_child_key_schema"] = len(set(child_key_sets)) == 1 if child_key_sets else None
    elif isinstance(obj, (list, tuple)):
        summary.update(
            {
                "kind": type(obj).__name__,
                "length": len(obj),
                "sample_child_types": dict(Counter(type_name(v) for v in obj[:100]).most_common()),
            }
        )
    elif is_numpy_array(obj):
        summary.update({"kind": "ndarray", **array_stats(obj)})
    else:
        summary.update({"kind": "other", "repr": safe_repr(obj)})
    return summary


def walk_object(
    obj: Any,
    *,
    file_name: str,
    path_parts: list[str],
    dict_rows: list[dict[str, Any]],
    leaf_rows: list[dict[str, Any]],
    array_template_counter: dict[str, Counter[str]],
    max_depth: int = 7,
    max_items_per_container: int = 2000,
) -> None:
    current_path = path_to_text(path_parts)
    current_normalized = normalized_path(path_parts)

    if isinstance(obj, dict):
        keys = list(obj.keys())
        values = list(obj.values())
        dict_rows.append(
            {
                "file": file_name,
                "path": current_path,
                "normalized_path": current_normalized,
                "depth": len(path_parts),
                "key_count": len(keys),
                "key_type_counts": json.dumps(dict(Counter(type_name(k) for k in keys).most_common())),
                "value_type_counts": json.dumps(dict(Counter(type_name(v) for v in values).most_common())),
                "sample_keys": json.dumps([safe_repr(k, 80) for k in keys[:20]]),
            }
        )
        if len(path_parts) >= max_depth:
            return
        for key in keys[:max_items_per_container]:
            walk_object(
                obj[key],
                file_name=file_name,
                path_parts=path_parts + [key_token(key)],
                dict_rows=dict_rows,
                leaf_rows=leaf_rows,
                array_template_counter=array_template_counter,
                max_depth=max_depth,
                max_items_per_container=max_items_per_container,
            )
        return

    if isinstance(obj, (list, tuple)):
        if len(leaf_rows) < MAX_REPRESENTATIVE_LEAF_ROWS:
            leaf_rows.append(
                {
                    "file": file_name,
                    "path": current_path,
                    "normalized_path": current_normalized,
                    "type": type_name(obj),
                    "detail": f"length={len(obj)}",
                    "sample": json.dumps([safe_repr(v, 80) for v in list(obj)[:8]]),
                }
            )
        if len(path_parts) >= max_depth:
            return
        for idx, item in enumerate(list(obj)[:max_items_per_container]):
            walk_object(
                item,
                file_name=file_name,
                path_parts=path_parts + [f"[{idx}]"],
                dict_rows=dict_rows,
                leaf_rows=leaf_rows,
                array_template_counter=array_template_counter,
                max_depth=max_depth,
                max_items_per_container=max_items_per_container,
            )
        return

    if is_numpy_array(obj):
        stats = array_stats(obj)
        template_key = current_normalized
        array_template_counter[template_key][f"shape={stats['shape']} dtype={stats['dtype']}"] += 1
        if len(leaf_rows) < MAX_REPRESENTATIVE_LEAF_ROWS:
            leaf_rows.append(
                {
                    "file": file_name,
                    "path": current_path,
                    "normalized_path": current_normalized,
                    "type": type_name(obj),
                    "detail": json.dumps(stats, sort_keys=True),
                    "sample": "",
                }
            )
        return

    if is_numpy_scalar(obj) or isinstance(obj, (str, int, float, bool, type(None))):
        if len(leaf_rows) < MAX_REPRESENTATIVE_LEAF_ROWS:
            leaf_rows.append(
                {
                    "file": file_name,
                    "path": current_path,
                    "normalized_path": current_normalized,
                    "type": type_name(obj),
                    "detail": summarize_scalar(obj),
                    "sample": "",
                }
            )
        return

    if len(leaf_rows) < MAX_REPRESENTATIVE_LEAF_ROWS:
        leaf_rows.append(
            {
                "file": file_name,
                "path": current_path,
                "normalized_path": current_normalized,
                "type": type_name(obj),
                "detail": safe_repr(obj, 160),
                "sample": "",
            }
        )


def write_tsv(path: Path, rows: Iterable[dict[str, Any]], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def build_cross_file_key_overlap(loaded_objects: dict[str, Any]) -> list[dict[str, Any]]:
    dict_objects = {name: obj for name, obj in loaded_objects.items() if isinstance(obj, dict)}
    names = list(dict_objects)
    rows: list[dict[str, Any]] = []
    key_sets = {name: set(obj.keys()) for name, obj in dict_objects.items()}
    for left in names:
        for right in names:
            if left >= right:
                continue
            left_keys = key_sets[left]
            right_keys = key_sets[right]
            intersection = left_keys & right_keys
            union = left_keys | right_keys
            rows.append(
                {
                    "left_file": left,
                    "right_file": right,
                    "left_key_count": len(left_keys),
                    "right_key_count": len(right_keys),
                    "intersection_count": len(intersection),
                    "union_count": len(union),
                    "jaccard": f"{(len(intersection) / len(union)):.6f}" if union else "",
                    "left_only_sample": json.dumps([safe_repr(k, 80) for k in list(left_keys - right_keys)[:20]]),
                    "right_only_sample": json.dumps([safe_repr(k, 80) for k in list(right_keys - left_keys)[:20]]),
                }
            )
    return rows


def iter_entry_dicts(obj: Any) -> Iterable[tuple[Any, int, dict[Any, Any]]]:
    """Yield per-mutation dictionaries from the observed S_921 layout."""

    if not isinstance(obj, dict):
        return
    for protein_key, entries in obj.items():
        if not isinstance(entries, list):
            continue
        for entry_index, entry in enumerate(entries):
            if isinstance(entry, dict):
                yield protein_key, entry_index, entry


def entry_value_signature(value: Any) -> str:
    if is_numpy_array(value):
        stats = array_stats(value)
        return f"ndarray shape={stats['shape']} dtype={stats['dtype']}"
    if isinstance(value, list):
        child_types = Counter(type_name(item) for item in value[:50])
        return f"list length={len(value)} child_types={dict(child_types.most_common())}"
    if isinstance(value, tuple):
        child_types = Counter(type_name(item) for item in value[:50])
        return f"tuple length={len(value)} child_types={dict(child_types.most_common())}"
    return f"{type_name(value)} value={safe_repr(value, 80)}"


def build_entry_schema_tables(
    loaded_objects: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    schema_rows: list[dict[str, Any]] = []
    field_rows: list[dict[str, Any]] = []
    count_rows: list[dict[str, Any]] = []
    field_sets: dict[str, set[str]] = {}

    for filename, obj in loaded_objects.items():
        if not isinstance(obj, dict):
            continue

        protein_entry_counts: dict[Any, int] = {}
        field_occurrences: Counter[str] = Counter()
        field_type_counts: dict[str, Counter[str]] = defaultdict(Counter)
        field_signature_counts: dict[str, Counter[str]] = defaultdict(Counter)
        field_samples: dict[str, list[str]] = defaultdict(list)
        entry_count = 0

        for protein_key, entries in obj.items():
            if isinstance(entries, list):
                protein_entry_counts[protein_key] = len(entries)
            else:
                protein_entry_counts[protein_key] = 0

        for _protein_key, _entry_index, entry in iter_entry_dicts(obj):
            entry_count += 1
            for key, value in entry.items():
                key_text = str(key)
                field_occurrences[key_text] += 1
                field_type_counts[key_text][type_name(value)] += 1
                field_signature_counts[key_text][entry_value_signature(value)] += 1
                if len(field_samples[key_text]) < 6:
                    field_samples[key_text].append(safe_repr(value, 120))

        entry_count_values = list(protein_entry_counts.values())
        all_entry_fields = set(field_occurrences)
        fields_in_all_entries = {
            field for field, count in field_occurrences.items() if count == entry_count
        }
        field_sets[filename] = all_entry_fields

        schema_rows.append(
            {
                "filename": filename,
                "protein_count": len(protein_entry_counts),
                "mutation_entry_count": entry_count,
                "entries_per_protein_min": min(entry_count_values) if entry_count_values else "",
                "entries_per_protein_median": (
                    statistics.median(entry_count_values) if entry_count_values else ""
                ),
                "entries_per_protein_max": max(entry_count_values) if entry_count_values else "",
                "entry_field_union_count": len(all_entry_fields),
                "entry_field_union": json.dumps(sorted(all_entry_fields)),
                "fields_in_all_entries": json.dumps(sorted(fields_in_all_entries)),
                "fields_not_in_all_entries": json.dumps(sorted(all_entry_fields - fields_in_all_entries)),
            }
        )

        for protein_key, count in sorted(protein_entry_counts.items(), key=lambda item: str(item[0])):
            count_rows.append(
                {
                    "filename": filename,
                    "protein_key": protein_key,
                    "mutation_entry_count": count,
                }
            )

        for field in sorted(field_occurrences):
            field_rows.append(
                {
                    "filename": filename,
                    "field": field,
                    "occurrence_count": field_occurrences[field],
                    "occurrence_fraction": f"{field_occurrences[field] / entry_count:.6f}"
                    if entry_count
                    else "",
                    "type_counts": json.dumps(dict(field_type_counts[field].most_common())),
                    "signature_counts": json.dumps(dict(field_signature_counts[field].most_common(20))),
                    "sample_values": json.dumps(field_samples[field]),
                }
            )

    overlap_rows: list[dict[str, Any]] = []
    filenames = list(field_sets)
    for left in filenames:
        for right in filenames:
            if left >= right:
                continue
            left_fields = field_sets[left]
            right_fields = field_sets[right]
            intersection = left_fields & right_fields
            union = left_fields | right_fields
            overlap_rows.append(
                {
                    "left_file": left,
                    "right_file": right,
                    "left_field_count": len(left_fields),
                    "right_field_count": len(right_fields),
                    "intersection_count": len(intersection),
                    "union_count": len(union),
                    "jaccard": f"{len(intersection) / len(union):.6f}" if union else "",
                    "shared_fields": json.dumps(sorted(intersection)),
                    "left_only_fields": json.dumps(sorted(left_fields - right_fields)),
                    "right_only_fields": json.dumps(sorted(right_fields - left_fields)),
                }
            )

    return schema_rows, field_rows, count_rows, overlap_rows


def main() -> None:
    ensure_dirs()
    records = collect_file_records()

    manifest_rows = [
        {
            "filename": record.filename,
            "copied_path": str(record.path.relative_to(WORKSPACE_ROOT)),
            "size_bytes": record.size_bytes,
            "mtime_utc": record.mtime_iso,
            "sha256": record.sha256,
            **ARTIFACT_CONTEXT[record.filename],
        }
        for record in records
    ]

    static_rows: list[dict[str, Any]] = []
    load_rows: list[dict[str, Any]] = []
    top_summary_rows: list[dict[str, Any]] = []
    dict_rows: list[dict[str, Any]] = []
    leaf_rows: list[dict[str, Any]] = []
    array_template_rows: list[dict[str, Any]] = []
    loaded_objects: dict[str, Any] = {}
    full_json: dict[str, Any] = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "input_dir": str(INPUT_DIR.relative_to(WORKSPACE_ROOT)),
        "files": {},
    }

    for record in records:
        static = static_pickle_global_scan(record.path)
        static_rows.append(
            {
                "filename": record.filename,
                "pickle_protocols": json.dumps(static["protocol_versions"]),
                "opcode_total": static["opcode_total"],
                "stack_global_count": static["stack_global_count"],
                "globals_seen": json.dumps(static["globals_seen"], sort_keys=True),
                "top_opcode_counts": json.dumps(dict(list(static["opcode_counts"].items())[:20])),
            }
        )

        load_status = "loaded"
        load_error = ""
        resolved_globals: list[str] = []
        top_summary: dict[str, Any] | None = None
        array_template_counter: dict[str, Counter[str]] = defaultdict(Counter)
        try:
            obj, resolved_globals = load_pickle_with_audit(record.path)
            loaded_objects[record.filename] = obj
            top_summary = summarize_top_level(obj)
            walk_object(
                obj,
                file_name=record.filename,
                path_parts=[],
                dict_rows=dict_rows,
                leaf_rows=leaf_rows,
                array_template_counter=array_template_counter,
            )
        except Exception as exc:  # noqa: BLE001 - this is a reportable evidence failure.
            load_status = "failed"
            load_error = f"{exc.__class__.__name__}: {exc}"

        load_rows.append(
            {
                "filename": record.filename,
                "status": load_status,
                "error": load_error,
                "resolved_globals": json.dumps(resolved_globals),
            }
        )

        if top_summary is not None:
            top_summary_rows.append(
                {
                    "filename": record.filename,
                    "artifact_role": ARTIFACT_CONTEXT[record.filename]["artifact_role"],
                    "top_type": top_summary.get("type", ""),
                    "kind": top_summary.get("kind", ""),
                    "key_count_or_length": top_summary.get("key_count", top_summary.get("length", "")),
                    "sample_keys": json.dumps(top_summary.get("sample_keys", [])),
                    "child_type_counts": json.dumps(top_summary.get("child_type_counts", {})),
                    "child_key_union_count": top_summary.get("child_key_union_count", ""),
                    "child_key_union_sample": json.dumps(top_summary.get("child_key_union_sample", [])),
                    "uniform_child_key_schema": top_summary.get("uniform_child_key_schema", ""),
                }
            )

        for template_path, shape_counter in array_template_counter.items():
            array_template_rows.append(
                {
                    "file": record.filename,
                    "normalized_path": template_path,
                    "array_count": sum(shape_counter.values()),
                    "shape_dtype_counts": json.dumps(dict(shape_counter.most_common())),
                }
            )

        full_json["files"][record.filename] = {
            "manifest": manifest_rows[-1],
            "static_pickle_scan": static,
            "load_status": load_status,
            "load_error": load_error,
            "resolved_globals": resolved_globals,
            "top_summary": top_summary,
        }

    overlap_rows = build_cross_file_key_overlap(loaded_objects)
    (
        entry_schema_rows,
        entry_field_rows,
        entry_count_rows,
        entry_field_overlap_rows,
    ) = build_entry_schema_tables(loaded_objects)

    write_tsv(
        TABLE_DIR / "S_921_pickle_file_manifest.tsv",
        manifest_rows,
        [
            "filename",
            "copied_path",
            "size_bytes",
            "mtime_utc",
            "sha256",
            "artifact_role",
            "known_notebook_links",
            "manuscript_relevance",
        ],
    )
    write_tsv(
        TABLE_DIR / "S_921_pickle_static_scan.tsv",
        static_rows,
        [
            "filename",
            "pickle_protocols",
            "opcode_total",
            "stack_global_count",
            "globals_seen",
            "top_opcode_counts",
        ],
    )
    write_tsv(
        TABLE_DIR / "S_921_pickle_load_audit.tsv",
        load_rows,
        ["filename", "status", "error", "resolved_globals"],
    )
    write_tsv(
        TABLE_DIR / "S_921_pickle_top_level_summary.tsv",
        top_summary_rows,
        [
            "filename",
            "artifact_role",
            "top_type",
            "kind",
            "key_count_or_length",
            "sample_keys",
            "child_type_counts",
            "child_key_union_count",
            "child_key_union_sample",
            "uniform_child_key_schema",
        ],
    )
    write_tsv(
        TABLE_DIR / "S_921_pickle_dict_inventory.tsv",
        dict_rows,
        [
            "file",
            "path",
            "normalized_path",
            "depth",
            "key_count",
            "key_type_counts",
            "value_type_counts",
            "sample_keys",
        ],
    )
    write_tsv(
        TABLE_DIR / "S_921_pickle_leaf_inventory.tsv",
        leaf_rows,
        ["file", "path", "normalized_path", "type", "detail", "sample"],
    )
    write_tsv(
        TABLE_DIR / "S_921_pickle_array_templates.tsv",
        array_template_rows,
        ["file", "normalized_path", "array_count", "shape_dtype_counts"],
    )
    write_tsv(
        TABLE_DIR / "S_921_pickle_top_key_overlap.tsv",
        overlap_rows,
        [
            "left_file",
            "right_file",
            "left_key_count",
            "right_key_count",
            "intersection_count",
            "union_count",
            "jaccard",
            "left_only_sample",
            "right_only_sample",
        ],
    )
    write_tsv(
        TABLE_DIR / "S_921_pickle_entry_schema.tsv",
        entry_schema_rows,
        [
            "filename",
            "protein_count",
            "mutation_entry_count",
            "entries_per_protein_min",
            "entries_per_protein_median",
            "entries_per_protein_max",
            "entry_field_union_count",
            "entry_field_union",
            "fields_in_all_entries",
            "fields_not_in_all_entries",
        ],
    )
    write_tsv(
        TABLE_DIR / "S_921_pickle_entry_field_summary.tsv",
        entry_field_rows,
        [
            "filename",
            "field",
            "occurrence_count",
            "occurrence_fraction",
            "type_counts",
            "signature_counts",
            "sample_values",
        ],
    )
    write_tsv(
        TABLE_DIR / "S_921_pickle_entry_count_by_protein.tsv",
        entry_count_rows,
        ["filename", "protein_key", "mutation_entry_count"],
    )
    write_tsv(
        TABLE_DIR / "S_921_pickle_entry_field_overlap.tsv",
        entry_field_overlap_rows,
        [
            "left_file",
            "right_file",
            "left_field_count",
            "right_field_count",
            "intersection_count",
            "union_count",
            "jaccard",
            "shared_fields",
            "left_only_fields",
            "right_only_fields",
        ],
    )

    with (JSON_DIR / "S_921_pickle_summaries.json").open("w", encoding="utf-8") as handle:
        json.dump(full_json, handle, indent=2, sort_keys=True)


if __name__ == "__main__":
    main()
