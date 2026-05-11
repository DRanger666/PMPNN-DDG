# Feature-Combination Pickle Utility Assessment

This note assesses the four historical `feature_combo` pickles in
`drive_evidence_copy/sajidahmedprotres_drive/Protein_MPNN_Digging` for
manuscript result recovery and reproduction.

## Files Assessed

| File | Stored object | Direct role |
| --- | --- | --- |
| `feature_combo_result_dict.pickle` | dict with keys `S_921`, `S_669`, `Ssym` | PCC results for all non-empty A-F feature combinations after RF training on `S_2648` |
| `feature_combo_model_dict.pickle` | dict with 63 `RandomForestRegressor` models | Saved RF models corresponding to `feature_combo_result_dict.pickle` |
| `S_669_feature_combo_result_dict.pickle` | dict with keys `S_921`, `S_2648`, `Ssym` | PCC results for all non-empty A-F feature combinations after RF training on `S_669` |
| `S_669_feature_combo_model_dict.pickle` | dict with 63 `RandomForestRegressor` models | Saved RF models corresponding to `S_669_feature_combo_result_dict.pickle` |

The generated inspection report is in
`code_inventory_analysis/feature_combo_pickle_inspection/`.

## Old A-F Feature Map

These pickles use the older six-feature map in
`Quick_Dirty_MPNN_ML_V2_V2.ipynb`:

| Label | Notebook meaning | Feature index |
| --- | --- | --- |
| A | `P_DP` | 0 |
| B | `BACK_KL` | 4 |
| C | `W/M` | 7 |
| D | `Neighbor_Energy` | 2 |
| E | `Neighbor_Entropy` | 6 |
| F | `PSSM` | 5 |

Do not equate this older A-F label map with the later manuscript Figure 6 A-H
map without an explicit code bridge. In the later Figure 6 notebook, feature E
is a five-column block and features G/H are present.

## Source-Code Evidence

`feature_combo_result_dict.pickle` and `feature_combo_model_dict.pickle` match
the S_2648-trained all-combinations loop in
`colab_notebooks_inventory_analysis/git_notebook_sources/Quick_Dirty_MPNN_ML_V2_V2.ipynb.py.txt:701`.
That cell:

- defines all non-empty combinations of A-F;
- trains `RandomForestRegressor(min_samples_split=5, n_estimators=300,
  max_samples=0.2, max_features="sqrt")` on `S_2648_X_aug`;
- evaluates the trained model on `S_921_X_aug`, `S_669_X_aug`, and
  `Ssym_X_aug`;
- stores models in `model_tracking_dict`;
- has adjacent save cells for `feature_combo_result_dict.pickle` and
  `feature_combo_model_dict.pickle`.

`S_669_feature_combo_result_dict.pickle` and
`S_669_feature_combo_model_dict.pickle` match the immediately following
S_669-trained all-combinations loop in the same notebook at line 769. That
cell explicitly says it is "training on S_669, and testing on the other
datasets"; the result dict therefore has `S_921`, `S_2648`, and `Ssym` keys,
not an `S_669` key.

## Pickle-Level Result Summary

From `feature_combo_result_entries.tsv`:

| Pickle | Evaluation key | Best combination | Best PCC | Full A-F PCC |
| --- | --- | --- | --- | --- |
| `feature_combo_result_dict.pickle` | `S_921` | `A+D+E+F` | 0.762562 | 0.748657 |
| `feature_combo_result_dict.pickle` | `S_669` | `A+B+C+F` | 0.602891 | 0.595910 |
| `feature_combo_result_dict.pickle` | `Ssym` | `A+B+C+D+E+F` | 0.762708 | 0.762708 |
| `S_669_feature_combo_result_dict.pickle` | `S_921` | `A+D+E+F` | 0.738361 | 0.694478 |
| `S_669_feature_combo_result_dict.pickle` | `S_2648` | `A+D+E+F` | 0.705228 | 0.684735 |
| `S_669_feature_combo_result_dict.pickle` | `Ssym` | `A+D+E` | 0.712194 | 0.656475 |

## Manuscript Utility

High utility:

- These files preserve an early RF feature-combination experiment over all
  non-empty combinations of the older A-F feature set.
- The unsuffixed pair is directly relevant to understanding early
  S_2648-trained feature-combination exploration and may explain draft-era
  feature-combination tables or plots.
- The model pickles let us inspect or rerun the exact saved RF objects if the
  corresponding feature matrices are reconstructed.

Limited utility for final manuscript-number reproduction:

- These four pickles are not the direct source of the current manuscript Table
  1 rows. Table 1 uses the later full A-H feature set and reports forward,
  reverse, total, forward-vs-reverse, and RMSE metrics.
- These four pickles are not the direct source of manuscript Figure 6 as
  described in the latest manuscript text. Figure 6 says RF was trained ten
  times on S_2648 and that features A-H were added incrementally. That maps to
  `list_incremental_feature_result_dict.pickle` and the
  `Quick_Dirty_MPNN_ML_V2_VGRAPHS_V1.ipynb` incremental-feature cells, not to
  these older A-F all-combination pickles.
- The `S_669_feature_combo_*` pair is especially unlikely to support final
  manuscript claims, because the final manuscript frames S_669 as an
  independent test set, whereas this pair trains on S_669.

## Working Decision

Treat these four pickles as historically useful exploratory evidence, not as
primary manuscript-result evidence unless a specific draft figure/table is
matched to their exact values.

For current recovery/reproduction, prioritize:

1. `list_incremental_feature_result_dict.pickle` for Figure 6.
2. Table 1 RF evaluation notebook cells and their loaded V3 feature pickles.
3. These four `feature_combo` pickles only when tracing older feature-selection
   or draft-figure history.

