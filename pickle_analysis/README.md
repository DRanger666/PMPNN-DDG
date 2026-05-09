# S_921 Pickle Analysis

This directory holds a targeted, workspace-local inspection of four historical
S_921 pickle artifacts from the copied `Protein_MPNN_Digging` evidence tree.

Entry points:

- `reports/S_921_PICKLE_CONTENT_REPORT.md`: content-level interpretation and
  manuscript/code linkage.
- `../scripts/inspect_s921_pickles.py`: conservative inspection script.
- `../scripts/fingerprint_v3_pickles.py`: V3/base/V2 fingerprinting script for
  the four PMPNN dataset pickle families.
- `v3_fingerprinting/`: TSV/JSON outputs from the V3 content-fingerprinting
  pass.
- `tables/`: TSV evidence tables emitted by the script.
- `json/S_921_pickle_summaries.json`: compact machine-readable summary.
- `uv_freeze.txt`: exact package versions used in `.venv_pickle_analysis`.

The copied binary pickle inputs live in `S_921_target_pickles/`. They are
intentionally ignored by git; the manifest records their hashes and preserved
mtimes.
