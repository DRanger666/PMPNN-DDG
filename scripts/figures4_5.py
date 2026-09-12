#!/usr/bin/env python3
"""Regenerate S_2648 training-set feature analyses for manuscript Figures 4–5.

Figure 4: A/B/C/D/E(+E-1..E-5) correlation heatmap (label + features).
Figure 5: Full A–H (+E components) correlation heatmap.

Figure 3 (Norm-Ratio vs Change-Norm for C/D) is NOT regenerated here: compact
features store a single C/D encoding. Dual-encoding comparison needs a dedicated
recompute path (documented as blocked).

Uses the same KPCA Feature-E construction as train_eval_rf_from_v3_features.py.
Feature E columns on the unaugmented 71-col matrix are 46:51 (message KPCA),
not FEATURE_TO_INDEX["E"] which applies only after forward/reverse augmentation.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

WORKSPACE = Path(__file__).resolve().parents[1]

# Manuscript-stated rounded targets (from stage-1 notebook evidence notes)
MANUSCRIPT_FIG45_CLAIMS = {
    "C_vs_ddg": -0.15,
    "A_vs_B": 0.52,  # notebook often 0.51
    "E1_vs_D": 0.49,
    "E2_vs_D_max": 0.17,
    "E4_vs_ddg": 0.21,
    "E3_vs_A": 0.55,
    "E3_vs_B": 0.40,
    "E3_vs_C": 0.55,  # magnitude; sign may be negative
    "E3_vs_ddg": 0.26,
    "E2_vs_E4": 0.20,
    "F_vs_A": 0.32,
    "G_vs_A": 0.15,
    "H_vs_E1_mag": 0.39,
}




def build_from_pickle(pickle_path: Path, kpca_seed: int = 0):
    import pickle
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "rfmod", WORKSPACE / "scripts/train_eval_rf_from_v3_features.py"
    )
    rfmod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rfmod)

    data = pickle.load(pickle_path.open("rb"))
    X, y, n_e, n_m, stats = rfmod.build_raw_instances(
        data, feature_b_mode="historical_weighted"
    )
    rng = np.random.default_rng(kpca_seed)
    proj = rfmod.fit_projection(n_e, n_m, kpca_sample_size=10000, rng=rng)
    Xf = np.asarray(rfmod.project_instances(X, proj), dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    return Xf, y, stats, rfmod.FEATURE_TO_INDEX



def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--features-pickle",
        type=Path,
        default=WORKSPACE
        / "data/features/S2648_features.pickle",
    )
    ap.add_argument(
        "--output-dir",
        type=Path,
        default=WORKSPACE
        / "results/figures",
    )
    ap.add_argument("--kpca-seed", type=int, default=0)
    args = ap.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    Xf, y, stats, idx = build_from_pickle(args.features_pickle, args.kpca_seed)
    # forward-only for correlations (notebook uses aug[0::2] == forward)
    # build_raw_instances returns forward mutations only; augmentation is later in RF.
    #
    # IMPORTANT: FEATURE_TO_INDEX["E"] = [31..35] is valid only on the *augmented*
    # 41-col matrix (message-KPCA block). project_instances returns a 71-col matrix
    # where message-KPCA is columns 46:56 — Feature E is the first 5 of those.
    # Using [31..35] here previously selected embedding-rev KPCA and fabricated
    # Fig 4–5 E mismatches (e.g. E1 vs D ≈ 0.91 instead of ≈ 0.49).
    from pmpnn_ddg.features.rf_feature_matrix_packing import (
        FEATURE_E_COLS_ON_DUAL_DIRECTION_ROW,
    )
    UNAUGMENTED_E_COLS = list(FEATURE_E_COLS_ON_DUAL_DIRECTION_ROW)
    print("matrix", Xf.shape, "stats", stats)
    print(
        "Feature E cols on dual-direction (71) row = message-change KPCA[:5]:",
        UNAUGMENTED_E_COLS,
    )

    def col(name):
        i = idx[name]
        if isinstance(i, list):
            return None
        return Xf[:, i]

    df4 = pd.DataFrame(
        {
            "DDG": y,
            "A": col("A"),
            "B": col("B"),
            "C": col("C"),
            "D": col("D"),
            "E-1": Xf[:, UNAUGMENTED_E_COLS[0]],
            "E-2": Xf[:, UNAUGMENTED_E_COLS[1]],
            "E-3": Xf[:, UNAUGMENTED_E_COLS[2]],
            "E-4": Xf[:, UNAUGMENTED_E_COLS[3]],
            "E-5": Xf[:, UNAUGMENTED_E_COLS[4]],
        }
    )
    df5 = df4.copy()
    df5["F"] = col("F")
    df5["G"] = col("G")
    df5["H"] = col("H")

    corr4 = df4.corr()
    corr5 = df5.corr()
    corr4.to_csv(args.output_dir / "figure4_corr_matrix.csv")
    corr5.to_csv(args.output_dir / "figure5_corr_matrix.csv")

    def save_heat(corr, path, title):
        fig, ax = plt.subplots(figsize=(8, 6), dpi=150)
        im = ax.imshow(corr.values, cmap="BrBG", vmin=-1.0, vmax=1.0)
        ax.set_xticks(range(len(corr.columns)))
        ax.set_yticks(range(len(corr.columns)))
        ax.set_xticklabels(corr.columns, rotation=90)
        ax.set_yticklabels(corr.columns)
        for i in range(corr.shape[0]):
            for j in range(corr.shape[1]):
                ax.plot([j-0.5,j+0.5,j+0.5,j-0.5,j-0.5],[i-0.5,i-0.5,i+0.5,i+0.5,i-0.5], color='black', lw=0.5)
        fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        ax.set_title(title)
        fig.tight_layout()
        fig.savefig(path)
        plt.close(fig)

    save_heat(corr4, args.output_dir / "figure4_feature_feature_correlation.png", "Figure 4 style (A–E)")
    save_heat(corr5, args.output_dir / "figure5_feature_feature_correlation.png", "Figure 5 style (A–H)")

    # Compare key manuscript claims (magnitudes where noted)
    claims = {
        "C_vs_ddg": float(corr5.loc["C", "DDG"]),
        "A_vs_B": float(corr5.loc["A", "B"]),
        "E1_vs_D": float(corr5.loc["E-1", "D"]),
        "E2_vs_D": float(corr5.loc["E-2", "D"]),
        "E4_vs_ddg": float(corr5.loc["E-4", "DDG"]),
        "E3_vs_A": float(corr5.loc["E-3", "A"]),
        "E3_vs_B": float(corr5.loc["E-3", "B"]),
        "E3_vs_C": float(corr5.loc["E-3", "C"]),
        "E3_vs_ddg": float(corr5.loc["E-3", "DDG"]),
        "E2_vs_E4": float(corr5.loc["E-2", "E-4"]),
        "F_vs_A": float(corr5.loc["F", "A"]),
        "G_vs_A": float(corr5.loc["G", "A"]),
        "H_vs_E1": float(corr5.loc["H", "E-1"]),
    }
    rows = []
    for k, paper in [
        ("C_vs_ddg", -0.15),
        ("A_vs_B", 0.52),
        ("E1_vs_D", 0.49),
        ("E2_vs_D", 0.17),
        ("E4_vs_ddg", 0.21),
        ("E3_vs_A", 0.55),
        ("E3_vs_B", 0.40),
        ("E3_vs_C", 0.55),
        ("E3_vs_ddg", 0.26),
        ("E2_vs_E4", 0.20),
        ("F_vs_A", 0.32),
        ("G_vs_A", 0.15),
        ("H_vs_E1", 0.39),
    ]:
        ours = claims[k] if k != "H_vs_E1" else abs(claims["H_vs_E1"])
        if k == "E3_vs_C":
            ours_cmp = abs(claims[k])
        else:
            ours_cmp = ours if k != "H_vs_E1" else ours
            if k in ("E3_vs_C",):
                pass
        if k == "E3_vs_C":
            ours_cmp = abs(claims[k])
            ours_disp = claims[k]
        elif k == "H_vs_E1":
            ours_cmp = abs(claims["H_vs_E1"])
            ours_disp = claims["H_vs_E1"]
        else:
            ours_cmp = claims[k]
            ours_disp = claims[k]
        d = abs(round(ours_cmp, 2) - round(paper, 2))
        verdict = "match" if d < 1e-9 else ("near" if d <= 0.02 else "mismatch")
        rows.append(
            {
                "claim": k,
                "manuscript": paper,
                "ours": ours_disp,
                "ours_rounded_2dp": round(ours_cmp, 2),
                "abs_diff_rounded": d,
                "verdict": verdict,
            }
        )

    pd.DataFrame(rows).to_csv(args.output_dir / "figure45_claim_comparison.tsv", sep="\t", index=False)
    summary = {
        "n_instances": int(len(y)),
        "stats": stats,
        "kpca_seed": args.kpca_seed,
        "features_pickle": str(args.features_pickle),
        "figure3_status": "blocked_need_dual_C_D_encodings",
        "n_match": sum(1 for r in rows if r["verdict"] == "match"),
        "n_near": sum(1 for r in rows if r["verdict"] == "near"),
        "n_mismatch": sum(1 for r in rows if r["verdict"] == "mismatch"),
        "claims": rows,
    }
    (args.output_dir / "figure45_summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps({k: summary[k] for k in ["n_instances", "n_match", "n_near", "n_mismatch", "figure3_status"]}, indent=2))


if __name__ == "__main__":
    main()
