# V3 Tensor Extraction Reconciliation

Purpose: focus the dedicated fork/worktree effort on the unresolved upstream
V3 direct-tensor extraction problem.

This directory is separate from:

- `manuscript_inventory_analysis/`, which inventories manuscript files.
- `manuscript_codebase_mapping/`, which maps manuscript claims, tables, and
  figures to code and artifacts.
- `pickle_analysis/`, which records artifact-level pickle inspection.
- `method_science/`, which stores durable scientific method notes that should
  remain useful after historical recovery is complete.

Use this directory for the focused reconciliation problem:

```text
PDB
+ mutation table
+ ProteinMPNN weights/code
+ RNG/order behavior
-> saved V3 direct tensor fields
```

This includes random decoder order, directed neighbor asymmetry, attended
neighbor ranking, tensor-value mismatch, and diagnostic variants that help
separate candidate historical behavior from future method design.

Each note should state:

1. The precise algorithmic question.
2. The current conclusion.
3. What is directly observed from code or experiments.
4. What is inferred from the observation.
5. What remains unresolved.

Current notes:

- `V3_TENSOR_RECONCILIATION_SESSION_START.md`: startup handoff for the V3
  tensor-reconciliation Codex session and Git worktree, including the current
  proven boundary, unresolved direct-tensor segment, initial questions, and
  runtime note.
- `RANDOM_DECODER_ORDER_SINGLE_MUTATION_MASKING.md`: why random decoder order
  can affect ProteinMPNN-DDG tensor extraction even when exactly one residue is
  designable.
