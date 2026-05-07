# Manuscript-Codebase Mapping

This directory is for evidence that connects manuscript claims, table rows, and
figures to code, notebook outputs, pickle files, datasets, and upstream
ProteinMPNN artifacts.

This is a separate stage from manuscript inventory. Manuscript inventory answers:
what manuscript files exist, how they relate to each other, and what text,
metadata, tracked-change artifacts, figures, and tables they contain.

Manuscript-codebase mapping answers: where did a manuscript number or figure
come from, and how far upstream can we prove its provenance?

Use this provenance chain as the working model:

```text
manuscript number, figure, or table row
<- notebook cell/output that emitted the value or artifact
<- RF training/evaluation variables used by that cell
<- feature matrix assembled from pickle dictionaries
<- pickle dictionary file loaded into the notebook
<- code that created the pickle dictionary
<- ProteinMPNN outputs, mutation rows, structures, and dataset files used by that code
```

Current notes:

- `MANUSCRIPT_NUMBER_PROVENANCE_VIEWPOINT.md`: general provenance standard.
- `S_921_TABLE1_NOTEBOOK_CELL_EVIDENCE.md`: Table 1 evidence for S_921.
- `S669_SSYM_S2648_STAGE1_NOTEBOOK_CELL_EVIDENCE.md`: stage-one notebook-cell
  evidence for S_669, Ssym, and S_2648.
- `STAGE5_PICKLE_GENERATION_BRIDGE.md`: working strategy and initial evidence
  for using V3 PMPNN pickle dictionaries as the bridge from ProteinMPNN feature
  extraction to RF evaluation.
- `TRAIN_TEST_FIGURE_TABLE_ANCHOR.md`: dataset-role anchor for figures and
  tables.
