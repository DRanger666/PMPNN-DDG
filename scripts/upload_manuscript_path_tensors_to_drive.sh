#!/usr/bin/env bash
# Upload manuscript-path tensor/feature artifacts to Google Drive (interim store).
#
# BLOCKER (2026-09-12): this box has no rclone binary and no configured remotes.
# After parent installs rclone and authorizes a remote (e.g. gdrive:), run:
#
#   export RCLONE_REMOTE=gdrive:ProteinMPNN-DDG/manuscript_path_tensors
#   bash scripts/upload_manuscript_path_tensors_to_drive.sh
#
# Local sources (preferred names first):
#   reproduction_runs/<date>/pdb_to_features_*/manuscript_path_features.pickle
#   reproduction_runs/<date>/manuscript_path_tensors/
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

DATE="${DATE:-2026-09-12}"
LOCAL_ROOT="${LOCAL_ROOT:-reproduction_runs/${DATE}}"
REMOTE="${RCLONE_REMOTE:-}"

if ! command -v rclone >/dev/null 2>&1; then
  echo "ERROR: rclone not installed on this box."
  echo "Install rclone, create a Google Drive remote, then re-run."
  echo "Suggested Drive layout:"
  echo "  ProteinMPNN-DDG/manuscript_path_tensors/${DATE}/{S_2648,S_669,S_921,Ssym}/"
  exit 2
fi
if [[ -z "$REMOTE" ]]; then
  echo "ERROR: set RCLONE_REMOTE, e.g. gdrive:ProteinMPNN-DDG/manuscript_path_tensors/${DATE}"
  exit 2
fi

mkdir -p "$LOCAL_ROOT/manuscript_path_tensors"
for ds in S_2648 S_669 S_921 Ssym ssym s2648; do
  :
done

# Map pipeline output dirs → Drive-facing names
declare -A MAP=(
  [pdb_to_features_s2648]=S_2648
  [pdb_to_features_s669]=S_669
  [pdb_to_features_s921]=S_921
  [pdb_to_features_ssym]=Ssym
)

for src in "${!MAP[@]}"; do
  src_dir="$LOCAL_ROOT/$src"
  [[ -d "$src_dir" ]] || continue
  dest_name="${MAP[$src]}"
  # Prefer manuscript_path_features.pickle; fall back to legacy alias
  pickle=""
  if [[ -f "$src_dir/manuscript_path_features.pickle" ]]; then
    pickle="$src_dir/manuscript_path_features.pickle"
  elif [[ -f "$src_dir/regenerated_v3_features.pickle" ]]; then
    pickle="$src_dir/regenerated_v3_features.pickle"
  fi
  echo "Sync $src_dir → ${REMOTE}/${dest_name}/"
  rclone copy "$src_dir" "${REMOTE}/${dest_name}/" \
    --include "manuscript_path_features.pickle" \
    --include "regenerated_v3_features.pickle" \
    --include "MANUSCRIPT_PATH_ARTIFACT_SCHEMA.md" \
    --include "PIPELINE_REPORT.md" \
    --include "json/**" \
    --include "tables/**" \
    --include "shards/*.out.pkl" \
    -v
done

echo "Upload complete to $REMOTE"
