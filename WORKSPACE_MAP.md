# ProteinMPNN-DDG Workspace Map

Date: 2026-05-12

Purpose: first-navigation helper for this physical workspace root:
`/home/mpr/github_account_history_porting_2022_continuation`.

This file should answer one question quickly: what does each root-level item do,
and where should a person go next? It is not a status log, evidence notebook, or
decision archive.

## Maintenance Rule

Keep this file current whenever a root-level file or directory in this physical
worktree is created, renamed, moved, or given a new role.

If a root-level item cannot be described here with a clear and useful purpose,
move it to the right subdirectory, rename it, or remove it from the durable
workspace.

## Root Directories

- `code_inventory_analysis/`
  - Generated inventories and summary notes about the old ProteinMPNN fork,
    copied code evidence, notebook/source relationships, and source-repo
    provenance.

- `colab_notebooks_inventory_analysis/`
  - Generated inventories, source exports, output-text exports, and
    cross-comparisons for copied 2022 Colab notebooks and Git-side notebooks.

- `drive_evidence_copy/`
  - Timestamp-preserving local evidence-copy manifests, rsync logs, and copied
    Drive payloads. The cleaned manuscript evidence folder, copied Colab
    notebooks, and selected ACCRE dataset-input snapshot under
    `drive_evidence_copy/sajidahmedprotres_drive/` are deliberately tracked.
    The local ACCRE snapshot is not a full mirror of the original FUSE-mount
    folder. The four promoted `Protein_MPNN_Digging/*_pmppn_info_dict_V3.pickle`
    files are tracked with Git LFS because they are dataset-specific
    recovery/reproduction reference artifacts. The promoted
    `Protein_MPNN_Digging/list_incremental_feature_result_dict.pickle` file is
    tracked with Git LFS because it is the recovered final RF result artifact
    for the Table 1 and Figure 6 evidence layer. Other bulk copied payloads
    remain ignored unless explicitly promoted for a concrete recovery need.

- `external_reference_structures/`
  - Downloaded external reference structure/metadata checks used to interpret
    historical dataset issues, currently including the S_669 `3DV0` reference
    check.

- `manuscript_codebase_mapping/`
  - Evidence linking manuscript numbers, figures, tables, notebook cells,
    pickles, datasets, and upstream ProteinMPNN-derived artifacts.

- `manuscript_inventory_analysis/`
  - Inventory of copied manuscript-folder contents, extracted text, document
    metadata, tracked-change/comment artifacts, comparisons, and manuscript
    file relationships.

- `method_science/`
  - Durable scientific method notes for ProteinMPNN-DDG: feature semantics,
    algorithmic interpretation, reviewer-facing reasoning, and pseudocode or
    diagram seeds that should remain useful beyond the recovery stage.

- `pickle_analysis/`
  - Pickle inspection reports, schema/field summaries, instance-coverage notes,
    mutation-table audits, and value-comparison outputs.

- `proteinmpnn_ddg_recovery/`
  - Workspace-local Python package for recovered ProteinMPNN-DDG reproduction
    code. Scripts import reusable recovery logic from here; edits can change
    downstream script behavior.

- `reproduction_inputs/`
  - Local input tables and manifests needed for reproduction attempts, including
    mutation/DDG tables for S_2648, S_669, S_921, and Ssym, plus the curated
    Git-LFS-tracked ProteinMPNN `v_48_020.pt` checkpoint used as the current
    tensor-extraction model input.

- `scripts/`
  - Runnable analysis, audit, comparison, and reproduction scripts. Reusable
    logic should live in `proteinmpnn_ddg_recovery/`, not be duplicated across
    scripts.

- `source_repos/`
  - Local clones of source/reference repositories used as evidence inputs.
    Nested repository contents are ignored by this workspace Git repo unless a
    small derived note or manifest is deliberately tracked elsewhere.

- `v3_tensor_extraction_reconciliation/`
  - Focused notes and handoff material for reconciling the unresolved upstream
    V3 direct-tensor extraction segment, including random decoder order,
    directed neighbor asymmetry, tensor-value mismatch, and diagnostic
    stabilization questions.

- `workspace_operations/`
  - Workspace-level operating rules, workstream boundaries, session/worktree
    coordination, recovery-boundary anchors, package-role decisions,
    runtime-environment contracts, and Git-tracking policy. This directory
    should stay clean and should not become a generic notes folder.

## Root Files

- `WORKSPACE_MAP.md`
  - This first-navigation map. Keep it short, accurate, and synchronized with
    the actual root.

- `.gitignore`
  - Tracked ignore policy for runtime scaffolding, copied evidence payloads,
    nested source clones, Python residue, and large binary artifacts.

- `.gitattributes`
  - Git LFS rules for the promoted V3 PMPNN info pickles, final incremental RF
    result pickle, and curated ProteinMPNN checkpoint.

## Local Runtime Items

These root items exist in this physical worktree but are not durable project
evidence:

- `.agents/`
  - Local agent/runtime scaffolding ignored by Git.

- `.codex/`
  - Local Codex/runtime scaffolding ignored by Git.

- `.venv_pickle_analysis/`
  - Earlier local Python environment created for pickle inspection.

- `.venv_proteinmpnn_ddg_reproduction/`
  - Current local Python environment for ProteinMPNN-DDG recovery and
    reproduction work. Its operating role is documented in
    `workspace_operations/RUNTIME_ENVIRONMENT.md`.

- `.venv_sklearn_legacy_pickle_inspection/`
  - Auxiliary local Python environment for inspecting old scikit-learn model
    pickles that cannot be deserialized by the current reproduction runtime.
    Its narrow role is documented in
    `workspace_operations/RUNTIME_ENVIRONMENT.md`.

- `RESUME_CODEX_THREAD.md`
  - Optional workspace-local Codex resume index ignored by Git. It should only
    list sessions operationally relevant from this physical workspace.

- `.git/`
  - Git repository metadata.

## Root Hygiene

The root should stay sparse. Detailed evidence notes, generated reports,
analysis outputs, and workflow policies belong in the named directories above.

When adding a new durable root item, update this file in the same commit.
