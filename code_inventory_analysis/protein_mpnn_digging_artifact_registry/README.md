# Protein_MPNN_Digging Artifact Registry

This report is generated from the copied local evidence tree:

- Evidence root: `drive_evidence_copy/sajidahmedprotres_drive/Protein_MPNN_Digging`
- Generated at: `2026-05-11T03:57:30.812070+00:00`
- File count: `184`
- Total bytes: `2238258031`

## Main Findings

- The copied `Protein_MPNN_Digging` tree is only partially tracked by the workspace Git repository; promoted files are represented in `artifact_registry.tsv` with `git_tracked_now=yes`.
- The V3 `*_pmppn_info_dict_V3.pickle` files, trained model pickles, and ProteinMPNN `.pt` checkpoints are binary artifacts; they need Git LFS or an external artifact-store decision before promotion.
- The nested `ProteinMPNN/.git` metadata should not be committed as a nested Git directory. Preserve the source state by pinned commit, patch/diff, or an archive/bundle decision.
- The nested copied ProteinMPNN checkout HEAD is `c602ced6ad4b6997d89afa9432607ac9d0572539` with status `M vanilla_proteinmpnn/protein_mpnn_utils.py`.
- Checkpoint usage lines mentioning `v_48_020` were found: `76`.

## Artifact Classes

- `base_pmpnn_info_pickle`: `4` files
- `binary_analysis_artifact`: `2` files
- `full_feature_pickle`: `4` files
- `ml_result_summary_pickle`: `5` files
- `nested_proteinmpnn_git_history`: `24` files
- `nested_proteinmpnn_source_or_example`: `121` files
- `notebook_artifact`: `3` files
- `proteinmpnn_checkpoint_weight`: `7` files
- `runtime_cache`: `2` files
- `trained_feature_combo_model_pickle`: `2` files
- `uncategorized_small_artifact`: `2` files
- `v2_pmpnn_info_pickle`: `4` files
- `v3_pmpnn_info_pickle`: `4` files

## Storage Route Counts

- `decide_after_dependency_review`: `2` files
- `do_not_track`: `2` files
- `git_lfs_candidate_after_deep_inspection`: `2` files
- `git_lfs_candidate_if_needed_for_lineage`: `8` files
- `git_lfs_candidate_if_needed_for_number_provenance`: `5` files
- `git_lfs_candidate_if_needed_for_scalar_feature_lineage`: `4` files
- `git_lfs_candidate_required_for_recovery`: `4` files
- `git_lfs_candidate_required_if_used`: `7` files
- `git_lfs_or_regular_git_case_by_case`: `2` files
- `preserve_as_evidence_archive_not_regular_git`: `24` files
- `regular_git_if_provenance_relevant`: `3` files
- `regular_git_or_source_snapshot_decision`: `121` files

## Largest Artifacts

- `feature_combo_model_dict.pickle`: `952599676` bytes, class `trained_feature_combo_model_pickle`, sha256 `620cfbee4488fb3f2fc29f3f1810eef792c963c2db4841359bdeae9eb4bf7ca4`
- `S_669_feature_combo_model_dict.pickle`: `237692804` bytes, class `trained_feature_combo_model_pickle`, sha256 `7d2c8ef4947166c985e9f04ac2a39b957893467f6c029b97eef9cfa0c30c9365`
- `S_2648_pmppn_info_dict_V3.pickle`: `183266414` bytes, class `v3_pmpnn_info_pickle`, sha256 `efa7596832b9ef5aad692f1c818cd759b8c43ddd3a5266fcc9938d93527e4aab`
- `S_2648_pmppn_info_dict_V2.pickle`: `156651038` bytes, class `v2_pmpnn_info_pickle`, sha256 `78053a907ca988c5f4ef15c0b41198411d16c47bb2149bab3ec45b1abc4e7bac`
- `S_2648_full_feature_dict.pickle`: `91064165` bytes, class `full_feature_pickle`, sha256 `91a01e5a7c42dac77b0de522f7b38804ba1f41b7c504d21397cd249011248d11`
- `S_2648_pmppn_info_dict.pickle`: `89167705` bytes, class `base_pmpnn_info_pickle`, sha256 `deb329e5163a3a3ee20698bd72677d481b3ac50cfbf670db719054e9b1dd1f63`
- `ProteinMPNN/.git/objects/pack/pack-f26fd0719e65f4546fe57ec9a63caa4bc20239fe.pack`: `69459008` bytes, class `nested_proteinmpnn_git_history`, sha256 `9fef7ccf5c0996500e32523e92df594b4ca9be678e17a791f427eebca448f5fb`
- `S_921_pmppn_info_dict_V3.pickle`: `64760657` bytes, class `v3_pmpnn_info_pickle`, sha256 `5941620bb56f94056da126d6b544c7796cb5b961d9b358aebd70656419fb7daa`
- `S_921_pmppn_info_dict_V2.pickle`: `55304432` bytes, class `v2_pmpnn_info_pickle`, sha256 `71d8ba6e81eca4009a73aca458b96b49ad0138c844da4bb49b499ca2a2f2833f`
- `S_669_pmppn_info_dict_V3.pickle`: `45318104` bytes, class `v3_pmpnn_info_pickle`, sha256 `7ce92a517bfb0b6377eab82b884baec669a177d85a059afbc8fbc15ba7ef87f9`
- `S_669_pmppn_info_dict_V2.pickle`: `38853566` bytes, class `v2_pmpnn_info_pickle`, sha256 `ac63e63bc25e5bd571b2c995afd763f5300f141c05902693d617bfdd25c99f8d`
- `S_921_full_feature_dict.pickle`: `32278828` bytes, class `full_feature_pickle`, sha256 `c17247cb6c79b3557eec97d091e9ab8e335d328580a337f469fea6d162aea295`

## Dependency Map

- Dependency/reference rows written: `527`
- Referenced artifacts: `36`
- Reference states are intentionally simple: `active_or_text`, `commented`, and `note_or_generated_inventory`.

## Generated Tables

- `artifact_registry.tsv`
- `artifact_class_summary.tsv`
- `dependency_references.tsv`
- `proteinmpnn_checkpoint_usage.tsv`
- `nested_proteinmpnn_source_state.tsv`

## Storage Decision Rule

Promote artifacts by class, not by accident. For each class, decide whether it is:

- core reproducibility evidence that must be portable,
- lineage evidence useful for historical comparison,
- rerunnable/generated output,
- runtime residue that should stay untracked, or
- nested upstream source state that should be represented by commit/diff/archive rather than a nested `.git` directory.
