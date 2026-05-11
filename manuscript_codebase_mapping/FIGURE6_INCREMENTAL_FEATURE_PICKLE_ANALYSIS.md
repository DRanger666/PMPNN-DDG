# Figure 6 Incremental-Feature Pickle Analysis

This note records the current evidence for the later A-H incremental-feature
workflow and its stored result pickle.

## Evidence Files

- Source notebook export:
  `code_inventory_analysis/notebook_sources/git_sajid_additions/Quick_Dirty_MPNN_ML_V2_VGRAPHS_V1.ipynb.py.txt`
- Historical result pickles:
  `drive_evidence_copy/sajidahmedprotres_drive/Protein_MPNN_Digging/incremental_feature_result_dict.pickle`
  and
  `drive_evidence_copy/sajidahmedprotres_drive/Protein_MPNN_Digging/list_incremental_feature_result_dict.pickle`
- Generated inspection report:
  `code_inventory_analysis/incremental_feature_pickle_inspection/`

## Code-Level Feature Map

The later A-H workflow defines this map in
`Quick_Dirty_MPNN_ML_V2_VGRAPHS_V1.ipynb.py.txt:929`:

| Label | Feature-matrix column(s) | Code-level meaning |
| --- | --- | --- |
| A | `0` | `center_mut_wild_energy` |
| B | `6` | `V2_backward_weighted_neighbor_entropy_changes` |
| C | `7` | `center_neighbor_weight_check_w_m` |
| D | `8` | `neighbor_embedding_change_m_w` |
| E | `31,32,33,34,35` | first five selected columns from the reverse neighbor-embedding KPCA block |
| F | `5` | `wild_pssm - alternate_pssm` |
| G | `9` | `wild_pssm` |
| H | `10` | `alternate_pssm` |

The full A-H RF therefore uses columns
`[0, 6, 7, 8, 31, 32, 33, 34, 35, 5, 9, 10]`.

Feature B's exact source field is weighted; it should not be described as a
plain unweighted neighbor-entropy sum.

Important reconciliation note: the same source file identifies columns
`31..40` as reverse neighbor-embedding KPCA features
(`Quick_Dirty_MPNN_ML_V2_VGRAPHS_V1.ipynb.py.txt:358`). Therefore, in this
code path, E is not selected from the message-change PCA/KPCA blocks. That is
code-level evidence; the manuscript wording still needs separate reconciliation
before final method text is locked.

## Training/Evaluation Loop

The ten-run workflow:

- loops `n_iterations = 10`;
- trains each RF on `S_2648_X_aug[:, f_index_comb]` and `S_2648_y_aug`;
- uses `RandomForestRegressor(min_samples_split=2, n_estimators=500,
  max_samples=0.5, max_features="sqrt")`;
- evaluates each model on `S_2648`, `S_921`, `S_669`, and `Ssym`;
- stores total/direct/reverse PCC and RMSE values in `results_tracking_dict`;
- appends each run dictionary to `list_results_tracking_dict`.

The adjacent save/load cells name `list_incremental_feature_result_dict.pickle`
as the ten-run storage object.

The visible source loop also contains optional `*_forward_reverse_PCC` scalar
assignments for the full feature set. The inspected saved list pickle does not
contain those scalar keys. That absence does not affect the Figure 6-style
total-PCC bars or the direct/reverse/total PCC/RMSE rows, because the
downstream averaging/printing cells comment out the forward-vs-reverse scalar
lists.

## Pickle Structure

`list_incremental_feature_result_dict.pickle` loads as a list of 10 dictionaries.
Each dictionary contains metric dictionaries for:

- datasets: `S_2648`, `S_921`, `S_669`, `Ssym`;
- splits: `total`, `direct`, `reverse`;
- metrics: `PCC`, `RMSE`;
- incremental feature combinations from `A` through `A+B+C+D+E+F+G+H`.

The older `incremental_feature_result_dict.pickle` is a single-run dictionary.
It lacks `S_2648` metrics and should not be treated as the final ten-run Figure
6 source object.

## Figure 6 Candidate Values

The combined bar-plot cell uses:

- `S_669_PCC_vals = [i for i in dict_mean(list_S_669_total_PCC).values()]`
- `Ssym_PCC_vals = [i for i in dict_mean(list_Ssym_total_PCC).values()]`

The ten-run means from `list_incremental_feature_result_dict.pickle` are:

| Dataset | A | A+B | A+B+C | A+B+C+D | A+B+C+D+E | A+B+C+D+E+F | A+B+C+D+E+F+G | A+B+C+D+E+F+G+H |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S_669 total PCC | 0.471635 | 0.526012 | 0.577201 | 0.601057 | 0.637371 | 0.643767 | 0.643525 | 0.643995 |
| Ssym total PCC | 0.641138 | 0.700699 | 0.716445 | 0.742638 | 0.786866 | 0.802690 | 0.808748 | 0.812228 |

These values are exactly the quantity series used by the Figure 6-style
S_669/Ssym total-PCC plotting cell. The code-to-pickle match is strong for the
stored result object. The remaining manuscript-level step is to compare these
values against the final embedded manuscript figure/caption and any exported
figure image.

## Full A-H Table-Level Metrics

For the full A-H combination, the ten-run means are:

| Dataset | Split | PCC mean | RMSE mean |
| --- | --- | --- | --- |
| S_669 | direct | 0.480021 | 1.451860 |
| S_669 | reverse | 0.478905 | 1.452820 |
| S_669 | total | 0.643995 | 1.452341 |
| S_921 | direct | 0.767839 | 1.492075 |
| S_921 | reverse | 0.766319 | 1.494486 |
| S_921 | total | 0.794155 | 1.493282 |
| Ssym | direct | 0.721961 | 1.098380 |
| Ssym | reverse | 0.718826 | 1.102374 |
| Ssym | total | 0.812228 | 1.100381 |

Rounded to two decimals, these match the expected style of the manuscript
reported table values for S_921 and provide the corresponding held-out values
for S_669 and Ssym.
