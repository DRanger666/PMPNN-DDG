# V3 Tensor Extraction Reconciliation Session Start

Date: 2026-05-10

Purpose: startup note for the dedicated Codex session and Git worktree focused
on V3 direct-tensor extraction reconciliation. This note is a narrow handoff.
It is not a general project summary.

## Read First

Start with these files, in this order:

1. `workspace_operations/CURRENT_RECOVERY_BOUNDARY.md`
2. `workspace_operations/CODEX_SESSION_AND_GIT_WORKTREE_SEPARATION.md`
3. `workspace_operations/RUNTIME_ENVIRONMENT.md`
4. `workspace_operations/PATH_REFERENCE_DISCIPLINE.md`
5. `v3_tensor_extraction_reconciliation/RANDOM_DECODER_ORDER_SINGLE_MUTATION_MASKING.md`
6. `manuscript_codebase_mapping/tensor_extraction_codeblock_recovery/TENSOR_EXTRACTION_ALGORITHM_DEBUGGING.md`

## Current Proven Boundary

For Ssym, this segment has been reproduced at value level:

```text
saved Ssym V3 direct tensor fields
+ local Ssym PDB residue mapping
+ local Ssym PSSM files
-> saved Ssym V3 engineered/PSSM fields
```

That result does not prove full V3 pickle regeneration. It proves the
feature-construction segment starting from already-saved direct tensor fields.

## Reconciliation Work Target

The unresolved segment is:

```text
PDB
+ mutation table
+ ProteinMPNN weights/code
+ RNG/order behavior
-> saved V3 direct tensor fields
```

The dedicated session should study this direct-tensor segment and the method
choices around it. Its job is not to rewrite historical recovery claims.

## Initial Questions

1. Which ProteinMPNN tensor-extraction choices can explain the mismatch between
   recovered V6_V2-style tensors and saved V3 direct tensor fields?
2. How does random decoder order affect center-residue tensors, neighbor
   tensors, attended-neighbor ranking, and downstream scalar features?
3. What are the consequences of directed neighbor-graph asymmetry, especially
   when the center residue is absent from a selected neighbor's local
   neighborhood?
4. Which diagnostic variants can be tested without labeling them as historical
   evidence?
5. Which tensor-generation choices are scientifically defensible for a future
   ProteinMPNN-DDG method, even if they differ from the 2022 pipeline?

## Operating Rules

- Keep historical recovery evidence separate from algorithmic alternatives.
- Label every diagnostic variant as diagnostic, candidate-historical, or future
  method design.
- Keep generated outputs small, summarized, or intentionally ignored unless a
  result must be preserved.
- Record direct-tensor reconciliation reasoning under
  `v3_tensor_extraction_reconciliation/`.
- Record durable scientific method notes under `method_science/`.
- Communicate back to the main recovery track through notes and commits.
- Assume the user is working interactively with the forked session; do not treat
  this as an autonomous background worker.

## Runtime Note

The runtime contract is documented in
`workspace_operations/RUNTIME_ENVIRONMENT.md`.

The canonical environment currently lives in the main workspace:

```text
/home/mpr/github_account_history_porting_2022_continuation/.venv_proteinmpnn_ddg_reproduction/
```

Because Git worktrees do not copy ignored virtual environments, the algorithmic
worktree may not contain its own `.venv_proteinmpnn_ddg_reproduction/`
directory. For initial read-only or diagnostic runs, use the main workspace
venv by absolute path, or deliberately create a separate equivalent venv in the
algorithmic worktree and record that decision.

Do not silently install packages into the main workspace venv from the
algorithmic worktree.

Also follow `workspace_operations/PATH_REFERENCE_DISCIPLINE.md`: repository
paths should usually be relative to the current worktree, while absolute paths
should be reserved for live mounts, separate worktree locations, shared runtime
environments, and exact command lines where the physical location is the point.
