# S_921 Pickle Content Report

Date: 2026-05-07

## Scope

This is a targeted, workspace-local analysis of four historical S_921 pickle
artifacts copied from the local evidence tree:

`drive_evidence_copy/sajidahmedprotres_drive/Protein_MPNN_Digging`

The analysis inputs were copied into:

`pickle_analysis/S_921_target_pickles`

The filenames use the historical spelling `pmppn`, not `pmpnn`:

- `S_921_full_feature_dict.pickle`
- `S_921_pmppn_info_dict.pickle`
- `S_921_pmppn_info_dict_V2.pickle`
- `S_921_pmppn_info_dict_V3.pickle`

The script does not read the FUSE mount. It only reads the copied local pickle
inputs under `pickle_analysis/S_921_target_pickles`.

## Method

Inspection script:

`scripts/inspect_s921_pickles.py`

Environment:

`.venv_pickle_analysis`

Package versions are recorded in `pickle_analysis/uv_freeze.txt`.

The script performs four conservative passes:

1. Records file size, preserved mtime, and SHA256.
2. Scans pickle opcodes/globals with `pickletools`.
3. Loads each pickle one by one with a restricted logging unpickler.
4. Emits compact TSV/JSON summaries instead of raw object dumps.

## Copied Inputs

| File | Size bytes | Preserved mtime UTC | SHA256 |
|---|---:|---|---|
| `S_921_full_feature_dict.pickle` | 32,278,828 | 2022-08-16T05:21:29.733000+00:00 | `c17247cb6c79b3557eec97d091e9ab8e335d328580a337f469fea6d162aea295` |
| `S_921_pmppn_info_dict.pickle` | 31,611,020 | 2022-08-15T16:19:15.981000+00:00 | `cd92a03224d6d3034e44db10076f7cc9e2922e017e2ccbcee3b3be7c7cfb5552` |
| `S_921_pmppn_info_dict_V2.pickle` | 55,304,432 | 2022-08-25T16:03:49.548000+00:00 | `71d8ba6e81eca4009a73aca458b96b49ad0138c844da4bb49b499ca2a2f2833f` |
| `S_921_pmppn_info_dict_V3.pickle` | 64,760,657 | 2022-08-30T14:42:04.484000+00:00 | `5941620bb56f94056da126d6b544c7796cb5b961d9b358aebd70656419fb7daa` |

Generated evidence tables:

- `pickle_analysis/tables/S_921_pickle_file_manifest.tsv`
- `pickle_analysis/tables/S_921_pickle_static_scan.tsv`
- `pickle_analysis/tables/S_921_pickle_load_audit.tsv`
- `pickle_analysis/tables/S_921_pickle_top_level_summary.tsv`
- `pickle_analysis/tables/S_921_pickle_entry_schema.tsv`
- `pickle_analysis/tables/S_921_pickle_entry_field_summary.tsv`
- `pickle_analysis/tables/S_921_pickle_array_templates.tsv`
- `pickle_analysis/tables/S_921_pickle_top_key_overlap.tsv`
- `pickle_analysis/tables/S_921_pickle_entry_field_overlap.tsv`
- `pickle_analysis/tables/S_921_pickle_entry_count_by_protein.tsv`
- `pickle_analysis/json/S_921_pickle_summaries.json`

## Load Audit

All four pickles loaded successfully with the restricted unpickler.

The only resolved globals were NumPy reconstruction/scalar/dtype/array globals:

- `numpy.core.multiarray._reconstruct`
- `numpy.core.multiarray.scalar`
- `numpy.dtype`
- `numpy.ndarray`

No scikit-learn, pandas, or custom project classes were required to load these
four files. At the pickle-object level, they are plain dictionaries/lists plus
NumPy arrays/scalars.

## Shared Dataset Structure

All four files are dictionaries with the same top-level S_921 protein keys.

| File | Protein keys | Mutation entries | Entries/protein min | Entries/protein median | Entries/protein max |
|---|---:|---:|---:|---:|---:|
| `S_921_pmppn_info_dict.pickle` | 195 | 921 | 1 | 1 | 153 |
| `S_921_full_feature_dict.pickle` | 195 | 921 | 1 | 1 | 153 |
| `S_921_pmppn_info_dict_V2.pickle` | 195 | 921 | 1 | 1 | 153 |
| `S_921_pmppn_info_dict_V3.pickle` | 195 | 921 | 1 | 1 | 153 |

Pairwise top-level key overlap is exact: every pair has `195/195` intersecting
protein keys and Jaccard `1.000000`.

Every mutation entry in every file contains `ddg` and `mut`.

## Per-File Content

### `S_921_pmppn_info_dict.pickle`

This is the base ProteinMPNN extraction dictionary for S_921.

It has 16 fields per mutation entry, all present in all 921 mutation entries:

- `ddg`
- `mut`
- `log_prob`
- `w_n_log_prob`
- `m_n_log_prob`
- `neighbor_aa_identities`
- `neighbor_w_message_vector_coming_from_center`
- `neighbor_m_message_vector_coming_from_center`
- `top_15_attention_weights`
- `top_10_attention_weights`
- `top_5_attention_weights`
- `top_15_neighbor_indices`
- `top_10_neighbor_indices`
- `top_5_neighbor_indices`
- `top_15_closest_neighbor_indices`
- `top_10_closest_neighbor_indices`

Interpretation: this is raw/intermediate ProteinMPNN state plus labels and
mutation IDs. It has enough information for neighbor log-probability and
message-vector based feature engineering, but it does not yet contain the final
engineered scalar fields or raw neighbor embedding/message change tensors.

### `S_921_full_feature_dict.pickle`

This has 34 fields per mutation entry, all present in all 921 mutation entries.

It contains all 16 raw fields from `S_921_pmppn_info_dict.pickle`, plus scalar
engineered features:

- `center_mut_wild_energy`
- `center_mut_max_energy`
- `center_entropy`
- `weighted_neighbor_entropies`
- `weighted_neighbor_energy_changes`
- `backward_weighted_neighbor_energy_changes`
- `V2_backward_weighted_neighbor_energy_changes`
- `weighted_neighbor_forward_KL`
- `weighted_neighbor_backward_KL`
- `backward_weighted_neighbor_backward_KL`
- `V2_backward_weighted_neighbor_backward_KL`
- `weighted_neighbor_entropy_changes`
- `backward_weighted_neighbor_entropy_changes`
- `V2_backward_weighted_neighbor_entropy_changes`
- `center_neighbor_weight_check_m_w`
- `center_neighbor_weight_check_w_m`
- `wild_pssm`
- `alternate_pssm`

Interpretation: despite the name `full_feature_dict`, this is not the final
V3-style artifact used by the final A-H notebooks. It is best treated as an
early raw-plus-scalar engineered feature dictionary.

### `S_921_pmppn_info_dict_V2.pickle`

This has 42 fields per mutation entry, all present in all 921 mutation entries.

Compared with `S_921_full_feature_dict.pickle`, V2 adds eight fields:

- `neighbor_w_neighbor_embedding`
- `neighbor_m_neighbor_embedding`
- `neighbor_embedding_change_m_w`
- `neighbor_embedding_change_m_w_raw`
- `sum_neighbor_embedding_change_m_w`
- `neighbor_message_change_m_w`
- `unweighted_backward_KL`
- `unweighted_forward_KL`

Important distinction: V2 has scalar `neighbor_message_change_m_w`, but it does
not have `neighbor_message_change_m_w_raw`.

Array evidence:

- `neighbor_embedding_change_m_w_raw`: 921 arrays, each shape `[15, 128]`,
  dtype `float32`.

Interpretation: V2 captures the transition from scalar hand-engineered features
into raw neighbor embedding changes suitable for PCA/KPCA, but it is still
missing raw message-change tensors.

### `S_921_pmppn_info_dict_V3.pickle`

This has 43 fields per mutation entry, all present in all 921 mutation entries.

Compared with V2, V3 adds exactly one field:

- `neighbor_message_change_m_w_raw`

Array evidence:

- `neighbor_message_change_m_w_raw`: 921 arrays, each shape `[15, 128, 1]`;
  dtype distribution is 619 `float32` and 302 `float64`.
- `neighbor_embedding_change_m_w_raw`: 921 arrays, each shape `[15, 128]`,
  dtype `float32`.
- `w_n_log_prob` and `m_n_log_prob`: 13,815 arrays each, shape `[21]`
  (`921 * 15` neighbor amino-acid distributions).
- `neighbor_w_message_vector_coming_from_center` and
  `neighbor_m_message_vector_coming_from_center`: 13,815 arrays each, shape
  `[128]`.

Interpretation: V3 is the final manuscript-relevant S_921 pickle for the A-H
feature mapping, because it contains the raw message-change tensor that the
final ML notebooks reduce with message-change PCA/KPCA.

## Schema Evolution

| Step | Field count | Main evidence |
|---|---:|---|
| `S_921_pmppn_info_dict.pickle` | 16 | Raw ProteinMPNN log-probability, neighbor, attention, and center-to-neighbor message vectors. |
| `S_921_full_feature_dict.pickle` | 34 | Adds scalar energy, entropy, KL, PSSM, and weighted neighbor feature fields. |
| `S_921_pmppn_info_dict_V2.pickle` | 42 | Adds neighbor embedding vectors, raw embedding-change arrays, scalar message-change, and unweighted KL. |
| `S_921_pmppn_info_dict_V3.pickle` | 43 | Adds raw message-change tensors for downstream PCA/KPCA. |

This is a coherent feature-engineering lineage over the same 921 S_921 mutation
entries, not four unrelated pickle formats.

## Code Linkage

### Feature extraction notebook

Source:

`colab_notebooks_inventory_analysis/git_notebook_sources/S921_ProteinMPNNTesting_V6_V2.ipynb.py.txt`

The saved source contains a commented intended save cell for
`S_921_pmppn_info_dict_V3.pickle` at lines 1951-1955. Because the save cell is
commented in the recovered source, this is not by itself active-write proof.

The same notebook contains the actual feature-assignment logic:

- Lines 2057-2059 initialize raw neighbor embedding/message change lists.
- Lines 2100-2103 compute embedding-change norm, raw embedding change, raw
  message change, and message-change norm.
- Lines 2121-2123 compute V2 backward weighted neighbor energy, KL, and entropy
  changes using `expit(center_neighbor_weight_check_w_m)`.
- Lines 2147-2159 assign `V2_backward_weighted_neighbor_entropy_changes`,
  `neighbor_embedding_change_m_w_raw`, `neighbor_message_change_m_w_raw`, and
  scalar `neighbor_message_change_m_w` into each mutation dictionary.

This code explains exactly why V3 differs from V2: V3 preserves raw
`neighbor_message_change_m_w_raw`, which V2 lacks.

### Final ML/graph notebook

Source:

`colab_notebooks_inventory_analysis/git_notebook_sources/Quick_Dirty_MPNN_ML_V2_VGRAPHS_V1.ipynb.py.txt`

Key source facts:

- Lines 47-50 actively load `S_2648_pmppn_info_dict_V3.pickle` and
  `S_921_pmppn_info_dict_V3.pickle`.
- Lines 57-58 set dataset order to `S_2648`, `S_921`, `S_669`, `Ssym`.
- Lines 171-172 extract `neighbor_embedding_change_m_w_raw` and squeezed
  `neighbor_message_change_m_w_raw`.
- Lines 177-238 build the per-mutation feature vector from scalar fields plus
  raw embedding/message change arrays.
- Lines 267-286 fit PCA/KPCA for neighbor embedding changes.
- Lines 293-312 fit PCA/KPCA for message changes.
- Lines 323-343 transform and sum PCA/KPCA projections.
- Lines 352-368 append the projected features into the final instance vector.
- Lines 929-936 define the final A-H feature map.

The final feature map is:

| Manuscript label | Final feature index |
|---|---|
| A | `0` |
| B | `6` |
| C | `7` |
| D | `8` |
| E | `[31, 32, 33, 34, 35]` |
| F | `5` |
| G | `9` |
| H | `10` |

Important resolved point: in the final 41-column augmented matrix used by the
A-H map, feature E points to message-change RBF-KPCA columns `31..35`. The
earlier confusion came from an intermediate/pre-final matrix where nearby
column comments referred to neighbor KPCA before later feature reduction and
re-indexing.

## Manuscript Tie-In

The S_921 V3 pickle is tied to manuscript-level evidence in two ways:

1. It provides all scalar fields and raw message-change tensors required by the
   final A-H map in `Quick_Dirty_MPNN_ML_V2_VGRAPHS_V1.ipynb`.
2. The notebook output preserves S_921 performance values for the final
   `A+B+C+D+E+F+G+H` model.

For S_921, the graph notebook prints final rounded values in this order:
direct PCC, reverse PCC, total PCC, direct RMSE, reverse RMSE, total RMSE
(`Quick_Dirty_MPNN_ML_V2_VGRAPHS_V1.ipynb.py.txt` lines 1139-1146).

The corresponding output lines 5129-5134 are:

| Metric | Value |
|---|---:|
| Direct PCC | 0.77 |
| Reverse PCC | 0.77 |
| Total PCC | 0.79 |
| Direct RMSE | 1.49 |
| Reverse RMSE | 1.49 |
| Total RMSE | 1.49 |

The output cell also preserves S_921 incremental total-PCC values:

| Feature set | S_921 total PCC |
|---|---:|
| A | 0.5655701626935924 |
| A+B | 0.6288149941804836 |
| A+B+C | 0.6412590948882598 |
| A+B+C+D | 0.6861844881476283 |
| A+B+C+D+E | 0.7291185753781343 |
| A+B+C+D+E+F | 0.7605354514204117 |
| A+B+C+D+E+F+G | 0.764134835491854 |
| A+B+C+D+E+F+G+H | 0.767839284168835 |

Those numbers are in
`colab_notebooks_inventory_analysis/git_notebook_outputs/Quick_Dirty_MPNN_ML_V2_VGRAPHS_V1.ipynb.outputs.txt`
lines 5140-5147.

## Feature B Caution

Feature B should remain flagged for manuscript-methods cleanup.

The final A-H map makes B column `6`. The feature-vector construction assigns
column `6` from `mut["V2_backward_weighted_neighbor_entropy_changes"]`
(`Quick_Dirty_MPNN_ML_V2_VGRAPHS_V1.ipynb.py.txt` lines 207-209).

The feature-extraction notebook computes this field as:

`sum(local_neighbor_entropy_change_vals[0:15] * expit(local_center_neighbor_weight_check_w_m[0:15]))`

That is entropy change weighted by a sigmoid-transformed center-to-neighbor
message norm ratio. It is not a plain unweighted neighbor entropy-change sum.

## Current Confidence

High confidence:

- The four copied pickle inputs were correctly identified and loaded.
- All four describe the same S_921 protein/mutation set.
- V3 is the final manuscript-relevant S_921 pickle for the A-H feature map.
- V3 is required for message-change PCA/KPCA because it adds
  `neighbor_message_change_m_w_raw`.
- The final graph notebook actively consumes V3 and preserves S_921 output
  values.

Remaining cautions:

- The recovered V3 producer save cell is commented, so we still need stronger
  active-write evidence if exact pickle generation provenance is required.
- The V3 pickle mtime and downstream active use are strong linkage evidence,
  but not a complete rerun proof.
- Feature B manuscript wording should be tightened after table/figure mapping
  confirms the exact final numbers to preserve.

## Next Evidence Step

The next targeted step should be table/figure provenance mapping:

- Match each manuscript S_921 table number to notebook output cells.
- Confirm whether `Quick_Dirty_MPNN_ML_V2_VGRAPHS_V1.ipynb` output cells are the
  exact source of the manuscript table values.
- Then map all four final datasets (`S_2648`, `S_921`, `S_669`, `Ssym`) through
  the same V3 pickle and A-H feature pipeline.
