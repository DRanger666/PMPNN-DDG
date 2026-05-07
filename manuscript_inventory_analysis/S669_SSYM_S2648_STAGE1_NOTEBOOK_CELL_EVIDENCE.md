# Stage 1 Notebook-Cell Evidence for S_669, Ssym, and S_2648

Stage 1 means: identify the notebook cell/output that emitted the manuscript
number or manuscript figure artifact. It does not yet prove the full upstream
pickle/code/dataset provenance.

## S_669

Manuscript values:

- Table 1 row: `S_669 | 0.48 | 0.48 | 0.64 | -0.99 | 1.45 | 1.45 | 1.45`
  in `SA_CEM_9_26_2022_MJ_Issue_Adressing.txt:159-166`.
- Table 2 PMPNN-DDG row repeats the same values in
  `SA_CEM_9_26_2022_MJ_Issue_Adressing.txt:290-297`.

Notebook-cell evidence:

- `Quick_Dirty_MPNN_ML_V2_VGRAPHS_V1.ipynb`, cell 35, emits the six non-`rF-R`
  values for S_669: `0.48, 0.48, 0.64, 1.45, 1.45, 1.45`.
  Evidence:
  `colab_notebooks_inventory_analysis/git_notebook_outputs/Quick_Dirty_MPNN_ML_V2_VGRAPHS_V1.ipynb.outputs.txt:5111-5120`.
- `Quick_Dirty_MPNN_ML_V2_V3.ipynb`, cell 31, emits the forward-vs-reverse
  PCC sequence. The second output is S_669: `-0.9939184352208846`, which rounds
  to `-0.99`.
  Evidence:
  `colab_notebooks_inventory_analysis/git_notebook_outputs/Quick_Dirty_MPNN_ML_V2_V3.ipynb.outputs.txt:565-570`.
  The visible source comments give the dataset order:
  S_921, S_669, Ssym.
  Evidence:
  `colab_notebooks_inventory_analysis/git_notebook_sources/Quick_Dirty_MPNN_ML_V2_V3.ipynb.py.txt:1064-1068`.

Status: stage 1 is satisfied for the PMPNN-DDG S_669 table row.

## Ssym

Manuscript values:

- Table 1 row: `Ssym | 0.72 | 0.72 | 0.81 | -0.99 | 1.10 | 1.10 | 1.10`
  in `SA_CEM_9_26_2022_MJ_Issue_Adressing.txt:167-174`.
- Table 3 PMPNN-DDG row repeats the same values in
  `SA_CEM_9_26_2022_MJ_Issue_Adressing.txt:350-357`.

Notebook-cell evidence:

- `Quick_Dirty_MPNN_ML_V2_VGRAPHS_V1.ipynb`, cell 35, emits the six non-`rF-R`
  values for Ssym: `0.72, 0.72, 0.81, 1.1, 1.1, 1.1`.
  Evidence:
  `colab_notebooks_inventory_analysis/git_notebook_outputs/Quick_Dirty_MPNN_ML_V2_VGRAPHS_V1.ipynb.outputs.txt:5111-5127`.
- `Quick_Dirty_MPNN_ML_V2_V3.ipynb`, cell 31, emits the forward-vs-reverse
  PCC sequence. The third output is Ssym: `-0.9946606797887094`, which rounds
  to `-0.99`.
  Evidence:
  `colab_notebooks_inventory_analysis/git_notebook_outputs/Quick_Dirty_MPNN_ML_V2_V3.ipynb.outputs.txt:565-570`.
  The visible source comments give the dataset order:
  S_921, S_669, Ssym.
  Evidence:
  `colab_notebooks_inventory_analysis/git_notebook_sources/Quick_Dirty_MPNN_ML_V2_V3.ipynb.py.txt:1064-1068`.

Status: stage 1 is satisfied for the PMPNN-DDG Ssym table row.

## S_2648

S_2648 is different from S_669 and Ssym in the manuscript. It is the training
set for feature analysis and RF training, not a Table 1 independent-test row.
Stage 1 therefore maps S_2648 manuscript figure/text claims rather than a single
performance table row.

### Figure 3

Manuscript claim:

- Figure 3 compares Norm-Ratio and Change-Norm encodings for features C and D
  on S_2648 training instances.
  Evidence:
  `SA_CEM_9_26_2022_MJ_Issue_Adressing.txt:62-75`.

Notebook-cell evidence:

- `Quick_Dirty_MPNN_ML_V2_VGRAPHS_V1.ipynb`, cell 15, prints `0.26 0.31` and
  emits a single-axis bar figure.
  Evidence:
  `colab_notebooks_inventory_analysis/git_notebook_outputs/Quick_Dirty_MPNN_ML_V2_VGRAPHS_V1.ipynb.outputs.txt:4601-4611`.
- `Quick_Dirty_MPNN_ML_V2_VGRAPHS_V1.ipynb`, cell 16, prints `0.15 0.03` and
  emits a single-axis bar figure.
  Evidence:
  `colab_notebooks_inventory_analysis/git_notebook_outputs/Quick_Dirty_MPNN_ML_V2_VGRAPHS_V1.ipynb.outputs.txt:4613-4623`.
- `Quick_Dirty_MPNN_ML_V2_VGRAPHS_V1.ipynb`, cell 17, emits the combined
  two-axis Figure 3-style artifact.
  Evidence:
  `colab_notebooks_inventory_analysis/git_notebook_outputs/Quick_Dirty_MPNN_ML_V2_VGRAPHS_V1.ipynb.outputs.txt:4625-4628`.

Status: stage 1 is satisfied for locating the Figure 3 artifact and its printed
component PCCs. The manuscript caption does not itself report the exact numeric
PCC values.

### Figures 4 and 5 / feature-correlation text

Manuscript claims include:

- Feature C has PCC `-0.15` with experimental DDG.
- Maximum A/B/C/D pairwise PCC is stated as `0.52` between A and B.
- E-1 has PCC `0.49` with D.
- E-2 has the highest label PCC among E-1..E-5 and is stated as having maximum
  PCC `0.17` with D.
- E-4 is described as having label PCC `0.21` and maximum other-feature PCC
  `0.20`.
- E-3 is described as having PCCs `0.55`, `0.40`, and `0.55` with A, B, and C,
  and `0.26` with DDG.
- E-2/E-4 are described as having maximum pairwise PCC `0.20`.
- F, G, and H are described as having maximum PCC magnitudes `0.32`, `0.15`,
  and `0.39` with A, A, and E-1.
  Evidence:
  `SA_CEM_9_26_2022_MJ_Issue_Adressing.txt:94-121`.

Notebook-cell evidence:

- `Quick_Dirty_MPNN_ML_V2_VGRAPHS_V1.ipynb`, cell 24, emits the A/B/C/D/E
  heatmap figure.
  Evidence:
  `colab_notebooks_inventory_analysis/git_notebook_outputs/Quick_Dirty_MPNN_ML_V2_VGRAPHS_V1.ipynb.outputs.txt:4694-4700`.
- `Quick_Dirty_MPNN_ML_V2_VGRAPHS_V1.ipynb`, cell 25, emits the full
  A/B/C/D/E/F/G/H heatmap figure.
  Evidence:
  `colab_notebooks_inventory_analysis/git_notebook_outputs/Quick_Dirty_MPNN_ML_V2_VGRAPHS_V1.ipynb.outputs.txt:4702-4708`.
- `Quick_Dirty_MPNN_ML_V2_VGRAPHS_V1.ipynb`, cell 26, emits the full
  correlation matrix text for A/B/C/D/E/F/G/H.
  Evidence:
  `colab_notebooks_inventory_analysis/git_notebook_outputs/Quick_Dirty_MPNN_ML_V2_VGRAPHS_V1.ipynb.outputs.txt:4710-4741`.

Clean matches in the cell 26 matrix:

- Feature C vs DDG: `-0.150304`, matching manuscript `-0.15`.
- E-1 vs D: `0.491047`, matching manuscript `0.49`.
- E-3 vs A/B/C/DDG: `0.544799`, `0.395248`, `-0.546681`, `0.255719`,
  matching manuscript magnitudes `0.55`, `0.40`, `0.55`, and `0.26`.
- E-2 vs E-4: `0.195571`, matching manuscript `0.20`.
- F vs A: `0.316624`, matching manuscript `0.32`.
- G vs A: `0.145881`, matching manuscript `0.15`.

Near or unresolved matches:

- Manuscript says maximum A/B/C/D pairwise PCC is `0.52` between A and B.
  Cell 26 has A/B = `0.514658`, which rounds to `0.51` at two decimals, not
  `0.52`.
- Manuscript says E-2 has maximum PCC `0.17` with D. Cell 26 has E-2/D =
  `0.181057`, while `Quick_Dirty_MPNN_ML_V2_V4.ipynb`, cell 23, has E-2/D =
  `0.171205`.
  Evidence:
  `colab_notebooks_inventory_analysis/git_notebook_outputs/Quick_Dirty_MPNN_ML_V2_V4.ipynb.outputs.txt:165-190`.
- Manuscript says E-4 label PCC is `0.21`; the checked matrices show E-4/DDG
  as `0.201329` in VGRAPHS/V3 and `0.204877` in V4.
- Manuscript says H has maximum PCC magnitude `0.39` with E-1. Cell 26 has
  H/E-1 = `-0.378840`, which rounds to `0.38` at two decimals.

Status: stage 1 is partially satisfied for S_2648 feature-correlation claims.
The relevant cells are located, and many values match directly. The `0.52`,
`0.17`, `0.21`, and `0.39` manuscript values need follow-up before claiming
complete number-level certainty.

### Figure 6 / held-out incremental feature contribution

Manuscript claim:

- Figure 6 reports incremental feature-combination PCC trends for S_669 and
  Ssym after RF training on S_2648, averaged over ten RF runs.
  Evidence:
  `SA_CEM_9_26_2022_MJ_Issue_Adressing.txt:135-144`.

Interpretation:

- Figure 6 supports the claim that the engineered feature groups contribute to
  predictive performance when evaluated on independent test sets. It is
  therefore feature-engineering validation evidence, but it remains held-out
  evaluation evidence rather than S_2648 feature-selection/tuning evidence
  unless code history shows it was used to choose features or parameters.

Notebook-cell evidence:

- `Quick_Dirty_MPNN_ML_V2_VGRAPHS_V1.ipynb`, cell 28, trains/evaluates ten
  random forest runs across incremental feature combinations and stores the
  per-run dictionaries.
  Evidence:
  `colab_notebooks_inventory_analysis/git_notebook_sources/Quick_Dirty_MPNN_ML_V2_VGRAPHS_V1.ipynb.py.txt:928-1031`.
- `Quick_Dirty_MPNN_ML_V2_VGRAPHS_V1.ipynb`, cell 38, emits the S_669
  incremental-feature bar figure.
  Evidence:
  source:
  `colab_notebooks_inventory_analysis/git_notebook_sources/Quick_Dirty_MPNN_ML_V2_VGRAPHS_V1.ipynb.py.txt:1184-1214`;
  output:
  `colab_notebooks_inventory_analysis/git_notebook_outputs/Quick_Dirty_MPNN_ML_V2_VGRAPHS_V1.ipynb.outputs.txt:5160-5169`.
- `Quick_Dirty_MPNN_ML_V2_VGRAPHS_V1.ipynb`, cell 39, emits the Ssym
  incremental-feature bar figure.
  Evidence:
  source:
  `colab_notebooks_inventory_analysis/git_notebook_sources/Quick_Dirty_MPNN_ML_V2_VGRAPHS_V1.ipynb.py.txt:1216-1246`;
  output:
  `colab_notebooks_inventory_analysis/git_notebook_outputs/Quick_Dirty_MPNN_ML_V2_VGRAPHS_V1.ipynb.outputs.txt:5171-5180`.
- `Quick_Dirty_MPNN_ML_V2_VGRAPHS_V1.ipynb`, cell 40, emits the combined
  S_669/Ssym incremental-feature figure.
  Evidence:
  source:
  `colab_notebooks_inventory_analysis/git_notebook_sources/Quick_Dirty_MPNN_ML_V2_VGRAPHS_V1.ipynb.py.txt:1248-1291`;
  output:
  `colab_notebooks_inventory_analysis/git_notebook_outputs/Quick_Dirty_MPNN_ML_V2_VGRAPHS_V1.ipynb.outputs.txt:5182-5185`.
- `Quick_Dirty_MPNN_ML_V2_VGRAPHS_V1.ipynb`, cell 26 correlation matrix emits
  the Figure 6 text's F/G/H correlation values: F/G = `0.781159`, F/H =
  `-0.788745`, matching manuscript `0.78` and `-0.79`.
  Evidence:
  `colab_notebooks_inventory_analysis/git_notebook_outputs/Quick_Dirty_MPNN_ML_V2_VGRAPHS_V1.ipynb.outputs.txt:4739-4741`.

Status: stage 1 is satisfied for locating the Figure 6 artifacts and the
F/G/H correlation values cited in the Figure 6 discussion.
