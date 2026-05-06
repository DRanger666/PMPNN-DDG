# Workspace Git Tracking Policy

Date: 2026-05-06

This repository is a local-only provenance repo for the
`github_account_history_porting_2022_continuation` workspace.

## Track

- Workspace notes and decision records.
- Tooling created for inventory, manuscript extraction, and provenance checks.
- Generated inventory TSVs and source-only notebook exports.
- Rsync manifests and logs documenting copied evidence provenance.
- Small text summaries derived from controlled inspection of old artifacts.

## Do Not Track By Default

- Copied Drive evidence payloads under
  `drive_evidence_copy/sajidahmedprotres_drive/`.
- Nested cloned repositories under `source_repos/`.
- Binary model/result artifacts such as pickle, NumPy, PyTorch, or joblib files.
- Runtime scaffolding under `.agents/` and `.codex/`.

## Promotion Rule

If a normally ignored artifact becomes important, promote it deliberately in a
separate commit with a commit message explaining:

1. why the artifact is needed,
2. how large it is,
3. whether it is source evidence, generated evidence, or publishable output,
4. whether it can be regenerated.

## Sandbox Note

Inside the current Codex sandbox, `.git` may appear as an empty read-only
`tmpfs` mountpoint. The real `.git` directory exists outside that sandbox mask.
For root-level Git commands from Codex, run Git outside the sandbox when normal
`git status` reports that the workspace is not a repository.

