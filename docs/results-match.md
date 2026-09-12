# Manuscript Results Match

> Path names below may still say `reproduction_runs/` or `reproduction_inputs/`. On this public layout those are `results/` and `data/`.

**Branch:** `reproduce-paper-results`  
**Manuscript:** PMPNN-DDG bioRxiv DOI 10.64898/2026.08.23.746499  
**Purpose:** Formal correspondence between **this branch’s regenerated pipeline**
and the manuscript’s full results layer. Linked from the [top-level README](../README.md).

This is distinct from historical pickle/notebook recovery
(`TABLE1_NUMERICAL_RECOVERY_MILESTONE.md`, `FIGURE6_NUMERICAL_BASIS_VERIFICATION.md`),
which prove that *saved* artifacts match published numbers. Here the claim is
that **code on this branch**, run end-to-end, reproduces those numbers.

## Public reproducibility bar

**tensors → features → RF / figures / tables**, with **every number** from
tensors, features, and derived artifacts published on this GitHub branch (LFS
as needed). Compact pickles are interim/convenience only; full extraction
tensors are required for a finished manuscript-corresponding release.

## Status summary

| ID | Claim | Regenerated-pipeline status | Notes |
| --- | --- | --- | --- |
| Table 1 | S669 / Ssym / S921 independent-test metrics | **5 match / 15 near / 1 mismatch of 21 (notebook_table1, 2dp)** | `rf_exact_reverse_feature_c` (exact reverse C = Eq. 2); mismatch = S921 rmsR 1.47 vs 1.49 |
| Table 2 | S669 PMPNN-DDG row | **near** | Same RF as Table 1 S669 (exact reverse C) |
| Table 3 | Ssym PMPNN-DDG row | **near** | Same RF as Table 1 Ssym (exact reverse C) |
| Figure 6 | Incremental A→H total-PCC on S669/Ssym | **5/8 combos both datasets within 0.02; 13/16 cells** | `rf_exact_reverse_feature_c`; S669 mid-combos with C dip ~0.02 vs Digging series |
| Figures 3–5 | S2648 train-set feature analyses | **milestone** | Fig3 from extraction tensors (message NR match); Figs4–5 5 match / 6 near / 2 mismatch of 13 |
| Figures 1–2 | Pipeline / method schematics | N/A (non-numeric) | |

**Last updated:** 2026-09-12 (exact reverse Feature C = branch default)
**Feature source:** extraction tensors (ProteinMPNN A–E + PSSM F–H) under `reproduction_inputs/pmpnn_ddg_extraction_tensors_2026-09-12/`; RF tables also `*_features.pickle` / `*_proteinmpnn_and_pssm_features.pickle`.
**Protocol:** `train_eval_rf_from_v3_features.py` with extraction-tensor overrides; Feature B `historical_weighted`; Feature C reverse **`exact_sum_inv`** (Eq. 2); KPCA seed 0; S_669 ΔΔG sign flip. Historical notebook `1/Σ` reverse C retired as primary (diagnostic flag only).

**Coverage note:** S_2648 kept 2647/2648; S_669 kept 638/669 (unprocessable gaps audited); Ssym 342/342; S_921 921/921.

## How to re-run verification

1. Feature pickles under `reproduction_inputs/pmpnn_ddg_features_2026-09-12/`.
2. `scripts/train_eval_rf_from_v3_features.py` with overrides for all four datasets, `--n-runs 10`, configs `notebook_table1` (+ optional `manuscript_literal`).
3. Refresh this file from `ours_vs_paper_table1.tsv` + `rf_per_run_metrics.json`.
4. Update the README Results correspondence status line.

## Table 1 — independent-test performance (PMPNN-DDG)

| Dataset | Metric | Manuscript | Regenerated | Verdict |
| --- | --- | ---: | ---: | --- |
| S_669 | rF | 0.48 | 0.4703 (→0.47) | **near** |
| S_669 | rR | 0.48 | 0.4686 (→0.47) | **near** |
| S_669 | rF+R | 0.64 | 0.6367 (→0.64) | **match** |
| S_669 | rF-R | -0.99 | -0.9934 (→-0.99) | **match** |
| S_669 | rmsF | 1.45 | 1.4628 (→1.46) | **near** |
| S_669 | rmsR | 1.45 | 1.4648 (→1.46) | **near** |
| S_669 | rmsF+R | 1.45 | 1.4638 (→1.46) | **near** |
| Ssym | rF | 0.72 | 0.7252 (→0.73) | **near** |
| Ssym | rR | 0.72 | 0.7248 (→0.72) | **match** |
| Ssym | rF+R | 0.81 | 0.8170 (→0.82) | **near** |
| Ssym | rF-R | -0.99 | -0.9950 (→-0.99) | **match** |
| Ssym | rmsF | 1.1 | 1.0916 (→1.09) | **near** |
| Ssym | rmsR | 1.1 | 1.0913 (→1.09) | **near** |
| Ssym | rmsF+R | 1.1 | 1.0915 (→1.09) | **near** |
| S_921 | rF | 0.77 | 0.7628 (→0.76) | **near** |
| S_921 | rR | 0.77 | 0.7641 (→0.76) | **near** |
| S_921 | rF+R | 0.79 | 0.8001 (→0.8) | **near** |
| S_921 | rF-R | -1 | -0.9962 (→-1) | **match** |
| S_921 | rmsF | 1.49 | 1.4765 (→1.48) | **near** |
| S_921 | rmsR | 1.49 | 1.4735 (→1.47) | **mismatch** |
| S_921 | rmsF+R | 1.49 | 1.4750 (→1.48) | **near** |

Primary headlines (rF+R): S_669 **0.64**; Ssym **0.82**; S_921 **0.80**.

Source: `reproduction_runs/2026-09-12/rf_exact_reverse_feature_c/` (extraction tensors; `--feature-c-reverse-mode exact_sum_inv`).
Pre-fix baseline (notebook `1/Σ` reverse C): `reproduction_runs/2026-09-12/rf_from_extraction_tensors/`.


## Table 2 — S669 external comparison (PMPNN-DDG row only)

| Method | Metrics (rounded) | Manuscript | Regenerated | Verdict |
| --- | --- | --- | --- | --- |
| PMPNN-DDG | rF/rR/rF+R/rF-R/rms* | 0.48 / 0.48 / 0.64 / -0.99 / 1.45 | rF=0.47; rR=0.47; rF+R=0.64; rF-R=-0.99; rmsF=1.46; rmsR=1.46; rmsF+R=1.46 | **near** |
| Other methods | — | literature | — | not re-run |


## Table 3 — Ssym external comparison (PMPNN-DDG row only)

| Method | Metrics (rounded) | Manuscript | Regenerated | Verdict |
| --- | --- | --- | --- | --- |
| PMPNN-DDG | rF/rR/rF+R/rF-R/rms* | 0.72 / 0.72 / 0.81 / -0.99 / 1.10 | rF=0.73; rR=0.73; rF+R=0.82; rF-R=-1.00; rmsF=1.08; rmsR=1.09; rmsF+R=1.09 | **near** |
| Other methods | — | literature | — | not re-run |


## Figure 6 — incremental feature contribution

| Combo | S_669 ours | S_669 hist | Δ | Ssym ours | Ssym hist | Δ | Approx |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| A | 0.4865 | 0.4716 | +0.0149 | 0.6607 | 0.6411 | +0.0196 | within 0.02 |
| A-B | 0.5222 | 0.5260 | -0.0038 | 0.7155 | 0.7007 | +0.0148 | within 0.02 |
| A-C | 0.5562 | 0.5772 | -0.0210 | 0.7360 | 0.7164 | +0.0196 | S669 Δ=-0.0210 (edge) |
| A-D | 0.5801 | 0.6011 | -0.0210 | 0.7498 | 0.7426 | +0.0072 | S669 Δ=-0.0210 (edge) |
| A-E | 0.6154 | 0.6374 | -0.0220 | 0.7864 | 0.7869 | -0.0005 | S669 Δ=-0.0220 (edge) |
| A-F | 0.6359 | 0.6438 | -0.0079 | 0.8081 | 0.8027 | +0.0054 | within 0.02 |
| A-G | 0.6362 | 0.6435 | -0.0073 | 0.8129 | 0.8087 | +0.0042 | within 0.02 |
| A-H | 0.6367 | 0.6440 | -0.0073 | 0.8170 | 0.8122 | +0.0048 | within 0.02 |

Hist: Digging incremental series (`FIGURE6_NUMERICAL_BASIS_VERIFICATION.md`). Ours: 10-run mean rF+R with **exact reverse Feature C**. **5/8** combos within 0.02 on both datasets (13/16 cells); mid-combos that include C dip slightly on S669 vs Digging — expected when replacing notebook `1/Σ` reverse C.

## Figures 3–5 — S2648 training analyses

**Milestone (figures that do not need RF).** ProteinMPNN-extracted features A–E and PSSM evolutionary features F–H.
Artifacts: `reproduction_runs/2026-09-12/s2648_train_feature_figures/`.

| Figure | Regenerated artifact | Verdict |
| --- | --- | --- |
| Figure 3 | Norm-Ratio vs Change-Norm for messages (C family) and neighbor embeddings (D family) from `S2648_extraction_tensors.pickle` | **partial** — message NR match (|r|≈0.15); message CN near; neighbor-embedding CN near; neighbor-embedding NR Δ≈0.02 vs notebook 0.26 |
| Figure 4 | Feature–feature correlations (A–E) | **5 match / 6 near / 2 mismatch of 13 at kpca_seed=0**; residuals = KPCA subsample stochasticity ([experiment](FIGURE45_KPCA_SUBSAMPLE_SENSITIVITY.md)) |
| Figure 5 | Feature–feature correlations (A–H) | **same** |

### Figure 3 — NR vs CN (extraction tensors)

| Encoding | abs PCC vs ddg | Notebook target | Verdict |
| --- | ---: | ---: | --- |
| neighbor_embedding_NR | 0.28 | 0.26 | **mismatch** |
| neighbor_embedding_CN | 0.32 | 0.31 | **near** |
| message_NR | 0.15 | 0.15 | **match** |
| message_CN | 0.04 | 0.03 | **near** |

Manuscript Feature C = message Norm-Ratio; Feature D = neighbor-embedding Change-Norm.

### Figure 4–5 claim spot-checks (2dp)

**Interpretation of residual mismatches:** explained by KernelPCA subsample seed (experiment: `FIGURE45_KPCA_SUBSAMPLE_SENSITIVITY.md`). Not a Feature A–H definition bug. seed=0 leaves two |Δ|=0.02 cells; seed=7 matches those cells at 2dp.

### Figure 4–5 claim spot-checks (2dp)

| Claim | Manuscript | Ours (2dp) | Verdict |
| --- | ---: | ---: | --- |
| C_vs_ddg | -0.15 | -0.15 | **match** |
| A_vs_B | 0.52 | 0.52 | **match** |
| E1_vs_D | 0.49 | 0.49 | **match** |
| E2_vs_D | 0.17 | 0.18 | **near** |
| E4_vs_ddg | 0.21 | 0.22 | **near** |
| E3_vs_A | 0.55 | 0.54 | **near** |
| E3_vs_B | 0.4 | 0.39 | **near** |
| E3_vs_C | 0.55 | 0.54 | **near** |
| E3_vs_ddg | 0.26 | 0.24 | **mismatch** |
| E2_vs_E4 | 0.2 | 0.18 | **mismatch** |
| F_vs_A | 0.32 | 0.32 | **match** |
| G_vs_A | 0.15 | 0.15 | **match** |
| H_vs_E1 | 0.39 | 0.38 | **near** |

Source for Figs 4–5: `reproduction_inputs/pmpnn_ddg_features_2026-09-12/S2648_proteinmpnn_and_pssm_features.pickle` (KPCA seed 0; Feature E = message-change KPCA).
Fig 3 source: `S2648_extraction_tensors.pickle`.


## Figures 1–2

Schematics — no numeric verification.

## Integrity caveats that affect counts

Any mutation omitted from regenerated matrices must appear in
`UNPROCESSABLE_MUTATIONS_AND_DATASET_GAPS.md` with justification. Do not treat
silent drops as matches. This RF run uses 2647 train / 638 S_669 eval mutations.

## Related docs

- `FIGURE45_KPCA_SUBSAMPLE_SENSITIVITY.md` — seed sweep showing Fig 4–5 residual |Δ|≈0.02 is KernelPCA subsample noise; suggested manuscript caveat

- `TRAIN_TEST_FIGURE_TABLE_ANCHOR.md` — dataset roles for each table/figure
- `MANUSCRIPT_TO_VARIABLE_NAMING.md` — BioRxiv method language → variable names
- `UNPROCESSABLE_MUTATIONS_AND_DATASET_GAPS.md` — integrity audit
- `REPRODUCTION_BAR_NOT_BYTE_IDENTICAL_V3.md` — manuscript numbers (not V3 bytes) are the bar
- `../README.md` — regenerated Tables 1–3 / Figures 3–6 + branch roles vs `main`
- RF outputs: `reproduction_runs/2026-09-12/rf_from_extraction_tensors/ours_vs_paper_table1.tsv`

### Full-tensor promotion log

- 2026-09-12 19:23 UTC: S2648 full tensors + ProteinMPNN+PSSM features (from extraction tensors) on LFS (`S2648_extraction_tensors.pickle`, `S2648_extraction_tensors.pickle` (includes A–H); 2647/2648 ok; gap 2a01A L141R missing PSSM). Fig3 regenerated from full tensors. S669 full extraction running.
- 2026-09-12 20:04 UTC: S669 present on LFS (S669_extraction_tensors.pickle)
- 2026-09-12 20:27 UTC: S669 full tensors+ProteinMPNN+PSSM features (from extraction tensors) on LFS after 2jieA batch recovery (638 entries; commit 576af46). S921 full mid-run.
- 2026-09-12 20:46 UTC: S921 present on LFS (S921_extraction_tensors.pickle)
- 2026-09-12 20:50 UTC: **ALL full extraction tensors on LFS** — Ssym, S2648 (2647), S669 (638 after 2jieA recover), S921 (921/921). ProteinMPNN+PSSM features pickles on LFS for S2648/S669/S921 (+Ssym). Public bar tensors→features path unblocked for RF/figures.
- 2026-09-12 20:59 UTC: Naming locked: extraction tensors source of truth (ProteinMPNN-extracted A–E + PSSM F–H). RF relaunched from `*_extraction_tensors.pickle`. Figs4–5 from S2648 tensors → 7/4/2 of 13.
- 2026-09-12 21:08 UTC: Figs 3–5 milestone + Tables 1–3/Fig6 from extraction-tensor RF. Table1 6/15/0; Fig6 7/8; Figs4–5 5/6/2.
- 2026-09-12 21:20 UTC: Documented Fig 4–5 KPCA subsample sensitivity experiment (seed 0 vs 1/2/7); residuals not treated as feature bugs.
