# Codex Session And Git Worktree Separation

Date: 2026-05-12

Purpose: prevent ambiguity between Codex conversation forks and Git
branch/worktree separation while the ProteinMPNN-DDG project splits into a main
recovery track and a focused V3 direct-tensor extraction reconciliation track.

## Stable Terms

Use these terms consistently.

- **Codex session fork**: a fork of the conversation/context. It changes the
  assistant's conversational state in a terminal. It does not create, select, or
  modify a Git branch by itself.
- **Git branch**: a version-control line inside the repository.
- **Git worktree**: a separate filesystem checkout of the same repository,
  usually checked out to a dedicated Git branch.
- **Main recovery session**: this Codex session, responsible for the whole
  manuscript/recovery/reproduction view.
- **V3 tensor-reconciliation Codex session**: a future Codex session fork
  dedicated to the unresolved upstream V3 direct-tensor extraction problem,
  including random decoder order, directed neighbor asymmetry, tensor-value
  mismatch, and scientifically defensible stabilization.
- **V3 tensor-reconciliation Git worktree branch**: the dedicated Git worktree
  plus branch used by the V3 tensor-reconciliation Codex session.

Avoid the phrase "branch fork" without qualification. Say either "Codex session
fork" or "Git branch/worktree".

## Core Rule

A Codex session fork and a Git branch are separate layers.

A Codex session fork must be deliberately launched with `-C` pointing at the
intended filesystem checkout. It does not automatically create a Git branch, and
it does not automatically move to a different Git worktree.

## Intended Operating Model

The project should run with two coordinated but separated workspaces:

| Role | Codex session | Filesystem checkout | Git branch | Primary goal |
| --- | --- | --- | --- | --- |
| Main recovery | current session | `/home/mpr/github_account_history_porting_2022_continuation` | `main` | recover/reproduce 2022 manuscript evidence and artifact provenance |
| V3 tensor reconciliation | Codex session fork | `/home/mpr/proteinmpnn_ddg_v3_tensor_extraction_reconciliation` | `v3-tensor-extraction-reconciliation` | reconcile saved V3 direct tensor fields with manuscript logic and executable ProteinMPNN-DDG tensor-extraction code |

The V3 tensor-reconciliation Codex session should own focused work under
`v3_tensor_extraction_reconciliation/` and any clearly labeled tensor
reconciliation experiment artifacts. It should not silently rewrite historical
recovery conclusions.

The Main recovery session should continue owning manuscript-code mapping,
pickle provenance, recovery scripts, durable method-science notes under
`method_science/`, and synthesis decisions that depend on historical evidence.

## Setup Sequence

Before creating the V3 tensor-reconciliation Codex session:

1. Ensure the current workspace is clean.
2. Push local commits from `main`.
3. Create a separate Git worktree checked out to the
   `v3-tensor-extraction-reconciliation` branch.
4. Resolve the current Codex session UUID from local session metadata.
5. Launch the Codex session fork with `-C` pointing at the V3
   tensor-reconciliation worktree.

Command shape, with the UUID verified at execution time:

```bash
codex fork -C /home/mpr/proteinmpnn_ddg_v3_tensor_extraction_reconciliation <current-session-uuid>
```

Do not infer the session UUID from chat memory. Verify it from local Codex
session metadata before emitting the final command.

## Communication Between Tracks

Communication should happen through durable artifacts first:

- commits;
- focused reconciliation notes under `v3_tensor_extraction_reconciliation/`;
- durable scientific method notes under `method_science/`;
- operating notes under `workspace_operations/`;
- explicit prompts from the user pointing one session to the other session's
  notes or commits.

The main recovery session can inspect the reconciliation worktree when needed, but
it should treat that work as a separate line of inquiry until deliberately
merged.

## Path Discipline

The two-worktree setup depends on path discipline. Repository-internal notes and
script defaults should use paths relative to the current worktree unless an
absolute machine path is intentionally required.

Use:

- `PATH_REFERENCE_DISCIPLINE.md` for relative-path and absolute-path rules;
- `RUNTIME_ENVIRONMENT.md` for the shared main-workspace venv rule.

## Workspace Map Discipline

`WORKSPACE_MAP.md` is a first-navigation helper for the physical worktree root
where it lives.

Once two Git worktrees have different root-level files or directories, their
`WORKSPACE_MAP.md` files should diverge deliberately. Each map should describe
the root items that actually exist in that physical checkout, including ignored
local items when they are important for navigation.

Do not force identical workspace maps across `main` and
`v3-tensor-extraction-reconciliation` just because both branches share
repository history.

## Merge Discipline

The V3 tensor-reconciliation Codex session may produce method notes or
experiments that are scientifically valuable but not historical evidence.

Before merging anything from the V3 tensor-reconciliation branch into `main`,
classify the change:

- Historical recovery evidence -> merge only if it strengthens provenance or
  reproduction.
- Durable method-science note -> merge if it belongs in the shared scientific
  method record under `method_science/`.
- Focused V3 tensor-reconciliation note -> merge if it should be visible to the
  main recovery track as part of the unresolved direct-tensor evidence.
- Experimental output -> merge only if small, interpretable, and needed for a
  durable conclusion; otherwise keep generated outputs local or summarized.
- Manuscript-facing decision -> defer until synthesis work explicitly uses both
  recovery evidence and algorithmic analysis.

## Status Verification

Do not rely on this note as proof of current Git or Codex state. Verify the
state directly before acting.

Useful checks:

```bash
git status --short --branch
git worktree list
git branch --list v3-tensor-extraction-reconciliation
```

The current V3 tensor-reconciliation worktree path is:

```text
/home/mpr/proteinmpnn_ddg_v3_tensor_extraction_reconciliation
```

The exact Codex session UUID must still be verified from local Codex session
metadata immediately before emitting or running a `codex fork` command.
