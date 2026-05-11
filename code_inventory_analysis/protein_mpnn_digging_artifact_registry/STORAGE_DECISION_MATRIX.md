# Protein_MPNN_Digging Storage Decision Matrix

Date: 2026-05-11

Scope: copied local evidence at
`drive_evidence_copy/sajidahmedprotres_drive/Protein_MPNN_Digging/`.

The decision here is class-level. Individual files can still be promoted later
when a manuscript-number or reproduction dependency requires them.

## Current Pinning Facts

- The copied nested ProteinMPNN checkout is at commit
  `c602ced6ad4b6997d89afa9432607ac9d0572539`.
- That nested checkout is dirty only at
  `vanilla_proteinmpnn/protein_mpnn_utils.py`.
- The current live canonical `dauparas/ProteinMPNN` HEAD checked on
  2026-05-11 is `8907e6671bfbfc92303b5f79c4b5e6ce47cdef57`.
  This is a time-stamped external check, not a stable historical input.
- Historical notebook evidence repeatedly sets `model_name = "v_48_020"` and
  loads it from `vanilla_model_weights`.
- The copied vanilla checkpoint selected by that code is
  `ProteinMPNN/vanilla_proteinmpnn/vanilla_model_weights/v_48_020.pt`, sha256
  `c9cb4a671d79604111231f8dbfc7c590e06f1197453b7a6854ac6661a642f5bd`.

## Decisions

| Artifact class | Decision | Reason |
|---|---|---|
| `v3_pmpnn_info_pickle` | Promote with Git LFS or an equivalent artifact store before this project depends on GitHub-only restoration. | These are the final V3 intermediate dictionaries used by manuscript-era RF notebooks and current recovery scripts. They are core reproduction evidence and too large/binary for regular Git. |
| `v2_pmpnn_info_pickle` | Keep local for now; promote with LFS only when lineage comparison or reproduction debugging requires them. | They explain schema evolution but are not yet the final target artifact. |
| `base_pmpnn_info_pickle` | Keep local for now; promote with LFS only when early-pipeline lineage is needed. | Useful historical evidence, but not currently the final V3 reproduction target. |
| `full_feature_pickle` | Keep local for now; promote with LFS if scalar-feature lineage or value-level comparisons require them. | They may validate saved-tensor-to-scalar-feature construction, but they are not the current upstream recovery target. |
| `trained_feature_combo_model_pickle` | Do not track in regular Git. Treat as high-value LFS candidates after direct manuscript-number dependency is verified. | Both large pickles deserialize as 63 `RandomForestRegressor` models saved from scikit-learn 1.0.2. They may be trained-model evidence, but direct table/figure dependence still needs to be proven. |
| `ml_result_summary_pickle` | Promote with LFS only when a result file is tied to a manuscript table/figure number. | These can be strong number-provenance evidence, but some may be rerunnable or superseded. |
| `proteinmpnn_checkpoint_weight` | Promote required checkpoints with LFS; at minimum, treat vanilla `v_48_020.pt` as required for historical tensor-extraction recovery. | The 2022 notebooks and recovered module point to vanilla `v_48_020.pt`; relying on current upstream weights is not acceptable for historical reproduction. |
| `nested_proteinmpnn_source_or_example` | Do not promote the whole nested checkout blindly. Promote a curated source snapshot or patch set centered on the dirty `protein_mpnn_utils.py` plus any required support files. | The nested checkout is source evidence, but committing an entire copied upstream tree without curation will pollute this workspace. |
| `nested_proteinmpnn_git_history` | Do not track the nested `.git` directory directly. Preserve by commit pin, diff, and possibly a Git bundle/archive if needed. | Nested Git metadata inside this repo is structurally unsafe and should not become normal workspace content. |
| `notebook_artifact` | Track normally if it contains historical code/provenance not already represented elsewhere. | Notebooks are evidence, but they should be tracked as source/provenance files, not as generated runtime output. |
| `binary_analysis_artifact` | Decide file-by-file; small stable evidence may be tracked, larger or generated binaries should use LFS or remain rerunnable. | Figure/spreadsheet artifacts need provenance context before promotion. |
| `small_text_or_source_artifact` | Track normally if it is evidence or maintained code; otherwise leave untracked. | Text/source artifacts are Git-suitable, but only if they have a clear role. |
| `runtime_cache` | Do not track. | Bytecode and cache files are rebuildable runtime residue. |
| `uncategorized_small_artifact` | Keep out of Git until assigned a role. | Small size is not enough to justify tracking. |

## Immediate Consequence

The next storage work should not be "track the whole directory." It should be:

1. Promote or package the exact vanilla `v_48_020.pt` checkpoint and the
   relevant ProteinMPNN source changes needed for tensor extraction.
2. Decide whether the four V3 pickles should be Git LFS objects now or kept as
   local copied evidence until the upstream reproduction path is stable.
3. Trace whether the two feature-combination model pickles are loaded by the
   manuscript-number-producing notebooks before promoting roughly 1.2 GB of
   trained-model artifacts.
