# Manuscript Results Match

**Branch:** `reproduce-paper-results`  
**Manuscript:** PMPNN-DDG bioRxiv DOI 10.64898/2026.08.23.746499  
**Purpose:** Formal correspondence between **this branch’s regenerated pipeline**
and the manuscript’s full results layer. Linked from the [top-level README](../README.md).

This is distinct from historical pickle/notebook recovery
(`TABLE1_NUMERICAL_RECOVERY_MILESTONE.md`, `FIGURE6_NUMERICAL_BASIS_VERIFICATION.md`),
which prove that *saved* artifacts match published numbers. Here the claim is
that **code on this branch**, run end-to-end, reproduces those numbers.

## Status summary

| ID | Claim | Regenerated-pipeline status | Notes |
| --- | --- | --- | --- |
| Table 1 | S669 / Ssym / S921 independent-test metrics | **7 match / 14 near / 0 mismatch of 21 (rounded-to-2dp vs BioRxiv)** | `reproduction_runs/2026-09-12/rf_from_promoted_compact_features`, config `notebook_table1`, 10 runs |
| Table 2 | S669 PMPNN-DDG row | **near** | Same RF outputs as Table 1 S669; external rows = literature |
| Table 3 | Ssym PMPNN-DDG row | **near** | Same RF outputs as Table 1 Ssym; external rows = literature |
| Figure 6 | Incremental A→H total-PCC on S669/Ssym | **8/8 combos within 0.02 abs of historical series (not bit-exact; trend retained)** | Incremental combos in same RF run |
| Figures 3–5 | S2648 train-set feature analyses | **Partial** | Figs 4–5 from compact S2648 features (4 match / 9 mismatch of 13 claims); Fig 3 blocked (dual C/D encodings) |
| Figures 1–2 | Pipeline / method schematics | N/A (non-numeric) | |

**Last updated:** 2026-09-12 18:16 UTC  
**Feature pickles:** `reproduction_inputs/pmpnn_ddg_features_2026-09-12/` (all four datasets, Git LFS)  
**Protocol:** `train_eval_rf_from_v3_features.py`; Feature B `historical_weighted`; KPCA seed 0; S_669 ΔΔG sign flip per notebook.

**Coverage note:** S_2648 kept 2647/2648; S_669 kept 638/669 (unprocessable gaps audited); Ssym 342/342; S_921 921/921.

## How to re-run verification

1. Feature pickles under `reproduction_inputs/pmpnn_ddg_features_2026-09-12/`.
2. `scripts/train_eval_rf_from_v3_features.py` with overrides for all four datasets, `--n-runs 10`, configs `notebook_table1` (+ optional `manuscript_literal`).
3. Refresh this file from `ours_vs_paper_table1.tsv` + `rf_per_run_metrics.json`.
4. Update the README Results correspondence status line.

## Table 1 — independent-test performance (PMPNN-DDG)

| Dataset | Metric | Manuscript | Regenerated | Verdict |
| --- | --- | ---: | ---: | --- |
| S_669 | rF | 0.48 | 0.4700 (→0.47) | **near** |
| S_669 | rR | 0.48 | 0.4686 (→0.47) | **near** |
| S_669 | rF+R | 0.64 | 0.6379 (→0.64) | **match** |
| S_669 | rF-R | -0.99 | -0.9938 (→-0.99) | **match** |
| S_669 | rmsF | 1.45 | 1.4612 (→1.46) | **near** |
| S_669 | rmsR | 1.45 | 1.4623 (→1.46) | **near** |
| S_669 | rmsF+R | 1.45 | 1.4617 (→1.46) | **near** |
| Ssym | rF | 0.72 | 0.7226 (→0.72) | **match** |
| Ssym | rR | 0.72 | 0.7269 (→0.73) | **near** |
| Ssym | rF+R | 0.81 | 0.8154 (→0.82) | **near** |
| Ssym | rF-R | -0.99 | -0.9958 (→-1.00) | **near** |
| Ssym | rmsF | 1.10 | 1.0960 (→1.10) | **match** |
| Ssym | rmsR | 1.10 | 1.0916 (→1.09) | **near** |
| Ssym | rmsF+R | 1.10 | 1.0938 (→1.09) | **near** |
| S_921 | rF | 0.77 | 0.7653 (→0.77) | **match** |
| S_921 | rR | 0.77 | 0.7632 (→0.76) | **near** |
| S_921 | rF+R | 0.79 | 0.7926 (→0.79) | **match** |
| S_921 | rF-R | -1.00 | -0.9961 (→-1.00) | **match** |
| S_921 | rmsF | 1.49 | 1.4955 (→1.50) | **near** |
| S_921 | rmsR | 1.49 | 1.4992 (→1.50) | **near** |
| S_921 | rmsF+R | 1.49 | 1.4973 (→1.50) | **near** |

Primary headline metrics (rF+R): S_669 **0.64** match; Ssym **0.82** near (paper 0.81); S_921 **0.79** match.

Historical recovery (saved pickle/notebook, not this regen):
`TABLE1_NUMERICAL_RECOVERY_MILESTONE.md`.

## Table 2 — S669 external comparison (PMPNN-DDG row only)

| Method | Metrics (rounded) | Manuscript | Regenerated | Verdict |
| --- | --- | --- | --- | --- |
| PMPNN-DDG | rF/rR/rF+R/rF-R/rms* | 0.48 / 0.48 / 0.64 / -0.99 / 1.45 | rF=0.47; rR=0.47; rF+R=0.64; rF-R=-0.99; rmsF=1.46; rmsR=1.46; rmsF+R=1.46 | **near** |
| Other methods | — | literature | — | not re-run |

## Table 3 — Ssym external comparison (PMPNN-DDG row only)

| Method | Metrics (rounded) | Manuscript | Regenerated | Verdict |
| --- | --- | --- | --- | --- |
| PMPNN-DDG | rF/rR/rF+R/rF-R/rms* | 0.72 / 0.72 / 0.81 / -0.99 / 1.10 | rF=0.72; rR=0.73; rF+R=0.82; rF-R=-1.00; rmsF=1.10; rmsR=1.09; rmsF+R=1.09 | **near** |
| Other methods | — | literature | — | not re-run |

## Figure 6 — incremental feature contribution

| Combo | S_669 ours | S_669 hist | Δ | Ssym ours | Ssym hist | Δ | Approx |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| A | 0.4534 | 0.4716 | -0.0183 | 0.6446 | 0.6411 | +0.0035 | within 0.02 |
| A-B | 0.5195 | 0.5260 | -0.0065 | 0.7107 | 0.7007 | +0.0100 | within 0.02 |
| A-C | 0.5690 | 0.5772 | -0.0082 | 0.7228 | 0.7164 | +0.0064 | within 0.02 |
| A-D | 0.5886 | 0.6011 | -0.0125 | 0.7433 | 0.7426 | +0.0006 | within 0.02 |
| A-E | 0.6307 | 0.6374 | -0.0067 | 0.7881 | 0.7869 | +0.0012 | within 0.02 |
| A-F | 0.6375 | 0.6438 | -0.0063 | 0.8063 | 0.8027 | +0.0036 | within 0.02 |
| A-G | 0.6379 | 0.6435 | -0.0056 | 0.8107 | 0.8087 | +0.0020 | within 0.02 |
| A-H | 0.6379 | 0.6440 | -0.0061 | 0.8154 | 0.8122 | +0.0031 | within 0.02 |

Hist basis: `FIGURE6_NUMERICAL_BASIS_VERIFICATION.md`.  
Ours: 10-run mean `rF+R` per incremental combo (`notebook_table1`).  
Interpretation: monotonic A→H lift is reproduced; pointwise values are close but not bit-exact vs the historical ten-run pickle (expected under regenerated features).

## Figures 3–5 — S2648 training analyses

Regenerated from promoted compact `S2648_features.pickle` (2647 instances) via
`scripts/regenerate_s2648_train_feature_figures.py` (matplotlib heatmaps; KPCA seed 0).
Artifacts: `reproduction_runs/2026-09-12/s2648_train_feature_figures/`.

| Figure | Regenerated artifact | Verdict |
| --- | --- | --- |
| Figure 3 | Norm-Ratio vs Change-Norm for C/D | **blocked** — compact features store a single C/D encoding; need dual-encoding recompute (see stage-1 notebook evidence) |
| Figure 4 | `figure4_feature_feature_correlation.png` + corr CSV | **partial** — non-E claims match; E* / H↔E1 claims mismatch (KPCA axis orientation / component ordering likely) |
| Figure 5 | `figure5_feature_feature_correlation.png` + corr CSV | **partial** — same claim table as Fig 4 (`figure45_claim_comparison.tsv`: 4 match / 9 mismatch of 13) |

### Figure 4–5 claim spot-checks (2dp)

| Claim | Manuscript | Ours (2dp) | Verdict |
| --- | ---: | ---: | --- |
| C vs ΔΔG | -0.15 | -0.15 | match |
| A vs B | 0.52 | 0.52 | match |
| F vs A | 0.32 | 0.32 | match |
| G vs A | 0.15 | 0.15 | match |
| E1 vs D | 0.49 | 0.91 | mismatch |
| E2 vs D | 0.17 | -0.11 | mismatch |
| E3 vs A/B/C/ΔΔG | 0.55/0.40/0.55/0.26 | 0.12/0.21/0.01/0.07 | mismatch |
| E4 vs ΔΔG | 0.21 | -0.10 | mismatch |
| E2 vs E4 | 0.20 | 0.13 | mismatch |
| H vs E1 | 0.39 | 0.34 (|r|) | mismatch (Δ=0.05) |

**Blockers:** (1) Fig 3 dual C/D encodings not in compact pickle; (2) Feature B wording still open (`MANUSCRIPT_TENSOR_EXTRACTION_FIDELITY.md` Item B) — RF uses `historical_weighted`; (3) E-component sign/order vs manuscript KPCA not locked.

**Full S2648 extraction tensors** still required for Feature B / tensor-fidelity audits, not for Figs 4–5 heatmaps from compact features.

## Figures 1–2

Schematics — no numeric verification.

## Integrity caveats that affect counts

Any mutation omitted from regenerated matrices must appear in
`UNPROCESSABLE_MUTATIONS_AND_DATASET_GAPS.md` with justification. Do not treat
silent drops as matches. This RF run uses 2647 train / 638 S_669 eval mutations.

## Related docs

- `TRAIN_TEST_FIGURE_TABLE_ANCHOR.md` — dataset roles for each table/figure
- `MANUSCRIPT_TO_VARIABLE_NAMING.md` — BioRxiv method language → variable names
- `UNPROCESSABLE_MUTATIONS_AND_DATASET_GAPS.md` — integrity audit
- `../workspace_operations/CURRENT_RECOVERY_BOUNDARY.md` — recovery vs regen boundary
- RF outputs: `reproduction_runs/2026-09-12/rf_from_promoted_compact_features/ours_vs_paper_table1.tsv`
