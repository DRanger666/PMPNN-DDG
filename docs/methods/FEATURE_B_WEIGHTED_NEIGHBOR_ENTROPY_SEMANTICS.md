# Feature B Weighted Neighbor-Entropy Semantics

Date: 2026-05-12

Status: active scientific/method note. This is not a final manuscript claim.

## Purpose

This note records a feature-B semantic caveat recovered from the code.

The manuscript-level idea is neighbor entropy change after the center mutation.
The recovered V3/RF code path is more specific: the final scalar used in the
RF-ready matrix is not a plain unweighted sum of neighbor entropy changes.

## Current Code-Level Interpretation

For each selected neighbor `j`, the local entropy-change term is:

```text
entropy_change[j] = H(P_j(MT center)) - H(P_j(WT center))
```

The RF input uses the V2 backward-weighted form:

```text
feature_B_candidate =
    sum_j entropy_change[j] * sigmoid(||M_j(WT center)|| / ||M_j(MT center)||)
```

In code, this corresponds to:

```text
V2_backward_weighted_neighbor_entropy_changes
```

and it is the value appended into the RF matrix in the final A-H workflow.

## Important Caution

Feature B should not be described simply as "neighbor entropy-change sum" unless
the weighting choice is explicitly discussed.

The current recovered implementation also preserves the historical notebook
array-shape behavior during V3 feature reconstruction. In
`pmpnn_ddg/engineered_features.py`, the message-norm-ratio
weights are intentionally not flattened because that preserves the saved V3
pickle values. Any future cleanup that changes this behavior must be treated as
a deliberate method revision, not as historical recovery.

## Relationship To Other Notes

- `V3_NEIGHBOR_VECTOR_EXTRACTION_SEMANTICS.md` explains where
  `P_j(WT center)`, `P_j(MT center)`, `M_j(WT center)`, and
  `M_j(MT center)` come from.
- `FORWARD_REVERSE_AUGMENTATION_FEATURE_SEMANTICS.md` records that the
  weighted neighbor entropy-change scalar is sign-flipped in the synthetic
  reverse row.
