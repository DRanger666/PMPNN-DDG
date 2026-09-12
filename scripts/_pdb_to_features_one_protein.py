#!/usr/bin/env python3
"""Worker: extract all jobs for one protein_key; write a shard pickle.

Save modes:
  rf_compact — RF training scalars only (small)
  full       — full full extraction+feature entry (ProteinMPNN tensors + engineered + A–H + PSSM)
  both       — write full shard; also emit compact entries in the same payload under
               keys entries_full / entries_rf_compact (pipeline splits as needed)
"""
from __future__ import annotations
import argparse, pickle, sys
from pathlib import Path
import numpy as np
import torch
WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(WORKSPACE_ROOT))
from proteinmpnn_ddg_recovery.features.compute_bundle import build_v3_entry_from_extraction
from proteinmpnn_ddg_recovery.recovered_v6v2 import (
    build_residue_index_map, extract_mutation_tensor_fields, load_runtime, load_single_chain_protein,
    resolve_pdb_path,
)
RF_KEEP_FIELDS = [
    "mut","ddg","center_mut_wild_energy","center_entropy",
    "V2_backward_weighted_neighbor_energy_changes","weighted_neighbor_forward_KL",
    "V2_backward_weighted_neighbor_backward_KL","wild_pssm","alternate_pssm",
    "V2_backward_weighted_neighbor_entropy_changes","center_neighbor_weight_check_w_m",
    "neighbor_embedding_change_m_w","neighbor_embedding_change_m_w_raw",
    "neighbor_message_change_m_w_raw","feature_A","feature_B_historical_weighted", "feature_B_entropy_change_sum_weighted",
    "feature_B_manuscript_unweighted", "feature_B_entropy_change_sum_unweighted","feature_C","feature_D","feature_F","feature_G","feature_H",
]
def compact(entry):
    return {k: entry[k] for k in RF_KEEP_FIELDS if k in entry}
def main():
    p = argparse.ArgumentParser()
    p.add_argument("--protein-key", required=True)
    p.add_argument("--jobs-pickle", type=Path, required=True)
    p.add_argument("--out-pickle", type=Path, required=True)
    p.add_argument("--pdb-dir", type=Path, required=True)
    p.add_argument("--pdb-fallback-dir", type=Path, default=None,
                   help="Optional dir of independently fetched PDBs used when pdb-dir lacks the file")
    p.add_argument("--pssm-dir", type=Path, required=True)
    p.add_argument("--checkpoint", type=Path, required=True)
    p.add_argument("--utils-path", type=Path, required=True)
    p.add_argument("--device", default="cpu")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--seed-mode", default="per_entry")
    p.add_argument("--compact-for-rf", action="store_true",
                   help="Deprecated alias for --save-mode rf_compact")
    p.add_argument("--save-mode", choices=["rf_compact", "full", "both"], default=None,
                   help="Artifact richness. Default: rf_compact if --compact-for-rf else full")
    p.add_argument("--global-index-base", type=int, default=0)
    args = p.parse_args()
    save_mode = args.save_mode
    if save_mode is None:
        save_mode = "rf_compact" if args.compact_for_rf else "full"
    jobs = pickle.load(args.jobs_pickle.open("rb"))
    np.random.seed(args.seed); torch.manual_seed(args.seed)
    runtime = load_runtime(utils_path=args.utils_path, checkpoint_path=args.checkpoint, device=args.device)
    chain_id = args.protein_key[-1]
    pdb_path = resolve_pdb_path(
        args.protein_key, args.pdb_dir, fallback_dirs=[args.pdb_fallback_dir] if args.pdb_fallback_dir else None
    )
    residue_map = build_residue_index_map(pdb_path, chain_id)
    protein = load_single_chain_protein(runtime, pdb_path, chain_id)
    entries_full, entries_rf, statuses = [], [], []
    for index, job in enumerate(jobs):
        if args.seed_mode == "per_entry":
            np.random.seed(args.seed + args.global_index_base + index)
            torch.manual_seed(args.seed + args.global_index_base + index)
        try:
            mut = job["mutation_label"]
            seq_idx = residue_map[mut[:-1]]
            extracted = extract_mutation_tensor_fields(runtime, protein, args.protein_key, mut, seq_idx)
            entry = build_v3_entry_from_extraction(extracted, float(job["ddg"]), pssm_dir=args.pssm_dir)
            entry["artifact_kind"] = "pmpnn_ddg_extraction"
            entry["protein_key"] = args.protein_key
            entry["sequence_index"] = int(seq_idx)
            if save_mode in ("full", "both"):
                entries_full.append(entry)
            if save_mode in ("rf_compact", "both"):
                entries_rf.append(compact(entry))
            statuses.append({"protein_key": args.protein_key, "mutation_label": mut, "sequence_index": str(seq_idx), "status": "ok", "elapsed_seconds": "", "error_type": "", "error_message": ""})
            print(f"ok {args.protein_key} {mut}", flush=True)
        except Exception as exc:
            statuses.append({"protein_key": args.protein_key, "mutation_label": job["mutation_label"], "sequence_index": "", "status": "error", "elapsed_seconds": "", "error_type": type(exc).__name__, "error_message": str(exc)[:500]})
            print(f"ERROR {args.protein_key} {job['mutation_label']}: {exc}", flush=True)
    if save_mode == "rf_compact":
        entries_primary = entries_rf
    elif save_mode == "full":
        entries_primary = entries_full
    else:
        entries_primary = entries_full
    payload = {
        "entries": entries_primary,
        "statuses": statuses,
        "save_mode": save_mode,
        "artifact_kind": "pmpnn_ddg_extraction",
    }
    if save_mode == "both":
        payload["entries_full"] = entries_full
        payload["entries_rf_compact"] = entries_rf
    pickle.dump(payload, args.out_pickle.open("wb"))
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
