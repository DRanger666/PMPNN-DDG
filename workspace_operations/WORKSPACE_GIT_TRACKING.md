# Workspace Git Tracking Policy

Date: 2026-05-11

This repository is a local-only provenance repo for the
`github_account_history_porting_2022_continuation` workspace.

## Track

- Workspace notes and decision records.
- Tooling created for inventory, manuscript extraction, and provenance checks.
- Generated inventory TSVs and source-only notebook exports.
- Rsync manifests and logs documenting copied evidence provenance.
- Small text summaries derived from controlled inspection of old artifacts.
- The cleaned manuscript evidence folder at
  `drive_evidence_copy/sajidahmedprotres_drive/MPNN_DDG_Manuscript/`, because
  the manuscript is the anchor artifact for recovery, reproduction, and
  algorithmic-deliberation work.
- The copied 2022 Colab notebook evidence folder at
  `drive_evidence_copy/sajidahmedprotres_drive/Colab Notebooks/`, because raw
  notebooks contain source cells, saved outputs, and metadata needed for
  code-provenance mapping and algorithmic recovery. The current snapshot is
  small enough to track directly.
- The selected ACCRE dataset-input snapshot at
  `drive_evidence_copy/sajidahmedprotres_drive/ACCRE_PyRun_Setup/`, because it
  contains dataset PDB files, PSSM files, and the S_669 mutation/prediction CSV
  needed for ProteinMPNN-DDG reproduction attempts. This local directory is not
  a full mirror of the original FUSE-mount folder with the same name.
- Narrowly promoted Protein_MPNN_Digging recovery artifacts, tracked with Git
  LFS rather than regular Git:
  `S_2648_pmppn_info_dict_V3.pickle`, `S_669_pmppn_info_dict_V3.pickle`,
  `S_921_pmppn_info_dict_V3.pickle`, `Ssym_pmppn_info_dict_V3.pickle`, and
  `reproduction_inputs/proteinmpnn_checkpoints/vanilla_model_weights/v_48_020.pt`.
  The checkpoint is a byte-identical curated copy from the nested historical
  ProteinMPNN checkout, because files inside an embedded Git repository cannot
  be safely promoted as ordinary files in the parent workspace repo.

## Do Not Track By Default

- Copied Drive evidence payloads under
  `drive_evidence_copy/sajidahmedprotres_drive/`, except explicitly promoted
  evidence such as the cleaned manuscript folder, the copied Colab notebook
  folder, and the selected ACCRE dataset-input snapshot.
- Nested cloned repositories under `source_repos/`.
- Binary model/result artifacts such as pickle, NumPy, PyTorch, or joblib files.
  The only current exceptions are the explicitly promoted Git LFS files listed
  above.
- Runtime scaffolding under `.agents/` and `.codex/`.
- `RESUME_CODEX_THREAD.md`, because it is a workspace-local operational resume
  index. It must not propagate across branches, Git worktrees, clones, or
  unrelated physical workspaces.

## Resume Note Rule

`RESUME_CODEX_THREAD.md` is local runtime state, not repository evidence.

Keep it untracked and ignored locally. A separate physical workspace or Git
worktree should create its own resume note only when that note points to
sessions that are operationally relevant from that directory.

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
