# Code Evidence Inventory: Initial Findings

Date: 2026-05-06

This note inventories the copied 2022 ProteinMPNN-DDG code evidence before any
manuscript-to-code cleanup or reproduction attempt. It is intentionally
evidence-first: the copied Drive evidence was read but not modified, old pickle
files were not unpickled, and notebooks were exported as source-only text with
outputs omitted.

## Scope

Primary code/evidence locations inspected:

- Old GitHub fork clone:
  `source_repos/SajidAhmeduiu_ProteinMPNN`
- Old fork additions:
  `source_repos/SajidAhmeduiu_ProteinMPNN/Sajid_Additions`
- Copied Drive evidence:
  `drive_evidence_copy/sajidahmedprotres_drive/Protein_MPNN_Digging`
- Nested Drive ProteinMPNN clone:
  `drive_evidence_copy/sajidahmedprotres_drive/Protein_MPNN_Digging/ProteinMPNN`
- Manuscript extraction used for feature/result definitions:
  `manuscript_inventory_analysis/extracted/docx_markdown_accept/SA_9_23_2022_CEM.md`

Generated inventory artifacts:

- `code_inventory_analysis/file_inventory.tsv`
- `code_inventory_analysis/notebook_inventory.tsv`
- `code_inventory_analysis/notebook_mentions.tsv`
- `code_inventory_analysis/notebook_feature_result_cells.tsv`
- `code_inventory_analysis/notebook_source_similarity.tsv`
- `code_inventory_analysis/source_repo_vs_drive_nested_repo.tsv`
- `code_inventory_analysis/drive_top_level_artifacts.tsv`
- `code_inventory_analysis/git_sajid_additions_file_history.tsv`
- `code_inventory_analysis/git_repo_states.tsv`
- `code_inventory_analysis/notebook_sources/`

Generator script:

- `tools/inventory_code_relationships.py`
- `MANUSCRIPT_TABLE_FIGURE_PROVENANCE_PLAN.md`

## High-Level Relationship Model

The current evidence splits into three layers:

1. `Sajid_Additions` in the old fork is the unique observed home of Sajid's
   custom notebooks. These notebooks are absent from the nested Drive
   `ProteinMPNN` clone.
2. The copied Drive `Protein_MPNN_Digging` root is primarily a generated-output
   cache: dataset-specific `*_pmppn_info_dict*.pickle`, `*_full_feature_dict`,
   feature-combination results/models, incremental feature results, and one
   feature-correlation PNG.
3. The nested Drive `ProteinMPNN` clone is mostly canonical upstream
   `dauparas/ProteinMPNN` at commit `c602ced`, with one dirty modified file:
   `vanilla_proteinmpnn/protein_mpnn_utils.py`.

This means the old fork and the Drive copy are complementary, not redundant:
the Git fork carries versioned notebook provenance; the Drive copy carries
large generated result artifacts and one dirty local upstream-code modification.

## Git Repo vs Drive Nested Repo

Tracked-file comparison between the old fork clone and the nested Drive
`ProteinMPNN` repo:

| Status | Count | Interpretation |
|---|---:|---|
| `same_hash` | 132 | Shared upstream files are byte-identical. |
| `source_only` | 20 | All are `Sajid_Additions/*.ipynb` notebooks. |
| `different_hash` | 1 | `vanilla_proteinmpnn/protein_mpnn_utils.py`. |

The source-only files are exactly these notebooks:

- `ProteinMPNNTesting.ipynb`
- `ProteinMPNNTesting_V2.ipynb`
- `ProteinMPNNTesting_V4.ipynb`
- `ProteinMPNNTesting_V5.ipynb`
- `ProteinMPNNTesting_V6.ipynb`
- `ProteinMPNNTesting_V6_V2.ipynb`
- `Quick_Dirty_MPNN_ML.ipynb`
- `Quick_Dirty_MPNN_ML_V2.ipynb`
- `Quick_Dirty_MPNN_ML_V2_V2.ipynb`
- `Quick_Dirty_MPNN_ML_V2_V3.ipynb`
- `Quick_Dirty_MPNN_ML_V2_V4.ipynb`
- `Quick_Dirty_MPNN_ML_V2_VGRAPHS_V1.ipynb`
- `S669_ProteinMPNNTesting_V3.ipynb`
- `S669_ProteinMPNNTesting_V6.ipynb`
- `S669_ProteinMPNNTesting_V6_V2.ipynb`
- `S921_ProteinMPNNTesting_V6_V2.ipynb`
- `Ssym_ProteinMPNNTesting_V3.ipynb`
- `Ssym_ProteinMPNNTesting_V6.ipynb`
- `Ssym_ProteinMPNNTesting_V6_V2.ipynb`
- `proteinmpnn_quickdemo.ipynb`

The one different tracked file is:

- `vanilla_proteinmpnn/protein_mpnn_utils.py`
  - source repo SHA256:
    `38d2c5e7f657b8c60ddc0650fab0f0cec417bddf7ae582ff0fb80a292904b09f`
  - Drive nested repo SHA256:
    `b197fe8ada3058e5543a289ec101eb99d4cf9e043cc9ab8e64e22fd5436ebbe1`
  - Drive nested diff stat: 159 insertions, 7 deletions.
  - The diff is mostly explanatory comments about `tied_featurize`, masks,
    chain handling, fixed/designable positions, and ProteinMPNN internals.
  - It also adds a `ProteinFeatures.return_neighbor_info(...)` stub that
    computes backbone atoms and `D_neighbors, E_idx = self._dist(Ca, mask)`
    but does not visibly return a result in the inspected diff.

Repo states:

| Repo | HEAD | Status | Remote |
|---|---|---|---|
| old fork clone | `121bef560acbf47ea98a47ba6fc08d35401cc17a` | clean | `https://github.com/SajidAhmeduiu/ProteinMPNN.git` |
| nested Drive clone | `c602ced6ad4b6997d89afa9432607ac9d0572539` | modified `vanilla_proteinmpnn/protein_mpnn_utils.py` | `https://github.com/dauparas/ProteinMPNN.git` |

## Notebook Families

The 20 old-fork notebooks separate into three functional families.

### Family 1: Early and General Feature Extraction

Representative files:

- `ProteinMPNNTesting.ipynb`
- `ProteinMPNNTesting_V2.ipynb`
- `ProteinMPNNTesting_V4.ipynb`
- `ProteinMPNNTesting_V5.ipynb`
- `ProteinMPNNTesting_V6.ipynb`
- `ProteinMPNNTesting_V6_V2.ipynb`

Likely role:

- Iterative extraction of ProteinMPNN-derived mutation features, mostly around
  `S_2648`, with later versions containing copied/modified ProteinMPNN class
  code directly inside notebooks.
- The V6/V6_V2 generation style appears to be the template later specialized
  to `S_921`, `S_669`, and `Ssym`.

Similarity evidence:

- `ProteinMPNNTesting_V6_V2.ipynb`, `S921_ProteinMPNNTesting_V6_V2.ipynb`,
  `S669_ProteinMPNNTesting_V6_V2.ipynb`, and
  `Ssym_ProteinMPNNTesting_V6_V2.ipynb` have near-identical source token
  sets, with containment around `0.994` to `0.997`.

### Family 2: Dataset-Specific V6_V2 Feature Extraction

These appear to be the main dataset-specific notebooks that generate
`*_pmppn_info_dict_V3.pickle` artifacts.

| Dataset | Notebook | Dataset source | Required PDB directory | Required PSSM directory | Saved artifact indicated in notebook |
|---|---|---|---|---|---|
| `S_2648` | `ProteinMPNNTesting_V6_V2.ipynb` | PremPS GitHub `Datasets/S2648/S2648.txt` | `/content/drive/MyDrive/ACCRE_PyRun_Setup/S_2648_PDB_Files` | `/content/drive/MyDrive/ACCRE_PyRun_Setup/S_2648_pssm_dir` | `S_2648_pmppn_info_dict_V3.pickle` |
| `S_921` | `S921_ProteinMPNNTesting_V6_V2.ipynb` | PremPS GitHub `Datasets/S921/S921.txt` | `/content/drive/MyDrive/ACCRE_PyRun_Setup/S_921_PDB_Files` | `/content/drive/MyDrive/ACCRE_PyRun_Setup/S_921_pssm_dir` | `S_921_pmppn_info_dict_V3.pickle` |
| `S_669` | `S669_ProteinMPNNTesting_V6_V2.ipynb` | `/content/drive/MyDrive/ACCRE_PyRun_Setup/Data_s669_with_predictions.csv` | `/content/drive/MyDrive/ACCRE_PyRun_Setup/S_669_PDB_Files` | `/content/drive/MyDrive/ACCRE_PyRun_Setup/S_669_pssm_dir` | `S_669_pmppn_info_dict_V3.pickle` |
| `Ssym` | `Ssym_ProteinMPNNTesting_V6_V2.ipynb` | PremPS GitHub `Datasets/Eight test sets/Ssym.txt` | `/content/drive/MyDrive/ACCRE_PyRun_Setup/Ssym_PDB_Files` | `/content/drive/MyDrive/ACCRE_PyRun_Setup/Ssym_pssm_dir` | `Ssym_pmppn_info_dict_V3.pickle` |

Important missing-evidence point:

- The `ACCRE_PyRun_Setup` folder, dataset PDB directories, PSSM directories,
  and `Data_s669_with_predictions.csv` were not found inside this workspace
  copy. The generated pickles are present, but the raw PDB/PSSM/CSV inputs
  needed to rerun feature extraction are not currently present here.

### Family 3: ML, Feature Assembly, Result Tables, and Figures

Representative files:

- `Quick_Dirty_MPNN_ML.ipynb`
- `Quick_Dirty_MPNN_ML_V2.ipynb`
- `Quick_Dirty_MPNN_ML_V2_V2.ipynb`
- `Quick_Dirty_MPNN_ML_V2_V3.ipynb`
- `Quick_Dirty_MPNN_ML_V2_V4.ipynb`
- `Quick_Dirty_MPNN_ML_V2_VGRAPHS_V1.ipynb`

Likely role:

- Assemble feature matrices from generated pickles.
- Test feature correlations and feature-combination models.
- Train RF models on `S_2648`.
- Evaluate on `S_921`, `S_669`, and `Ssym`.
- Generate incremental A-to-H feature contribution results and likely figure
  and table values.

Evolution:

- `Quick_Dirty_MPNN_ML.ipynb` and `Quick_Dirty_MPNN_ML_V2.ipynb` are older
  feature-combination scripts based on `*_full_feature_dict.pickle`.
- `Quick_Dirty_MPNN_ML_V2_V3.ipynb`,
  `Quick_Dirty_MPNN_ML_V2_V4.ipynb`, and
  `Quick_Dirty_MPNN_ML_V2_VGRAPHS_V1.ipynb` use
  `*_pmppn_info_dict_V3.pickle` and the final A-H feature-map machinery.
- `Quick_Dirty_MPNN_ML_V2_V3.ipynb` and
  `Quick_Dirty_MPNN_ML_V2_VGRAPHS_V1.ipynb` are very similar
  (`jaccard = 0.9665`, `containment_smaller = 0.9873`), so the `VGRAPHS`
  notebook is likely the graph/final-results evolution rather than an
  unrelated branch.

## Drive Top-Level Artifact Timeline

Top-level generated artifacts in the copied Drive `Protein_MPNN_Digging` root:

| Date | Artifact pattern | Role |
|---|---|---|
| 2022-08-05 | `res_dict.pickle` | Early result dictionary. |
| 2022-08-11 | `dat.xlsx` | Spreadsheet data. |
| 2022-08-15 to 2022-08-16 | `*_pmppn_info_dict.pickle` | First dataset-specific ProteinMPNN intermediate info dicts. |
| 2022-08-16 | `*_full_feature_dict.pickle` | First assembled feature dictionaries. |
| 2022-08-18 | `feature_combo_*`, `S_669_feature_combo_*` | Feature-combination models and summaries. |
| 2022-08-25 | `*_pmppn_info_dict_V2.pickle` | V2 ProteinMPNN intermediate info dicts. |
| 2022-08-30 | `*_pmppn_info_dict_V3.pickle` | V3 ProteinMPNN intermediate info dicts used by later ML notebooks. |
| 2022-09-01 | `incremental_feature_result_dict.pickle` | Incremental feature result summary. |
| 2022-09-12 | `list_incremental_feature_result_dict.pickle` | Ten-iteration incremental feature result summary. |
| 2022-09-15 | `Feature-Feature_Correlation.png` | Feature-correlation figure output. |

Key interpretation:

- The Drive artifacts are temporally consistent with the notebook history:
  feature extraction outputs appear in mid/late August 2022, followed by
  feature-combination and incremental result artifacts in late August and
  September.
- The `*_pmppn_info_dict_V3.pickle` artifacts look like the most important
  inputs for the final ML notebook family.

## Manuscript to Code: Current Mapping

The manuscript describes PMPNN-DDG as a feature extractor plus RF predictor:

- Feature A: mutation-position probability / one-body energy change.
- Feature B: neighbor entropy-change summation.
- Feature C: center-to-neighbor message norm-ratio summation.
- Feature D: neighbor embedding-change norm summation.
- Feature E: five-dimensional RBF-kernel PCA projection of center-to-neighbor
  message-change vectors.
- Feature F: PSSM wildtype minus mutant value.
- Feature G: wildtype PSSM value.
- Feature H: mutant PSSM value.
- Main result pattern: train RF on `S_2648`, add A through H incrementally,
  average over 10 RF runs, evaluate on `S_921`, `S_669`, and `Ssym`.

The strongest code candidate for this final pipeline is:

- `Quick_Dirty_MPNN_ML_V2_VGRAPHS_V1.ipynb`

Evidence:

- Loads `S_2648_pmppn_info_dict_V3.pickle`,
  `S_921_pmppn_info_dict_V3.pickle`,
  `S_669_pmppn_info_dict_V3.pickle`, and
  `Ssym_pmppn_info_dict_V3.pickle`.
- Defines `list_dataset_names = ["S_2648","S_921","S_669","Ssym"]`.
- Builds final feature map:
  - `A -> 0`
  - `B -> 6`
  - `C -> 7`
  - `D -> 8`
  - `E -> [31,32,33,34,35]`
  - `F -> 5`
  - `G -> 9`
  - `H -> 10`
- Uses RF with `min_samples_split=2`, `n_estimators=500`,
  `max_samples=0.5`, `max_features="sqrt"`.
- Runs `n_iterations = 10`.
- Builds incremental feature combinations:
  `A`, `A+B`, `A+B+C`, ..., `A+B+C+D+E+F+G+H`.
- Tracks total/direct/reverse PCC and RMSE for `S_2648`, `S_921`, `S_669`,
  and `Ssym`.
- Saves or reloads `list_incremental_feature_result_dict.pickle`.

## Resolved Reconciliation Issue: Feature E

The initial high-priority concern about feature E has been resolved by tracing
the post-KPCA augmentation logic.

The manuscript says feature E is the five-dimensional RBF-kernel PCA projection
of center-to-neighbor message-change vectors. The final ML notebook maps:

- `E -> [31,32,33,34,35]`

Those indices are applied to the post-augmentation `S_*_X_aug` matrices, not to
the pre-augmentation 75-column `S_*_X` matrices. In the pre-augmentation layout,
columns `31..40` are reverse-oriented neighbor-embedding KPCA features. After
the notebook compacts direct and synthetic reverse-mutant rows into `S_*_X_aug`,
columns `31..40` are message-change KPCA features. Therefore `E -> 31..35`
matches the manuscript feature family at the current evidence level.

The detailed equation-to-code mapping is recorded in:

- `FEATURE_EQUATION_CODE_MAPPING_INITIAL.md`

Remaining caution:

- Feature B is not just an unweighted neighbor entropy-change sum in the final
  code. It is `V2_backward_weighted_neighbor_entropy_changes`, which weights
  entropy changes by a center-to-neighbor message norm-ratio term. This must be
  revisited after the manuscript table/figure numbers are traced to exact
  notebook outputs or result artifacts.
- The notebook has at least one stale copy-paste comment: the extension around
  pre-augmentation columns `61..70` says "neighbor_kpca_features", but the
  variables being extended there are reverse message-KPCA variables.

## What Is Reproducible From Current Evidence

Currently plausible without searching other locations:

- Reconstruct the notebook-level provenance and timeline.
- Reconstruct which notebooks correspond to feature extraction vs ML/results.
- Reconstruct which generated pickles/results exist and when they were
  modified.
- Reconstruct much of the final A-H ML evaluation logic from source exports.
- Inspect small result pickles later in a controlled way, if needed.

Not yet reproducible from current evidence alone:

- Full feature extraction from raw datasets, because PDB directories, PSSM
  directories, and `Data_s669_with_predictions.csv` are missing from this
  workspace copy.
- Exact Figure 6/Table 1/Table 2/Table 3 values without controlled inspection
  of result pickles or notebook output history.
- Exact manuscript wording cleanup, especially for feature B's message-ratio
  weighting and feature E's "10 KPCA components fit, first five used" detail.
- Clean runnable tools or notebooks, because the observed notebooks are still
  Colab/path-specific and heavily stateful.

## Missing Evidence Watchlist

Search next, if needed:

- `ACCRE_PyRun_Setup/`
- `Data_s669_with_predictions.csv`
- `S_2648_PDB_Files/`
- `S_921_PDB_Files/`
- `S_669_PDB_Files/`
- `Ssym_PDB_Files/`
- `S_2648_pssm_dir/`
- `S_921_pssm_dir/`
- `S_669_pssm_dir/`
- `Ssym_pssm_dir/`
- Any Colab runtime folders named `Colab_Installations_V2`
- Any old manuscript figure/table output notebooks containing executed outputs

## Recommended Next Phase

Before touching or cleaning the codebase, the next phase should be a controlled
mapping pass:

1. Build a manuscript claim-to-code matrix:
   - Figure 2/3/4/5/6
   - Table 1/2/3
   - Feature A-H definitions
   - Dataset definitions and splits
2. Safely inspect only small or necessary pickle artifacts first:
   - `feature_combo_result_dict.pickle`
   - `S_669_feature_combo_result_dict.pickle`
   - `incremental_feature_result_dict.pickle`
   - `list_incremental_feature_result_dict.pickle`
3. Avoid unpickling large model artifacts until there is a sandboxed plan.
4. Use `FEATURE_EQUATION_CODE_MAPPING_INITIAL.md` as the entry point for the
   now-resolved feature E index question.
5. Search for missing `ACCRE_PyRun_Setup` evidence only after this mapping is
   explicit, so any found files can be classified instead of dumped into the
   workspace blindly.
