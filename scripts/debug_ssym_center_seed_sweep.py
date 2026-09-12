#!/usr/bin/env python3
"""Sweep center-pass random seeds for one Ssym V3 tensor target.

This is a narrow debugging helper for the ProteinMPNN-DDG V3 tensor-extraction
segment. It only tests the first manuscript step: mask the mutation position,
run the patched ProteinMPNN forward pass, rank neighbors by last-decoder message
norms, and compare those rankings to a saved V3 pickle entry.
"""

from __future__ import annotations

import argparse
import csv
import json
import pickle
import sys
from pathlib import Path
from typing import Any

import numpy as np
import torch

WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from proteinmpnn_ddg_recovery.recovered_v6v2 import (  # noqa: E402
    DEFAULT_SSYM_PDB_DIR,
    build_residue_index_map,
    featurize_for_one_designable_position,
    load_runtime,
    load_single_chain_protein,
    return_neighbor_info,
)


DEFAULT_TARGET_PICKLE = (
    WORKSPACE_ROOT
    / "reproduction_inputs"
    / "historical_reference_pickles"
    / "Ssym_pmppn_info_dict_V3.pickle"
)
DEFAULT_OUTPUT_DIR = (
    WORKSPACE_ROOT
    / "manuscript_codebase_mapping"
    / "tensor_extraction_codeblock_recovery"
    / "ssym_algorithm_debugging"
)
FIELDNAMES = [
    "seed",
    "top5_exact",
    "top10_exact",
    "top15_exact",
    "top15_ordered_match_count",
    "top15_set_match_count",
    "log_prob_max_abs_diff",
    "generated_top5",
    "generated_top10",
    "generated_top15",
]


def load_target_entry(
    path: Path,
    protein_key: str,
    mutation_label: str,
) -> dict[str, Any]:
    """Load one mutation entry from the saved Ssym V3 pickle."""

    with path.open("rb") as handle:
        obj = pickle.load(handle)
    for entry in obj[protein_key]:
        if entry["mut"] == mutation_label:
            return entry
    raise ValueError(f"{protein_key} {mutation_label} not found in {path}")


def as_int_list(value: Any) -> list[int]:
    """Convert a saved/generated index array to a plain int list."""

    return [int(item) for item in np.asarray(value).tolist()]


def run_seed_sweep(args: argparse.Namespace) -> list[dict[str, Any]]:
    """Run center-pass seed variants and return comparison rows."""

    target_entry = load_target_entry(
        args.target_pickle,
        args.protein_key,
        args.mutation_label,
    )
    runtime = load_runtime(device=args.device)
    chain_id = args.protein_key[-1]
    pdb_path = args.pdb_dir / f"{args.protein_key}.pdb"
    residue_map = build_residue_index_map(pdb_path, chain_id)
    sequence_index = residue_map[args.mutation_label[:-1]]
    protein = load_single_chain_protein(runtime, pdb_path, chain_id)
    featurized = featurize_for_one_designable_position(
        runtime,
        protein,
        chain_id,
        sequence_index,
    )
    _local_distances, local_neighbors = return_neighbor_info(
        featurized.X,
        featurized.mask,
        runtime.checkpoint["num_edges"],
    )

    target_top5 = as_int_list(target_entry["top_5_neighbor_indices"])
    target_top10 = as_int_list(target_entry["top_10_neighbor_indices"])
    target_top15 = as_int_list(target_entry["top_15_neighbor_indices"])

    rows: list[dict[str, Any]] = []
    for seed in range(args.seed_start, args.seed_start + args.seed_count):
        torch.manual_seed(seed)
        randn = torch.randn(featurized.chain_M.shape, device=featurized.X.device)
        with torch.no_grad():
            log_probs, decoder_messages, _embeddings = runtime.model(
                featurized.X,
                featurized.S,
                featurized.mask,
                featurized.chain_M * featurized.chain_M_pos,
                featurized.residue_idx,
                featurized.chain_encoding_all,
                randn,
            )

        message_norms = torch.linalg.vector_norm(
            decoder_messages[0, sequence_index, :, :],
            ord=2,
            dim=1,
        )
        _values15, indices15 = torch.topk(message_norms, k=15)
        _values10, indices10 = torch.topk(message_norms, k=10)
        _values5, indices5 = torch.topk(message_norms, k=5)
        generated_top15 = as_int_list(local_neighbors[0, sequence_index, indices15])
        generated_top10 = as_int_list(local_neighbors[0, sequence_index, indices10])
        generated_top5 = as_int_list(local_neighbors[0, sequence_index, indices5])

        rows.append(
            {
                "seed": seed,
                "top5_exact": generated_top5 == target_top5,
                "top10_exact": generated_top10 == target_top10,
                "top15_exact": generated_top15 == target_top15,
                "top15_ordered_match_count": sum(
                    left == right for left, right in zip(generated_top15, target_top15)
                ),
                "top15_set_match_count": len(set(generated_top15) & set(target_top15)),
                "log_prob_max_abs_diff": float(
                    np.max(np.abs(log_probs.cpu().numpy() - target_entry["log_prob"]))
                ),
                "generated_top5": ",".join(str(item) for item in generated_top5),
                "generated_top10": ",".join(str(item) for item in generated_top10),
                "generated_top15": ",".join(str(item) for item in generated_top15),
            }
        )
    return rows


def write_tsv(path: Path, rows: list[dict[str, Any]]) -> None:
    """Write seed-sweep rows."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            delimiter="\t",
            fieldnames=FIELDNAMES,
            lineterminator="\n",
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target-pickle", type=Path, default=DEFAULT_TARGET_PICKLE)
    parser.add_argument("--pdb-dir", type=Path, default=DEFAULT_SSYM_PDB_DIR)
    parser.add_argument("--protein-key", default="1amqA")
    parser.add_argument("--mutation-label", default="C191Y")
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--seed-start", type=int, default=0)
    parser.add_argument("--seed-count", type=int, default=100)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    rows = run_seed_sweep(args)
    table_path = (
        args.output_dir
        / "tables"
        / f"{args.protein_key}_{args.mutation_label}_center_seed_sweep.tsv"
    )
    json_path = (
        args.output_dir
        / "json"
        / f"{args.protein_key}_{args.mutation_label}_center_seed_sweep.json"
    )
    write_tsv(table_path, rows)

    best_rows = sorted(
        rows,
        key=lambda row: (
            row["top15_ordered_match_count"],
            row["top15_set_match_count"],
            -row["log_prob_max_abs_diff"],
        ),
        reverse=True,
    )[:10]
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(
        json.dumps(
            {
                "protein_key": args.protein_key,
                "mutation_label": args.mutation_label,
                "seed_start": args.seed_start,
                "seed_count": args.seed_count,
                "best_rows": best_rows,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(json.dumps({"best_rows": best_rows}, indent=2))


if __name__ == "__main__":
    main()
