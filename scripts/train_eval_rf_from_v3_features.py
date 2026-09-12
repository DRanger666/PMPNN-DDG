#!/usr/bin/env python3
"""Train/evaluate RF on Features A–H built from saved historical V3 pickles.

Feature source label: saved_historical_V3_engineered (+ KPCA Feature E fit on
S_2648 neighbor_message_change_m_w_raw from those same pickles).

This does NOT regenerate ProteinMPNN tensors from PDB. It proves the RF +
metrics loop against manuscript Table 1 targets.

Primary RF hyperparams follow the BioRxiv manuscript text:
  RandomForestRegressor(n_estimators=500, max_samples=0.5)  # other defaults

Secondary (notebook Table-1 / Fig-6 source cell) explicitly sets:
  min_samples_split=2, n_estimators=500, max_samples=0.5, max_features="sqrt"

Optional tertiary: early notebook settings
  min_samples_split=5, n_estimators=300, max_samples=0.2, max_features="sqrt"

Protocol mirrors Quick_Dirty_MPNN_ML_V2_VGRAPHS_V1.ipynb cells that produced
list_incremental_feature_result_dict.pickle (train on S2648 with forward+reverse
augmentation; evaluate S669/Ssym/S921; 10 RF runs for means).
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import pickle
import time
from pathlib import Path
from typing import Any

import numpy as np
from scipy.stats import pearsonr, entropy
from sklearn.decomposition import KernelPCA, PCA
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler


WORKSPACE = Path(__file__).resolve().parents[1]
DEFAULT_DIGGING = (
    WORKSPACE
    / "drive_evidence_copy"
    / "sajidahmedprotres_drive"
    / "Protein_MPNN_Digging"
)
DEFAULT_OUTPUT = WORKSPACE / "reproduction_runs" / "latest" / "rf_from_v3_features"

REQUIRED_FIELDS = [
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
]

# Manuscript A–H map from VGRAPHS notebook feature_to_index_map
FEATURE_TO_INDEX = {
    "A": 0,  # center_mut_wild_energy
    "B": 6,  # V2_backward_weighted_neighbor_entropy_changes
    "C": 7,  # center_neighbor_weight_check_w_m
    "D": 8,  # neighbor_embedding_change_m_w
    "E": [31, 32, 33, 34, 35],  # first 5 message-KPCA cols in augmented matrix
    "F": 5,  # wild_pssm - alternate_pssm
    "G": 9,  # wild_pssm
    "H": 10,  # alternate_pssm
}

FULL_AH = ("A", "B", "C", "D", "E", "F", "G", "H")
INCREMENTAL = [
    ("A",),
    ("A", "B"),
    ("A", "B", "C"),
    ("A", "B", "C", "D"),
    ("A", "B", "C", "D", "E"),
    ("A", "B", "C", "D", "E", "F"),
    ("A", "B", "C", "D", "E", "F", "G"),
    ("A", "B", "C", "D", "E", "F", "G", "H"),
]

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

RF_CONFIGS = {
    "manuscript_literal": {
        "n_estimators": 500,
        "max_samples": 0.5,
        # remaining sklearn RandomForestRegressor defaults
    },
    "notebook_table1": {
        "n_estimators": 500,
        "max_samples": 0.5,
        "min_samples_split": 2,
        "max_features": "sqrt",
    },
    "notebook_early": {
        "n_estimators": 300,
        "max_samples": 0.2,
        "min_samples_split": 5,
        "max_features": "sqrt",
    },
}


def load_v3(path: Path) -> dict[str, list[dict[str, Any]]]:
    with path.open("rb") as handle:
        obj = pickle.load(handle)
    if not isinstance(obj, dict):
        raise TypeError(f"Expected dict pickle at {path}, got {type(obj)!r}")
    return obj


def entry_complete(mut: dict[str, Any]) -> bool:
    for field in REQUIRED_FIELDS:
        if field not in mut or mut[field] is None:
            return False
    return True



def manuscript_unweighted_feature_b(mut: dict[str, Any]) -> float:
    """Manuscript Eq.1 Feature B: Σ_j (H(P_j^WT) - H(P_j^MT)), unweighted.

    Uses saved neighbor log-prob vectors from historical V3 pickles
    (w_n_log_prob / m_n_log_prob), first 15 attended neighbors.
    """
    total = 0.0
    for neighbor_w, neighbor_m in zip(mut["w_n_log_prob"][:15], mut["m_n_log_prob"][:15]):
        h_wt = float(entropy(np.exp(np.asarray(neighbor_w, dtype=np.float64))))
        h_mt = float(entropy(np.exp(np.asarray(neighbor_m, dtype=np.float64))))
        total += h_wt - h_mt
    return total


def build_raw_instances(
    two_level: dict[str, list[dict[str, Any]]],
    feature_b_mode: str = "historical_weighted",
) -> tuple[list[list[Any]], list[float], list[np.ndarray], list[np.ndarray], dict[str, int]]:
    """Build per-mutation raw feature lists before KPCA projection.

    Matches notebook cell 8 scalar packing (indices 0..10 + 4 raw matrices).
    """
    X: list[list[Any]] = []
    y: list[float] = []
    n_e_c_raw: list[np.ndarray] = []
    n_m_c_raw: list[np.ndarray] = []
    skipped = 0
    kept = 0
    for _prot, muts in two_level.items():
        for mut in muts:
            if not entry_complete(mut):
                skipped += 1
                continue
            cur_X: list[Any] = []
            cur_X.append(float(mut["center_mut_wild_energy"]))  # 0
            cur_X.append(float(mut["center_entropy"]))  # 1
            cur_X.append(float(mut["V2_backward_weighted_neighbor_energy_changes"]))  # 2
            cur_X.append(float(mut["weighted_neighbor_forward_KL"]))  # 3
            cur_X.append(float(mut["V2_backward_weighted_neighbor_backward_KL"]))  # 4
            pssm_feature = float(mut["wild_pssm"]) - float(mut["alternate_pssm"])
            cur_X.append(pssm_feature)  # 5
            if feature_b_mode == "manuscript_unweighted":
                if "w_n_log_prob" not in mut or "m_n_log_prob" not in mut:
                    skipped += 1
                    continue
                cur_X.append(float(manuscript_unweighted_feature_b(mut)))  # 6 manuscript Eq.1
            else:
                cur_X.append(float(mut["V2_backward_weighted_neighbor_entropy_changes"]))  # 6 historical
            cur_X.append(float(mut["center_neighbor_weight_check_w_m"]))  # 7
            cur_X.append(float(mut["neighbor_embedding_change_m_w"]))  # 8
            cur_X.append(float(mut["wild_pssm"]))  # 9
            cur_X.append(float(mut["alternate_pssm"]))  # 10

            emb_raw = np.asarray(mut["neighbor_embedding_change_m_w_raw"], dtype=np.float64)
            msg_raw = np.asarray(mut["neighbor_message_change_m_w_raw"], dtype=np.float64).squeeze()
            cur_X.append(emb_raw)  # -4
            cur_X.append(-1.0 * emb_raw)  # -3
            cur_X.append(msg_raw)  # -2
            cur_X.append(-1.0 * msg_raw)  # -1

            X.append(cur_X)
            y.append(float(mut["ddg"]))
            n_e_c_raw.append(emb_raw)
            n_m_c_raw.append(msg_raw)
            kept += 1
    stats = {"kept": kept, "skipped_incomplete": skipped}
    return X, y, n_e_c_raw, n_m_c_raw, stats


def fit_projection(
    n_e_c_raw_2648: list[np.ndarray],
    n_m_c_raw_2648: list[np.ndarray],
    kpca_sample_size: int,
    rng: np.random.Generator,
) -> dict[str, Any]:
    """Fit StandardScaler + PCA/KPCA for embedding and message change vectors."""
    full_e = np.concatenate(n_e_c_raw_2648, axis=0)
    full_m = np.concatenate(n_m_c_raw_2648, axis=0)
    reduced_dimension = 5

    def _fit_pair(full: np.ndarray) -> tuple[StandardScaler, PCA, KernelPCA]:
        n_sample = min(kpca_sample_size, full.shape[0])
        indices = rng.choice(full.shape[0], size=n_sample, replace=False)
        scaling = StandardScaler()
        scaling.fit(full)
        pca = PCA(n_components=reduced_dimension)
        kpca = KernelPCA(n_components=reduced_dimension + 5, kernel="rbf")
        scaled_sample = scaling.transform(full[indices, :])
        pca.fit(scaled_sample)
        kpca.fit(scaled_sample)
        return scaling, pca, kpca

    e_scaling, e_pca, e_kpca = _fit_pair(full_e)
    m_scaling, m_pca, m_kpca = _fit_pair(full_m)
    return {
        "e_scaling": e_scaling,
        "e_pca": e_pca,
        "e_kpca": e_kpca,
        "m_scaling": m_scaling,
        "m_pca": m_pca,
        "m_kpca": m_kpca,
        "full_e_shape": list(full_e.shape),
        "full_m_shape": list(full_m.shape),
    }


def project_instances(X: list[list[Any]], proj: dict[str, Any]) -> list[list[float]]:
    """Append summed PCA/KPCA features; return flat float lists (length 71)."""
    out: list[list[float]] = []
    for instance in X:
        scalars = [float(v) for v in instance[:11]]
        emb = np.asarray(instance[-4], dtype=np.float64)
        emb_rev = np.asarray(instance[-3], dtype=np.float64)
        msg = np.asarray(instance[-2], dtype=np.float64)
        msg_rev = np.asarray(instance[-1], dtype=np.float64)

        e_s = proj["e_scaling"]
        e_pca = proj["e_pca"]
        e_kpca = proj["e_kpca"]
        m_s = proj["m_scaling"]
        m_pca = proj["m_pca"]
        m_kpca = proj["m_kpca"]

        cur_pca = e_pca.transform(e_s.transform(emb)).sum(axis=0)
        cur_kpca = e_kpca.transform(e_s.transform(emb)).sum(axis=0)
        rev_pca = e_pca.transform(e_s.transform(emb_rev)).sum(axis=0)
        rev_kpca = e_kpca.transform(e_s.transform(emb_rev)).sum(axis=0)
        m_cur_pca = m_pca.transform(m_s.transform(msg)).sum(axis=0)
        m_cur_kpca = m_kpca.transform(m_s.transform(msg)).sum(axis=0)
        m_rev_pca = m_pca.transform(m_s.transform(msg_rev)).sum(axis=0)
        m_rev_kpca = m_kpca.transform(m_s.transform(msg_rev)).sum(axis=0)

        flat = list(scalars)
        flat.extend(cur_pca.tolist())  # 11:16
        flat.extend(cur_kpca.tolist())  # 16:26
        flat.extend(rev_pca.tolist())  # 26:31
        flat.extend(rev_kpca.tolist())  # 31:41
        flat.extend(m_cur_pca.tolist())  # 41:46
        flat.extend(m_cur_kpca.tolist())  # 46:56
        flat.extend(m_rev_pca.tolist())  # 56:61
        flat.extend(m_rev_kpca.tolist())  # 61:71
        out.append(flat)
    return out


def augment_forward_reverse(X: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Build augmented matrix matching notebook cell 19 layout (41 cols)."""
    X_aug = []
    y_aug = []
    for row, label in zip(X, y):
        forward = []
        forward.extend(row[0:11])
        forward.extend(row[11:16])
        forward.extend(row[16:26])
        forward.extend(row[41:46])
        forward.extend(row[46:56])
        forward_arr = np.asarray(forward, dtype=np.float64)

        rev = np.zeros_like(forward_arr)
        rev[0] = -1.0 * row[0]
        rev[1] = row[1]
        rev[2] = -1.0 * row[2]
        rev[3] = row[4]
        rev[4] = row[3]
        rev[5] = -1.0 * row[5]
        rev[6] = -1.0 * row[6]
        # notebook: rev_X[7] = 1/X[7]
        denom = row[7]
        rev[7] = 1.0 / denom if abs(denom) > 1e-12 else 0.0
        rev[8] = row[8]
        rev[9] = row[10]
        rev[10] = row[9]
        rev[11:16] = row[26:31]
        rev[16:26] = row[31:41]
        rev[26:31] = row[56:61]
        rev[31:41] = row[61:71]

        X_aug.append(forward_arr)
        X_aug.append(rev)
        y_aug.append(label)
        y_aug.append(-1.0 * label)
    return np.asarray(X_aug, dtype=np.float64), np.asarray(y_aug, dtype=np.float64)


def combo_indices(combo: tuple[str, ...]) -> list[int]:
    idxs: list[int] = []
    for label in combo:
        mapped = FEATURE_TO_INDEX[label]
        if isinstance(mapped, list):
            idxs.extend(mapped)
        else:
            idxs.append(mapped)
    return idxs


def evaluate_split(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    """Compute rF/rR/rF+R/rF-R and RMSE splits for interleaved forward/reverse."""
    forward_y = y_true[0::2]
    reverse_y = y_true[1::2]
    forward_p = y_pred[0::2]
    reverse_p = y_pred[1::2]
    return {
        "rF": float(pearsonr(forward_y, forward_p)[0]),
        "rR": float(pearsonr(reverse_y, reverse_p)[0]),
        "rF+R": float(pearsonr(y_true, y_pred)[0]),
        "rF-R": float(pearsonr(forward_p, reverse_p)[0]),
        "rmsF": float(math.sqrt(((forward_y - forward_p) ** 2).mean())),
        "rmsR": float(math.sqrt(((reverse_y - reverse_p) ** 2).mean())),
        "rmsF+R": float(math.sqrt(((y_true - y_pred) ** 2).mean())),
    }


def round2(value: float) -> float:
    return float(f"{value:.2f}")


def mean_metrics(runs: list[dict[str, float]]) -> dict[str, float]:
    keys = runs[0].keys()
    return {k: float(np.mean([r[k] for r in runs])) for k in keys}


def train_eval_config(
    config_name: str,
    rf_kwargs: dict[str, Any],
    datasets_aug: dict[str, tuple[np.ndarray, np.ndarray]],
    n_runs: int,
    train_only_full_ah: bool,
    n_jobs: int,
) -> dict[str, Any]:
    train_X, train_y = datasets_aug["S_2648"]
    combos = [FULL_AH] if train_only_full_ah else INCREMENTAL
    per_run: list[dict[str, Any]] = []
    t0 = time.time()
    for run_i in range(n_runs):
        run_record: dict[str, Any] = {"run_index": run_i}
        for combo in combos:
            idxs = combo_indices(combo)
            key = "+".join(combo)
            # Do not pin random_state so the 10 runs vary like the notebook loop.
            model = RandomForestRegressor(n_jobs=n_jobs, **rf_kwargs)
            model.fit(train_X[:, idxs], train_y)
            for ds_name, (X_aug, y_aug) in datasets_aug.items():
                preds = model.predict(X_aug[:, idxs])
                metrics = evaluate_split(y_aug, preds)
                run_record[f"{ds_name}::{key}"] = metrics
        per_run.append(run_record)
        print(
            f"  [{config_name}] run {run_i + 1}/{n_runs} done "
            f"({time.time() - t0:.1f}s elapsed)",
            flush=True,
        )

    # Aggregate means for full A–H on test sets
    summary: dict[str, Any] = {
        "config_name": config_name,
        "feature_b_mode": None,  # filled by caller
        "rf_kwargs": rf_kwargs,
        "n_runs": n_runs,
        "elapsed_sec": time.time() - t0,
        "full_ah_means": {},
        "full_ah_vs_manuscript": {},
    }
    full_key = "+".join(FULL_AH)
    for ds_name in ["S_669", "Ssym", "S_921"]:
        run_metrics = [r[f"{ds_name}::{full_key}"] for r in per_run]
        means = mean_metrics(run_metrics)
        summary["full_ah_means"][ds_name] = means
        paper = MANUSCRIPT_ROUNDED[ds_name]
        comparison = {}
        for metric, paper_val in paper.items():
            ours = means[metric]
            comparison[metric] = {
                "ours_mean": ours,
                "ours_rounded": round2(ours),
                "paper_rounded": paper_val,
                "abs_diff_rounded": abs(round2(ours) - paper_val),
                "match_rounded": round2(ours) == paper_val,
            }
        summary["full_ah_vs_manuscript"][ds_name] = comparison
    summary["per_run"] = per_run
    return summary


def write_comparison_tsv(path: Path, summaries: list[dict[str, Any]]) -> None:
    rows = []
    for summary in summaries:
        cfg = summary["config_name"]
        for ds_name, comparison in summary["full_ah_vs_manuscript"].items():
            for metric, info in comparison.items():
                rows.append(
                    {
                        "config": cfg,
                        "dataset": ds_name,
                        "metric": metric,
                        "ours_mean": f"{info['ours_mean']:.6f}",
                        "ours_rounded": f"{info['ours_rounded']:.2f}",
                        "paper_rounded": f"{info['paper_rounded']:.2f}",
                        "abs_diff_rounded": f"{info['abs_diff_rounded']:.2f}",
                        "match_rounded": str(info["match_rounded"]),
                        "feature_source": f"saved_historical_V3_engineered+KPCA_E|B={summary.get('feature_b_mode', '?')}",
                    }
                )
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "config",
                "dataset",
                "metric",
                "ours_mean",
                "ours_rounded",
                "paper_rounded",
                "abs_diff_rounded",
                "match_rounded",
                "feature_source",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--digging-dir", type=Path, default=DEFAULT_DIGGING)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--n-runs", type=int, default=10)
    parser.add_argument("--kpca-sample-size", type=int, default=10000)
    parser.add_argument("--kpca-seed", type=int, default=0)
    parser.add_argument(
        "--configs",
        nargs="+",
        default=["manuscript_literal", "notebook_table1"],
        choices=list(RF_CONFIGS.keys()),
    )
    parser.add_argument(
        "--full-ah-only",
        action="store_true",
        help="Train only A+B+C+D+E+F+G+H (skip incremental combos).",
    )
    parser.add_argument("--n-jobs", type=int, default=-1)
    parser.add_argument(
        "--feature-b-mode",
        choices=["historical_weighted", "manuscript_unweighted"],
        default="historical_weighted",
        help=(
            "historical_weighted: saved V3 V2_backward_weighted_neighbor_entropy_changes "
            "(Table1/Fig6 notebooks). manuscript_unweighted: recompute unweighted "
            "Σ(H_WT-H_MT) from w_n/m_n_log_prob per manuscript Eq.1."
        ),
    )
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    digging = args.digging_dir

    print(f"Feature B mode: {args.feature_b_mode}", flush=True)
    print("Loading saved historical V3 pickles...", flush=True)
    names = ["S_2648", "S_921", "S_669", "Ssym"]
    pickles = {
        "S_2648": digging / "S_2648_pmppn_info_dict_V3.pickle",
        "S_921": digging / "S_921_pmppn_info_dict_V3.pickle",
        "S_669": digging / "S_669_pmppn_info_dict_V3.pickle",
        "Ssym": digging / "Ssym_pmppn_info_dict_V3.pickle",
    }
    raw: dict[str, Any] = {}
    coverage = {}
    for name in names:
        two_level = load_v3(pickles[name])
        X, y, n_e, n_m, stats = build_raw_instances(two_level, feature_b_mode=args.feature_b_mode)
        raw[name] = {"X": X, "y": y, "n_e": n_e, "n_m": n_m}
        coverage[name] = stats
        print(f"  {name}: kept={stats['kept']} skipped={stats['skipped_incomplete']}", flush=True)

    print(
        f"Fitting PCA/KPCA on S_2648 raw vectors (seed={args.kpca_seed}, "
        f"sample={args.kpca_sample_size})...",
        flush=True,
    )
    rng = np.random.default_rng(args.kpca_seed)
    proj = fit_projection(raw["S_2648"]["n_e"], raw["S_2648"]["n_m"], args.kpca_sample_size, rng)
    print(
        f"  embedding neighbors stacked shape={proj['full_e_shape']}; "
        f"message stacked shape={proj['full_m_shape']}",
        flush=True,
    )

    print("Projecting instances and building forward+reverse matrices...", flush=True)
    datasets_aug: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    matrix_shapes = {}
    for name in names:
        projected = project_instances(raw[name]["X"], proj)
        X_mat = np.asarray(projected, dtype=np.float64)
        y_mat = np.asarray(raw[name]["y"], dtype=np.float64)
        # Notebook (VGRAPHS cell ~398-400): flip S_669 experimental DDG signs so
        # correlations are coherent with S_2648 / Ssym / S_921 convention.
        if name == "S_669":
            y_mat = y_mat * (-1.0)
            print("  Applied S_669 DDG sign flip (y *= -1) per notebook protocol", flush=True)
        X_aug, y_aug = augment_forward_reverse(X_mat, y_mat)
        datasets_aug[name] = (X_aug, y_aug)
        matrix_shapes[name] = {
            "n_forward": int(X_mat.shape[0]),
            "n_aug": int(X_aug.shape[0]),
            "n_aug_features": int(X_aug.shape[1]),
            "full_ah_n_features": len(combo_indices(FULL_AH)),
        }
        print(
            f"  {name}: forward={X_mat.shape[0]} aug={X_aug.shape} "
            f"full_AH_dims={matrix_shapes[name]['full_ah_n_features']}",
            flush=True,
        )

    summaries = []
    for config_name in args.configs:
        print(f"Training/evaluating config={config_name} n_runs={args.n_runs}...", flush=True)
        summary = train_eval_config(
            config_name=config_name,
            rf_kwargs=dict(RF_CONFIGS[config_name]),
            datasets_aug=datasets_aug,
            n_runs=args.n_runs,
            train_only_full_ah=args.full_ah_only,
            n_jobs=args.n_jobs,
        )
        summary["feature_b_mode"] = args.feature_b_mode
        summaries.append(summary)
        for ds_name, means in summary["full_ah_means"].items():
            paper = MANUSCRIPT_ROUNDED[ds_name]
            print(
                f"  {ds_name}: rF+R ours={means['rF+R']:.4f} (round {round2(means['rF+R']):.2f}) "
                f"paper={paper['rF+R']:.2f}; "
                f"RMSE ours={means['rmsF+R']:.4f} (round {round2(means['rmsF+R']):.2f}) "
                f"paper={paper['rmsF+R']:.2f}; "
                f"rF-R ours={means['rF-R']:.4f} (round {round2(means['rF-R']):.2f}) "
                f"paper={paper['rF-R']:.2f}",
                flush=True,
            )

    meta = {
        "feature_source": "saved_historical_V3_engineered+KPCA_E_from_same_pickles",
        "feature_b_mode": args.feature_b_mode,
        "feature_source_paths": {k: str(v) for k, v in pickles.items()},
        "kpca_seed": args.kpca_seed,
        "kpca_sample_size": args.kpca_sample_size,
        "coverage": coverage,
        "matrix_shapes": matrix_shapes,
        "feature_to_index": FEATURE_TO_INDEX,
        "note": (
            "Feature E is re-fit KernelPCA on S_2648 message-change vectors "
            "(notebook used unseeded np.random.choice); KPCA values are therefore "
            "not bit-identical to the historical Colab run, but protocol-aligned."
        ),
    }

    comparison_path = args.output_dir / "ours_vs_paper_table1.tsv"
    write_comparison_tsv(comparison_path, summaries)

    # JSON-serializable summaries (drop huge per-run detail optionally keep)
    serializable = []
    for summary in summaries:
        slim = {
            "config_name": summary["config_name"],
            "rf_kwargs": summary["rf_kwargs"],
            "n_runs": summary["n_runs"],
            "elapsed_sec": summary["elapsed_sec"],
            "full_ah_means": summary["full_ah_means"],
            "full_ah_vs_manuscript": summary["full_ah_vs_manuscript"],
        }
        serializable.append(slim)

    out_json = {
        "meta": meta,
        "summaries": serializable,
    }
    json_path = args.output_dir / "rf_train_eval_summary.json"
    with json_path.open("w") as handle:
        json.dump(out_json, handle, indent=2, sort_keys=True)

    # Also dump per-run metrics for primary configs (compact)
    per_run_path = args.output_dir / "rf_per_run_metrics.json"
    with per_run_path.open("w") as handle:
        json.dump(
            {
                s["config_name"]: s["per_run"]
                for s in summaries
            },
            handle,
            indent=2,
        )

    print(f"Wrote {comparison_path}", flush=True)
    print(f"Wrote {json_path}", flush=True)
    print(f"Wrote {per_run_path}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
