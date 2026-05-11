# V3 Neighbor-Vector Extraction Semantics

Date: 2026-05-12

Status: active scientific/method note. This is not a final manuscript claim.

## Purpose

This note records the ProteinMPNN-DDG neighbor-vector extraction semantics that
affect features B, C, D, and E.

It exists separately from feature-specific notes because the same extracted
neighbor-level objects feed multiple features:

```text
P_j(WT center), P_j(MT center) -> feature B and KL/energy variants
M_j(WT center), M_j(MT center) -> feature C and feature E
E_j(WT center), E_j(MT center) -> feature D
```

## Core Semantics

For each real mutation entry `WTPosMT`, the pipeline first identifies the
center residue and selects K neighbors from a center-designable ProteinMPNN
pass.

The resulting V3 object stores K-row bundles per mutation entry, but that
storage shape should not be read as "all K selected neighbors were designable
in one ProteinMPNN pass."

The manuscript text and recovered V6_V2-style code indicate this multi-pass
procedure:

```text
1. Make the center residue designable.
2. Run ProteinMPNN on the WT-centered sequence.
3. Rank/select K center-attended neighbors from center decoder messages.
4. For each selected neighbor j:
   a. make only neighbor j designable;
   b. run ProteinMPNN with the center residue left WT;
   c. run ProteinMPNN with the center residue changed to MT;
   d. store neighbor-j probability, embedding, and center-to-neighbor message
      information.
```

The saved V3 object can therefore contain arrays shaped like `K x 128`, but
those arrays appear to be assembled one selected neighbor at a time.

## Feature Reach

This extraction logic is upstream of several features:

- Feature B and related KL/energy variants use the neighbor probability
  distributions extracted for each selected neighbor.
- Feature C uses center-to-neighbor message norm ratios.
- Feature D uses neighbor embedding difference norms.
- Feature E uses center-to-neighbor message difference vectors before
  PCA/KPCA projection.

## Evidence

- The manuscript's neighbor-vector extraction section says top-K neighbor
  positions are masked one by one separately while the mutation position is
  unmasked and set to WT or MT.
- `proteinmpnn_ddg_recovery/recovered_v6v2.py` makes the center residue
  designable first, then loops over `top_15_neighbor_indices` and makes each
  selected neighbor designable one at a time.
- The extracted `ProteinMPNNTesting_V6_V2.ipynb` source says the neighbor
  positions are masked one by one and stores neighbor log-probabilities,
  embeddings, and center-to-neighbor messages inside that per-neighbor loop.

## Why It Matters

This distinction matters for:

- random decoder-order analysis;
- directed neighbor-graph asymmetry;
- zero-vector handling when the directed center-to-neighbor edge is absent;
- value-level V3 direct-tensor reconciliation;
- future method wording, pseudocode, and reviewer-facing explanation.
