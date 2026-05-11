# Runtime Environment

Date: 2026-05-11

Purpose: define the operating role of the local Python environment used for
ProteinMPNN-DDG recovery and reproduction work.

## Canonical Environment

Path:

```text
.venv_proteinmpnn_ddg_reproduction/
```

Python:

```text
Python 3.12.3
```

This environment is the current local runtime for main-worker
ProteinMPNN-DDG recovery, reproduction, inspection, and focused experiments.
The V3 tensor-reconciliation worktree/session should treat this file as the
runtime contract unless a separate environment decision is recorded.

## Role

Use this environment for:

- running recovery and reproduction scripts under `scripts/`;
- importing the workspace-local `proteinmpnn_ddg_recovery/` package;
- conservative pickle, notebook-output, PDB/PSSM, and mutation-table analyses;
- CPU-only ProteinMPNN-DDG tensor/feature recovery experiments.

This environment is an operating dependency. Changing it can change analysis
behavior, even when no Python source file changes.

## Current Capability Snapshot

This is a compact capability snapshot, not a full dependency manifest:

- CPU PyTorch: `torch==2.11.0+cpu`
- Biopython: `1.87`
- NumPy: `2.4.4`
- pandas: `3.0.2`
- SciPy: `1.17.1`
- scikit-learn: `1.8.0`
- matplotlib: `3.10.9`
- openpyxl: `3.1.5`

Do not expand this document into a full package dump. If a full frozen package
list is needed, place it in a dedicated environment manifest file and reference
that file from here.

## Inspection Commands

Use the venv Python directly:

```bash
.venv_proteinmpnn_ddg_reproduction/bin/python -V
```

This venv currently does not provide `python -m pip`. Use `uv` for package
inspection:

```bash
uv pip list --python .venv_proteinmpnn_ddg_reproduction/bin/python
```

For targeted version checks without a full package list:

```bash
.venv_proteinmpnn_ddg_reproduction/bin/python -c "import torch; print(torch.__version__)"
```

## Update Discipline

Before changing this environment:

1. State why the dependency/runtime change is needed.
2. Prefer CPU-only installs unless there is a deliberate GPU decision.
3. Run focused scripts affected by the dependency change.
4. Record any behavior change in the relevant analysis note.
5. Commit the note/spec update with a message explaining the runtime implication.

Do not silently mutate this environment from the V3 tensor-reconciliation
worktree if that mutation can affect the main recovery workspace. Record the
decision first.

## Known Gap

There is currently no root `pyproject.toml`, `uv.lock`, or complete rebuild
specification for this environment. That is acceptable for the current recovery
stage, but it is a reproducibility gap.

When the dependency set stabilizes, create a deliberate rebuild spec or frozen
manifest in a dedicated location and reference it from this document.

## Auxiliary Legacy Inspection Environment

Path:

```text
.venv_sklearn_legacy_pickle_inspection/
```

Python/scikit-learn:

```text
Python 3.10.15
scikit-learn 1.1.3
```

Purpose: deserialize and inspect 2022-era scikit-learn model pickles that cannot
be loaded by the canonical reproduction venv's newer scikit-learn runtime.

Known trigger: `feature_combo_model_dict.pickle` and
`S_669_feature_combo_model_dict.pickle` fail under scikit-learn 1.8.0 because
their saved tree-node dtype is from an older scikit-learn version. Under this
auxiliary runtime, both load with warnings identifying the saved estimator
version as scikit-learn 1.0.2.

This environment is not the canonical runtime for ProteinMPNN-DDG reproduction.
Use it only for legacy model-pickle inspection unless a separate runtime
decision is recorded.
