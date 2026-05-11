# Algorithmic Deliberations

Purpose: capture scientific and method-level issues that arise while recovering
the ProteinMPNN-DDG pipeline.

This directory is separate from:

- `manuscript_inventory_analysis/`, which inventories manuscript files.
- `manuscript_codebase_mapping/`, which maps manuscript claims, tables, and
  figures to code and artifacts.
- `pickle_analysis/`, which records artifact-level pickle inspection.

Use this directory for questions that may matter scientifically even after the
historical pipeline is recovered. These notes should be written tightly enough
to support future manuscript revision, reviewer response planning, and method
design decisions.

Each note should state:

1. The precise algorithmic question.
2. The current conclusion.
3. What is directly observed from code or experiments.
4. What is inferred from the observation.
5. What remains unresolved.

Current notes:

- `ALGORITHMIC_SESSION_START.md`: startup handoff for the Algorithmic Codex
  session and Git worktree, including the current proven boundary, unresolved
  direct-tensor segment, initial questions, and runtime note.
- `FEATURE_E_MESSAGE_KPCA_AND_AUGMENTATION.md`: scientific/method note on
  feature E as message-KPCA in the augmented RF matrix, K-neighbor tensor-bundle
  semantics, and why pre-augmentation column numbers caused confusion.
- `RANDOM_DECODER_ORDER_SINGLE_MUTATION_MASKING.md`: why random decoder order
  can affect ProteinMPNN-DDG tensor extraction even when exactly one residue is
  designable.
