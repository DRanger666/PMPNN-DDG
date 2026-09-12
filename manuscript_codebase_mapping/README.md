# Manuscript–codebase mapping

**Still useful on this branch:** living match / integrity / fidelity / naming
docs for the regenerated pipeline. Not the pruned inventory archaeology on
`main`. On `main`, the same directory name holds earlier notebook↔pickle
provenance from the recovery phase.

Evidence and notes that connect **this branch’s regenerated pipeline** to the
bioRxiv PMPNN-DDG manuscript (DOI `10.64898/2026.08.23.746499`).

Primary chain on this branch:

```text
extraction tensors → ProteinMPNN features A–E + PSSM features F–H
  → Figures 3–5 / RF → Tables 1–3 + Figure 6
  → MANUSCRIPT_RESULTS_MATCH.md
```

## Start here

- `REPRODUCTION_BAR_NOT_BYTE_IDENTICAL_V3.md` — **retired** V3 byte-reconciliation; manuscript numbers + mismatch probing is the bar

- `MANUSCRIPT_RESULTS_MATCH.md` — formal regenerated vs manuscript tallies
- `TRAIN_TEST_FIGURE_TABLE_ANCHOR.md` — which dataset each table/figure uses
- `MANUSCRIPT_TO_VARIABLE_NAMING.md` — BioRxiv method language → variable names
- `UNPROCESSABLE_MUTATIONS_AND_DATASET_GAPS.md` — integrity audit (+ `tables/`)
- `MANUSCRIPT_TENSOR_EXTRACTION_FIDELITY.md` — open fidelity questions (e.g. Feature B)
- `FIGURE45_KPCA_SUBSAMPLE_SENSITIVITY.md` — Fig 4–5 residual E* PCCs vs KernelPCA seed
- `CLEAN_MODIFIED_PROTEINMPNN_AND_FEATURES.md` — clean fork + per-feature modules

## Supporting notes (still useful)

- `REGENERATED_FEATURES_VS_HISTORICAL_V3.md` — regen vs historical naming/save modes
- `FEATURE_EQUATION_CODE_MAPPING_INITIAL.md` — equation ↔ code map
- `S669_3DV0I_*` / `S2648_INSTANCE_LEVEL_FEATURE_ABSENCE.md` — specific gap investigations
- `TABLE1_NUMERICAL_RECOVERY_MILESTONE.md` / `FIGURE6_*` — historical saved-artifact provenance (not a substitute for regen match)
- `S_921_TABLE1_NOTEBOOK_CELL_EVIDENCE.md` / `S669_SSYM_S2648_STAGE1_NOTEBOOK_CELL_EVIDENCE.md` — notebook-cell provenance

Obsolete inventory trees and the **`v3_tensor_extraction_reconciliation`**
track were removed from this branch (git history only). That reconciliation
goal is retired — see `REPRODUCTION_BAR_NOT_BYTE_IDENTICAL_V3.md`.
