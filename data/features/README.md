# ProteinMPNN + PSSM evolutionary feature pickles (2026-09-12)

These are the **engineered features** used for RF / train-set figures:

| Group | Source | Features |
| --- | --- | --- |
| ProteinMPNN-extracted | decoder tensors (log-probs, messages, neighbor embeddings, …) | **A–E** (E needs KernelPCA of message-change matrices) |
| Evolutionary (PSSM) | PSI-BLAST / PSSM log-odds at the mutation site | **F, G, H** |

## Files

| File | Dataset | Notes |
| --- | --- | --- |
| `Ssym_features.pickle` | Ssym | 342 |
| `S2648_features.pickle` | S_2648 | 2647 (gap: `2a01A` missing PSSM) |
| `S669_features.pickle` | S_669 | 638 (audited gaps, e.g. `3dv0I`) |
| `S921_features.pickle` | S_921 | 921 |

`*_proteinmpnn_and_pssm_features.pickle` are descriptive symlinks to the same files.  
`*_features_rf.pickle` also symlink to the same files (legacy RF entry name).

Do **not** use process labels like “features-from-full.”  

## Full extraction tensors (source of truth)

Full §3.1 intermediates **plus** the same A–H feature fields live under:

`../pmpnn_ddg_extraction_tensors_2026-09-12/{Dataset}_extraction_tensors.pickle`

Those are the public tensors → features assets. This directory’s pickles are the thinner RF-oriented feature tables (A–H + raw ΔE/ΔM matrices for KPCA), not a second scientific object.
