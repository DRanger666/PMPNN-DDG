# PMPNN-DDG feature pickles (2026-09-12)

Compact RF feature dictionaries produced by:

`PDB → modified ProteinMPNN → extraction tensors → feature functions A–H`

## Files (Git LFS)

| File | Dataset | Mutations (ok) |
| --- | --- | ---: |
| `Ssym_features_compact.pickle` | Ssym | 342 |
| `S2648_features_compact.pickle` | S_2648 | 2647 |
| `S669_features_compact.pickle` | S_669 | 638 |

`S_921` will be added when regeneration finishes.

## Contents

Per-protein lists of mutation entries with RF scalars (A–H, energies, PSSMs) and
raw neighbor matrices used for Feature E. Intermediate extraction tensors
(`log_prob`, attended neighbors, messages, embeddings, …) are stored separately
when generated with `--save-mode full`.

## Integrity

See `manuscript_codebase_mapping/UNPROCESSABLE_MUTATIONS_AND_DATASET_GAPS.md`.
