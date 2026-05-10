# Manuscript Table/Figure Provenance Plan

Date: 2026-05-06

This note records the next required provenance pass before any manuscript
rewrite or code cleanup claim. The goal is number-level reproducibility: every
table value, plotted point, bar height, and feature-correlation number in the
manuscript should be traced to an exact notebook cell, saved output, or result
artifact.

## Current Rule

Do not treat the current manuscript feature definitions as final until the
manuscript numbers have been matched back to the exact code path that produced
them.

Reason: the old notebooks contain repeated and copied variants of the same
pipeline. A feature may have been computed one way in one notebook and another
way in a later or earlier copy. The final manuscript numbers are the deciding
evidence for which implementation actually supported the manuscript.

## Immediate Open Caution: Feature B

Current code evidence from the final ML notebook family maps feature B to:

```text
V2_backward_weighted_neighbor_entropy_changes
```

That is not a plain unweighted neighbor entropy-change sum. It is:

```text
sum over top-15 neighbors:
  sigmoid(||M_w^{c->n}||_2 / ||M_m^{c->n}||_2)
  * (H(p_m^n) - H(p_w^n))
```

This caution must be revisited after table/figure provenance is traced. If the
manuscript numbers came from this final code path, the method text should say
that feature B is message-ratio-weighted entropy change. If a different
notebook/output produced the manuscript numbers, feature B must be remapped to
that exact source instead.

Detailed feature-equation evidence is in:

- `manuscript_codebase_mapping/FEATURE_EQUATION_CODE_MAPPING_INITIAL.md`
- `colab_notebooks_inventory_analysis/COLAB_NOTEBOOKS_DEEP_INVENTORY.md`

## Provenance Targets

Trace each manuscript item separately:

- Every table in the manuscript.
- Every figure panel in the manuscript.
- Every reported Pearson correlation, RMSE, standard deviation, and average.
- Every A-to-H incremental feature result.
- Every feature-feature correlation or heatmap value.
- Every dataset split/count used in result reporting.

For each item, record:

| Manuscript item | Reported value(s) | Candidate code file | Exact cell/output source | Input artifact(s) | Status |
|---|---|---|---|---|---|
| TBD | TBD | TBD | TBD | TBD | not started |

## Evidence Sources to Prefer

1. Saved notebooks with executed outputs, if available.
   The current deep inventory of the copied Drive `Colab Notebooks` folder and
   the Git-side notebook copies is in
   `colab_notebooks_inventory_analysis/COLAB_NOTEBOOKS_DEEP_INVENTORY.md`.
2. Result pickles that store final numerical summaries:
   - `feature_combo_result_dict.pickle`
   - `S_669_feature_combo_result_dict.pickle`
   - `incremental_feature_result_dict.pickle`
   - `list_incremental_feature_result_dict.pickle`
3. Source-only notebook exports when output-bearing notebooks are unavailable.
4. Generated figure files and timestamps, especially when paired with nearby
   notebook code.

## Important Distinction

Source code can show what a notebook would compute, but manuscript
reproducibility requires knowing what was actually used. For this project, that
means the priority is not just "find the cleanest final code"; it is:

```text
manuscript value -> exact executed notebook/output/result artifact -> code cell
```

Only after that mapping is stable should the manuscript methods be updated.
