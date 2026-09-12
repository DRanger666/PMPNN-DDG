#!/usr/bin/env python3
"""Regenerate and verify manuscript Table 1 from the saved RF result pickle.

This is a results-layer check only:
  list_incremental_feature_result_dict.pickle
  + saved notebook-output rF-R evidence
  -> Table 1 PMPNN-DDG rows for S_669, Ssym, S_921

It does not regenerate RF models or V3 tensors.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import pickle
import statistics
from pathlib import Path
from typing import Any


WORKSPACE = Path(__file__).resolve().parents[1]
DEFAULT_PICKLE = (
    WORKSPACE
    / "reproduction_inputs"
    / "historical_reference_pickles"
    / "list_incremental_feature_result_dict.pickle"
)
DEFAULT_OUTPUT_DIR = (
    WORKSPACE / "reproduction_runs" / "latest" / "table1_results_layer"
)

FULL_AH = "A+B+C+D+E+F+G+H"
DATASETS = ["S_669", "Ssym", "S_921"]

# Manuscript Table 1 rounded cells (PMPNN-DDG independent-test rows).
MANUSCRIPT_ROUNDED = {
    "S_669": {
        "rF": 0.48,
        "rR": 0.48,
        "rF+R": 0.64,
        "rF-R": -0.99,
        "rmsF": 1.45,
        "rmsR": 1.45,
        "rmsF+R": 1.45,
    },
    "Ssym": {
        "rF": 0.72,
        "rR": 0.72,
        "rF+R": 0.81,
        "rF-R": -0.99,
        "rmsF": 1.10,
        "rmsR": 1.10,
        "rmsF+R": 1.10,
    },
    "S_921": {
        "rF": 0.77,
        "rR": 0.77,
        "rF+R": 0.79,
        "rF-R": -1.00,
        "rmsF": 1.49,
        "rmsR": 1.49,
        "rmsF+R": 1.49,
    },
}

# Saved notebook-output evidence for rF-R (not stored in the ten-run pickle).
NOTEBOOK_RF_MINUS_R = {
    "S_669": {
        "value": -0.9939184352208846,
        "source": (
            "colab_notebooks_inventory_analysis/git_notebook_outputs/"
            "Quick_Dirty_MPNN_ML_V2_V3.ipynb.outputs.txt (cell 31, 2nd printed value)"
        ),
    },
    "Ssym": {
        "value": -0.9946606797887094,
        "source": (
            "colab_notebooks_inventory_analysis/git_notebook_outputs/"
            "Quick_Dirty_MPNN_ML_V2_V3.ipynb.outputs.txt (cell 31, 3rd printed value)"
        ),
    },
    "S_921": {
        "value": -0.9960837257021014,
        "source": (
            "colab_notebooks_inventory_analysis/git_notebook_outputs/"
            "Quick_Dirty_MPNN_ML_V2_V3.ipynb.outputs.txt (cell 31, 1st printed value)"
        ),
    },
}

PICKLE_METRIC_MAP = {
    "rF": ("direct", "PCC"),
    "rR": ("reverse", "PCC"),
    "rF+R": ("total", "PCC"),
    "rmsF": ("direct", "RMSE"),
    "rmsR": ("reverse", "RMSE"),
    "rmsF+R": ("total", "RMSE"),
}


def round2(value: float) -> float:
    return float(f"{value:.2f}")


def load_runs(path: Path) -> list[dict[str, Any]]:
    with path.open("rb") as handle:
        obj = pickle.load(handle)
    if not isinstance(obj, list):
        raise TypeError(f"Expected list pickle, got {type(obj)!r}")
    return obj


def ten_run_mean(runs: list[dict[str, Any]], dataset: str, split: str, metric: str) -> float:
    key = f"{dataset}_{split}_{metric}"
    values = []
    for run in runs:
        combo_dict = run[key]
        values.append(float(combo_dict[FULL_AH]))
    if len(values) != 10:
        raise ValueError(f"{key}: expected 10 runs, got {len(values)}")
    return statistics.fmean(values)


def write_tsv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result-pickle", type=Path, default=DEFAULT_PICKLE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    runs = load_runs(args.result_pickle)
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, Any]] = []
    pickle_matches = 0
    notebook_matches = 0
    pickle_cells = 0
    notebook_cells = 0

    for dataset in DATASETS:
        for column, (split, metric) in PICKLE_METRIC_MAP.items():
            mean_value = ten_run_mean(runs, dataset, split, metric)
            manuscript = MANUSCRIPT_ROUNDED[dataset][column]
            rounded = round2(mean_value)
            match = math.isclose(rounded, manuscript, abs_tol=5e-3)
            pickle_cells += 1
            pickle_matches += int(match)
            rows.append(
                {
                    "dataset": dataset,
                    "column": column,
                    "evidence": "pickle_ten_run_mean",
                    "raw_mean": f"{mean_value:.12g}",
                    "rounded_2": f"{rounded:.2f}",
                    "manuscript_rounded": f"{manuscript:.2f}",
                    "match": str(match),
                }
            )

        notebook = NOTEBOOK_RF_MINUS_R[dataset]
        raw = float(notebook["value"])
        manuscript = MANUSCRIPT_ROUNDED[dataset]["rF-R"]
        rounded = round2(raw)
        match = math.isclose(rounded, manuscript, abs_tol=5e-3)
        notebook_cells += 1
        notebook_matches += int(match)
        rows.append(
            {
                "dataset": dataset,
                "column": "rF-R",
                "evidence": "notebook_output",
                "raw_mean": f"{raw:.12g}",
                "rounded_2": f"{rounded:.2f}",
                "manuscript_rounded": f"{manuscript:.2f}",
                "match": str(match),
                "notebook_source": notebook["source"],
            }
        )

    fields = [
        "dataset",
        "column",
        "evidence",
        "raw_mean",
        "rounded_2",
        "manuscript_rounded",
        "match",
        "notebook_source",
    ]
    for row in rows:
        row.setdefault("notebook_source", "")
    write_tsv(output_dir / "table1_cell_comparison.tsv", rows, fields)

    summary = {
        "result_pickle": str(args.result_pickle.relative_to(WORKSPACE)),
        "n_runs": len(runs),
        "pickle_supported_cells": pickle_cells,
        "pickle_matches": pickle_matches,
        "notebook_supported_rf_minus_r_cells": notebook_cells,
        "notebook_matches": notebook_matches,
        "total_table1_cells": pickle_cells + notebook_cells,
        "total_matches": pickle_matches + notebook_matches,
        "all_matched": (pickle_matches + notebook_matches) == (pickle_cells + notebook_cells),
        "manuscript_columns": ["rF", "rR", "rF+R", "rF-R", "rmsF", "rmsR", "rmsF+R"],
        "datasets": DATASETS,
    }
    (output_dir / "table1_verification_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    readme = f"""# Table 1 Results-Layer Verification

Generated from `{summary['result_pickle']}`.

## Result

- Pickle-supported cells matched: `{pickle_matches}/{pickle_cells}`
- Notebook-supported rF-R cells matched: `{notebook_matches}/{notebook_cells}`
- Total Table 1 numeric cells matched: `{summary['total_matches']}/{summary['total_table1_cells']}`
- All matched: `{summary['all_matched']}`

## Scope

This verifies the final RF-result evidence layer only. It does not prove
PDB→V3 tensor→feature→RF end-to-end regeneration.
"""
    (output_dir / "README.md").write_text(readme, encoding="utf-8")

    print(json.dumps(summary, indent=2, sort_keys=True))
    if not summary["all_matched"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
