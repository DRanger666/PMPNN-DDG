# Clean ProteinMPNN Modifications for PMPNN-DDG

## Base

- Upstream: `source_repos/dauparas_ProteinMPNN/vanilla_proteinmpnn/protein_mpnn_utils.py`
- Digging nested copy is **byte-identical** to that upstream file
  (`NESTED_PROTEINMPNN_DIRTY_UTILS_AUDIT.md`).
- `source_repos/SajidAhmeduiu_ProteinMPNN/.../protein_mpnn_utils.py` adds
  exploratory comments and an **incomplete** `ProteinFeatures.return_neighbor_info`
  — **not** used here.

## Behavioral diffs vs upstream (only these)

| Location | Upstream | This fork | Why (manuscript) |
| --- | --- | --- | --- |
| `DecLayer.forward` | returns `h_V` | returns `(h_V, h_message/scale)` | §3.1: L2-norm of last-decoder neighbor→center messages ranks top-K neighbors |
| `ProteinMPNN.forward` | returns `log_probs` | returns `(log_probs, decoder_messages, h_V)` | Feature A from center `log_probs`; messages for ranking / C / E; `h_V` for neighbor embeddings (D) |
| `sample` / `tied_sample` / `conditional_probs` / `unconditional_probs` | call `DecLayer` as single-tensor | unpack `[0]` / `_decoder_messages` | Keep design APIs runnable on the same fork |

## Explicitly not included

- Notebook comment dumps
- Incomplete `ProteinFeatures.return_neighbor_info`
- Monkeypatches at import time (hooks are source-level)
- Changes to encoder, featurizer geometry, or checkpoint loading

## Evidence sources for the hooks

- V6_V2 notebook cells (`Ssym_ProteinMPNNTesting_V6_V2` et al.): DecLayer /
  ProteinMPNN.forward return shapes above
- Prior recovery: `pmpnn_ddg/recovered_v6v2.py` (historically
  monkeypatched Digging utils; now loads this clean package by default)
