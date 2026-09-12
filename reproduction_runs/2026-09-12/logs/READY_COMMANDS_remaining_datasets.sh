#!/usr/bin/env bash
# Ready commands for remaining PDB→features + full E2E RF.
# Always use --by-protein-subprocess on this host (OOM otherwise).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
cd "$ROOT"
PY=.venv_proteinmpnn_ddg_reproduction/bin/python
RUN=reproduction_runs/2026-09-12
LOG=$RUN/logs

# --- Feature regeneration (resume-safe) ---
# S_2648 (train) — expect ~2h CPU on this host
$PY scripts/run_pdb_to_features_pipeline.py \
  --dataset S_2648 --seed-mode per_entry \
  --by-protein-subprocess --compact-for-rf --resume --compare-reference \
  --output-dir $RUN/pdb_to_features_s2648 \
  | tee -a $LOG/pdb_to_features_s2648.log

# S_669
$PY scripts/run_pdb_to_features_pipeline.py \
  --dataset S_669 --seed-mode per_entry \
  --by-protein-subprocess --compact-for-rf --resume --compare-reference \
  --output-dir $RUN/pdb_to_features_s669 \
  | tee -a $LOG/pdb_to_features_s669.log

# S_921
$PY scripts/run_pdb_to_features_pipeline.py \
  --dataset S_921 --seed-mode per_entry \
  --by-protein-subprocess --compact-for-rf --resume --compare-reference \
  --output-dir $RUN/pdb_to_features_s921 \
  | tee -a $LOG/pdb_to_features_s921.log

# --- Full E2E RF: regenerated train + regenerated eval sets ---
$PY scripts/train_eval_rf_from_v3_features.py \
  --v3-pickle-override S_2648=$RUN/pdb_to_features_s2648/regenerated_v3_features.pickle \
  --v3-pickle-override Ssym=$RUN/pdb_to_features_ssym/regenerated_v3_features.pickle \
  --v3-pickle-override S_669=$RUN/pdb_to_features_s669/regenerated_v3_features.pickle \
  --v3-pickle-override S_921=$RUN/pdb_to_features_s921/regenerated_v3_features.pickle \
  --output-dir $RUN/rf_from_regenerated_full_e2e \
  --n-runs 10 --full-ah-only --configs notebook_table1 manuscript_literal \
  --feature-b-mode historical_weighted --kpca-seed 0 \
  | tee -a $LOG/rf_from_regenerated_full_e2e.log

# Minimal E2E if only S_2648 + Ssym ready:
# $PY scripts/train_eval_rf_from_v3_features.py \
#   --v3-pickle-override S_2648=$RUN/pdb_to_features_s2648/regenerated_v3_features.pickle \
#   --v3-pickle-override Ssym=$RUN/pdb_to_features_ssym/regenerated_v3_features.pickle \
#   --output-dir $RUN/rf_from_regenerated_s2648_ssym \
#   --n-runs 10 --full-ah-only --configs notebook_table1 \
#   --feature-b-mode historical_weighted --kpca-seed 0
