# Workspace Operations

Purpose: workspace-level operating records for the ProteinMPNN-DDG continuation
effort.

Use this directory for decisions and rules that govern how the workspace is
operated across multiple evidence areas.

This directory must stay clean. It is not a generic notes folder.

Belongs here:

- workstream boundaries;
- Codex-session and Git-worktree coordination rules;
- package-role and update-discipline decisions;
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

Current documents:

- `WORKSTREAM_SEPARATION.md`: separates historical recovery/reproduction,
  algorithm design/implication analysis, and later manuscript synthesis.
- `CODEX_SESSION_AND_GIT_WORKTREE_SEPARATION.md`: defines the two-Codex-session
  and two-Git-worktree/branch operating plan, with terminology rules.
- `RECOVERY_PACKAGE_ROLE.md`: defines the role, boundaries, and update
  discipline for the `proteinmpnn_ddg_recovery/` Python package.
- `WORKSPACE_GIT_TRACKING.md`: defines tracked versus ignored workspace
  artifacts and the promotion rule for normally ignored evidence.
