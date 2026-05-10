# ProteinMPNN-DDG Workspace Map

Date: 2026-05-10

Purpose: quick map of the major workspace directories and their intended roles.

This workspace is for recovering, reproducing, and later extending the 2022
ProteinMPNN-DDG work. Directory names should make ownership and evidence status
clear.

## Active Recovery Code

- `proteinmpnn_ddg_recovery/`
  - Workspace-local Python package for recovered/reproduction code.
  - Built gradually from recovered notebook/code evidence.
  - Imported by scripts under `scripts/`.
  - Behavior changes here can change downstream analysis scripts.
  - This is not the final cleaned ProteinMPNN-DDG package.

- `scripts/`
  - Runnable analysis, audit, comparison, and reproduction scripts.
  - Scripts should import reusable recovered logic from
    `proteinmpnn_ddg_recovery/` instead of duplicating it.

## Evidence And Analysis Areas

- `drive_evidence_copy/`
  - Timestamp-preserving local copy of selected Drive evidence.
  - Bulk copied payloads are not tracked by Git by default.

- `source_repos/`
  - Local clones of source/reference repositories.
  - Treated as evidence inputs, not code owned by this workspace repo.

- `manuscript_inventory_analysis/`
  - Inventory of manuscript-folder contents, extracted text, metadata,
    comparisons, and manuscript-file relationships.

- `manuscript_codebase_mapping/`
  - Evidence linking manuscript numbers, figures, tables, notebook cells,
    pickles, datasets, and upstream ProteinMPNN-derived artifacts.

- `pickle_analysis/`
  - Pickle inspection, schema/field summaries, instance-coverage notes, and
    value-comparison outputs.

- `algorithmic_deliberations/`
  - Scientific/method-level analysis that may matter for manuscript framing,
    robustness, reviewer response, or future method design.

- `project_planning/`
  - Workflow-level decision records that govern how this workspace is operated.

## Current Workflow Anchor

Historical recovery should use `proteinmpnn_ddg_recovery/` for shared recovered
logic and `scripts/` for executable analyses. When a script result changes after
editing `proteinmpnn_ddg_recovery/`, the change should be treated as a package
behavior change, not an isolated script change.

Algorithmic redesign ideas should first be recorded under
`algorithmic_deliberations/` and should not silently overwrite the historical
recovery target.
