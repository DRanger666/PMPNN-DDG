# Path Reference Discipline

Date: 2026-05-12

Purpose: prevent accidental cross-worktree writes now that the project uses a
main recovery worktree and a separate V3 tensor-reconciliation worktree.

## Rule

Use workspace-relative paths by default in notes, scripts, reports, and command
examples for files that live inside this repository checkout.

Use absolute paths only when the physical machine location is part of the
meaning.

## Relative Paths

Use relative paths for repository-internal material:

```text
scripts/...
proteinmpnn_ddg_recovery/...
workspace_operations/...
method_science/...
v3_tensor_extraction_reconciliation/...
manuscript_codebase_mapping/...
pickle_analysis/...
drive_evidence_copy/sajidahmedprotres_drive/...
```

These paths should mean "inside the current Git worktree", whether the current
worktree is the main recovery checkout or the V3 tensor-reconciliation checkout.

## Allowed Absolute Paths

Absolute paths are appropriate for:

- live source mounts, for example `/home/mpr/sajidahmedprotres_drive`;
- separate Git worktree locations, for example
  `/home/mpr/proteinmpnn_ddg_v3_tensor_extraction_reconciliation`;
- shared runtime environments, for example the main-workspace venv path used
  by the V3 tensor-reconciliation worktree before it has its own venv;
- exact shell commands where the filesystem location is the point;
- source/copy comparisons where both the live source and local copied evidence
  path must be shown.

When a note uses an absolute path, it should be clear why that path is
machine-location-specific.

## Script Defaults

Runnable scripts should not hardcode the main workspace directory unless they
are intentionally pinned to the main recovery checkout.

Preferred pattern:

```python
WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
```

or explicit CLI arguments for input/output locations.

This lets the same tracked script run inside either Git worktree without
silently writing into the other checkout.

## Shared-Write Caution

The two Git worktrees prevent ordinary working-directory interference. They do
not isolate writes to machine-global paths.

Be careful with:

```text
/home/mpr/sajidahmedprotres_drive
/home/mpr/github_account_history_porting_2022_continuation/.venv_proteinmpnn_ddg_reproduction
/tmp
/home/mpr/.cache
/home/mpr/.codex_apos
```

The live Drive mount should remain source-only unless the user explicitly asks
for a write. The shared venv can be used to run code, but dependency changes
must be recorded before they are made from either worktree.
