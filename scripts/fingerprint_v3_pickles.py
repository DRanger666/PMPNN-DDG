#!/usr/bin/env python3
"""Fingerprint V3 PMPNN pickle dictionaries against candidate generator notebooks.

This script implements the plan in:

``manuscript_codebase_mapping/V3_PICKLE_CONTENT_FINGERPRINTING_PLAN.md``

It reads only workspace-local copied evidence under
``drive_evidence_copy/sajidahmedprotres_drive/Protein_MPNN_Digging``. It does
not read the live FUSE mount and does not execute notebooks.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import math
import pickle
import re
import statistics
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
PICKLE_SOURCE_DIR = (
    WORKSPACE_ROOT
    / "drive_evidence_copy"
    / "sajidahmedprotres_drive"
    / "Protein_MPNN_Digging"
)
ANALYSIS_DIR = WORKSPACE_ROOT / "pickle_analysis" / "v3_fingerprinting"
TABLE_DIR = ANALYSIS_DIR / "tables"
JSON_DIR = ANALYSIS_DIR / "json"

NOTEBOOK_SOURCE_DIR = (
    WORKSPACE_ROOT
    / "code_inventory_analysis"
    / "notebook_sources"
    / "git_sajid_additions"
)
NOTEBOOK_OUTPUT_DIRS = [
    WORKSPACE_ROOT / "colab_notebooks_inventory_analysis" / "git_notebook_outputs",
    WORKSPACE_ROOT / "colab_notebooks_inventory_analysis" / "notebook_outputs",
]
DOWNSTREAM_SOURCE_DIRS = [
    WORKSPACE_ROOT / "colab_notebooks_inventory_analysis" / "git_notebook_sources",
    WORKSPACE_ROOT / "colab_notebooks_inventory_analysis" / "notebook_sources",
    WORKSPACE_ROOT / "code_inventory_analysis" / "notebook_sources" / "git_sajid_additions",
]

DATASETS = {
    "S_2648": {
        "generator_source": "ProteinMPNNTesting_V6_V2.ipynb.py.txt",
        "generator_output": "ProteinMPNNTesting_V6_V2.ipynb.outputs.txt",
        "pickle_prefix": "S_2648",
    },
    "S_921": {
        "generator_source": "S921_ProteinMPNNTesting_V6_V2.ipynb.py.txt",
        "generator_output": "S921_ProteinMPNNTesting_V6_V2.ipynb.outputs.txt",
        "pickle_prefix": "S_921",
    },
    "S_669": {
        "generator_source": "S669_ProteinMPNNTesting_V6_V2.ipynb.py.txt",
        "generator_output": "S669_ProteinMPNNTesting_V6_V2.ipynb.outputs.txt",
        "pickle_prefix": "S_669",
    },
    "Ssym": {
        "generator_source": "Ssym_ProteinMPNNTesting_V6_V2.ipynb.py.txt",
        "generator_output": "Ssym_ProteinMPNNTesting_V6_V2.ipynb.outputs.txt",
        "pickle_prefix": "Ssym",
    },
}

VERSIONS = {
    "base": "{prefix}_pmppn_info_dict.pickle",
    "V2": "{prefix}_pmppn_info_dict_V2.pickle",
    "V3": "{prefix}_pmppn_info_dict_V3.pickle",
}

EXPECTED_GENERATOR_FIELDS = {
    "w_n_log_prob",
    "m_n_log_prob",
    "neighbor_aa_identities",
    "neighbor_w_message_vector_coming_from_center",
    "neighbor_m_message_vector_coming_from_center",
    "neighbor_w_neighbor_embedding",
    "neighbor_m_neighbor_embedding",
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
class PickleTarget:
    dataset: str
    version: str
    filename: str
    path: Path


class RestrictedLoggingUnpickler(pickle.Unpickler):
    """Unpickler that records globals and blocks unexpected imports."""

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


def write_tsv(path: Path, rows: Iterable[dict[str, Any]], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def iso_mtime(path: Path) -> str:
    return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat()


def safe_repr(value: Any, max_len: int = 120) -> str:
    text = repr(value)
    if len(text) <= max_len:
        return text
    return text[: max_len - 3] + "..."


def type_name(value: Any) -> str:
    cls = value.__class__
    return f"{cls.__module__}.{cls.__name__}"


def is_numpy_array(value: Any) -> bool:
    return (
        value.__class__.__module__.startswith("numpy")
        and value.__class__.__name__ == "ndarray"
    )


def collect_targets() -> list[PickleTarget]:
    targets: list[PickleTarget] = []
    missing: list[str] = []
    for dataset, meta in DATASETS.items():
        for version, template in VERSIONS.items():
            filename = template.format(prefix=meta["pickle_prefix"])
            path = PICKLE_SOURCE_DIR / filename
            if not path.exists():
                missing.append(str(path.relative_to(WORKSPACE_ROOT)))
            targets.append(PickleTarget(dataset, version, filename, path))
    if missing:
        raise FileNotFoundError(f"Missing expected pickle files: {missing}")
    return targets


def load_pickle_with_audit(path: Path) -> tuple[Any, list[str]]:
    with path.open("rb") as handle:
        unpickler = RestrictedLoggingUnpickler(handle)
        obj = unpickler.load()
        return obj, sorted(unpickler.resolved_globals)


def iter_entry_dicts(obj: Any) -> Iterable[tuple[str, int, dict[Any, Any]]]:
    if not isinstance(obj, dict):
        return
    for protein_key, entries in obj.items():
        if not isinstance(entries, list):
            continue
        for entry_index, entry in enumerate(entries):
            if isinstance(entry, dict):
                yield str(protein_key), entry_index, entry


def normalize_protein_key(value: str) -> str:
    cleaned = Path(value.strip().strip("'\"")).stem
    cleaned = cleaned.split("/")[-1]
    cleaned = cleaned.split("\\")[-1]
    return cleaned.lower()


def compact_numeric_fingerprint(value: Any) -> dict[str, Any]:
    import numpy as np

    arr = value
    stats: dict[str, Any] = {
        "shape": list(arr.shape),
        "dtype": str(arr.dtype),
        "size": int(arr.size),
    }
    if arr.size == 0:
        stats["sha256_first_values"] = ""
        return stats
    flat = arr.reshape(-1)
    sample = flat[: min(32, flat.size)]
    stats["sha256_first_values"] = hashlib.sha256(sample.tobytes()).hexdigest()
    if np.issubdtype(arr.dtype, np.number):
        finite = flat[np.isfinite(flat)]
        stats["nan_count"] = (
            int(np.isnan(flat).sum()) if np.issubdtype(arr.dtype, np.floating) else 0
        )
        if finite.size:
            stats["finite_min"] = float(np.min(finite))
            stats["finite_max"] = float(np.max(finite))
            stats["finite_mean"] = float(np.mean(finite))
            stats["finite_std"] = float(np.std(finite))
    return stats


def value_signature(value: Any) -> tuple[str, str, str]:
    if is_numpy_array(value):
        stats = compact_numeric_fingerprint(value)
        shape_dtype = f"ndarray shape={stats['shape']} dtype={stats['dtype']}"
        detail = json.dumps(stats, sort_keys=True)
        fingerprint = stats.get("sha256_first_values", "")
        return shape_dtype, detail, fingerprint
    if isinstance(value, list):
        child_types = Counter(type_name(item) for item in value[:50])
        child_shapes: Counter[str] = Counter()
        child_hashes: list[str] = []
        for item in value[:20]:
            if is_numpy_array(item):
                stats = compact_numeric_fingerprint(item)
                child_shapes[f"shape={stats['shape']} dtype={stats['dtype']}"] += 1
                if len(child_hashes) < 5:
                    child_hashes.append(str(stats.get("sha256_first_values", "")))
        detail = {
            "length": len(value),
            "child_type_counts_sample": dict(child_types.most_common()),
            "array_shape_dtype_counts_sample": dict(child_shapes.most_common()),
            "child_array_hashes_sample": child_hashes,
        }
        return f"list length={len(value)}", json.dumps(detail, sort_keys=True), "|".join(child_hashes)
    if isinstance(value, tuple):
        child_types = Counter(type_name(item) for item in value[:50])
        detail = {
            "length": len(value),
            "child_type_counts_sample": dict(child_types.most_common()),
        }
        return f"tuple length={len(value)}", json.dumps(detail, sort_keys=True), ""
    if isinstance(value, (str, int, float, bool, type(None))):
        if isinstance(value, float):
            if math.isnan(value):
                rendered = "nan"
            elif math.isinf(value):
                rendered = "inf" if value > 0 else "-inf"
            else:
                rendered = f"{value:.8g}"
        else:
            rendered = safe_repr(value, 80)
        return type_name(value), rendered, hashlib.sha256(rendered.encode()).hexdigest()
    rendered = safe_repr(value, 160)
    return type_name(value), rendered, hashlib.sha256(rendered.encode()).hexdigest()


def summarize_pickle(
    target: PickleTarget,
) -> tuple[
    dict[str, Any],
    dict[str, Any],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    dict[str, Any],
]:
    stat = target.path.stat()
    manifest = {
        "dataset": target.dataset,
        "version": target.version,
        "filename": target.filename,
        "path": str(target.path.relative_to(WORKSPACE_ROOT)),
        "size_bytes": stat.st_size,
        "mtime_utc": iso_mtime(target.path),
        "sha256": sha256_file(target.path),
    }

    load_audit: dict[str, Any] = {
        "dataset": target.dataset,
        "version": target.version,
        "filename": target.filename,
        "status": "",
        "error": "",
        "resolved_globals": "[]",
    }
    entry_schema: dict[str, Any] = {
        "dataset": target.dataset,
        "version": target.version,
        "filename": target.filename,
    }
    field_rows: list[dict[str, Any]] = []
    count_rows: list[dict[str, Any]] = []
    missing_expected_field_rows: list[dict[str, Any]] = []
    summary_json: dict[str, Any] = {"manifest": manifest}

    try:
        obj, resolved_globals = load_pickle_with_audit(target.path)
        load_audit["status"] = "loaded"
        load_audit["resolved_globals"] = json.dumps(resolved_globals)
    except Exception as exc:  # noqa: BLE001 - reportable evidence failure.
        load_audit["status"] = "failed"
        load_audit["error"] = f"{exc.__class__.__name__}: {exc}"
        summary_json["load_audit"] = load_audit
        return (
            manifest,
            load_audit,
            [entry_schema],
            field_rows,
            count_rows,
            missing_expected_field_rows,
            summary_json,
        )

    top_keys = list(obj.keys()) if isinstance(obj, dict) else []
    protein_entry_counts: dict[str, int] = {}
    field_occurrences: Counter[str] = Counter()
    field_type_counts: dict[str, Counter[str]] = defaultdict(Counter)
    field_signature_counts: dict[str, Counter[str]] = defaultdict(Counter)
    field_fingerprints: dict[str, list[str]] = defaultdict(list)
    field_sample_details: dict[str, list[str]] = defaultdict(list)
    entry_count = 0

    if isinstance(obj, dict):
        for protein_key, entries in obj.items():
            protein_entry_counts[str(protein_key)] = len(entries) if isinstance(entries, list) else 0

    for protein_key, entry_index, entry in iter_entry_dicts(obj):
        entry_count += 1
        missing_expected_fields = sorted(EXPECTED_GENERATOR_FIELDS - {str(key) for key in entry})
        if target.version == "V3" and missing_expected_fields:
            missing_expected_field_rows.append(
                {
                    "dataset": target.dataset,
                    "version": target.version,
                    "filename": target.filename,
                    "protein_key": protein_key,
                    "normalized_protein_key": normalize_protein_key(protein_key),
                    "entry_index": entry_index,
                    "mut": safe_repr(entry.get("mut", ""), 80),
                    "ddg": safe_repr(entry.get("ddg", ""), 80),
                    "present_expected_fields": json.dumps(
                        sorted(EXPECTED_GENERATOR_FIELDS & {str(key) for key in entry})
                    ),
                    "missing_expected_fields": json.dumps(missing_expected_fields),
                }
            )
        for field_key, value in entry.items():
            field = str(field_key)
            signature, detail, fingerprint = value_signature(value)
            field_occurrences[field] += 1
            field_type_counts[field][type_name(value)] += 1
            field_signature_counts[field][signature] += 1
            if fingerprint and len(field_fingerprints[field]) < 8:
                field_fingerprints[field].append(fingerprint)
            if len(field_sample_details[field]) < 5:
                field_sample_details[field].append(detail)

    entry_count_values = list(protein_entry_counts.values())
    all_fields = set(field_occurrences)
    fields_in_all_entries = {
        field for field, count in field_occurrences.items() if count == entry_count
    }
    expected_field_min_fraction = ""
    if entry_count:
        expected_field_min_fraction = min(
            field_occurrences.get(field, 0) / entry_count
            for field in EXPECTED_GENERATOR_FIELDS
        )

    entry_schema.update(
        {
            "object_type": type_name(obj),
            "top_level_key_count": len(top_keys),
            "top_level_key_sample": json.dumps([safe_repr(k, 80) for k in top_keys[:12]]),
            "protein_count": len(protein_entry_counts),
            "mutation_entry_count": entry_count,
            "entries_per_protein_min": min(entry_count_values) if entry_count_values else "",
            "entries_per_protein_median": (
                statistics.median(entry_count_values) if entry_count_values else ""
            ),
            "entries_per_protein_max": max(entry_count_values) if entry_count_values else "",
            "entry_field_union_count": len(all_fields),
            "entry_field_union": json.dumps(sorted(all_fields)),
            "fields_in_all_entries": json.dumps(sorted(fields_in_all_entries)),
            "fields_not_in_all_entries": json.dumps(sorted(all_fields - fields_in_all_entries)),
            "expected_generator_fields_present": json.dumps(
                sorted(EXPECTED_GENERATOR_FIELDS & all_fields)
            ),
            "expected_generator_fields_missing": json.dumps(
                sorted(EXPECTED_GENERATOR_FIELDS - all_fields)
            ),
            "expected_generator_fields_in_all_entries": json.dumps(
                sorted(EXPECTED_GENERATOR_FIELDS & fields_in_all_entries)
            ),
            "expected_generator_fields_not_in_all_entries": json.dumps(
                sorted(EXPECTED_GENERATOR_FIELDS - fields_in_all_entries)
            ),
            "expected_generator_field_min_occurrence_fraction": (
                f"{expected_field_min_fraction:.6f}"
                if isinstance(expected_field_min_fraction, float)
                else expected_field_min_fraction
            ),
        }
    )

    for protein_key, count in sorted(protein_entry_counts.items(), key=lambda item: item[0]):
        count_rows.append(
            {
                "dataset": target.dataset,
                "version": target.version,
                "filename": target.filename,
                "protein_key": protein_key,
                "normalized_protein_key": normalize_protein_key(protein_key),
                "mutation_entry_count": count,
            }
        )

    for field in sorted(field_occurrences):
        field_rows.append(
            {
                "dataset": target.dataset,
                "version": target.version,
                "filename": target.filename,
                "field": field,
                "occurrence_count": field_occurrences[field],
                "occurrence_fraction": (
                    f"{field_occurrences[field] / entry_count:.6f}" if entry_count else ""
                ),
                "type_counts": json.dumps(dict(field_type_counts[field].most_common())),
                "signature_counts": json.dumps(
                    dict(field_signature_counts[field].most_common(20))
                ),
                "sample_fingerprints": json.dumps(field_fingerprints[field]),
                "sample_details": json.dumps(field_sample_details[field]),
            }
        )

    summary_json.update(
        {
            "load_audit": load_audit,
            "entry_schema": entry_schema,
            "field_summary": {
                field: {
                    "occurrence_count": field_occurrences[field],
                    "type_counts": dict(field_type_counts[field].most_common()),
                    "signature_counts": dict(field_signature_counts[field].most_common(20)),
                    "sample_fingerprints": field_fingerprints[field],
                }
                for field in sorted(field_occurrences)
            },
            "entry_count_by_protein": protein_entry_counts,
        }
    )

    del obj
    return (
        manifest,
        load_audit,
        [entry_schema],
        field_rows,
        count_rows,
        missing_expected_field_rows,
        summary_json,
    )


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except FileNotFoundError:
        return ""


def line_number_for_offset(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def line_text_for_offset(text: str, offset: int) -> str:
    line_start = text.rfind("\n", 0, offset) + 1
    line_end = text.find("\n", offset)
    if line_end == -1:
        line_end = len(text)
    return text[line_start:line_end]


def is_commented_line(line: str) -> bool:
    return line.lstrip().startswith("#")


def extract_generator_schema() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    assignment_re = re.compile(r'mut\["([^"]+)"\]\s*=')
    save_re = re.compile(r'with open\("([^"]*pmppn_info_dict[^"]*\.pickle)"\s*,\s*"wb"\)')
    load_re = re.compile(r'with open\("([^"]*pmppn_info_dict[^"]*\.pickle)"\s*,\s*"rb"\)')

    for dataset, meta in DATASETS.items():
        source_path = NOTEBOOK_SOURCE_DIR / meta["generator_source"]
        text = read_text(source_path)
        assignments: list[dict[str, Any]] = []
        for match in assignment_re.finditer(text):
            assignments.append(
                {"field": match.group(1), "line": line_number_for_offset(text, match.start())}
            )
        save_refs = [
            {
                "filename": match.group(1),
                "line": line_number_for_offset(text, match.start()),
                "is_commented": is_commented_line(line_text_for_offset(text, match.start())),
            }
            for match in save_re.finditer(text)
        ]
        load_refs = [
            {
                "filename": match.group(1),
                "line": line_number_for_offset(text, match.start()),
                "is_commented": is_commented_line(line_text_for_offset(text, match.start())),
            }
            for match in load_re.finditer(text)
        ]
        assignment_fields = sorted({item["field"] for item in assignments})
        rows.append(
            {
                "dataset": dataset,
                "candidate_code_cell_text_file": str(source_path.relative_to(WORKSPACE_ROOT)),
                "code_cell_text_file_exists": source_path.exists(),
                "mut_assignment_fields": json.dumps(assignment_fields),
                "mut_assignment_count": len(assignments),
                "expected_generator_fields_found": json.dumps(
                    sorted(EXPECTED_GENERATOR_FIELDS & set(assignment_fields))
                ),
                "expected_generator_fields_missing": json.dumps(
                    sorted(EXPECTED_GENERATOR_FIELDS - set(assignment_fields))
                ),
                "save_refs": json.dumps(save_refs),
                "load_refs": json.dumps(load_refs),
            }
        )
    return rows


def extract_execution_traces(
    count_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    count_lookup: dict[tuple[str, str], int] = {}
    for row in count_rows:
        if row["version"] != "V3":
            continue
        count_lookup[(row["dataset"], row["normalized_protein_key"])] = int(
            row["mutation_entry_count"]
        )

    trace_re = re.compile(
        r"Took\s+([0-9.eE+-]+)\s+for\s+(.+?)\s+with\s+([0-9]+)\s+forward-mutations"
    )
    rows: list[dict[str, Any]] = []
    for dataset, meta in DATASETS.items():
        output_name = meta["generator_output"]
        for output_dir in NOTEBOOK_OUTPUT_DIRS:
            output_path = output_dir / output_name
            text = read_text(output_path)
            if not text:
                rows.append(
                    {
                        "dataset": dataset,
                        "output_file": str(output_path.relative_to(WORKSPACE_ROOT)),
                        "output_exists": output_path.exists(),
                        "line": "",
                        "protein_or_file": "",
                        "normalized_protein_key": "",
                        "printed_forward_mutations": "",
                        "pickle_v3_mutation_count": "",
                        "count_match": "",
                        "trace_text": "",
                    }
                )
                continue
            matches = list(trace_re.finditer(text))
            if not matches:
                rows.append(
                    {
                        "dataset": dataset,
                        "output_file": str(output_path.relative_to(WORKSPACE_ROOT)),
                        "output_exists": True,
                        "line": "",
                        "protein_or_file": "",
                        "normalized_protein_key": "",
                        "printed_forward_mutations": "",
                        "pickle_v3_mutation_count": "",
                        "count_match": "",
                        "trace_text": "NO_TRACE_MATCH",
                    }
                )
                continue
            for match in matches:
                protein_text = match.group(2).strip()
                normalized = normalize_protein_key(protein_text)
                printed_count = int(match.group(3))
                pickle_count = count_lookup.get((dataset, normalized))
                rows.append(
                    {
                        "dataset": dataset,
                        "output_file": str(output_path.relative_to(WORKSPACE_ROOT)),
                        "output_exists": True,
                        "line": line_number_for_offset(text, match.start()),
                        "protein_or_file": protein_text,
                        "normalized_protein_key": normalized,
                        "printed_forward_mutations": printed_count,
                        "pickle_v3_mutation_count": pickle_count if pickle_count is not None else "",
                        "count_match": (
                            pickle_count == printed_count if pickle_count is not None else ""
                        ),
                        "trace_text": match.group(0),
                    }
                )
    return rows


def extract_downstream_consumer_refs() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    targets = {
        dataset: f"{meta['pickle_prefix']}_pmppn_info_dict_V3.pickle"
        for dataset, meta in DATASETS.items()
    }
    seen: set[tuple[str, str, int, str]] = set()
    for source_dir in DOWNSTREAM_SOURCE_DIRS:
        if not source_dir.exists():
            continue
        for path in sorted(source_dir.glob("*.txt")):
            text = read_text(path)
            lines = text.splitlines()
            for line_no, line in enumerate(lines, start=1):
                for dataset, filename in targets.items():
                    if filename not in line:
                        continue
                    ref_type = "text_ref"
                    if re.search(r'with open\("[^"]*pmppn_info_dict[^"]*\.pickle"\s*,\s*"rb"\)', line):
                        ref_type = "load_rb"
                    elif re.search(r'with open\("[^"]*pmppn_info_dict[^"]*\.pickle"\s*,\s*"wb"\)', line):
                        ref_type = "save_wb"
                    is_commented = is_commented_line(line)
                    key = (dataset, str(path.relative_to(WORKSPACE_ROOT)), line_no, filename)
                    if key in seen:
                        continue
                    seen.add(key)
                    rows.append(
                        {
                            "dataset": dataset,
                            "v3_pickle": filename,
                            "consumer_file": str(path.relative_to(WORKSPACE_ROOT)),
                            "line": line_no,
                            "ref_type": ref_type,
                            "is_commented": is_commented,
                            "is_downstream_load": ref_type == "load_rb" and not is_commented,
                            "line_text": line.strip(),
                        }
                    )
    return rows


def build_version_field_diff(
    schema_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    field_sets: dict[tuple[str, str], set[str]] = {}
    for row in schema_rows:
        try:
            fields = set(json.loads(row.get("entry_field_union", "[]")))
        except json.JSONDecodeError:
            fields = set()
        field_sets[(row["dataset"], row["version"])] = fields

    rows: list[dict[str, Any]] = []
    for dataset in DATASETS:
        for left, right in [("base", "V2"), ("V2", "V3"), ("base", "V3")]:
            left_fields = field_sets.get((dataset, left), set())
            right_fields = field_sets.get((dataset, right), set())
            rows.append(
                {
                    "dataset": dataset,
                    "left_version": left,
                    "right_version": right,
                    "left_field_count": len(left_fields),
                    "right_field_count": len(right_fields),
                    "shared_field_count": len(left_fields & right_fields),
                    "left_only_fields": json.dumps(sorted(left_fields - right_fields)),
                    "right_only_fields": json.dumps(sorted(right_fields - left_fields)),
                    "expected_generator_fields_added_on_right": json.dumps(
                        sorted((right_fields - left_fields) & EXPECTED_GENERATOR_FIELDS)
                    ),
                    "expected_generator_fields_present_on_right": json.dumps(
                        sorted(right_fields & EXPECTED_GENERATOR_FIELDS)
                    ),
                }
            )
    return rows


def build_evidence_status(
    schema_rows: list[dict[str, Any]],
    generator_rows: list[dict[str, Any]],
    trace_rows: list[dict[str, Any]],
    consumer_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    v3_schema_by_dataset = {
        row["dataset"]: row for row in schema_rows if row.get("version") == "V3"
    }
    generator_by_dataset = {row["dataset"]: row for row in generator_rows}
    downstream_loads_by_dataset: dict[str, int] = Counter(
        row["dataset"] for row in consumer_rows if row.get("is_downstream_load") is True
    )
    traces_by_dataset: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in trace_rows:
        if row.get("trace_text") and row.get("trace_text") != "NO_TRACE_MATCH":
            traces_by_dataset[row["dataset"]].append(row)

    rows: list[dict[str, Any]] = []
    for dataset in DATASETS:
        schema = v3_schema_by_dataset.get(dataset, {})
        generator = generator_by_dataset.get(dataset, {})
        v3_missing = set(json.loads(schema.get("expected_generator_fields_missing", "[]")))
        v3_not_in_all_entries = set(
            json.loads(schema.get("expected_generator_fields_not_in_all_entries", "[]"))
        )
        generator_missing = set(json.loads(generator.get("expected_generator_fields_missing", "[]")))
        schema_match = not v3_missing
        complete_v3_expected_field_coverage = schema_match and not v3_not_in_all_entries
        generator_schema_match = not generator_missing
        downstream_load_refs = downstream_loads_by_dataset.get(dataset, 0)
        trace_list = traces_by_dataset.get(dataset, [])
        v3_protein_count = int(schema.get("protein_count") or 0)
        v3_mutation_entry_count = int(schema.get("mutation_entry_count") or 0)

        traces_by_file: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in trace_list:
            traces_by_file[str(row.get("output_file", ""))].append(row)

        best_trace_file = ""
        best_trace_count = 0
        best_trace_unique_protein_count = 0
        best_trace_printed_mutation_sum = 0
        best_trace_all_counts_match = False
        for output_file, file_rows in traces_by_file.items():
            unique_proteins = {str(row.get("normalized_protein_key", "")) for row in file_rows}
            printed_sum = sum(int(row.get("printed_forward_mutations") or 0) for row in file_rows)
            all_counts_match = all(row.get("count_match") is True for row in file_rows)
            candidate_score = (
                all_counts_match,
                len(unique_proteins),
                printed_sum,
                len(file_rows),
            )
            current_score = (
                best_trace_all_counts_match,
                best_trace_unique_protein_count,
                best_trace_printed_mutation_sum,
                best_trace_count,
            )
            if candidate_score > current_score:
                best_trace_file = output_file
                best_trace_count = len(file_rows)
                best_trace_unique_protein_count = len(unique_proteins)
                best_trace_printed_mutation_sum = printed_sum
                best_trace_all_counts_match = all_counts_match

        complete_trace_coverage = (
            bool(best_trace_count)
            and best_trace_all_counts_match
            and best_trace_unique_protein_count == v3_protein_count
            and best_trace_printed_mutation_sum == v3_mutation_entry_count
        )

        if (
            complete_v3_expected_field_coverage
            and generator_schema_match
            and downstream_load_refs
            and complete_trace_coverage
        ):
            status = "proven"
        elif schema_match and generator_schema_match and downstream_load_refs:
            status = "strong_candidate"
        else:
            status = "unresolved"

        caveats: list[str] = []
        if not schema_match:
            caveats.append(f"V3 pickle missing generator fields: {sorted(v3_missing)}")
        elif not complete_v3_expected_field_coverage:
            caveats.append(
                "V3 expected generator fields are not present on all entries: "
                f"{sorted(v3_not_in_all_entries)}"
            )
        if not generator_schema_match:
            caveats.append(f"candidate generator missing expected fields: {sorted(generator_missing)}")
        if not best_trace_count:
            caveats.append("no saved execution trace matched the Took ... forward-mutations pattern")
        elif not best_trace_all_counts_match:
            caveats.append("saved execution traces exist but do not all map cleanly to V3 pickle counts")
        elif not complete_trace_coverage:
            caveats.append(
                "best saved execution trace covers "
                f"{best_trace_unique_protein_count}/{v3_protein_count} proteins and "
                f"{best_trace_printed_mutation_sum}/{v3_mutation_entry_count} mutation entries"
            )
        if not downstream_load_refs:
            caveats.append("no downstream V3 RF load reference found")
        if status != "proven":
            caveats.append(
                "V3 with open(..., \"wb\") save statement is commented in the "
                "inspected .ipynb.py.txt code-cell text file"
            )

        rows.append(
            {
                "dataset": dataset,
                "status": status,
                "v3_schema_match": schema_match,
                "complete_v3_expected_field_coverage": complete_v3_expected_field_coverage,
                "v3_expected_field_min_occurrence_fraction": schema.get(
                    "expected_generator_field_min_occurrence_fraction", ""
                ),
                "generator_schema_match": generator_schema_match,
                "downstream_v3_load_ref_count": downstream_load_refs,
                "total_execution_trace_count": len(trace_list),
                "best_execution_trace_file": best_trace_file,
                "best_execution_trace_count": best_trace_count,
                "best_trace_unique_protein_count": best_trace_unique_protein_count,
                "v3_protein_count": v3_protein_count,
                "best_trace_printed_mutation_sum": best_trace_printed_mutation_sum,
                "v3_mutation_entry_count": v3_mutation_entry_count,
                "best_trace_all_counts_match": best_trace_all_counts_match,
                "complete_execution_trace_coverage": complete_trace_coverage,
                "caveats": " | ".join(caveats),
            }
        )
    return rows


def main() -> None:
    ensure_dirs()
    targets = collect_targets()

    manifest_rows: list[dict[str, Any]] = []
    load_rows: list[dict[str, Any]] = []
    schema_rows: list[dict[str, Any]] = []
    field_rows: list[dict[str, Any]] = []
    count_rows: list[dict[str, Any]] = []
    missing_expected_field_rows: list[dict[str, Any]] = []
    summary_json: dict[str, Any] = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_dir": str(PICKLE_SOURCE_DIR.relative_to(WORKSPACE_ROOT)),
        "files": {},
    }

    for target in targets:
        (
            manifest,
            load_audit,
            schema_list,
            file_field_rows,
            file_count_rows,
            file_missing_expected_field_rows,
            file_json,
        ) = (
            summarize_pickle(target)
        )
        manifest_rows.append(manifest)
        load_rows.append(load_audit)
        schema_rows.extend(schema_list)
        field_rows.extend(file_field_rows)
        count_rows.extend(file_count_rows)
        missing_expected_field_rows.extend(file_missing_expected_field_rows)
        summary_json["files"][target.filename] = file_json

    diff_rows = build_version_field_diff(schema_rows)
    generator_rows = extract_generator_schema()
    trace_rows = extract_execution_traces(count_rows)
    consumer_rows = extract_downstream_consumer_refs()
    evidence_rows = build_evidence_status(
        schema_rows, generator_rows, trace_rows, consumer_rows
    )

    write_tsv(
        TABLE_DIR / "v3_pickle_file_manifest.tsv",
        manifest_rows,
        ["dataset", "version", "filename", "path", "size_bytes", "mtime_utc", "sha256"],
    )
    write_tsv(
        TABLE_DIR / "v3_pickle_load_audit.tsv",
        load_rows,
        ["dataset", "version", "filename", "status", "error", "resolved_globals"],
    )
    write_tsv(
        TABLE_DIR / "v3_pickle_entry_schema.tsv",
        schema_rows,
        [
            "dataset",
            "version",
            "filename",
            "object_type",
            "top_level_key_count",
            "top_level_key_sample",
            "protein_count",
            "mutation_entry_count",
            "entries_per_protein_min",
            "entries_per_protein_median",
            "entries_per_protein_max",
            "entry_field_union_count",
            "entry_field_union",
            "fields_in_all_entries",
            "fields_not_in_all_entries",
            "expected_generator_fields_present",
            "expected_generator_fields_missing",
            "expected_generator_fields_in_all_entries",
            "expected_generator_fields_not_in_all_entries",
            "expected_generator_field_min_occurrence_fraction",
        ],
    )
    write_tsv(
        TABLE_DIR / "v3_pickle_entry_field_summary.tsv",
        field_rows,
        [
            "dataset",
            "version",
            "filename",
            "field",
            "occurrence_count",
            "occurrence_fraction",
            "type_counts",
            "signature_counts",
            "sample_fingerprints",
            "sample_details",
        ],
    )
    write_tsv(
        TABLE_DIR / "v3_pickle_entry_count_by_protein.tsv",
        count_rows,
        [
            "dataset",
            "version",
            "filename",
            "protein_key",
            "normalized_protein_key",
            "mutation_entry_count",
        ],
    )
    write_tsv(
        TABLE_DIR / "v3_missing_expected_fields_by_entry.tsv",
        missing_expected_field_rows,
        [
            "dataset",
            "version",
            "filename",
            "protein_key",
            "normalized_protein_key",
            "entry_index",
            "mut",
            "ddg",
            "present_expected_fields",
            "missing_expected_fields",
        ],
    )
    write_tsv(
        TABLE_DIR / "v3_pickle_version_field_diff.tsv",
        diff_rows,
        [
            "dataset",
            "left_version",
            "right_version",
            "left_field_count",
            "right_field_count",
            "shared_field_count",
            "left_only_fields",
            "right_only_fields",
            "expected_generator_fields_added_on_right",
            "expected_generator_fields_present_on_right",
        ],
    )
    write_tsv(
        TABLE_DIR / "v3_generator_notebook_schema.tsv",
        generator_rows,
        [
            "dataset",
            "candidate_code_cell_text_file",
            "code_cell_text_file_exists",
            "mut_assignment_fields",
            "mut_assignment_count",
            "expected_generator_fields_found",
            "expected_generator_fields_missing",
            "save_refs",
            "load_refs",
        ],
    )
    write_tsv(
        TABLE_DIR / "v3_generator_execution_traces.tsv",
        trace_rows,
        [
            "dataset",
            "output_file",
            "output_exists",
            "line",
            "protein_or_file",
            "normalized_protein_key",
            "printed_forward_mutations",
            "pickle_v3_mutation_count",
            "count_match",
            "trace_text",
        ],
    )
    write_tsv(
        TABLE_DIR / "v3_downstream_consumer_refs.tsv",
        consumer_rows,
        [
            "dataset",
            "v3_pickle",
            "consumer_file",
            "line",
            "ref_type",
            "is_commented",
            "is_downstream_load",
            "line_text",
        ],
    )
    write_tsv(
        TABLE_DIR / "v3_dataset_evidence_status.tsv",
        evidence_rows,
        [
            "dataset",
            "status",
            "v3_schema_match",
            "complete_v3_expected_field_coverage",
            "v3_expected_field_min_occurrence_fraction",
            "generator_schema_match",
            "downstream_v3_load_ref_count",
            "total_execution_trace_count",
            "best_execution_trace_file",
            "best_execution_trace_count",
            "best_trace_unique_protein_count",
            "v3_protein_count",
            "best_trace_printed_mutation_sum",
            "v3_mutation_entry_count",
            "best_trace_all_counts_match",
            "complete_execution_trace_coverage",
            "caveats",
        ],
    )

    summary_json["version_field_diff"] = diff_rows
    summary_json["missing_expected_fields_by_entry"] = missing_expected_field_rows
    summary_json["generator_schema"] = generator_rows
    summary_json["execution_traces"] = trace_rows
    summary_json["downstream_consumer_refs"] = consumer_rows
    summary_json["evidence_status"] = evidence_rows
    with (JSON_DIR / "v3_pickle_fingerprints.json").open("w", encoding="utf-8") as handle:
        json.dump(summary_json, handle, indent=2, sort_keys=True)


if __name__ == "__main__":
    main()
