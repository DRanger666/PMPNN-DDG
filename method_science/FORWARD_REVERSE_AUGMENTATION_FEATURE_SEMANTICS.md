# Forward-Reverse Augmentation Feature Semantics

Date: 2026-05-12

Status: active scientific/method note. This is not a final manuscript claim.

## Purpose

This note records the feature-orientation rules used when a real forward
mutation row `WTPosMT` is paired with a synthetic reverse row `MTPosWT` in the
RF-ready augmented matrix.

It is separate from the feature-E note because the same forward/reverse
orientation logic affects features B, C, D, E, PSSM-difference features, and
the target DDG label.

## Raw Vector Sign Convention

The raw vector convention is:

```text
neighbor_embedding_change[j] = E_j(WT center) - E_j(MT center)
neighbor_message_change[j]   = M_j(WT center) - M_j(MT center)
```

For the synthetic reverse mutation `MTPosWT`, WT-center and MT-center swap.
Therefore, the reverse-oriented raw vectors are algebraically the negative of
the forward-oriented raw vectors:

```text
reverse_embedding_change[j] = -neighbor_embedding_change[j]
reverse_message_change[j]   = -neighbor_message_change[j]
```

This is why the RF matrix-construction notebook builds reverse-oriented
embedding/message PCA and KPCA inputs from `-1 *` the forward raw vectors.

## Scalar Versus Raw-Vector Behavior

The sign flip applies to raw vector ingredients before PCA/KPCA projection.
It should not be applied blindly to every scalar feature.

Feature D is the important example. The manuscript defines D as a sum of L2
norms:

```text
D = sum_j ||E_j(WT center) - E_j(MT center)||_2
```

Since norms are sign-invariant, scalar D is unchanged in the reverse row. The
raw embedding vectors used for projection can change sign; the scalar D column
does not.

## Observed Reverse-Row Rules

The final RF matrix-construction code builds a forward row and then a synthetic
reverse row. For the non-PCA/non-KPCA scalar block, the observed rules include:

```text
DDG label                          -> sign flip
feature A                          -> sign flip
center entropy                     -> unchanged
weighted neighbor energy change    -> sign flip
neighbor forward/backward KL       -> swap
PSSM difference                    -> sign flip
weighted neighbor entropy change   -> sign flip
message norm ratio                 -> reciprocal
scalar feature D                   -> unchanged
wild/alternate PSSM scalar fields  -> swap
```

For PCA/KPCA blocks:

```text
reverse embedding PCA/KPCA -> transform sign-flipped raw embedding changes
reverse message PCA/KPCA   -> transform sign-flipped raw message changes
```

## Working Rule

When discussing forward/reverse augmentation, specify whether the object is:

- a raw vector difference;
- a scalar norm or entropy/energy/KL summary;
- a PCA/KPCA projection derived from raw vector differences;
- the augmented RF matrix row itself.

Do not say "the feature is multiplied by -1" unless the specific feature and
matrix stage are named.
