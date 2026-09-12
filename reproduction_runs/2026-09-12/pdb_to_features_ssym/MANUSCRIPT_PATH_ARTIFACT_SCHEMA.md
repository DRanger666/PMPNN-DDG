# Manuscript-path artifact schema

See `manuscript_codebase_mapping/MANUSCRIPT_PATH_VS_HISTORICAL_V3.md`.

This directory’s primary pickle may still be named `regenerated_v3_features.pickle`
for historical path compatibility; `manuscript_path_features.pickle` is the
preferred name (symlink when present).

**save_mode for this run:** `rf_compact` (RF scalars). A follow-up `--save-mode full`
or `both` pass is required for durable full extraction tensors.
