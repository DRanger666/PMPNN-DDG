# Method Science Notes

Purpose: durable scientific notes for the ProteinMPNN-DDG method.

This directory is for method definitions, feature semantics, reviewer-facing
scientific reasoning, pseudocode seeds, and diagram seeds that should remain
useful after historical recovery is complete.

It is separate from:

- `manuscript_codebase_mapping/`, which records evidence linking manuscript
  claims, tables, figures, notebooks, code, and artifacts.
- `pickle_analysis/`, which records artifact-level pickle inspection.
- `v3_tensor_extraction_reconciliation/`, which focuses on the unresolved
  upstream direct-tensor extraction mismatch.

Use this directory when a finding is scientifically durable, even if the
finding first appeared during recovery work.

Current notes:

- `V3_NEIGHBOR_VECTOR_EXTRACTION_SEMANTICS.md`: center-designable plus
  one-selected-neighbor-designable-at-a-time extraction semantics that feed
  features B, C, D, and E.
- `FORWARD_REVERSE_AUGMENTATION_FEATURE_SEMANTICS.md`: feature-orientation
  rules for synthetic reverse rows, including sign flips, swaps, reciprocals,
  and the distinction between raw vector differences and scalar features.
- `FEATURE_B_WEIGHTED_NEIGHBOR_ENTROPY_SEMANTICS.md`: feature B as recovered
  from the code path, including the message-norm-ratio weighting caveat.
- `FEATURE_D_NEIGHBOR_EMBEDDING_CHANGE_SEMANTICS.md`: feature D as a
  sign-invariant norm-sum over raw neighbor-embedding difference vectors.
- `FEATURE_E_MESSAGE_KPCA_AUGMENTED_MATRIX_SEMANTICS.md`: feature E as
  message-KPCA in the augmented RF matrix, including the pre-augmentation versus
  post-augmentation column-number distinction.
