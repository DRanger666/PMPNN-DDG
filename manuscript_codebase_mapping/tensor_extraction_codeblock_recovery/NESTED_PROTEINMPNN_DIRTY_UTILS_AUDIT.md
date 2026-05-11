# Nested ProteinMPNN Dirty Utility Source Audit

Scope: old nested ProteinMPNN checkout at
`drive_evidence_copy/sajidahmedprotres_drive/Protein_MPNN_Digging/ProteinMPNN`.

## Current State

- Nested checkout commit: `c602ced6ad4b6997d89afa9432607ac9d0572539`.
- Dirty file: `vanilla_proteinmpnn/protein_mpnn_utils.py`.
- Diff size: `159` inserted lines, `7` deleted lines.

## What Changed

Most dirty changes are explanatory comments added while studying how the
ProteinMPNN utility code works for a DDG/energy-style use case. The comments
focus on:

- PDB chain parsing and chain-name constraints.
- `tied_featurize` inputs and outputs.
- `chain_M`, `chain_M_pos`, fixed positions, designable positions, padding,
  and chain encoding.
- Neighbor selection through `ProteinFeatures._dist`.
- `ProteinMPNN.forward`, `sample`, `conditional_probs`, and
  `unconditional_probs`.

There is one substantive-looking code addition:

```python
def return_neighbor_info(self, X, mask, residue_idx, chain_labels):
    ...
    D_neighbors, E_idx = self._dist(Ca, mask)
```

This method is incomplete as written in the dirty source. It computes nearest
neighbor distances and indices, but it does not return them.

There is also one harmless whitespace-level code change:

```python
coords_dict = {}
```

became:

```python
coords_dict = {} 
```

## Why These Changes Probably Existed

The dirty source looks like an exploratory annotation and scratch-modification
step from 2022. The comments document how to control fixed vs designable
positions and how to obtain neighbor indices. The incomplete
`ProteinFeatures.return_neighbor_info` method appears to be an early attempt to
surface nearest-neighbor information from inside ProteinMPNN.

This dirty source does not contain the complete V6_V2 tensor-extraction
behavior. In particular, it does not modify `DecLayer.forward` to return
decoder messages, and it does not modify `ProteinMPNN.forward` to return
`log_probs`, `decoder_messages`, and `h_V`.

## Relationship To V6_V2 Notebooks

The V6_V2 notebook exports include the same incomplete
`ProteinFeatures.return_neighbor_info` method, but the actual call-site uses a
separate standalone helper:

```python
def return_neighbor_info(X, mask):
    ...
    return D_neighbors, E_idx
```

The V6_V2 notebooks also contain the tensor-return behavior that the dirty
nested source does not contain:

- `DecLayer.forward` returns `(h_V, h_message / self.scale)`.
- `ProteinMPNN.forward` returns `(log_probs, decoder_messages, h_V)`.

## Relationship To The Recovered Package

`proteinmpnn_ddg_recovery/recovered_v6v2.py` imports the dirty nested
`protein_mpnn_utils.py` path by default, so the historical parser,
`tied_featurize`, class definitions, comments, and incomplete scratch method
are present in the loaded module.

The recovered package does not call the dirty source's incomplete
`ProteinFeatures.return_neighbor_info` method.

Instead, the recovered package incorporates the V6_V2 behavior explicitly by:

- monkeypatching `DecLayer.forward`;
- monkeypatching `ProteinMPNN.forward`;
- defining its own standalone `return_neighbor_info(X, mask, num_edges)` helper
  that returns nearest-neighbor distances and indices from CA coordinates.

## Interpretation

The dirty nested `protein_mpnn_utils.py` is important historical evidence, but
it is not the full tensor generator. It helps explain the transition from
reading ProteinMPNN internals toward notebook-side tensor extraction, but the
direct evidence for V3 tensor extraction remains the V6_V2 notebook code and
the recovered package implementation derived from it.

The current direct-tensor value mismatch should not be attributed to this dirty
source file alone. The dirty file does not implement the message and embedding
returns needed for the V3 tensor fields, and its only new method is incomplete
and unused by the recovered package.
