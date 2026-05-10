# Codex Session And Git Worktree Separation

Date: 2026-05-10

Purpose: prevent ambiguity between Codex conversation forks and Git
branch/worktree separation while the ProteinMPNN-DDG project splits into a main
recovery track and a focused algorithmic-deliberation track.

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
- **Algorithmic Codex session**: a future Codex session fork dedicated to
  algorithmic analysis, tensor-generation implications, robustness experiments,
  and method-design thinking.
- **Algorithmic Git worktree branch**: the dedicated Git worktree plus branch
  used by the Algorithmic Codex session.

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
| Algorithmic deliberation | Codex session fork | `/home/mpr/proteinmpnn_ddg_algorithmic_deliberations` | `algorithmic-deliberations` | study tensor-generation design, implications, robustness, and future framing |

The Algorithmic Codex session should own new work under
`algorithmic_deliberations/` and any clearly labeled algorithmic experiment
artifacts. It should not silently rewrite historical recovery conclusions.

The Main recovery session should continue owning manuscript-code mapping,
pickle provenance, recovery scripts, and synthesis decisions that depend on
historical evidence.

## Setup Sequence

Before creating the Algorithmic Codex session:

1. Ensure the current workspace is clean.
2. Push local commits from `main`.
3. Create a separate Git worktree checked out to the
   `algorithmic-deliberations` branch.
4. Resolve the current Codex session UUID from local session metadata.
5. Launch the Codex session fork with `-C` pointing at the algorithmic
   worktree.

Command shape, with the UUID verified at execution time:

```bash
codex fork -C /home/mpr/proteinmpnn_ddg_algorithmic_deliberations <current-session-uuid>
```

Do not infer the session UUID from chat memory. Verify it from local Codex
session metadata before emitting the final command.

## Communication Between Tracks

Communication should happen through durable artifacts first:

- commits;
- notes under `algorithmic_deliberations/`;
- operating notes under `workspace_operations/`;
- explicit prompts from the user pointing one session to the other session's
  notes or commits.

The main recovery session can inspect the algorithmic worktree when needed, but
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
`algorithmic-deliberations` just because both branches share repository
history.

## Merge Discipline

The Algorithmic Codex session may produce method notes or experiments that are
scientifically valuable but not historical evidence.

Before merging anything from the algorithmic branch into `main`, classify the
change:

- Historical recovery evidence -> merge only if it strengthens provenance or
  reproduction.
- Algorithmic method note -> merge if it belongs in the shared scientific
  deliberation record.
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
git branch --list algorithmic-deliberations
```

The intended algorithmic worktree path is:

```text
/home/mpr/proteinmpnn_ddg_algorithmic_deliberations
```

The exact Codex session UUID must still be verified from local Codex session
metadata immediately before emitting or running a `codex fork` command.
