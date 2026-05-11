# Table 1 Numerical Recovery Milestone

Date: 2026-05-11

Purpose: record the current numerical match between manuscript Table 1 and the
historical result artifacts.

This note concerns final RF result evidence. It does not prove upstream V3
pickle regeneration or direct tensor extraction.

## Scope

Manuscript Table 1 reports PMPNN-DDG performance on three independent test sets:
`S_669`, `Ssym`, and `S_921`.

The table columns are:

```text
Dataset | rF | rR | rF+R | rF-R | rmsF | rmsR | rmsF+R
```

The extracted manuscript text records the rows at
`manuscript_inventory_analysis/extracted/docx_text/SA_CEM_9_26_2022_MJ_Issue_Adressing.txt:151-183`.

## Core Finding

`list_incremental_feature_result_dict.pickle` supports the Table 1 values for
the full A-H feature set for these six columns:

```text
rF, rR, rF+R, rmsF, rmsR, rmsF+R
```

For those six columns, the ten-run means in the pickle round to the manuscript
values for all three datasets:

```text
3 datasets * 6 columns = 18 matched table cells
```

The remaining column, `rF-R`, is not stored in the inspected
`list_incremental_feature_result_dict.pickle`. It is supported by saved notebook
outputs from the forward-vs-reverse PCC calculation:

```text
3 datasets * 1 column = 3 matched table cells from notebook-output evidence
```

Strict statement:

```text
pickle-only evidence matches 18/21 Table 1 numeric cells.
The remaining 3/21 rF-R cells match through saved notebook-output evidence,
not through the saved result pickle itself.
```

Including saved notebook-output evidence, all Table 1 numeric cells for the
three independent test-set rows are currently numerically matched.

## Pickle-Supported Cells

Evidence table:
`code_inventory_analysis/incremental_feature_pickle_inspection/full_ah_metric_summary.tsv`

| Dataset | Pickle ten-run means | Rounded values |
| --- | --- | --- |
| `S_669` | `0.480021, 0.478905, 0.643995, 1.451860, 1.452820, 1.452341` | `0.48, 0.48, 0.64, 1.45, 1.45, 1.45` |
| `Ssym` | `0.721961, 0.718826, 0.812228, 1.098380, 1.102374, 1.100381` | `0.72, 0.72, 0.81, 1.10, 1.10, 1.10` |
| `S_921` | `0.767839, 0.766319, 0.794155, 1.492075, 1.494486, 1.493282` | `0.77, 0.77, 0.79, 1.49, 1.49, 1.49` |

The six numbers in each row correspond to:

```text
rF, rR, rF+R, rmsF, rmsR, rmsF+R
```

## Notebook-Output-Supported rF-R Cells

The saved notebook-output evidence gives:

| Dataset | Saved output | Manuscript rounded value |
| --- | --- | --- |
| `S_669` | `-0.9939184352208846` | `-0.99` |
| `Ssym` | `-0.9946606797887094` | `-0.99` |
| `S_921` | `-0.9960837257021014` | `-1.00` |

Evidence notes:

- `manuscript_codebase_mapping/S669_SSYM_S2648_STAGE1_NOTEBOOK_CELL_EVIDENCE.md`
- `manuscript_codebase_mapping/S_921_TABLE1_NOTEBOOK_CELL_EVIDENCE.md`

## Figure 6 Implication

The same ten-run result pickle also stores the A through A-H total-PCC series
for `S_669` and `Ssym`.

This strongly supports the current interpretation that the underlying numerical
values used for the Figure 6-style incremental-feature plot have been recovered
from `list_incremental_feature_result_dict.pickle`.

Remaining Figure 6-specific work: compare the recovered total-PCC series against
the final embedded manuscript figure, caption, and any exported figure image.

## Not Table 1 Sources

The older `feature_combo_*` pickles are not the final Table 1 source. They are
older A-F, PCC-only all-subset experiment artifacts and do not contain the final
A-H Table 1 result shape.
