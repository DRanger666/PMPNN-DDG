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

- `FEATURE_E_MESSAGE_KPCA_AND_AUGMENTATION.md`: feature E as message-KPCA in
  the augmented RF matrix, K-neighbor tensor-bundle semantics, and the
  pre-augmentation versus post-augmentation column-number distinction. Also
  records the raw vector sign convention for reverse augmentation and the
  distinction between sign-flipped raw embedding vectors and sign-invariant
  scalar feature D.
