# V3 Directed Neighbor-Asymmetry Semantics

Date: 2026-05-12

Status: active scientific/method note. This is not a final manuscript claim.

## Purpose

This note records the directed-neighbor asymmetry that matters for
ProteinMPNN-DDG V3 tensor extraction.

The key distinction is:

```text
neighbor j -> center i message used for neighbor selection
center i   -> neighbor j message used for center-to-neighbor message features
```

Those are not guaranteed to be the same directed edge in ProteinMPNN's
top-k neighbor graph.

## Two Filters

Let the mutated center residue be `i`, and let a candidate neighbor residue be
`j`.

### 1. Center-neighbor selection

ProteinMPNN first constructs a local spatial neighbor list for the center:

```text
E_idx[i, :] = top-k CA-nearest residues around center i
```

The recovered V6_V2-style extraction then ranks those center-local candidates
by the decoder-message norm at the center:

```text
||message_{i <- j}||
```

So the selected K neighbors are not simply the K closest residues. They are the
highest-message-norm residues among the center's ProteinMPNN spatial-neighbor
candidates.

Practical consequence: if `j1` is spatially closer than `j2`, but both are in
`E_idx[i, :]`, then `j2` can be selected while `j1` is dropped if
`||message_{i <- j2}||` is larger than `||message_{i <- j1}||`.

### 2. Center-to-neighbor message extraction

For message-based features, the method then tries to read the message in the
opposite direction:

```text
message_{j <- i}
```

In the recovered code, this exists only if the center residue `i` appears in
the selected neighbor residue's own local spatial neighbor list:

```text
i in E_idx[j, :]
```

Because ProteinMPNN uses a directed top-k neighbor graph, the relation is not
guaranteed to be reciprocal:

```text
j in E_idx[i, :] does not imply i in E_idx[j, :]
```

If the reciprocal directed edge is absent, there is no stored decoder message
for `message_{j <- i}` in that forward pass. The current recovered scaffold
therefore inserts a zero vector for that center-to-neighbor message.

## Correct Interpretation

The user's conceptual framing is mostly right, with one necessary precision.

The first drop event is message-norm driven inside the center's spatial
candidate list. A closer residue can lose to a farther residue if the farther
residue sends a larger message to the center.

The second missing-edge event is graph-topology driven. The center-to-neighbor
message can be unavailable because the center is not in the neighbor's own
top-k spatial list. That absence is not evidence that the center sent a small
message to the neighbor; it means the directed edge was not present in the
ProteinMPNN local graph for that neighbor.

Here, "spatial" means ProteinMPNN's CA-distance top-k graph after masking and
featurization, not necessarily a simple human-visible nearest-residue rule.

## Feature Implications

This asymmetry matters most directly for features that use center-to-neighbor
message vectors or message norms:

- Feature C: center-to-neighbor message norm ratios.
- Feature E: center-to-neighbor message-change vectors before PCA/KPCA.
- Feature B: the recovered weighted neighbor-entropy implementation uses
  message-norm-ratio weighting, so it can also be affected.

Feature D uses neighbor embedding changes, not the center-to-neighbor message
vector itself. However, it still depends on the same selected-neighbor set, so
the message-norm-based selection stage remains relevant for Feature D.

## Optional diagnostics (not a V3-reconciliation milestone)

Byte-identical historical V3 extraction is **not** the branch bar
(`REPRODUCTION_BAR_NOT_BYTE_IDENTICAL_V3.md`). If measuring directed-graph
effects is useful for method clarity, optional counts on **regenerated**
extraction tensors (or reference V3 dumps) can still include:

- reciprocal-edge coverage for selected top-15 neighbors;
- zero-vector frequency in center-to-neighbor message fields;
- whether zero-vector patterns match non-reciprocal `E_idx` cases;
- how reciprocal-edge absence relates to distance rank, message-norm rank, and
  protein/dataset identity;
- whether alternate handling changes scalar features and RF-level performance
  vs **manuscript** metrics (not vs V3 pickle identity).
