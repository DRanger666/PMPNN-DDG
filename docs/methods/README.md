# Method Science Notes

Purpose: durable scientific notes for the ProteinMPNN-DDG method.

This directory is for method definitions, feature semantics, reviewer-facing
scientific reasoning, pseudocode seeds, and diagram seeds that should remain
useful after historical recovery is complete.

It is separate from `manuscript_codebase_mapping/`, which records evidence
linking manuscript claims, tables, figures, code, and regenerated artifacts.

**Note:** `v3_tensor_extraction_reconciliation/` and pickle-inventory trees are
**not** active goals on this branch. Byte-identical historical V3 extraction is
retired as a success criterion; see
`manuscript_codebase_mapping/REPRODUCTION_BAR_NOT_BYTE_IDENTICAL_V3.md`.
Filenames below still say “V3” where they discuss neighbor-extraction semantics
recovered from that era — that is naming history, not a call to re-reconcile
pickles.

Current notes:

- `V3_NEIGHBOR_VECTOR_EXTRACTION_SEMANTICS.md`: center-designable plus
  one-selected-neighbor-designable-at-a-time extraction semantics that feed
  features B, C, D, and E.
- `V3_DIRECTED_NEIGHBOR_ASYMMETRY_SEMANTICS.md`: directed top-k graph
  asymmetry between neighbor-to-center selection messages and
  center-to-neighbor feature messages.
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
