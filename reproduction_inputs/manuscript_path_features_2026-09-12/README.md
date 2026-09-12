# Manuscript-path feature artifacts (2026-09-12)

These pickles are **manuscript-path** regeneration outputs from:

`PDB → modified_proteinmpnn → tensors → feature functions A–H (compact RF fields)`

They are **not** historical “V3” recovery pickles. The filenames say `manuscript_path` on purpose.

## Files (Git LFS)

| File | Dataset | Jobs (ok/total) | Notes |
| --- | --- | ---: | --- |
| `Ssym_manuscript_path_features_compact.pickle` | Ssym | 342/342 | compact-for-rf |
| `S2648_manuscript_path_features_compact.pickle` | S_2648 | 2619/2648 | see unprocessable audit |
| `S669_manuscript_path_features_compact.pickle` | S_669 | 638/669 | see unprocessable audit |

`S_921` will be added when regeneration finishes.

## Compact schema

Each protein key maps to a list of mutation dicts with RF scalars (A–H, energies, PSSMs)
plus raw neighbor matrices used for Feature E (`neighbor_message_change_m_w_raw`,
`neighbor_embedding_change_m_w_raw`). Full extraction tensors (`log_prob`, attended
neighbor indices, …) are a separate future artifact class.

## Integrity

`manuscript_codebase_mapping/UNPROCESSABLE_MUTATIONS_AND_DATASET_GAPS.md`

## Branch

`reproduce-paper-results` / PR #2
