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
| E | `31,32,33,34,35` | first five selected message-KPCA columns in the augmented RF matrix |
| F | `5` | `wild_pssm - alternate_pssm` |
| G | `9` | `wild_pssm` |
| H | `10` | `alternate_pssm` |

The full A-H RF therefore uses columns
`[0, 6, 7, 8, 31, 32, 33, 34, 35, 5, 9, 10]`.

Feature B's exact source field is weighted; it should not be described as a
plain unweighted neighbor-entropy sum.

Important column-interpretation note: the feature map is applied to
`S_*_X_aug`, not to the pre-augmentation `S_*_X`. In the pre-augmentation
matrix, columns `31..40` are reverse-oriented neighbor-embedding KPCA features.
During augmentation/column compaction, message-KPCA columns move into augmented
columns `31..40`. Therefore, in the final RF input, E is selected from the
message-KPCA block and is aligned with the manuscript-level feature family.

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

## Figure 6 Verified Image Values

The combined bar-plot cell uses:

- `S_669_PCC_vals = [i for i in dict_mean(list_S_669_total_PCC).values()]`
- `Ssym_PCC_vals = [i for i in dict_mean(list_Ssym_total_PCC).values()]`

The ten-run means from `list_incremental_feature_result_dict.pickle` are:

| Dataset | A | A+B | A+B+C | A+B+C+D | A+B+C+D+E | A+B+C+D+E+F | A+B+C+D+E+F+G | A+B+C+D+E+F+G+H |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S_669 total PCC | 0.471635 | 0.526012 | 0.577201 | 0.601057 | 0.637371 | 0.643767 | 0.643525 | 0.643995 |
| Ssym total PCC | 0.641138 | 0.700699 | 0.716445 | 0.742638 | 0.786866 | 0.802690 | 0.808748 | 0.812228 |

These values are exactly the quantity series used by the Figure 6 S_669/Ssym
total-PCC plotting cell.

The standalone manuscript image
`drive_evidence_copy/sajidahmedprotres_drive/MPNN_DDG_Manuscript/Feature_Combinations_MultiPlot.png`
is byte-identical to the saved output of
`source_repos/SajidAhmeduiu_ProteinMPNN/Sajid_Additions/Quick_Dirty_MPNN_ML_V2_VGRAPHS_V1.ipynb`
cell index `40`, output index `0`.

Exact shared SHA256:

```text
9cec9fcf1d3f466b8bf0f1766bc98c20152b2c617c5d872d3e3588f79143da95
```

Therefore the numerical basis of the manuscript Figure 6 image is verified at
the result-pickle/plotting layer. See:

```text
manuscript_codebase_mapping/FIGURE6_NUMERICAL_BASIS_VERIFICATION.md
code_inventory_analysis/figure6_image_verification/
```

DOCX note: the final DOCX references Figure 6 as `media/image6.png`. That
embedded PNG is not byte-identical to the standalone manuscript image, but this
is not a scientific-content discrepancy. Manual visual comparison found the same
S_669/Ssym incremental total-PCC content; the differences are layout/rendering
differences.

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

Rounded to two decimals, these match the manuscript Table 1 values for the six
non-`rF-R` columns for S_669, S_921, and Ssym.
