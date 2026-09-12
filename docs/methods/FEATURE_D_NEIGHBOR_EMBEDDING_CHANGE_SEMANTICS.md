# Feature D Neighbor-Embedding Change Semantics

Date: 2026-05-12

Status: active scientific/method note. This is not a final manuscript claim.

## Purpose

This note records the feature-D distinction between raw neighbor-embedding
difference vectors and the scalar feature D used in the RF-ready matrix.

## Current Interpretation

For each selected neighbor `j`, the raw embedding-change vector is:

```text
embedding_change[j] = E_j(WT center) - E_j(MT center)
```

The scalar feature D is the sum of L2 norms of those per-neighbor differences:

```text
D = sum_j ||E_j(WT center) - E_j(MT center)||_2
```

Therefore, feature D summarizes the magnitude of neighbor-embedding change
caused by the center mutation, not the signed direction of that change.

## Forward/Reverse Consequence

For the synthetic reverse mutation `MTPosWT`, the raw embedding-change vector
changes sign:

```text
reverse_embedding_change[j] = -embedding_change[j]
```

But scalar D is sign-invariant because it is norm-based:

```text
||-embedding_change[j]||_2 = ||embedding_change[j]||_2
```

So the reverse augmented row keeps scalar D unchanged. This is different from
raw embedding vectors that are later used for PCA/KPCA-style projection blocks,
where sign reversal matters.

## Relationship To Other Notes

- `V3_NEIGHBOR_VECTOR_EXTRACTION_SEMANTICS.md` explains where the WT-center and
  MT-center neighbor embeddings come from.
- `FORWARD_REVERSE_AUGMENTATION_FEATURE_SEMANTICS.md` records the broader
  reverse-row transformation rules.
