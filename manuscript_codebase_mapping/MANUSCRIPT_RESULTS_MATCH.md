# Manuscript Results Match

**Branch:** `reproduce-paper-results`  
**Manuscript:** PMPNN-DDG bioRxiv DOI 10.64898/2026.08.23.746499  
**Purpose:** Formal correspondence between **this branch’s regenerated pipeline**
and the manuscript’s full results layer. Linked from the [top-level README](../README.md).

This is distinct from historical pickle/notebook recovery
(`TABLE1_NUMERICAL_RECOVERY_MILESTONE.md`, `FIGURE6_NUMERICAL_BASIS_VERIFICATION.md`),
which prove that *saved* artifacts match published numbers. Here the claim is
that **code on this branch**, run end-to-end, reproduces those numbers.

## Status summary

| ID | Claim | Regenerated-pipeline status | Notes |
| --- | --- | --- | --- |
| Table 1 | S669 / Ssym / S921 independent-test metrics | **Pending** | Awaiting RF on regenerated features (S921 features in progress) |
| Table 2 | S669 PMPNN-DDG row | **Pending** | Same RF outputs as Table 1 S669 row; external rows = literature |
| Table 3 | Ssym PMPNN-DDG row | **Pending** | Same RF outputs as Table 1 Ssym row; external rows = literature |
| Figure 6 | Incremental A→H total-PCC on S669/Ssym | **Pending** | Requires incremental RF protocol on regenerated features |
| Figures 3–5 | S2648 train-set feature analyses | **Pending** | After S2648 feature matrix is finalized |
| Figures 1–2 | Pipeline / method schematics | N/A (non-numeric) | |

**Last updated:** 2026-09-12 (scaffold; numeric cells empty until RF completes).

## How to re-run verification

1. Ensure feature pickles exist under
   `reproduction_inputs/pmpnn_ddg_features_2026-09-12/` (or regenerate via
   `scripts/run_pdb_to_features_pipeline.py` with `--save-mode full` or `both`).
2. Train/eval RF with the manuscript protocol
   (`scripts/train_eval_rf_from_v3_features.py`; `n_estimators=500`,
   `max_samples=0.5`, train on S2648 + reverse augmentation).
3. Fill the metric tables below from that run’s outputs.
4. Update the status summary and the README one-liner if the match state changes.

## Table 1 — independent-test performance (PMPNN-DDG)

Fill from regenerated RF (columns as in manuscript). Mark each cell
`match` / `near` / `mismatch` vs BioRxiv.

| Dataset | Metric | Manuscript | Regenerated | Verdict |
| --- | --- | --- | --- | --- |
| S_669 | *(cells TBD from manuscript Table 1)* | | | pending |
| Ssym | | | | pending |
| S_921 | | | | pending |

Historical recovery (saved pickle/notebook, not this regen):
`TABLE1_NUMERICAL_RECOVERY_MILESTONE.md`.

## Table 2 — S669 external comparison (PMPNN-DDG row only)

| Method | Metric set | Manuscript | Regenerated | Verdict |
| --- | --- | --- | --- | --- |
| PMPNN-DDG | *(as in Table 2)* | | | pending |
| Other methods | — | literature | — | not re-run |

## Table 3 — Ssym external comparison (PMPNN-DDG row only)

| Method | Metric set | Manuscript | Regenerated | Verdict |
| --- | --- | --- | --- | --- |
| PMPNN-DDG | *(as in Table 3)* | | | pending |
| Other methods | — | literature | — | not re-run |

## Figure 6 — incremental feature contribution

| Series | Manuscript basis | Regenerated | Verdict |
| --- | --- | --- | --- |
| S_669 total-PCC vs feature combo | see `FIGURE6_NUMERICAL_BASIS_VERIFICATION.md` | | pending |
| Ssym total-PCC vs feature combo | same | | pending |

## Figures 3–5 — S2648 training analyses

| Figure | Regenerated artifact | Verdict |
| --- | --- | --- |
| Figure 3 | | pending |
| Figure 4 | | pending |
| Figure 5 | | pending |

## Integrity caveats that affect counts

Any mutation omitted from regenerated matrices must appear in
`UNPROCESSABLE_MUTATIONS_AND_DATASET_GAPS.md` with justification. Do not treat
silent drops as matches.

## Related docs

- `TRAIN_TEST_FIGURE_TABLE_ANCHOR.md` — dataset roles for each table/figure
- `MANUSCRIPT_TO_VARIABLE_NAMING.md` — BioRxiv method language → variable names
- `UNPROCESSABLE_MUTATIONS_AND_DATASET_GAPS.md` — integrity audit
- `../workspace_operations/CURRENT_RECOVERY_BOUNDARY.md` — recovery vs regen boundary
