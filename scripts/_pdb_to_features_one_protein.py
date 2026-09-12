#!/usr/bin/env python3
"""Worker: extract all jobs for one protein_key; write a shard pickle."""
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
)
RF_KEEP_FIELDS = [
    "mut","ddg","center_mut_wild_energy","center_entropy",
    "V2_backward_weighted_neighbor_energy_changes","weighted_neighbor_forward_KL",
    "V2_backward_weighted_neighbor_backward_KL","wild_pssm","alternate_pssm",
    "V2_backward_weighted_neighbor_entropy_changes","center_neighbor_weight_check_w_m",
    "neighbor_embedding_change_m_w","neighbor_embedding_change_m_w_raw",
    "neighbor_message_change_m_w_raw","feature_A","feature_B_historical_weighted",
    "feature_B_manuscript_unweighted","feature_C","feature_D","feature_F","feature_G","feature_H",
]
def compact(entry):
    return {k: entry[k] for k in RF_KEEP_FIELDS if k in entry}
def main():
    p = argparse.ArgumentParser()
    p.add_argument("--protein-key", required=True)
    p.add_argument("--jobs-pickle", type=Path, required=True)
    p.add_argument("--out-pickle", type=Path, required=True)
    p.add_argument("--pdb-dir", type=Path, required=True)
    p.add_argument("--pssm-dir", type=Path, required=True)
    p.add_argument("--checkpoint", type=Path, required=True)
    p.add_argument("--utils-path", type=Path, required=True)
    p.add_argument("--device", default="cpu")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--seed-mode", default="per_entry")
    p.add_argument("--compact-for-rf", action="store_true")
    p.add_argument("--global-index-base", type=int, default=0)
    args = p.parse_args()
    jobs = pickle.load(args.jobs_pickle.open("rb"))
    np.random.seed(args.seed); torch.manual_seed(args.seed)
    runtime = load_runtime(utils_path=args.utils_path, checkpoint_path=args.checkpoint, device=args.device)
    chain_id = args.protein_key[-1]
    pdb_path = args.pdb_dir / f"{args.protein_key}.pdb"
    residue_map = build_residue_index_map(pdb_path, chain_id)
    protein = load_single_chain_protein(runtime, pdb_path, chain_id)
    entries, statuses = [], []
    for index, job in enumerate(jobs):
        if args.seed_mode == "per_entry":
            np.random.seed(args.seed + args.global_index_base + index)
            torch.manual_seed(args.seed + args.global_index_base + index)
        try:
            mut = job["mutation_label"]
            seq_idx = residue_map[mut[:-1]]
            extracted = extract_mutation_tensor_fields(runtime, protein, args.protein_key, mut, seq_idx)
            entry = build_v3_entry_from_extraction(extracted, float(job["ddg"]), pssm_dir=args.pssm_dir)
            if args.compact_for_rf:
                entry = compact(entry)
            entries.append(entry)
            statuses.append({"protein_key": args.protein_key, "mutation_label": mut, "sequence_index": str(seq_idx), "status": "ok", "elapsed_seconds": "", "error_type": "", "error_message": ""})
            print(f"ok {args.protein_key} {mut}", flush=True)
        except Exception as exc:
            statuses.append({"protein_key": args.protein_key, "mutation_label": job["mutation_label"], "sequence_index": "", "status": "error", "elapsed_seconds": "", "error_type": type(exc).__name__, "error_message": str(exc)[:500]})
            print(f"ERROR {args.protein_key} {job['mutation_label']}: {exc}", flush=True)
    pickle.dump({"entries": entries, "statuses": statuses}, args.out_pickle.open("wb"))
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
