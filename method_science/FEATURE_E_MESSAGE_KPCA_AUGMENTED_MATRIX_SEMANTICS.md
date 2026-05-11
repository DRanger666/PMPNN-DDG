# Feature E Message-KPCA Augmented-Matrix Semantics

Date: 2026-05-11

Status: active scientific/method note. This is not a final manuscript claim.

## Question

How should feature E be understood scientifically and operationally, given that
the V3 pickles do not store final RF-ready E columns, and the final RF notebook
uses augmented matrix columns `31..35`?

## Current Answer

Feature E should be treated as a downstream RF-matrix feature family derived
from center-to-neighbor message-change tensors, not as a field directly saved
inside the V3 pickle.

The current code-level evidence says the final A-H random-forest workflow
selects feature E from `S_*_X_aug[:, 31:36]`. Those columns are message-KPCA
slots after augmentation/column compaction.

This matters because pre-augmentation and post-augmentation column numbers do
not mean the same thing.

## Feature-E Raw Ingredient

For one real mutation entry, such as `WTPosMT`, the V3 pickle stores a paired
WT-center vs MT-center K-neighbor message bundle. It does not store one
message vector per mutation.

For K selected neighbors, usually K = 15 in the inspected Ssym/V3 artifacts,
the feature-E-relevant conceptual shapes are:

```text
neighbor_w_message_vector_coming_from_center   K x 128
neighbor_m_message_vector_coming_from_center   K x 128
```

Thus, the feature-E raw ingredient is a K x 128 matrix of center-to-neighbor
message differences:

```text
message_change[j] = M_j(WT center) - M_j(MT center)
for j = 1..K
```

The extraction-pass semantics for producing these K-neighbor tensors are
recorded in `V3_NEIGHBOR_VECTOR_EXTRACTION_SEMANTICS.md`.

The forward/reverse sign and row-orientation rules are recorded in
`FORWARD_REVERSE_AUGMENTATION_FEATURE_SEMANTICS.md`.

## Feature E Construction

The final notebook first builds a staging matrix `S_*_X`. That matrix contains
both direct-oriented and reverse-oriented PCA/KPCA blocks.

In the staging matrix:

```text
raw 11..15 = forward neighbor-embedding PCA
raw 16..25 = forward neighbor-embedding KPCA
raw 26..30 = reverse-oriented neighbor-embedding PCA
raw 31..40 = reverse-oriented neighbor-embedding KPCA
raw 41..45 = forward message PCA
raw 46..55 = forward message KPCA
raw 56..60 = reverse-oriented message PCA
raw 61..70 = reverse-oriented message KPCA
```

The RF notebook then builds an augmented matrix `S_*_X_aug` where each real
mutation contributes two rows:

```text
forward row: label = ddg
reverse row: label = -ddg
```

The augmented matrix has a shared column schema for both orientations. During
augmentation/column compaction:

```text
aug 0..10  = scalar/PSSM features in current row orientation
aug 11..15 = neighbor-embedding PCA in current row orientation
aug 16..25 = neighbor-embedding KPCA in current row orientation
aug 26..30 = message PCA in current row orientation
aug 31..40 = message KPCA in current row orientation
```

Therefore, feature E in the final A-H RF feature map:

```text
E = augmented columns 31..35
```

means the first five message-KPCA components in the current row orientation.

For forward rows, those values come from the forward message-KPCA block. For
synthetic reverse rows, those values come from the reverse-oriented
message-KPCA block.

## Why The Column Confusion Happened

The same numeric column label, `31..35`, refers to different matrices depending
on stage:

- In `S_*_X`, columns `31..35` are inside the reverse-oriented
  neighbor-embedding KPCA block.
- In `S_*_X_aug`, columns `31..35` are inside the message-KPCA block used by
  the final RF feature map.

The final RF loop trains on `S_2648_X_aug[:, f_index_comb]`, so the augmented
matrix interpretation is the relevant one for Table 1 and Figure 6.

## Scientific Implication

This resolves the immediate manuscript-code tension at the feature-family
level: the final A-H model input appears aligned with the manuscript statement
that feature E is based on center-to-neighbor message-change KPCA.

It does not prove full RF-ready feature-matrix reproduction yet, because V3
does not store final E columns. The V3 pickle stores the upstream K-neighbor
message-change ingredients from which E can be reconstructed.

## Current Evidence

Observed from code:

- The V3 field-reconstruction experiment matched
  `neighbor_message_change_m_w_raw` for all inspected Ssym entries.
- The final RF notebook constructs both direct and reverse message-KPCA blocks.
- The RF feature map is applied to `S_*_X_aug`, not `S_*_X`.
- `S_*_X_aug[:, 31:41]` is populated from message-KPCA blocks.

Inferred from those observations:

- Feature E for the final A-H workflow is message-KPCA in the RF input.
- Reverse augmentation is a row-orientation transformation, not a separate
  saved V3 artifact.

## Remaining Checks

1. Implement the staging-matrix and augmented-matrix construction in
   `proteinmpnn_ddg_recovery/` without training RF models yet.
2. Confirm matrix shapes, row identities, labels, and column blocks for all
   four datasets.
3. Confirm that `E = columns 31..35` pulls message-KPCA columns after
   augmentation.
4. Run structural checks on E columns: finite values, nonconstant columns,
   direct/reverse orientation behavior, and train/test-safe fitting of the
   scaler/KPCA only on S_2648.
5. Only after these pass, run repeated RF evaluation and compare against the
   recovered `list_incremental_feature_result_dict.pickle`, Table 1, and
   Figure 6 evidence.

## Working Rule

When discussing feature E, always specify the matrix being referenced:

- `S_*_X`: staging matrix before reverse augmentation.
- `S_*_X_aug`: RF input matrix after reverse augmentation.

Do not describe feature E by column number alone.
