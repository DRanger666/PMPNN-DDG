# Figures 4–5: KernelPCA subsample sensitivity (not a feature bug)

**Date:** 2026-09-12  
**Branch:** `reproduce-paper-results`  
**Purpose:** Explain the residual Fig 4–5 correlation mismatches after Feature E
was confirmed to be **center→neighbor message-change** KernelPCA (not
neighbor-embedding projections). This note is **repo documentation** of a
reproduction experiment. It is not manuscript narrative about “re-fitting in
2026.”

## Scientific context

Manuscript §3.2.4: Feature E projects center→neighbor message-difference vectors
with RBF KernelPCA trained on **randomly selected** S2648 neighbor-position rows
for tractability. Figures 4–5 quote pairwise PCCs that include E-1…E-5.

Those quoted PCCs therefore inherit **stochastic dependence on the KernelPCA
training subsample** (and component sign). Exact 2-decimal figures can move
slightly across draws even when Features A–D and F–H are fixed.

## What looked like a bug (and was)

An earlier verification applied **augmented-matrix** Feature E column indices to
the **dual-direction (71-col)** matrix, so “E” was neighbor-embedding-change
KPCA. That produced large errors (e.g. E1↔D ≈ 0.91 vs manuscript 0.49). Fixing
the column map (`rf_feature_matrix_packing.py`) restored E1↔D ≈ 0.49.

**That was a reproduction-code bug.** The remaining |Δ|≈0.02 cells are a
different question.

## Residual mismatches under default seed=0

Using `S2648_proteinmpnn_and_pssm_features.pickle` (2647 mutations),
`kpca_sample_size=10000`, message-change KPCA Feature E:

| Claim | Manuscript | seed=0 (2dp) | Verdict |
| --- | ---: | ---: | --- |
| E3 ↔ ΔΔG | 0.26 | 0.24 | mismatch |
| E2 ↔ E4 | 0.20 | 0.18 | mismatch |

Non-E claims (C↔ΔΔG, A↔B, F↔A, G↔A, …) matched at 2dp under the same fit.

## Experiment: vary only the KernelPCA subsample seed

Same feature table and protocol; only `np.random.default_rng(seed)` for the
10k-row draw changes.

| seed | E1↔D | E2↔D | E3↔ΔΔG | E2↔E4 | E3↔A |
| ---: | ---: | ---: | ---: | ---: | ---: |
| Manuscript | 0.49 | 0.17 | 0.26 | 0.20 | 0.55 |
| 0 | 0.49 | 0.18 | **0.24** | **0.18** | 0.54 |
| 1 | 0.49 | 0.17 | **0.26** | 0.18 | 0.55 |
| 2 | 0.49 | 0.16 | 0.27 | 0.21 | 0.54 |
| 7 | 0.49 | 0.16 | **0.26** | **0.20** | 0.55 |

Raw probe log: `reproduction_runs/2026-09-12/s2648_train_feature_figures/kpca_seed_probe.log`

### Conclusion

- Residual Fig 4–5 mismatches under seed=0 are **explained by KernelPCA
  subsample stochasticity**, not by wrong Feature A–D / F–H definitions or a
  wrong Feature E object.
- Changing only the subsample seed moves E3↔ΔΔG and E2↔E4 onto (or next to) the
  manuscript 2dp values (seed **7** matches both residual cells at 2dp).
- Reproduction should **record `kpca_seed` and `kpca_sample_size`** with any
  Fig 4–5 / RF claim. Default reporting seed remains 0 unless a paper-facing
  figure intentionally selects another documented seed.

## Division of labor: repo vs manuscript

| Where | What to say |
| --- | --- |
| **This repo** | Full experiment: 2026 re-fit, seed table, distinction from the column-index bug, links to pickles/scripts. |
| **Manuscript** | Short scientific caveat only: Fig 4–5 (and Feature E) PCCs depend on the random KernelPCA training subsample, so quoted correlations can vary slightly across draws. **Do not** narrate the recovery / re-fit chronology in the paper. |

### Suggested manuscript sentence (optional; place near §3.2.4 or Fig 4–5 discussion)

> Because Feature E is obtained from an RBF KernelPCA fit on a random subsample
> of S2648 center→neighbor message-difference vectors, the exact Pearson
> correlations involving E-1…E-5 in Figures 4 and 5 can vary slightly across
> draws; the qualitative patterns (relative magnitudes and which components
> correlate with D or with ΔΔG) are robust.

Exact wording is for the authors to finalize.

## How to re-run

```bash
# Figs 4–5 heatmaps + claim table (seed 0 by default)
.venv_proteinmpnn_ddg_reproduction/bin/python scripts/regenerate_s2648_train_feature_figures.py \
  --features-pickle reproduction_inputs/pmpnn_ddg_features_2026-09-12/S2648_proteinmpnn_and_pssm_features.pickle \
  --output-dir reproduction_runs/2026-09-12/s2648_train_feature_figures \
  --kpca-seed 0
```

Seed sweep used the same `fit_projection` / `project_instances` path as RF
(`scripts/train_eval_rf_from_v3_features.py`) with
`FEATURE_E_COLS_ON_DUAL_DIRECTION_ROW` from
`proteinmpnn_ddg_recovery/features/rf_feature_matrix_packing.py`.
