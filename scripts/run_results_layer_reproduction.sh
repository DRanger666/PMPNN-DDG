#!/usr/bin/env bash
# One-command results-layer reproduction for manuscript Table 1 and Figure 6.
# Scope: saved RF result pickle + notebook/image evidence only.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PY="${ROOT}/.venv_proteinmpnn_ddg_reproduction/bin/python"
if [[ ! -x "$PY" ]]; then
  echo "Missing venv python at $PY" >&2
  echo "Create it per workspace_operations/RUNTIME_ENVIRONMENT.md" >&2
  exit 1
fi

# Fig6 PNG byte-match needs the SajidAhmeduiu notebook with embedded outputs.
if [[ ! -f source_repos/SajidAhmeduiu_ProteinMPNN/Sajid_Additions/Quick_Dirty_MPNN_ML_V2_VGRAPHS_V1.ipynb ]]; then
  echo "Cloning SajidAhmeduiu/ProteinMPNN into source_repos/ for Figure 6 PNG match..."
  mkdir -p source_repos
  git clone --depth 1 https://github.com/SajidAhmeduiu/ProteinMPNN.git \
    source_repos/SajidAhmeduiu_ProteinMPNN
fi

STAMP="${REPRO_STAMP:-$(date -u +%Y-%m-%d)}"
OUT="${ROOT}/reproduction_runs/${STAMP}"
mkdir -p "$OUT"/{table1_results_layer,figure6_image_verification,incremental_feature_pickle_inspection,logs}

echo "[1/3] Analyze incremental-feature result pickle -> Table1/Fig6 numeric series"
"$PY" scripts/analyze_incremental_feature_results.py \
  >"$OUT/logs/analyze_incremental_feature_results.log" 2>&1
# Copy generated inspection outputs into the dated run folder.
cp -a code_inventory_analysis/incremental_feature_pickle_inspection/. \
  "$OUT/incremental_feature_pickle_inspection/"

echo "[2/3] Verify Table 1 cells against manuscript rounded values"
"$PY" scripts/verify_table1_results_layer.py \
  --output-dir "$OUT/table1_results_layer" \
  | tee "$OUT/logs/verify_table1_results_layer.log"

echo "[3/3] Verify Figure 6 image basis + plotted total-PCC series"
"$PY" scripts/verify_figure6_image_basis.py \
  >"$OUT/logs/verify_figure6_image_basis.log" 2>&1
cp -a code_inventory_analysis/figure6_image_verification/. \
  "$OUT/figure6_image_verification/"

# Stable "latest" symlink for docs/scripts that point at a fixed path.
ln -sfn "$STAMP" "${ROOT}/reproduction_runs/latest"

cat >"$OUT/RESULTS_LAYER_SUMMARY.md" <<SUMMARY
# Results-Layer Reproduction (${STAMP})

Commands:

\`\`\`bash
./scripts/run_results_layer_reproduction.sh
\`\`\`

Outputs under \`reproduction_runs/${STAMP}/\`:

- \`table1_results_layer/\` — Table 1 cell-by-cell match report
- \`figure6_image_verification/\` — Figure 6 PNG hash + plotted PCC series
- \`incremental_feature_pickle_inspection/\` — ten-run metric summaries
- \`logs/\` — stdout/stderr from each step

Scope limit: final RF result / plotting evidence only. Does not regenerate V3
tensors from PDB+ProteinMPNN.
SUMMARY

echo "Wrote $OUT"
echo "Symlink reproduction_runs/latest -> $STAMP"
