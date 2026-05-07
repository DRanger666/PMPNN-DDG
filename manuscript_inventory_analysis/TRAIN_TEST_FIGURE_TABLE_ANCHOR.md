# Training-vs-Test Anchor for Manuscript Figures and Tables

This note records the dataset role for each manuscript figure/table. It is a
reasoning anchor for code-to-manuscript mapping: S_2648 evidence supports
feature engineering and model-development decisions; S_669, Ssym, and S_921
evidence supports held-out evaluation.

The user referred to `Ssy` and `S_691`; the manuscript and current extracted
artifacts use `Ssym` and `S_669`.

## Dataset Roles

- `S_2648`: training and validation dataset.
  Manuscript evidence: `SA_CEM_9_26_2022_MJ_Issue_Adressing.txt:27-35`.
- `S_669`: independent test set.
  Manuscript evidence: `SA_CEM_9_26_2022_MJ_Issue_Adressing.txt:31-35`.
- `Ssym`: independent test set.
  Manuscript evidence: `SA_CEM_9_26_2022_MJ_Issue_Adressing.txt:32-35`.
- `S_921`: independent test set.
  Manuscript evidence: `SA_CEM_9_26_2022_MJ_Issue_Adressing.txt:33-35`.

## Figures

| Figure | Dataset role | Classification | Mapping implication |
| --- | --- | --- | --- |
| Figure 1 | S_2648 plus S_669/Ssym/S_921 | Pipeline schematic | This is an overview figure, not a numeric result. It states the intended train/test separation. |
| Figure 2 | Not dataset-specific | Feature-extraction schematic | This is method logic. It can be supported by code that extracts PMPNN tensors/features, but it should not depend on test-set performance. |
| Figure 3 | S_2648 only | Training-set feature-engineering/encoding analysis | Match against S_2648 feature-correlation code only. Do not search for S_669/Ssym/S_921 versions as manuscript evidence. |
| Figure 4 | S_2648 only | Training-set feature-label and feature-feature correlation analysis | Match against S_2648 correlation matrices/heatmaps for A, B, C, D, E. |
| Figure 5 | S_2648 only | Training-set full feature-set decorrelation analysis | Match against S_2648 A-H correlation matrices/heatmaps. |
| Figure 6 | S_669 and Ssym predictions from RF models trained on S_2648 | Independent-test evaluation / ablation-style result | Match against code that trains on S_2648 and evaluates incremental feature combinations on S_669/Ssym. Treat as held-out evaluation, not as feature-selection evidence, unless code/history proves it influenced feature choice. |

Supporting manuscript evidence:

- Figure 1 caption: `SA_CEM_9_26_2022_MJ_Issue_Adressing.txt:20-23`.
- Figure 2 caption and method context:
  `SA_CEM_9_26_2022_MJ_Issue_Adressing.txt:41-49`.
- Figure 3 caption and C/D encoding decision:
  `SA_CEM_9_26_2022_MJ_Issue_Adressing.txt:62-75`.
- Figure 4 caption and text:
  `SA_CEM_9_26_2022_MJ_Issue_Adressing.txt:94-103`.
- Figure 5 caption and text:
  `SA_CEM_9_26_2022_MJ_Issue_Adressing.txt:112-121`.
- Figure 6 text and caption:
  `SA_CEM_9_26_2022_MJ_Issue_Adressing.txt:135-144`.

## Tables

| Table | Dataset role | Classification | Mapping implication |
| --- | --- | --- | --- |
| Table 1 | S_669, Ssym, S_921 | Independent-test performance | Match against RF evaluation outputs for full feature set on all three test sets. |
| Table 2 | S_669 | Independent-test comparison against external methods | PMPNN-DDG row should map to our RF evaluation outputs; external-method rows likely map to literature/benchmark sources. |
| Table 3 | Ssym | Independent-test comparison against external methods | PMPNN-DDG row should map to our RF evaluation outputs; external-method rows likely map to literature/benchmark sources. |

Supporting manuscript evidence:

- Table 1 and discussion:
  `SA_CEM_9_26_2022_MJ_Issue_Adressing.txt:148-220`.
- Table 2 and discussion:
  `SA_CEM_9_26_2022_MJ_Issue_Adressing.txt:222-341`.
- Table 3 and discussion:
  `SA_CEM_9_26_2022_MJ_Issue_Adressing.txt:341-458`.

## Rule for Future Matching

When searching for manuscript-to-code matches:

- For feature construction, feature efficacy, feature-feature correlation,
  kernel-PCA basis choice, and hyperparameter tuning, search first for S_2648
  code and outputs.
- For Table 1, Table 2 PMPNN-DDG row, Table 3 PMPNN-DDG row, and Figure 6,
  search for code that trains on S_2648 and evaluates on the independent test
  set named in the figure/table.
- If a notebook uses S_669, Ssym, or S_921 to choose features, tune parameters,
  or decide which feature group to retain, flag it as a possible leakage risk.
  If it only reports predictions after S_2648-based model-development choices,
  treat it as held-out evaluation.
