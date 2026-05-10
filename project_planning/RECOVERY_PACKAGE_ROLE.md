# Recovery Package Role

Date: 2026-05-10

Purpose: define the workflow role of `proteinmpnn_ddg_recovery/`.

## Decision

`proteinmpnn_ddg_recovery/` is the workspace-local Python package for recovered
ProteinMPNN-DDG pipeline code.

It exists because recovery work is no longer just ad hoc notebook inspection.
We are gradually extracting recovered logic into reusable, testable Python code
that can be imported by analysis and reproduction scripts.

The name is intentionally explicit:

- `proteinmpnn_ddg` would imply a canonical or final project implementation.
- `proteinmpnn_ddg_recovery` says the package is for historical recovery and
  reproduction scaffolding.

## What Belongs In This Package

Use this package for reusable recovered code, including:

- behavior-preserving recovered ProteinMPNN tensor-extraction logic;
- recovered V3 engineered-feature construction;
- shared validation helpers for tensor/feature comparison;
- small utilities that multiple recovery scripts need.

Code should move into this package when duplicate script-local logic would make
future recovery work harder to reason about.

## What Does Not Belong Here Yet

Do not treat this package as:

- a cleaned final ProteinMPNN-DDG library;
- a publishable user-facing API;
- a place for speculative algorithm redesign before the historical behavior is
  separately understood;
- a dumping ground for one-off scripts or large generated outputs.

If an algorithmic design alternative is being studied, first record the
scientific reasoning under `algorithmic_deliberations/`. Only move code into
`proteinmpnn_ddg_recovery/` when it is either recovered historical behavior or a
clearly labeled recovery-support helper.

## Relationship To Scripts

Scripts under `scripts/` should import shared recovered logic from
`proteinmpnn_ddg_recovery/`.

This means a change to `proteinmpnn_ddg_recovery/` can change behavior in many
scripts at once. Package edits should therefore be treated as workflow-level
changes, not as isolated local fixes.

When editing the package:

1. State which recovered behavior or helper contract is changing.
2. Update scripts that import the changed behavior.
3. Update notes if the change alters the interpretation of prior analysis.
4. Run focused checks for the affected scripts.
5. Commit the package change with a body explaining the behavioral implication.

## Relationship To Historical Evidence

This package is derived from evidence, but it is not itself primary 2022
evidence.

Primary evidence remains in:

- copied Drive artifacts under `drive_evidence_copy/`;
- old source repositories under `source_repos/`;
- notebook source/output exports under inventory directories;
- saved pickle artifacts and their analysis outputs.

`proteinmpnn_ddg_recovery/` is our recovered implementation layer built from
that evidence.

## Relationship To Future Method Design

Future ProteinMPNN-DDG method improvements may eventually reuse or replace this
package, but that is a later decision.

For now:

- historical recovery/reproduction code lives here;
- algorithmic deliberation lives in `algorithmic_deliberations/`;
- manuscript-facing synthesis waits until recovery evidence and algorithmic
  analysis are intentionally merged.

This prevents three meanings from collapsing into one package:

1. recovered 2022 behavior;
2. current scientific interpretation;
3. future cleaned method implementation.
