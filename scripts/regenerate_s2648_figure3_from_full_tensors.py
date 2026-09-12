#!/usr/bin/env python3
"""Figure 3: Norm-Ratio vs Change-Norm for message (C) and neighbor-embedding (D) families.

Source of truth: full S2648 extraction tensors (not compact-only features).

For each mutation entry (top-15 neighbors):
  message NR  = Σ_j ‖M_j^WT‖ / ‖M_j^MT‖     (manuscript Feature C encoding)
  message CN  = Σ_j ‖M_j^WT − M_j^MT‖
  neighbor-embedding NR = Σ_j ‖E_j^WT‖ / ‖E_j^MT‖
  neighbor-embedding CN = Σ_j ‖E_j^WT − E_j^MT‖  (manuscript Feature D encoding)

Notebook VGRAPHS cells 15–16 printed |PCC| pairs vs experimental ΔΔG
(assignment confirmed on partial full shards: neighbor-embedding NR/CN ≈ 0.27/0.29 → 0.26 0.31;
message NR/CN ≈ 0.16/0.045 → 0.15 0.03). Manuscript Feature C = message NR (|r|≈0.15);
Feature D = neighbor-embedding CN.
"""
from __future__ import annotations

import argparse
import json
import pickle
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TENSORS = ROOT / "reproduction_inputs/pmpnn_ddg_extraction_tensors_2026-09-12/S2648_extraction_tensors.pickle"
DEFAULT_OUT = ROOT / "reproduction_runs/2026-09-12/s2648_train_feature_figures"


def _norm_ratio_sum(wt: np.ndarray, mt: np.ndarray, eps: float = 1e-8) -> float:
    wt = np.asarray(wt, dtype=np.float64)
    mt = np.asarray(mt, dtype=np.float64)
    total = 0.0
    for a, b in zip(wt, mt):
        total += float(np.linalg.norm(a) + eps) / float(np.linalg.norm(b) + eps)
    return total


def _change_norm_sum(wt: np.ndarray, mt: np.ndarray) -> float:
    wt = np.asarray(wt, dtype=np.float64)
    mt = np.asarray(mt, dtype=np.float64)
    total = 0.0
    for a, b in zip(wt, mt):
        total += float(np.linalg.norm(a - b))
    return total


def _iter_entries(obj):
    """Yield (protein_key, entry_dict) from pickle layouts."""
    if isinstance(obj, dict):
        for pk, ents in obj.items():
            if isinstance(ents, list):
                for e in ents:
                    if isinstance(e, dict):
                        yield pk, e
            elif isinstance(ents, dict) and "entries" in ents:
                for e in ents["entries"]:
                    if isinstance(e, dict):
                        yield pk, e
    elif isinstance(obj, list):
        for e in obj:
            if isinstance(e, dict):
                yield e.get("protein_key", "?"), e


def encodings_from_entry(e: dict) -> dict[str, float] | None:
    msg_wt = e.get("center_to_neighbor_messages_wt")
    msg_mt = e.get("center_to_neighbor_messages_mt")
    emb_wt = e.get("neighbor_embeddings_wt")
    emb_mt = e.get("neighbor_embeddings_mt")
    if msg_wt is None or msg_mt is None or emb_wt is None or emb_mt is None:
        return None
    ddg = e.get("ddg", e.get("DDG", e.get("experimental_ddg")))
    if ddg is None:
        return None
    return {
        "ddg": float(ddg),
        "message_NR": _norm_ratio_sum(msg_wt, msg_mt),
        "message_CN": _change_norm_sum(msg_wt, msg_mt),
        "neighbor_embedding_NR": _norm_ratio_sum(emb_wt, emb_mt),
        "neighbor_embedding_CN": _change_norm_sum(emb_wt, emb_mt),
    }


def pearson(x, y) -> float:
    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    if x.size < 3:
        return float("nan")
    return float(np.corrcoef(x, y)[0, 1])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tensors", type=Path, default=DEFAULT_TENSORS)
    ap.add_argument("--shards-dir", type=Path, default=None,
                    help="Optional: load shards/*.out.pkl if promoted pickle missing")
    ap.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    missing = 0
    if args.tensors.exists():
        obj = pickle.load(args.tensors.open("rb"))
        for _, e in _iter_entries(obj):
            enc = encodings_from_entry(e)
            if enc is None:
                missing += 1
                continue
            rows.append(enc)
        source = str(args.tensors)
    elif args.shards_dir and args.shards_dir.exists():
        for p in sorted(args.shards_dir.glob("*.out.pkl")):
            obj = pickle.load(p.open("rb"))
            ents = obj.get("entries", []) if isinstance(obj, dict) else obj
            for e in ents:
                if not isinstance(e, dict):
                    continue
                enc = encodings_from_entry(e)
                if enc is None:
                    missing += 1
                    continue
                rows.append(enc)
        source = str(args.shards_dir)
    else:
        raise SystemExit(f"missing tensors {args.tensors} and no shards-dir")

    ddg = [r["ddg"] for r in rows]
    claims = {
        "message_NR_vs_ddg": pearson([r["message_NR"] for r in rows], ddg),
        "message_CN_vs_ddg": pearson([r["message_CN"] for r in rows], ddg),
        "neighbor_embedding_NR_vs_ddg": pearson([r["neighbor_embedding_NR"] for r in rows], ddg),
        "neighbor_embedding_CN_vs_ddg": pearson([r["neighbor_embedding_CN"] for r in rows], ddg),
    }
    # Notebook printed absolute PCCs (0.26 0.31) and (0.15 0.03)
    notebook = {
        "neighbor_embedding_pair_abs": (0.26, 0.31),  # cell 15
        "message_pair_abs": (0.15, 0.03),  # cell 16
    }
    abs_msg = (abs(claims["message_NR_vs_ddg"]), abs(claims["message_CN_vs_ddg"]))
    abs_emb = (abs(claims["neighbor_embedding_NR_vs_ddg"]), abs(claims["neighbor_embedding_CN_vs_ddg"]))

    def verdict(ours_abs, target, tol_near=0.02):
        d = abs(round(ours_abs, 2) - target)
        if d == 0:
            return "match"
        if d <= tol_near:
            return "near"
        return "mismatch"

    # Best assignment of printed pairs to (NR, CN) order
    summary = {
        "n_instances": len(rows),
        "n_missing_keys": missing,
        "source": source,
        "pearson_signed": claims,
        "pearson_abs": {
            "message_NR": abs_msg[0],
            "message_CN": abs_msg[1],
            "neighbor_embedding_NR": abs_emb[0],
            "neighbor_embedding_CN": abs_emb[1],
        },
        "notebook_printed_abs": notebook,
        "vs_notebook": {
            "neighbor_embedding_NR": verdict(abs_emb[0], 0.26),
            "neighbor_embedding_CN": verdict(abs_emb[1], 0.31),
            "message_NR": verdict(abs_msg[0], 0.15),
            "message_CN": verdict(abs_msg[1], 0.03),
        },
    }

    # Bar figure: two panels (messages | neighbor embeddings)
    fig, axes = plt.subplots(1, 2, figsize=(8, 4), dpi=150)
    axes[0].bar(["NR", "CN"], [abs_emb[0], abs_emb[1]], color=["#4C72B0", "#55A868"])
    axes[0].set_ylim(0, 0.4)
    axes[0].set_title("Neighbor embeddings (Feature D family)\n|PCC| vs ΔΔG")
    axes[0].axhline(0.26, ls="--", lw=0.8, color="gray")
    axes[0].axhline(0.31, ls=":", lw=0.8, color="gray")
    axes[1].bar(["NR", "CN"], [abs_msg[0], abs_msg[1]], color=["#4C72B0", "#55A868"])
    axes[1].set_ylim(0, 0.4)
    axes[1].set_title("Messages (Feature C family)\n|PCC| vs ΔΔG")
    axes[1].axhline(0.15, ls="--", lw=0.8, color="gray")
    axes[1].axhline(0.03, ls=":", lw=0.8, color="gray")
    fig.tight_layout()
    fig_path = args.out_dir / "figure3_norm_ratio_vs_change_norm.png"
    fig.savefig(fig_path)
    plt.close(fig)

    (args.out_dir / "figure3_summary.json").write_text(json.dumps(summary, indent=2))
    # TSV
    lines = ["encoding\tpearson_signed\tpearson_abs\tnotebook_target_abs\tverdict"]
    mapping = [
        ("neighbor_embedding_NR", claims["neighbor_embedding_NR_vs_ddg"], abs_emb[0], 0.26),
        ("neighbor_embedding_CN", claims["neighbor_embedding_CN_vs_ddg"], abs_emb[1], 0.31),
        ("message_NR", claims["message_NR_vs_ddg"], abs_msg[0], 0.15),
        ("message_CN", claims["message_CN_vs_ddg"], abs_msg[1], 0.03),
    ]
    for name, signed, ab, tgt in mapping:
        lines.append(f"{name}\t{signed:.6f}\t{ab:.6f}\t{tgt}\t{verdict(ab, tgt)}")
    (args.out_dir / "figure3_claim_comparison.tsv").write_text("\n".join(lines) + "\n")
    print(json.dumps(summary, indent=2))
    print("wrote", fig_path)


if __name__ == "__main__":
    main()
