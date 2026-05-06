# Colab Notebooks Deep Inventory

Date of this inventory pass: 2026-05-06

This note inventories the copied 2022 Google Drive folder:

`/home/mpr/sajidahmedprotres_drive/Colab Notebooks`

The source mount was treated as read-only. The folder was copied into this
workspace with preserved modification times:

`drive_evidence_copy/sajidahmedprotres_drive/Colab Notebooks/`

The generated inventory artifacts are under:

`colab_notebooks_inventory_analysis/`

The inventory script is:

`tools/inventory_colab_notebooks.py`

The script reads notebook JSON, source text, notebook output metadata, and text
outputs. It does not execute notebooks and does not unpickle old result
artifacts.

## Copy and Analysis Status

- Source mount check showed `/home/mpr/sajidahmedprotres_drive` mounted as
  `fuse.rclone` and read-only.
- The Colab notebook folder was copied with `rsync -a --human-readable
  --itemize-changes`, preserving file modification times.
- Source and copied relative manifests match by path, size, and modification
  time.
- A verify dry-run after copy produced no itemized file differences.
- The copied Colab folder contains 32 files, all parseable as notebook JSON by
  the inventory script.

Important limitation: filesystem mtimes in `source_repos/` reflect the current
clone, not 2022 history. For Git notebooks, use `git log --follow`, not local
file mtime.

## Generated Tables

Colab-side tables:

- `colab_notebook_inventory.tsv`
- `colab_notebook_cell_index.tsv`
- `colab_notebook_output_cells.tsv`
- `colab_notebook_feature_result_cells.tsv`
- `colab_notebook_mentions.tsv`
- `colab_artifact_mentions_by_cell.tsv`
- `protein_mpnn_digging_artifact_to_colab_candidates.tsv`
- `colab_notebook_internal_similarity.tsv`
- `colab_vs_git_notebooks_by_filename.tsv`
- `colab_vs_git_notebook_similarity.tsv`

Git-side tables added in this pass:

- `git_notebook_inventory.tsv`
- `git_notebook_cell_index.tsv`
- `git_notebook_output_cells.tsv`
- `git_notebook_feature_result_cells.tsv`
- `git_notebook_mentions.tsv`
- `git_artifact_mentions_by_cell.tsv`
- `protein_mpnn_digging_artifact_to_git_candidates.tsv`

Notebook source exports:

- `colab_notebooks_inventory_analysis/notebook_sources/*.py.txt`
- `colab_notebooks_inventory_analysis/git_notebook_sources/*.py.txt`

Notebook output text exports:

- `colab_notebooks_inventory_analysis/notebook_outputs/*.outputs.txt`
- `colab_notebooks_inventory_analysis/git_notebook_outputs/*.outputs.txt`

The source exports are cell-source reconstructions only. The output exports
include text output and image-output summaries; image payloads are summarized,
not embedded.

## Corpus Structure

The copied Drive `Colab Notebooks` folder is not just a duplicate of the Git
repo. It is a mixed record of:

- July 2022 setup, PROVEAN, FASTA, and PyRun notebooks.
- Early August 2022 ProteinMPNN probing notebooks.
- Mid/Late August 2022 dataset-specific feature extraction notebooks.
- Late August to October 2022 ML, feature-combination, and figure notebooks.
- Small later exploratory notebooks from late October/November 2022.

High-value Colab notebooks:

| Notebook | Why it matters |
|---|---|
| `ProteinMPNNTesting_V6_V2.ipynb` | Drive version for S_2648 V2-era feature extraction. |
| `ProteinMPNNTesting_V6_V2_debug.ipynb` | Colab-only debug branch with output-rich feature-extraction evidence. |
| `S669_ProteinMPNNTesting_V6_V2.ipynb` | Drive version for S_669 feature extraction. |
| `Ssym_ProteinMPNNTesting_V6_V2.ipynb` | Drive version for Ssym feature extraction. |
| `Quick_Dirty_MPNN_ML_V2_V2.ipynb` | V2 feature/ML transition notebook. |
| `Quick_Dirty_MPNN_ML_V2_V3.ipynb` | Output-rich V3 ML notebook using V3 pickles and final A-H feature map. |
| `Quick_Dirty_MPNN_ML_V2_VGRAPHS_V1.ipynb` | Colab-side graph notebook, very close to V2_V3 but graph-focused. |

High-value Git-only or Git-divergent notebooks:

| Notebook | Why it matters |
|---|---|
| `Sajid_Additions/S921_ProteinMPNNTesting_V6_V2.ipynb` | Git-only S_921 V6_V2 feature extraction notebook. Missing from Drive Colab folder. |
| `Sajid_Additions/Quick_Dirty_MPNN_ML_V2_V4.ipynb` | Git-only ML notebook from commit `cc993ad` (`Manuscript previous`). |
| `Sajid_Additions/Quick_Dirty_MPNN_ML_V2_VGRAPHS_V1.ipynb` | Git manuscript-facing/local-run graph notebook, updated in commit `121bef5` (`Local Run Updated Copy`). |

## Colab to Git Relationship

The filename comparison table shows three categories:

1. Same source/code despite different notebook metadata:
   - `ProteinMPNNTesting.ipynb`
   - `ProteinMPNNTesting_V2.ipynb`
   - `ProteinMPNNTesting_V4.ipynb`
   - `ProteinMPNNTesting_V5.ipynb`
   - `Quick_Dirty_MPNN_ML.ipynb`
   - `Quick_Dirty_MPNN_ML_V2_V2.ipynb`
   - `S669_ProteinMPNNTesting_V3.ipynb`
   - `Ssym_ProteinMPNNTesting_V3.ipynb`
   - `Ssym_ProteinMPNNTesting_V6.ipynb`
   - `proteinmpnn_quickdemo.ipynb`

2. Same filename but source/code differs:
   - `ProteinMPNNTesting_V6.ipynb`
   - `ProteinMPNNTesting_V6_V2.ipynb`
   - `Quick_Dirty_MPNN_ML_V2.ipynb`
   - `Quick_Dirty_MPNN_ML_V2_V3.ipynb`
   - `Quick_Dirty_MPNN_ML_V2_VGRAPHS_V1.ipynb`
   - `S669_ProteinMPNNTesting_V6.ipynb`
   - `S669_ProteinMPNNTesting_V6_V2.ipynb`
   - `Ssym_ProteinMPNNTesting_V6_V2.ipynb`

3. Important one-sided files:
   - Colab-only: `ProteinMPNNTesting_V3.ipynb`,
     `ProteinMPNNTesting_V6_V2_debug.ipynb`, `ProteinMPNNTesting_V7.ipynb`,
     `PROVEAN_VAR_creation.ipynb`, `Preparing_Fasta_Files_For_PROVEAN.ipynb`,
     and `PyRun_Notebook_V16*`.
   - Git-only: `Quick_Dirty_MPNN_ML_V2_V4.ipynb` and
     `S921_ProteinMPNNTesting_V6_V2.ipynb`.

The Git `Quick_Dirty_MPNN_ML_V2_VGRAPHS_V1.ipynb` differs from the Colab copy
in a manuscript-relevant way: it uses local `/home/ahmes10/...` paths instead
of Google Drive paths, has 44 code cells instead of 42, inserts an additional
feature-correlation heatmap cell, and uses graph styling closer to a local
manuscript run.

## Git Commit Provenance for Key Notebooks

`Quick_Dirty_MPNN_ML_V2_VGRAPHS_V1.ipynb`:

| Commit | Date | Author email | Subject |
|---|---|---|---|
| `121bef5` | 2022-10-25T14:20:44-05:00 | `sahmed133002@bscse.uiu.ac.bd` | `Local Run Updated Copy` |
| `cc993ad` | 2022-10-25T14:11:45-05:00 | `sahmed133002@bscse.uiu.ac.bd` | `Manuscript previous` |
| `8891ef5` | 2022-09-23T20:00:27-05:00 | `sahmed133002@bscse.uiu.ac.bd` | `Final Figures on 23_9_2022` |
| `670d024` | 2022-08-31T21:50:20-05:00 | `sahmed133002@bscse.uiu.ac.bd` | `Progress Pushing` |

`Quick_Dirty_MPNN_ML_V2_V3.ipynb`:

| Commit | Date | Author email | Subject |
|---|---|---|---|
| `8891ef5` | 2022-09-23T20:00:27-05:00 | `sahmed133002@bscse.uiu.ac.bd` | `Final Figures on 23_9_2022` |
| `670d024` | 2022-08-31T21:50:20-05:00 | `sahmed133002@bscse.uiu.ac.bd` | `Progress Pushing` |

Dataset-specific V6_V2 notebooks:

- `ProteinMPNNTesting_V6_V2.ipynb`, `S669_ProteinMPNNTesting_V6_V2.ipynb`,
  `Ssym_ProteinMPNNTesting_V6_V2.ipynb`, and
  `S921_ProteinMPNNTesting_V6_V2.ipynb` all have relevant history through
  `7db74de` on 2022-08-30T21:13:07-05:00, subject `Huge Stuff Added For
  Feature Generation, and Classification`.
- The S_2648 file has additional earlier commits down to 2022-08-09.
- The S_921 V6_V2 notebook is Git-only in the current evidence set; no same
  filename exists in the copied Drive Colab folder.

## Protein_MPNN_Digging Artifact Linkage

The copied `Protein_MPNN_Digging` folder contains 25 top-level files. The key
V3 pickles have preserved mtimes:

| Artifact | Size | Preserved mtime |
|---|---:|---|
| `S_2648_pmppn_info_dict_V3.pickle` | 183,266,414 | 2022-08-30 20:09:55.762 |
| `S_921_pmppn_info_dict_V3.pickle` | 64,760,657 | 2022-08-30 20:42:04.484 |
| `Ssym_pmppn_info_dict_V3.pickle` | 24,447,664 | 2022-08-30 21:19:29.919 |
| `S_669_pmppn_info_dict_V3.pickle` | 45,318,104 | 2022-08-30 21:35:10.589 |

The corrected artifact-candidate tables distinguish active lines from
commented-out lines. This distinction matters.

Colab-side evidence:

- The copied Colab ML notebooks actively consume all four V3 pickles in
  `Quick_Dirty_MPNN_ML_V2_V3.ipynb:cell4` and
  `Quick_Dirty_MPNN_ML_V2_VGRAPHS_V1.ipynb:cell4`.
- No active Colab-side producer for any V3 pickle was found.

Git-side evidence:

- Git ML notebooks actively consume all four V3 pickles in:
  - `Quick_Dirty_MPNN_ML_V2_V3.ipynb:cell4`
  - `Quick_Dirty_MPNN_ML_V2_V4.ipynb:cell4`
  - `Quick_Dirty_MPNN_ML_V2_VGRAPHS_V1.ipynb:cell5`
- Git dataset-specific V6_V2 notebooks contain the exact intended V3 save
  cells, but the save cells are commented in the saved source:
  - `ProteinMPNNTesting_V6_V2.ipynb:cell16` for
    `S_2648_pmppn_info_dict_V3.pickle`
  - `S921_ProteinMPNNTesting_V6_V2.ipynb:cell16` for
    `S_921_pmppn_info_dict_V3.pickle`
  - `S669_ProteinMPNNTesting_V6_V2.ipynb:cell16` for
    `S_669_pmppn_info_dict_V3.pickle`
  - `Ssym_ProteinMPNNTesting_V6_V2.ipynb:cell16` for
    `Ssym_pmppn_info_dict_V3.pickle`

Interpretation: the V3 pickle names, preserved mtimes, and downstream active
loads strongly point to the dataset-specific V6_V2 notebooks as the generation
lineage. But because the save cells are commented in the saved notebook source,
this is not yet a 100% active-source proof of the actual file writes.

## Feature Extraction Code Evidence

The Git dataset-specific V6_V2 notebooks contain the most relevant feature
extraction code for the final V3 pickles.

For S_2648, the source export shows active assignment of the final raw and
summary mutation features in:

`colab_notebooks_inventory_analysis/git_notebook_sources/ProteinMPNNTesting_V6_V2.ipynb.py.txt`

Relevant code region: around lines 2120-2159.

This active code assigns, among other fields:

- `mut["center_mut_wild_energy"]`
- `mut["center_entropy"]`
- `mut["V2_backward_weighted_neighbor_energy_changes"]`
- `mut["weighted_neighbor_forward_KL"]`
- `mut["V2_backward_weighted_neighbor_backward_KL"]`
- `mut["V2_backward_weighted_neighbor_entropy_changes"]`
- `mut["center_neighbor_weight_check_w_m"]`
- `mut["neighbor_embedding_change_m_w"]`
- `mut["neighbor_embedding_change_m_w_raw"]`
- `mut["neighbor_message_change_m_w_raw"]`
- `mut["neighbor_message_change_m_w"]`
- `mut["unweighted_backward_KL"]`
- `mut["unweighted_forward_KL"]`

The same active feature-assignment pattern is present in the Git S_669, S_921,
and Ssym V6_V2 notebooks. This is the strongest current code evidence for the
contents expected inside V3 `pmppn_info_dict` pickles.

Important nuance:

- The notebooks have preserved outputs for later analysis cells.
- The heavy feature-extraction loop cell itself has no saved stream output in
  the Git copies for cell 15, so the notebook does not prove the full loop ran
  during the saved session.
- The downstream V3 artifacts exist with Aug 30, 2022 mtimes and are actively
  loaded by the ML notebooks.

## ML Feature Matrix and Manuscript Feature Labels

The strongest current A-H feature map evidence is in:

`colab_notebooks_inventory_analysis/notebook_sources/Quick_Dirty_MPNN_ML_V2_V3.ipynb.py.txt`

and in the Git-local graph version:

`colab_notebooks_inventory_analysis/git_notebook_sources/Quick_Dirty_MPNN_ML_V2_VGRAPHS_V1.ipynb.py.txt`

Both use the V3 pickles and build the augmented matrix.

Key source facts:

- All four V3 pickles are loaded.
- Dataset order is `S_2648`, `S_921`, `S_669`, `Ssym`.
- Base per-mutation features occupy initial columns.
- Raw neighbor-embedding and message-change arrays are appended for PCA/KPCA.
- The augmented matrix `S_*_X_aug` has 41 final columns.
- The final manuscript-facing feature map is:

| Manuscript label | Final augmented matrix index |
|---|---|
| A | `0` |
| B | `6` |
| C | `7` |
| D | `8` |
| E | `[31, 32, 33, 34, 35]` |
| F | `5` |
| G | `9` |
| H | `10` |

This resolves the earlier E-feature confusion at the final model level:

- In the pre-augmentation 75-column matrix, columns `31..40` refer to reverse
  neighbor KPCA.
- In the final 41-column augmented matrix used by the A-H map, `E = 31..35`
  refers to message-change RBF-KPCA.

## Feature B Caution

Feature B remains a manuscript-methods caution.

In the final feature map, B is column `6` of `S_*_X_aug`.

In source construction, column `6` comes from:

`mut["V2_backward_weighted_neighbor_entropy_changes"]`

The feature-extraction code computes this as a top-neighbor entropy-change
quantity weighted by a sigmoid transform of the center-to-neighbor message norm
ratio/change signal. It is not merely an unweighted neighbor entropy-change
sum.

This is already important enough to preserve for manuscript cleanup. It should
not be changed in manuscript text until the table/figure outputs are fully
matched, but the current code evidence says the methods text needs to describe
the weighting.

## Figure and Table Evidence

### Feature-Feature Correlation

The copied `Protein_MPNN_Digging/Feature-Feature_Correlation.png` exists and
has preserved mtime 2022-09-15 22:14:15.873. It is a 1200 x 800 PNG, but visual
inspection shows it is blank.

This matches the notebook source pattern: the figure cells call `plt.show()`
before `plt.savefig("Feature-Feature_Correlation.png", dpi=dpi_loc)`. The
saved PNG is therefore not reliable figure evidence.

The usable evidence is the notebook output, not the standalone PNG file:

- Git `Quick_Dirty_MPNN_ML_V2_VGRAPHS_V1.ipynb` output has the A-H correlation
  matrix in cell 26.
- Colab `Quick_Dirty_MPNN_ML_V2_V3.ipynb` and Colab
  `Quick_Dirty_MPNN_ML_V2_VGRAPHS_V1.ipynb` also preserve the corresponding
  output image/text evidence.

Key DDG-row values from Git `Quick_Dirty_MPNN_ML_V2_VGRAPHS_V1.ipynb` output:

| Feature | DDG correlation |
|---|---:|
| A | 0.506653 |
| B | 0.291537 |
| C | -0.150304 |
| D | 0.308701 |
| E-1 | 0.071515 |
| E-2 | 0.342572 |
| E-3 | 0.255719 |
| E-4 | 0.201329 |
| E-5 | -0.006065 |
| F | 0.275204 |
| G | 0.176183 |
| H | -0.255264 |

### Final Random-Forest Table-Like Values

Git `Quick_Dirty_MPNN_ML_V2_VGRAPHS_V1.ipynb` is the strongest current
manuscript-facing source for the final rounded performance table because it
contains the local-run path setup, the final A-H feature map, and explicit
rounded print output.

In its output cell 35, the printed values are:

| Dataset | Direct PCC | Reverse PCC | Total PCC | Direct RMSE | Reverse RMSE | Total RMSE |
|---|---:|---:|---:|---:|---:|---:|
| S_669 | 0.48 | 0.48 | 0.64 | 1.45 | 1.45 | 1.45 |
| Ssym | 0.72 | 0.72 | 0.81 | 1.1 | 1.1 | 1.1 |
| S_921 | 0.77 | 0.77 | 0.79 | 1.49 | 1.49 | 1.49 |

Unrounded nearby output from the same notebook includes:

- S_921 total/direct/reverse PCC:
  0.794812394160082, 0.7676490111897645, 0.7664592926227518
- S_669 total/direct/reverse PCC:
  0.6446850135590241, 0.4828833365844248, 0.4786043879501776
- Ssym total/direct/reverse PCC:
  0.8109171834749661, 0.7207685171384137, 0.7155704942190042
- S_921 total/direct/reverse RMSE:
  1.490922463194474, 1.4923570338701817, 1.489486510839876
- S_669 total/direct/reverse RMSE:
  1.4512746723236831, 1.4531230545935272, 1.4494239329006553
- Ssym total/direct/reverse RMSE:
  1.1026531137656468, 1.10551441755194, 1.099784365764011

This is close to a number-level manuscript map, but the manuscript table itself
still needs to be compared directly against these exact rounded and unrounded
outputs.

### Incremental Feature Result Pickles

The small result pickles:

- `incremental_feature_result_dict.pickle`
- `list_incremental_feature_result_dict.pickle`

are referenced in Colab and Git notebooks, but the saved source lines are
commented. The notebook outputs show the in-memory results, so the values were
computed in the notebook session even if the saved source currently does not
show active pickle writing/loading.

Do not use these pickle references as active I/O proof until the pickles are
safely inspected or the original notebook cell state is reconstructed.

## Current Evidence Strengths

Strong evidence:

- The Drive Colab notebook copy is faithful by relative path, size, and mtime.
- The Colab folder contains output-rich ML notebooks that actively load V3
  pickles and preserve final feature/result outputs.
- The Git repo contains additional manuscript-facing notebooks not present in
  the Drive Colab folder.
- Git `Quick_Dirty_MPNN_ML_V2_VGRAPHS_V1.ipynb` is currently the strongest
  manuscript-facing notebook for final rounded table values.
- Feature E in the final A-H model is message-change RBF-KPCA over final
  augmented columns 31..35.
- Feature B is weighted neighbor entropy change, not a plain unweighted sum.

Moderate evidence:

- The dataset-specific Git V6_V2 notebooks contain the active code that creates
  the feature fields expected in V3 pickles.
- The V3 save cells in those notebooks name the exact V3 pickle files, but the
  save lines are commented in the saved source.
- The V3 pickle mtimes are all on 2022-08-30 and align with the Git commit that
  introduced the final feature-generation/classification push.

Weak or unresolved evidence:

- There is not yet active-source proof of the exact V3 pickle writes.
- The standalone `Feature-Feature_Correlation.png` is blank and should not be
  treated as a final figure artifact.
- Some notebook output values may come from in-memory state rather than from
  active source cells as currently saved.
- `Quick_Dirty_MPNN_ML_V2_V4.ipynb` has useful outputs but also at least one
  saved error output, so it needs careful cell-by-cell treatment before being
  used as manuscript proof.

## Next Evidence Tasks

1. Compare manuscript tables directly against Git
   `Quick_Dirty_MPNN_ML_V2_VGRAPHS_V1.ipynb` outputs, especially output cell
   35 and the unrounded RF output block.
2. Extract embedded image outputs from the relevant notebooks into an analysis
   folder, preserving notebook/cell provenance, because the standalone
   `Feature-Feature_Correlation.png` is blank.
3. Safely inspect small result pickles first, especially
   `list_incremental_feature_result_dict.pickle`, using a restricted or
   controlled read path. Do not casually unpickle large legacy artifacts.
4. Find stronger active-write evidence for the V3 `pmppn_info_dict` pickles:
   possible locations include old runtime logs, older notebook revisions,
   hidden Drive copies, Colab checkpoints, or ACCRE/local run residues.
5. Build a table mapping each manuscript figure/table to:
   source notebook, cell number, source hash, output hash/text, and artifact
   file if any.

