#!/usr/bin/env python3
"""Inspect historical incremental-feature result pickles.

This script answers two narrow recovery questions:

1. What exact code-level feature map was used by the later A-H incremental
   feature workflow?
2. What numeric results are stored in the saved one-run and ten-run
   incremental-feature result pickles?

The script is read-only with respect to copied evidence files.
"""

from __future__ import annotations

import csv
import json
import math
import pickle
import statistics
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


WORKSPACE = Path(__file__).resolve().parents[1]
EVIDENCE_ROOT = (
    WORKSPACE
    / "drive_evidence_copy"
    / "sajidahmedprotres_drive"
    / "Protein_MPNN_Digging"
)
OUTPUT_DIR = WORKSPACE / "code_inventory_analysis" / "incremental_feature_pickle_inspection"

PICKLE_FILES = [
    "incremental_feature_result_dict.pickle",
    "list_incremental_feature_result_dict.pickle",
]

DATASETS = ["S_2648", "S_921", "S_669", "Ssym"]
INCREMENTAL_COMBOS = [
    "A",
    "A+B",
    "A+B+C",
    "A+B+C+D",
    "A+B+C+D+E",
    "A+B+C+D+E+F",
    "A+B+C+D+E+F+G",
    "A+B+C+D+E+F+G+H",
]

LEGACY_AF_FEATURE_MAP = [
    {
        "label": "A",
        "columns": "0",
        "code_field_or_expression": "center_mut_wild_energy",
        "notebook_comment_name": "P_DP",
        "workflow": "feature_combo_* V2 all-combinations",
    },
    {
        "label": "B",
        "columns": "4",
        "code_field_or_expression": "V2_backward_weighted_neighbor_backward_KL",
        "notebook_comment_name": "BACK_KL",
        "workflow": "feature_combo_* V2 all-combinations",
    },
    {
        "label": "C",
        "columns": "7",
        "code_field_or_expression": "center_neighbor_weight_check_w_m",
        "notebook_comment_name": "W/M",
        "workflow": "feature_combo_* V2 all-combinations",
    },
    {
        "label": "D",
        "columns": "2",
        "code_field_or_expression": "V2_backward_weighted_neighbor_energy_changes",
        "notebook_comment_name": "Neighbor_Energy",
        "workflow": "feature_combo_* V2 all-combinations",
    },
    {
        "label": "E",
        "columns": "6",
        "code_field_or_expression": "V2_backward_weighted_neighbor_entropy_changes",
        "notebook_comment_name": "Neighbor_Entropy",
        "workflow": "feature_combo_* V2 all-combinations",
    },
    {
        "label": "F",
        "columns": "5",
        "code_field_or_expression": "wild_pssm - alternate_pssm",
        "notebook_comment_name": "PSSM",
        "workflow": "feature_combo_* V2 all-combinations",
    },
]

INCREMENTAL_AH_FEATURE_MAP = [
    {
        "label": "A",
        "columns": "0",
        "code_field_or_expression": "center_mut_wild_energy",
        "column_block_meaning_from_source": "center wild-vs-mutant log-probability/energy change",
    },
    {
        "label": "B",
        "columns": "6",
        "code_field_or_expression": "V2_backward_weighted_neighbor_entropy_changes",
        "column_block_meaning_from_source": "weighted backward neighbor entropy change",
    },
    {
        "label": "C",
        "columns": "7",
        "code_field_or_expression": "center_neighbor_weight_check_w_m",
        "column_block_meaning_from_source": "center-to-neighbor message norm ratio",
    },
    {
        "label": "D",
        "columns": "8",
        "code_field_or_expression": "neighbor_embedding_change_m_w",
        "column_block_meaning_from_source": "summed neighbor embedding change",
    },
    {
        "label": "E",
        "columns": "31,32,33,34,35",
        "code_field_or_expression": "first five columns selected from reverse neighbor-embedding KPCA block",
        "column_block_meaning_from_source": "columns 31..40 are reverse neighbor-embedding KPCA",
    },
    {
        "label": "F",
        "columns": "5",
        "code_field_or_expression": "wild_pssm - alternate_pssm",
        "column_block_meaning_from_source": "PSSM delta",
    },
    {
        "label": "G",
        "columns": "9",
        "code_field_or_expression": "wild_pssm",
        "column_block_meaning_from_source": "wild-type PSSM value",
    },
    {
        "label": "H",
        "columns": "10",
        "code_field_or_expression": "alternate_pssm",
        "column_block_meaning_from_source": "mutant amino-acid PSSM value",
    },
]


def write_tsv(path: Path, rows: Iterable[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            delimiter="\t",
            fieldnames=fields,
            extrasaction="ignore",
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def json_safe(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, bool)):
        return value
    if isinstance(value, float):
        if math.isfinite(value):
            return value
        return repr(value)
    if isinstance(value, dict):
        return {str(key): json_safe(child) for key, child in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(child) for child in value]
    if hasattr(value, "item"):
        try:
            return json_safe(value.item())
        except Exception:
            pass
    return repr(value)


def load_pickle(name: str) -> Any:
    with (EVIDENCE_ROOT / name).open("rb") as handle:
        return pickle.load(handle)


def parse_metric_key(metric_key: str) -> dict[str, str]:
    for dataset in DATASETS:
        prefix = f"{dataset}_"
        if metric_key.startswith(prefix):
            remainder = metric_key[len(prefix) :]
            if remainder == "forward_reverse_PCC":
                return {
                    "dataset": dataset,
                    "split": "forward_reverse",
                    "metric": "PCC",
                    "metric_kind": "scalar_full_feature_only",
                }
            split, metric = remainder.rsplit("_", 1)
            return {
                "dataset": dataset,
                "split": split,
                "metric": metric,
                "metric_kind": "feature_combo_dict",
            }
    return {
        "dataset": "",
        "split": "",
        "metric": "",
        "metric_kind": "unparsed",
    }


def numeric_value(value: Any) -> float:
    if hasattr(value, "item"):
        value = value.item()
    return float(value)


def flatten_result_dict(
    pickle_file: str,
    result_dict: dict[str, Any],
    run_index: int | None,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for metric_key, value in result_dict.items():
        parsed = parse_metric_key(metric_key)
        if isinstance(value, dict):
            for feature_combo, numeric in value.items():
                rows.append(
                    {
                        "pickle_file": pickle_file,
                        "run_index": "" if run_index is None else run_index,
                        "metric_key": metric_key,
                        "dataset": parsed["dataset"],
                        "split": parsed["split"],
                        "metric": parsed["metric"],
                        "metric_kind": parsed["metric_kind"],
                        "feature_combo": feature_combo,
                        "value": numeric_value(numeric),
                    }
                )
        else:
            rows.append(
                {
                    "pickle_file": pickle_file,
                    "run_index": "" if run_index is None else run_index,
                    "metric_key": metric_key,
                    "dataset": parsed["dataset"],
                    "split": parsed["split"],
                    "metric": parsed["metric"],
                    "metric_kind": parsed["metric_kind"],
                    "feature_combo": "A+B+C+D+E+F+G+H",
                    "value": numeric_value(value),
                }
            )
    return rows


def flatten_pickle(pickle_file: str, obj: Any) -> list[dict[str, object]]:
    if isinstance(obj, list):
        rows: list[dict[str, object]] = []
        for run_index, result_dict in enumerate(obj):
            rows.extend(flatten_result_dict(pickle_file, result_dict, run_index))
        return rows
    if isinstance(obj, dict):
        return flatten_result_dict(pickle_file, obj, None)
    raise TypeError(f"Unsupported object type in {pickle_file}: {type(obj)!r}")


def summarize_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    groups: dict[tuple[object, ...], list[float]] = defaultdict(list)
    for row in rows:
        key = (
            row["pickle_file"],
            row["metric_key"],
            row["dataset"],
            row["split"],
            row["metric"],
            row["metric_kind"],
            row["feature_combo"],
        )
        groups[key].append(float(row["value"]))

    summary_rows: list[dict[str, object]] = []
    for key, values in sorted(groups.items(), key=lambda item: tuple(str(part) for part in item[0])):
        (
            pickle_file,
            metric_key,
            dataset,
            split,
            metric,
            metric_kind,
            feature_combo,
        ) = key
        n = len(values)
        mean_value = statistics.fmean(values)
        sample_std = statistics.stdev(values) if n > 1 else 0.0
        population_std = statistics.pstdev(values) if n > 1 else 0.0
        summary_rows.append(
            {
                "pickle_file": pickle_file,
                "metric_key": metric_key,
                "dataset": dataset,
                "split": split,
                "metric": metric,
                "metric_kind": metric_kind,
                "feature_combo": feature_combo,
                "n": n,
                "mean": mean_value,
                "sample_std": sample_std,
                "population_std": population_std,
                "min": min(values),
                "max": max(values),
                "round_mean_2": round(mean_value, 2),
            }
        )
    return summary_rows


def object_summary(name: str, obj: Any) -> dict[str, Any]:
    summary: dict[str, Any] = {
        "pickle_file": name,
        "type": f"{obj.__class__.__module__}.{obj.__class__.__name__}",
    }
    if isinstance(obj, list):
        summary["len"] = len(obj)
        summary["item_types"] = sorted({f"{item.__class__.__module__}.{item.__class__.__name__}" for item in obj})
        summary["first_item_keys"] = sorted(str(key) for key in obj[0].keys()) if obj else []
    elif isinstance(obj, dict):
        summary["len"] = len(obj)
        summary["keys"] = sorted(str(key) for key in obj.keys())
    return summary


def filter_summary(
    summary_rows: list[dict[str, object]],
    pickle_file: str,
    datasets: set[str],
    split: str,
    metric: str,
) -> list[dict[str, object]]:
    combo_order = {combo: idx for idx, combo in enumerate(INCREMENTAL_COMBOS)}
    return sorted(
        [
            row
            for row in summary_rows
            if row["pickle_file"] == pickle_file
            and row["dataset"] in datasets
            and row["split"] == split
            and row["metric"] == metric
            and row["feature_combo"] in combo_order
        ],
        key=lambda row: (str(row["dataset"]), combo_order[str(row["feature_combo"])]),
    )


def format_table(rows: list[dict[str, object]], fields: list[str]) -> str:
    lines = ["| " + " | ".join(fields) + " |", "| " + " | ".join("---" for _ in fields) + " |"]
    for row in rows:
        values: list[str] = []
        for field in fields:
            value = row[field]
            if isinstance(value, float):
                if field == "round_mean_2":
                    values.append(f"{value:.2f}")
                else:
                    values.append(f"{value:.6f}")
            else:
                values.append(str(value))
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def build_readme(
    object_summaries: list[dict[str, Any]],
    figure6_rows: list[dict[str, object]],
    full_ah_rows: list[dict[str, object]],
) -> str:
    generated_at = datetime.now(timezone.utc).isoformat()
    feature_map_table = format_table(
        INCREMENTAL_AH_FEATURE_MAP,
        ["label", "columns", "code_field_or_expression", "column_block_meaning_from_source"],
    )
    legacy_map_table = format_table(
        LEGACY_AF_FEATURE_MAP,
        ["label", "columns", "code_field_or_expression", "notebook_comment_name"],
    )
    figure6_table = format_table(
        figure6_rows,
        ["dataset", "feature_combo", "n", "mean", "sample_std", "round_mean_2"],
    )
    full_ah_table = format_table(
        full_ah_rows,
        ["dataset", "split", "metric", "n", "mean", "sample_std", "round_mean_2"],
    )
    summary_json = json.dumps(json_safe(object_summaries), indent=2, sort_keys=True)

    return f"""# Incremental-Feature Pickle Inspection

Generated at: `{generated_at}`.

This report inspects the two saved incremental-feature result pickles in
`drive_evidence_copy/sajidahmedprotres_drive/Protein_MPNN_Digging`.

## Loaded Pickles

```json
{summary_json}
```

## Later A-H Incremental Feature Map

This is the feature map in `Quick_Dirty_MPNN_ML_V2_VGRAPHS_V1.ipynb.py.txt`.
The RFs are trained on `S_2648_X_aug[:, f_index_comb]` and `S_2648_y_aug`.

{feature_map_table}

The full A-H model therefore uses these feature-matrix columns:
`[0, 6, 7, 8, 31, 32, 33, 34, 35, 5, 9, 10]`.

Important reconciliation note: in this code path, feature E is columns 31..35.
The same source file identifies columns 31..40 as reverse neighbor-embedding
KPCA features. This is code-level evidence and should be reconciled separately
against manuscript wording before making a final methods claim.

Observed saved-object note: the inspected ten-run list pickle contains the
feature-combination metric dictionaries shown above. It does not contain the
optional `*_forward_reverse_PCC` scalar keys visible in the source loop. Those
scalars are commented out in the downstream averaging/printing cells and are
not used by the Figure 6-style total-PCC bar plot.

## Older A-F Feature Map for `feature_combo_*`

The unsuffixed `feature_combo_*` pickles are not the A-H incremental workflow.
They come from the older V2 all-combinations workflow. For each model key,
the RF is trained on the corresponding subset of the six features below.

{legacy_map_table}

The full A-F model uses columns `[0, 4, 7, 2, 6, 5]` in label order.
The result pickle contains all 63 non-empty subsets of A-F.

## Figure 6 Candidate Values

The plotting cell for the manuscript-like combined bar chart uses
`dict_mean(list_S_669_total_PCC)` and `dict_mean(list_Ssym_total_PCC)`.
The table below summarizes the ten-run `list_incremental_feature_result_dict`
values for exactly those two total-PCC series.

{figure6_table}

## Full A-H Metrics

These are the full A-H mean values from the ten-run list pickle for the held-out
datasets that appear in manuscript Table 1 / Figure 6 discussions.

{full_ah_table}

## Generated Files

- `incremental_feature_object_summary.json`
- `incremental_feature_raw_rows.tsv`
- `incremental_feature_summary.tsv`
- `figure6_total_pcc_summary.tsv`
- `full_ah_metric_summary.tsv`
- `legacy_af_feature_map.tsv`
- `incremental_ah_feature_map.tsv`
"""


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    all_rows: list[dict[str, object]] = []
    object_summaries: list[dict[str, Any]] = []
    for pickle_file in PICKLE_FILES:
        pickle_path = EVIDENCE_ROOT / pickle_file
        if not pickle_path.exists():
            print(f"skip missing pickle: {pickle_file}")
            continue
        obj = load_pickle(pickle_file)
        object_summaries.append(object_summary(pickle_file, obj))
        all_rows.extend(flatten_pickle(pickle_file, obj))
    if not all_rows:
        raise SystemExit("No incremental-feature pickles found under evidence root.")

    summary_rows = summarize_rows(all_rows)
    figure6_rows = filter_summary(
        summary_rows,
        "list_incremental_feature_result_dict.pickle",
        {"S_669", "Ssym"},
        "total",
        "PCC",
    )
    full_ah_rows = [
        row
        for row in summary_rows
        if row["pickle_file"] == "list_incremental_feature_result_dict.pickle"
        and row["dataset"] in {"S_921", "S_669", "Ssym"}
        and row["feature_combo"] == "A+B+C+D+E+F+G+H"
    ]
    full_ah_rows.sort(key=lambda row: (str(row["dataset"]), str(row["metric"]), str(row["split"])))

    with (OUTPUT_DIR / "incremental_feature_object_summary.json").open("w", encoding="utf-8") as handle:
        json.dump(json_safe(object_summaries), handle, indent=2, sort_keys=True)

    raw_fields = [
        "pickle_file",
        "run_index",
        "metric_key",
        "dataset",
        "split",
        "metric",
        "metric_kind",
        "feature_combo",
        "value",
    ]
    summary_fields = [
        "pickle_file",
        "metric_key",
        "dataset",
        "split",
        "metric",
        "metric_kind",
        "feature_combo",
        "n",
        "mean",
        "sample_std",
        "population_std",
        "min",
        "max",
        "round_mean_2",
    ]
    write_tsv(OUTPUT_DIR / "incremental_feature_raw_rows.tsv", all_rows, raw_fields)
    write_tsv(OUTPUT_DIR / "incremental_feature_summary.tsv", summary_rows, summary_fields)
    write_tsv(OUTPUT_DIR / "figure6_total_pcc_summary.tsv", figure6_rows, summary_fields)
    write_tsv(OUTPUT_DIR / "full_ah_metric_summary.tsv", full_ah_rows, summary_fields)
    write_tsv(
        OUTPUT_DIR / "legacy_af_feature_map.tsv",
        LEGACY_AF_FEATURE_MAP,
        ["label", "columns", "code_field_or_expression", "notebook_comment_name", "workflow"],
    )
    write_tsv(
        OUTPUT_DIR / "incremental_ah_feature_map.tsv",
        INCREMENTAL_AH_FEATURE_MAP,
        ["label", "columns", "code_field_or_expression", "column_block_meaning_from_source"],
    )

    readme = build_readme(object_summaries, figure6_rows, full_ah_rows)
    (OUTPUT_DIR / "README.md").write_text(readme, encoding="utf-8")


if __name__ == "__main__":
    main()
