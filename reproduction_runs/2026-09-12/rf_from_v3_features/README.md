# RF retrain from saved historical V3 features (primary)

Date: 2026-09-12

## Feature source (labeled)

- Saved historical V3 pickles under `drive_evidence_copy/.../Protein_MPNN_Digging/`
- Engineered scalars + PSSM from those pickles
- Feature E: **re-fit** RBF KernelPCA on S_2648 `neighbor_message_change_m_w_raw`
  (`--kpca-seed 0`, 10k subsample); first 5 message-KPCA components
- Feature B mode: **`historical_weighted`**
  (`V2_backward_weighted_neighbor_entropy_changes` — Table 1 / Fig 6 notebook map)
- S_669 experimental ΔΔG sign flip applied (`y *= -1`) as in ML notebooks

Not claimed: PDB→V3 tensor regeneration; bit-exact Feature E vs 2022 Colab.

## Command

```bash
.venv_proteinmpnn_ddg_reproduction/bin/python scripts/train_eval_rf_from_v3_features.py \
  --output-dir reproduction_runs/2026-09-12/rf_from_v3_features \
  --n-runs 10 --full-ah-only \
  --configs manuscript_literal notebook_table1 \
  --feature-b-mode historical_weighted
```

## Coverage

| Dataset | Forward mutations used | Skipped incomplete |
| --- | ---: | ---: |
| S_2648 | 2620 | 28 |
| S_669 | 638 | 31 |
| S_921 | 921 | 0 |
| Ssym | 342 | 0 |

## Measured means vs manuscript Table 1 (PMPNN-DDG)

Rounded match counts below use manuscript 2-decimal rounding.

### Config `notebook_table1` (n_estimators=500, max_samples=0.5, max_features=sqrt)

Closest to the historical ten-run pickle protocol.

| Dataset | Metric | Ours mean | Ours round | Paper | Match? |
| --- | --- | ---: | ---: | ---: | --- |
| S_669 | rF+R | 0.6443 | 0.64 | 0.64 | yes |
| S_669 | rmsF+R | 1.4517 | 1.45 | 1.45 | yes |
| S_669 | rF-R | -0.9940 | -0.99 | -0.99 | yes |
| Ssym | rF+R | 0.8108 | 0.81 | 0.81 | yes |
| Ssym | rmsF+R | 1.1039 | 1.10 | 1.10 | yes |
| S_921 | rF+R | 0.7954 | 0.80 | 0.79 | no (±0.01) |
| S_921 | rmsF+R | 1.4915 | 1.49 | 1.49 | yes |

Full cell-by-cell: `ours_vs_paper_table1.tsv`.

### Config `manuscript_literal` (n_estimators=500, max_samples=0.5, sklearn defaults)

Also close (rF+R within ~0.01 of paper on all three sets); slightly farther than
`notebook_table1` on several rounded cells.

## Interpretation

Retraining RF from **saved historical V3 engineered features** recovers
manuscript Table 1 at the rounded level for the notebook hyperparams on
S_669/Ssym and nearly on S_921. Manuscript-method RF reproduction from these
features is **promising**; remaining gaps are upstream PDB→tensor regeneration
and Feature E subsample seed vs 2022 Colab.
