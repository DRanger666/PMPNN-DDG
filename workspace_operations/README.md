# Workspace Operations

Purpose: workspace-level operating records for the ProteinMPNN-DDG continuation
effort.

Use this directory for decisions and rules that govern how the workspace is
operated across multiple evidence areas.

This directory must stay clean. It is not a generic notes folder.

Belongs here:

- workstream boundaries;
- current recovery-boundary summaries;
- Codex-session and Git-worktree coordination rules;
- path-reference discipline for relative paths, absolute paths, and
  cross-worktree write safety;
- package-role and update-discipline decisions;
- runtime-environment operating contracts;
- Git-tracking policy and other workspace-wide operating constraints;
- concise status summaries, if later needed, that point to detailed evidence
  instead of duplicating it.

Does not belong here:

- manuscript-folder inventories;
- manuscript-to-code mapping evidence;
- pickle analysis outputs;
- scientific/method deliberation notes;
- generated data tables;
- one-off scratch notes.

If information is important but would clutter this directory, create or use a
more specific home for it and make the route visible from `WORKSPACE_MAP.md`.

Current documents:

- `CURRENT_RECOVERY_BOUNDARY.md`: states the current reproduced segment, the
  unresolved direct-tensor segment, and the main/fork work ownership boundary.
- `WORKSTREAM_SEPARATION.md`: separates historical recovery/reproduction,
  algorithm design/implication analysis, and later manuscript synthesis.
- `CODEX_SESSION_AND_GIT_WORKTREE_SEPARATION.md`: defines the two-Codex-session
  and two-Git-worktree/branch operating plan, with terminology rules.
- `PATH_REFERENCE_DISCIPLINE.md`: defines when to use relative paths, when
  absolute paths are justified, and how scripts should avoid writing into the
  wrong worktree.
- `RECOVERY_PACKAGE_ROLE.md`: defines the role, boundaries, and update
  discipline for the `proteinmpnn_ddg_recovery/` Python package.
- `RUNTIME_ENVIRONMENT.md`: defines the role, inspection commands, and update
  discipline for the local Python runtime used by recovery/reproduction work.
- `WORKSPACE_GIT_TRACKING.md`: defines tracked versus ignored workspace
  artifacts and the promotion rule for normally ignored evidence.
