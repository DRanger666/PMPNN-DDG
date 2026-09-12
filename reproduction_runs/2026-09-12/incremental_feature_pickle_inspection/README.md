# Incremental-Feature Pickle Inspection

Generated at: `2026-09-12T12:51:27.591541+00:00`.

This report inspects the two saved incremental-feature result pickles in
`drive_evidence_copy/sajidahmedprotres_drive/Protein_MPNN_Digging`.

## Loaded Pickles

```json
[
  {
    "first_item_keys": [
      "S_2648_direct_PCC",
      "S_2648_direct_RMSE",
      "S_2648_reverse_PCC",
      "S_2648_reverse_RMSE",
      "S_2648_total_PCC",
      "S_2648_total_RMSE",
      "S_669_direct_PCC",
      "S_669_direct_RMSE",
      "S_669_reverse_PCC",
      "S_669_reverse_RMSE",
      "S_669_total_PCC",
      "S_669_total_RMSE",
      "S_921_direct_PCC",
      "S_921_direct_RMSE",
      "S_921_reverse_PCC",
      "S_921_reverse_RMSE",
      "S_921_total_PCC",
      "S_921_total_RMSE",
      "Ssym_direct_PCC",
      "Ssym_direct_RMSE",
      "Ssym_reverse_PCC",
      "Ssym_reverse_RMSE",
      "Ssym_total_PCC",
      "Ssym_total_RMSE"
    ],
    "item_types": [
      "builtins.dict"
    ],
    "len": 10,
    "pickle_file": "list_incremental_feature_result_dict.pickle",
    "type": "builtins.list"
  }
]
```

## Later A-H Incremental Feature Map

This is the feature map in `Quick_Dirty_MPNN_ML_V2_VGRAPHS_V1.ipynb.py.txt`.
The RFs are trained on `S_2648_X_aug[:, f_index_comb]` and `S_2648_y_aug`.

| label | columns | code_field_or_expression | column_block_meaning_from_source |
| --- | --- | --- | --- |
| A | 0 | center_mut_wild_energy | center wild-vs-mutant log-probability/energy change |
| B | 6 | V2_backward_weighted_neighbor_entropy_changes | weighted backward neighbor entropy change |
| C | 7 | center_neighbor_weight_check_w_m | center-to-neighbor message norm ratio |
| D | 8 | neighbor_embedding_change_m_w | summed neighbor embedding change |
| E | 31,32,33,34,35 | first five columns selected from reverse neighbor-embedding KPCA block | columns 31..40 are reverse neighbor-embedding KPCA |
| F | 5 | wild_pssm - alternate_pssm | PSSM delta |
| G | 9 | wild_pssm | wild-type PSSM value |
| H | 10 | alternate_pssm | mutant amino-acid PSSM value |

The full A-H model therefore uses these feature-matrix columns:
`[0, 6, 7, 8, 31, 32, 33, 34, 35, 5, 9, 10]`.

Important reconciliation note: in this code path, feature E is columns 31..35.
The same source file identifies columns 31..40 as reverse neighbor-embedding
KPCA features. This is code-level evidence and should be reconciled separately
against manuscript wording before making a final methods claim.

Observed saved-object note: the inspected ten-run list pickle contains the
feature-combination metric dictionaries shown above. It does not contain the
optional `*_forward_reverse_PCC` scalar keys visible in the source loop. Those
scalars are commented out in the downstream averaging/printing cells and are
not used by the Figure 6-style total-PCC bar plot.

## Older A-F Feature Map for `feature_combo_*`

The unsuffixed `feature_combo_*` pickles are not the A-H incremental workflow.
They come from the older V2 all-combinations workflow. For each model key,
the RF is trained on the corresponding subset of the six features below.

| label | columns | code_field_or_expression | notebook_comment_name |
| --- | --- | --- | --- |
| A | 0 | center_mut_wild_energy | P_DP |
| B | 4 | V2_backward_weighted_neighbor_backward_KL | BACK_KL |
| C | 7 | center_neighbor_weight_check_w_m | W/M |
| D | 2 | V2_backward_weighted_neighbor_energy_changes | Neighbor_Energy |
| E | 6 | V2_backward_weighted_neighbor_entropy_changes | Neighbor_Entropy |
| F | 5 | wild_pssm - alternate_pssm | PSSM |

The full A-F model uses columns `[0, 4, 7, 2, 6, 5]` in label order.
The result pickle contains all 63 non-empty subsets of A-F.

## Figure 6 Candidate Values

The plotting cell for the manuscript-like combined bar chart uses
`dict_mean(list_S_669_total_PCC)` and `dict_mean(list_Ssym_total_PCC)`.
The table below summarizes the ten-run `list_incremental_feature_result_dict`
values for exactly those two total-PCC series.

| dataset | feature_combo | n | mean | sample_std | round_mean_2 |
| --- | --- | --- | --- | --- | --- |
| S_669 | A | 10 | 0.471635 | 0.001027 | 0.47 |
| S_669 | A+B | 10 | 0.526012 | 0.001255 | 0.53 |
| S_669 | A+B+C | 10 | 0.577201 | 0.000770 | 0.58 |
| S_669 | A+B+C+D | 10 | 0.601057 | 0.001158 | 0.60 |
| S_669 | A+B+C+D+E | 10 | 0.637371 | 0.000906 | 0.64 |
| S_669 | A+B+C+D+E+F | 10 | 0.643767 | 0.000855 | 0.64 |
| S_669 | A+B+C+D+E+F+G | 10 | 0.643525 | 0.001191 | 0.64 |
| S_669 | A+B+C+D+E+F+G+H | 10 | 0.643995 | 0.001312 | 0.64 |
| Ssym | A | 10 | 0.641138 | 0.001442 | 0.64 |
| Ssym | A+B | 10 | 0.700699 | 0.001113 | 0.70 |
| Ssym | A+B+C | 10 | 0.716445 | 0.000781 | 0.72 |
| Ssym | A+B+C+D | 10 | 0.742638 | 0.000962 | 0.74 |
| Ssym | A+B+C+D+E | 10 | 0.786866 | 0.000920 | 0.79 |
| Ssym | A+B+C+D+E+F | 10 | 0.802690 | 0.000919 | 0.80 |
| Ssym | A+B+C+D+E+F+G | 10 | 0.808748 | 0.000942 | 0.81 |
| Ssym | A+B+C+D+E+F+G+H | 10 | 0.812228 | 0.001209 | 0.81 |

## Full A-H Metrics

These are the full A-H mean values from the ten-run list pickle for the held-out
datasets that appear in manuscript Table 1 / Figure 6 discussions.

| dataset | split | metric | n | mean | sample_std | round_mean_2 |
| --- | --- | --- | --- | --- | --- | --- |
| S_669 | direct | PCC | 10 | 0.480021 | 0.002514 | 0.48 |
| S_669 | reverse | PCC | 10 | 0.478905 | 0.002804 | 0.48 |
| S_669 | total | PCC | 10 | 0.643995 | 0.001312 | 0.64 |
| S_669 | direct | RMSE | 10 | 1.451860 | 0.002315 | 1.45 |
| S_669 | reverse | RMSE | 10 | 1.452820 | 0.002560 | 1.45 |
| S_669 | total | RMSE | 10 | 1.452341 | 0.002029 | 1.45 |
| S_921 | direct | PCC | 10 | 0.767839 | 0.001034 | 0.77 |
| S_921 | reverse | PCC | 10 | 0.766319 | 0.001332 | 0.77 |
| S_921 | total | PCC | 10 | 0.794155 | 0.001118 | 0.79 |
| S_921 | direct | RMSE | 10 | 1.492075 | 0.002732 | 1.49 |
| S_921 | reverse | RMSE | 10 | 1.494486 | 0.003059 | 1.49 |
| S_921 | total | RMSE | 10 | 1.493282 | 0.002633 | 1.49 |
| Ssym | direct | PCC | 10 | 0.721961 | 0.002326 | 0.72 |
| Ssym | reverse | PCC | 10 | 0.718826 | 0.002848 | 0.72 |
| Ssym | total | PCC | 10 | 0.812228 | 0.001209 | 0.81 |
| Ssym | direct | RMSE | 10 | 1.098380 | 0.003272 | 1.10 |
| Ssym | reverse | RMSE | 10 | 1.102374 | 0.003888 | 1.10 |
| Ssym | total | RMSE | 10 | 1.100381 | 0.002650 | 1.10 |

## Generated Files

- `incremental_feature_object_summary.json`
- `incremental_feature_raw_rows.tsv`
- `incremental_feature_summary.tsv`
- `figure6_total_pcc_summary.tsv`
- `full_ah_metric_summary.tsv`
- `legacy_af_feature_map.tsv`
- `incremental_ah_feature_map.tsv`
