#!/usr/bin/env python3
"""PDB + mutation table + ProteinMPNN → V3 tensors → engineered/PSSM features.

This is the clean manuscript-aligned reproduction path:

  PDB files
  + mutation/DDG table
  + vanilla ProteinMPNN checkpoint (v_48_020)
  + clean modified_proteinmpnn (baked-in V6_V2 extraction hooks)
  → direct ProteinMPNN tensor fields
  → engineered + PSSM features (V3-shaped pickle)

It does NOT require bit-exact match to historical V3 pickles. Optional comparison
against a saved reference pickle is diagnostic only.

Seed / decoder-order policy (open fidelity question — see
manuscript_codebase_mapping/MANUSCRIPT_TENSOR_EXTRACTION_FIDELITY.md Item A):

  continuous  (default, notebook-like): seed once at start; consume RNG across
               mutations/neighbors without reset.
  per_entry:   reset torch/numpy seed before each mutation (smoke-test style).
  fixed:       same as continuous but documents a single global seed.

Outputs under --output-dir:
  regenerated_v3_features.pickle   two-level dict {protein_key: [entry, ...]}
  tables/mutation_status.tsv
  json/pipeline_summary.json
  PIPELINE_REPORT.md
"""

from __future__ import annotations

import argparse
import gc
import csv
import json
import pickle
import re
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
import torch

WORKSPACE_ROOT = Path(__file__).resolve().parents[1]

def rel_workspace(path: Path) -> str:
    path = Path(path)
    try:
        return str(path.resolve().relative_to(WORKSPACE_ROOT))
    except ValueError:
        return str(path)

if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from proteinmpnn_ddg_recovery.features.compute_bundle import (  # noqa: E402
    build_v3_entry_from_extraction,
)
from proteinmpnn_ddg_recovery.recovered_v6v2 import (  # noqa: E402
    DEFAULT_CHECKPOINT_PATH,
    DEFAULT_UTILS_PATH,
    V3_TENSOR_FIELDS,
    build_residue_index_map,
    extract_mutation_tensor_fields,
    load_runtime,
    load_single_chain_protein,
)
from proteinmpnn_ddg_recovery.tensor_field_checks import write_tsv  # noqa: E402


ACCRE = (
    WORKSPACE_ROOT
    / "drive_evidence_copy"
    / "sajidahmedprotres_drive"
    / "ACCRE_PyRun_Setup"
)
TABLES = WORKSPACE_ROOT / "reproduction_inputs" / "mutation_ddg_tables"
DIGGING = (
    WORKSPACE_ROOT
    / "drive_evidence_copy"
    / "sajidahmedprotres_drive"
    / "Protein_MPNN_Digging"
)

DATASET_PRESETS: dict[str, dict[str, Any]] = {
    "Ssym": {
        "mutation_table": TABLES / "Ssym" / "Ssym.txt",
        "table_kind": "ssym_tsv",
        "pdb_dir": ACCRE / "Ssym_PDB_Files",
        "pssm_dir": ACCRE / "Ssym_pssm_dir",
        "reference_pickle": DIGGING / "Ssym_pmppn_info_dict_V3.pickle",
        "forward_only": True,
    },
    "S_2648": {
        "mutation_table": TABLES / "S_2648" / "S2648.txt",
        "table_kind": "premps_tsv",
        "pdb_dir": ACCRE / "S_2648_PDB_Files",
        "pssm_dir": ACCRE / "S_2648_pssm_dir",
        "reference_pickle": DIGGING / "S_2648_pmppn_info_dict_V3.pickle",
        "forward_only": False,
    },
    "S_669": {
        "mutation_table": TABLES / "S_669" / "Data_s669_with_predictions.csv",
        "table_kind": "s669_csv",
        "pdb_dir": ACCRE / "S_669_PDB_Files",
        "pssm_dir": ACCRE / "S_669_pssm_dir",
        "reference_pickle": DIGGING / "S_669_pmppn_info_dict_V3.pickle",
        "forward_only": False,
    },
    "S_921": {
        "mutation_table": TABLES / "S_921" / "S921.txt",
        "table_kind": "premps_tsv",
        "pdb_dir": ACCRE / "S_921_PDB_Files",
        "pssm_dir": ACCRE / "S_921_pssm_dir",
        "reference_pickle": DIGGING / "S_921_pmppn_info_dict_V3.pickle",
        "forward_only": False,
    },
}

STATUS_FIELDS = [
    "protein_key",
    "mutation_label",
    "sequence_index",
    "status",
    "elapsed_seconds",
    "error_type",
    "error_message",
]


def load_mutation_jobs(
    table_path: Path,
    table_kind: str,
    forward_only: bool,
    protein_key_filter: str | None,
    limit: int | None,
) -> list[dict[str, Any]]:
    """Load (protein_key, mut, ddg) jobs from a curated mutation table."""

    jobs: list[dict[str, Any]] = []
    if table_kind in ("ssym_tsv", "premps_tsv"):
        with table_path.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle, delimiter="\t"))
        for row in rows:
            if table_kind == "ssym_tsv" and forward_only:
                if "forward" not in str(row.get("Label", "")):
                    continue
            pdb_id = str(row["PDB Id"]).lower()
            chain = str(row["Mutated Chain"])
            mutation = str(row["Mutation_PDB"])
            ddg = float(row["DDGexp"])
            protein_key = f"{pdb_id}{chain}"
            if protein_key_filter is not None and protein_key != protein_key_filter:
                continue
            jobs.append(
                {
                    "protein_key": protein_key,
                    "mutation_label": mutation,
                    "ddg": ddg,
                }
            )
            if limit is not None and len(jobs) >= limit:
                return jobs
        return jobs

    if table_kind == "s669_csv":
        with table_path.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        for row in rows:
            # Notebooks use Protein like 1A0FA (pdb+chain already) and PDB_Mut.
            protein = str(row["Protein"])
            # Historical V3 keys are lowercase pdb id + chain, e.g. 1a0fA.
            pdb_wild = str(row.get("PDB_wild", protein[:4])).lower()
            chain = protein[4:] if len(protein) > 4 else "A"
            protein_key = f"{pdb_wild}{chain}"
            mutation = str(row["PDB_Mut"])
            ddg = float(row["DDG_checked_dir"])
            if protein_key_filter is not None and protein_key != protein_key_filter:
                continue
            jobs.append(
                {
                    "protein_key": protein_key,
                    "mutation_label": mutation,
                    "ddg": ddg,
                }
            )
            if limit is not None and len(jobs) >= limit:
                return jobs
        return jobs

    raise ValueError(f"Unknown table_kind={table_kind!r}")


def maybe_seed(seed: int, mode: str, entry_index: int) -> None:
    if mode == "per_entry":
        np.random.seed(seed + entry_index)
        torch.manual_seed(seed + entry_index)
    elif mode in ("continuous", "fixed"):
        if entry_index == 0:
            np.random.seed(seed)
            torch.manual_seed(seed)
    else:
        raise ValueError(f"Unknown seed mode {mode!r}")


def process_job(
    runtime: Any,
    job: dict[str, Any],
    pdb_dir: Path,
    pssm_dir: Path,
    residue_maps: dict[str, dict[str, int]],
    proteins: dict[str, dict[str, Any]],
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Extract tensors + features for one mutation; return (entry, status_row)."""

    protein_key = job["protein_key"]
    mutation_label = job["mutation_label"]
    chain_id = protein_key[-1]
    pdb_path = pdb_dir / f"{protein_key}.pdb"
    t0 = time.time()

    if not pdb_path.exists():
        raise FileNotFoundError(f"Missing PDB: {pdb_path}")

    if protein_key not in residue_maps:
        residue_maps[protein_key] = build_residue_index_map(pdb_path, chain_id)
    if protein_key not in proteins:
        proteins[protein_key] = load_single_chain_protein(runtime, pdb_path, chain_id)

    residue_map = residue_maps[protein_key]
    mutation_residue_key = mutation_label[:-1]
    if mutation_residue_key not in residue_map:
        raise KeyError(
            f"Residue {mutation_residue_key!r} not in map for {protein_key}"
        )
    sequence_index = residue_map[mutation_residue_key]
    protein = proteins[protein_key]

    extracted = extract_mutation_tensor_fields(
        runtime,
        protein,
        protein_key,
        mutation_label,
        sequence_index,
    )
    entry = build_v3_entry_from_extraction(
        extracted,
        float(job["ddg"]),
        pssm_dir=pssm_dir,
    )

    status = {
        "protein_key": protein_key,
        "mutation_label": mutation_label,
        "sequence_index": str(sequence_index),
        "status": "ok",
        "elapsed_seconds": f"{time.time() - t0:.3f}",
        "error_type": "",
        "error_message": "",
    }
    return entry, status


def compare_to_reference(
    regenerated: dict[str, list[dict[str, Any]]],
    reference_path: Path | None,
    atol: float = 1e-5,
) -> dict[str, Any] | None:
    if reference_path is None or not reference_path.exists():
        return None
    with reference_path.open("rb") as handle:
        reference = pickle.load(handle)

    scalar_fields = [
        "center_mut_wild_energy",
        "center_entropy",
        "V2_backward_weighted_neighbor_entropy_changes",
        "center_neighbor_weight_check_w_m",
        "neighbor_embedding_change_m_w",
        "wild_pssm",
        "alternate_pssm",
    ]
    n_compared = 0
    n_scalar_close = {field: 0 for field in scalar_fields}
    n_top15_exact = 0
    n_log_prob_close = 0
    n_missing_in_ref = 0

    for protein_key, entries in regenerated.items():
        ref_entries = {e["mut"]: e for e in reference.get(protein_key, [])}
        for entry in entries:
            mut = entry["mut"]
            if mut not in ref_entries:
                n_missing_in_ref += 1
                continue
            ref = ref_entries[mut]
            n_compared += 1
            if np.array_equal(
                np.asarray(entry["top_15_neighbor_indices"]),
                np.asarray(ref["top_15_neighbor_indices"]),
            ):
                n_top15_exact += 1
            if np.allclose(
                np.asarray(entry["log_prob"]),
                np.asarray(ref["log_prob"]),
                atol=atol,
                rtol=atol,
            ):
                n_log_prob_close += 1
            for field in scalar_fields:
                if field not in entry or field not in ref:
                    continue
                if np.allclose(
                    np.asarray(entry[field], dtype=np.float64),
                    np.asarray(ref[field], dtype=np.float64),
                    atol=atol,
                    rtol=atol,
                ):
                    n_scalar_close[field] += 1

    return {
        "reference_pickle": rel_workspace(reference_path),
        "n_compared": n_compared,
        "n_missing_in_ref": n_missing_in_ref,
        "top15_neighbor_exact": n_top15_exact,
        "log_prob_allclose": n_log_prob_close,
        "scalar_allclose": n_scalar_close,
        "note": (
            "Diagnostic only. Manuscript-faithful regeneration does not require "
            "bit-exact historical pickle match."
        ),
    }


def write_report(
    output_dir: Path,
    summary: dict[str, Any],
) -> None:
    lines = [
        "# PDB → ProteinMPNN → Features Pipeline Report",
        "",
        "Clean reproduction path: local PDBs + mutation table + checkpoint +",
        "recovered V6_V2 tensor extraction → engineered/PSSM features.",
        "",
        "## Run",
        "",
        f"- Dataset: `{summary['dataset']}`",
        f"- Jobs requested: `{summary['n_jobs']}`",
        f"- OK: `{summary['n_ok']}`",
        f"- Errors: `{summary['n_error']}`",
        f"- Seed mode: `{summary['seed_mode']}` (seed={summary['seed']})",
        f"- Device: `{summary['runtime']['device']}`",
        f"- Elapsed seconds: `{summary['elapsed_seconds']:.1f}`",
        "",
        "## Artifacts",
        "",
        "- `regenerated_v3_features.pickle`",
        "- `tables/mutation_status.tsv`",
        "- `json/pipeline_summary.json`",
        "",
        "## Open fidelity questions (not assumed bugs)",
        "",
        "- Decoder RNG / order among fixed residues (Item A)",
        "- Feature B weighted vs manuscript unweighted wording (Item B)",
        "- Zero-vector fallback for non-reciprocal edges (Item C)",
        "",
        "See `manuscript_codebase_mapping/MANUSCRIPT_TENSOR_EXTRACTION_FIDELITY.md`.",
        "",
    ]
    if summary.get("reference_compare"):
        cmp_ = summary["reference_compare"]
        lines.extend(
            [
                "## Optional historical pickle compare (diagnostic)",
                "",
                f"- Compared entries: `{cmp_['n_compared']}`",
                f"- top_15_neighbor exact: `{cmp_['top15_neighbor_exact']}`",
                f"- log_prob allclose: `{cmp_['log_prob_allclose']}`",
                f"- scalar allclose: `{json.dumps(cmp_['scalar_allclose'])}`",
                "",
            ]
        )
    (output_dir / "PIPELINE_REPORT.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dataset",
        choices=list(DATASET_PRESETS.keys()),
        default="Ssym",
    )
    parser.add_argument("--mutation-table", type=Path, default=None)
    parser.add_argument("--pdb-dir", type=Path, default=None)
    parser.add_argument("--pssm-dir", type=Path, default=None)
    parser.add_argument("--checkpoint", type=Path, default=DEFAULT_CHECKPOINT_PATH)
    parser.add_argument("--utils-path", type=Path, default=DEFAULT_UTILS_PATH)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument(
        "--seed-mode",
        choices=["continuous", "per_entry", "fixed"],
        default="continuous",
        help="Primary manuscript/notebook-aligned path is continuous RNG.",
    )
    parser.add_argument("--protein-key", default=None)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=WORKSPACE_ROOT
        / "reproduction_runs"
        / "2026-09-12"
        / "pdb_to_features_ssym",
    )
    parser.add_argument(
        "--compare-reference",
        action="store_true",
        help="Compare regenerated scalars/tensors to historical V3 pickle (diagnostic).",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Skip mutations already ok in mutation_status.tsv / partial pickle.",
    )
    parser.add_argument(
        "--skip-reference-compare",
        action="store_true",
        help="Explicitly skip reference compare even if --compare-reference set.",
    )
    args = parser.parse_args()

    preset = DATASET_PRESETS[args.dataset]
    mutation_table = args.mutation_table or preset["mutation_table"]
    pdb_dir = args.pdb_dir or preset["pdb_dir"]
    pssm_dir = args.pssm_dir or preset["pssm_dir"]
    output_dir = Path(args.output_dir).expanduser()
    if not output_dir.is_absolute():
        output_dir = (WORKSPACE_ROOT / output_dir).resolve()
    else:
        output_dir = output_dir.resolve()
    table_dir = output_dir / "tables"
    json_dir = output_dir / "json"
    table_dir.mkdir(parents=True, exist_ok=True)
    json_dir.mkdir(parents=True, exist_ok=True)

    jobs = load_mutation_jobs(
        mutation_table,
        preset["table_kind"],
        forward_only=bool(preset["forward_only"]),
        protein_key_filter=args.protein_key,
        limit=args.limit,
    )
    print(
        f"Dataset={args.dataset} jobs={len(jobs)} pdb_dir={pdb_dir} "
        f"seed_mode={args.seed_mode} seed={args.seed}",
        flush=True,
    )

    t_run = time.time()
    runtime = load_runtime(
        utils_path=args.utils_path,
        checkpoint_path=args.checkpoint,
        device=args.device,
    )
    regenerated: dict[str, list[dict[str, Any]]] = {}
    status_rows: list[dict[str, Any]] = []
    residue_maps: dict[str, dict[str, int]] = {}
    proteins: dict[str, dict[str, Any]] = {}
    n_ok = 0
    n_error = 0

    completed_keys: set[tuple[str, str]] = set()
    status_path = table_dir / "mutation_status.tsv"
    existing_status = []
    if args.resume and status_path.exists():
        with status_path.open("r", newline="", encoding="utf-8") as handle:
            existing_status = list(csv.DictReader(handle, delimiter="\t"))
        for row in existing_status:
            if row.get("status") == "ok":
                completed_keys.add((row["protein_key"], row["mutation_label"]))
        if (output_dir / "regenerated_v3_features.partial.pickle").exists():
            with (output_dir / "regenerated_v3_features.partial.pickle").open("rb") as handle:
                regenerated = pickle.load(handle)
            print(
                f"Resume: loaded partial pickle with "
                f"{sum(len(v) for v in regenerated.values())} entries; "
                f"skipping {len(completed_keys)} completed jobs",
                flush=True,
            )
        status_rows.extend(existing_status)

    last_protein = None
    for index, job in enumerate(jobs):
        key = (job["protein_key"], job["mutation_label"])
        if key in completed_keys:
            continue
        maybe_seed(args.seed, args.seed_mode, index)
        try:
            entry, status = process_job(
                runtime,
                job,
                pdb_dir,
                pssm_dir,
                residue_maps,
                proteins,
            )
            regenerated.setdefault(job["protein_key"], []).append(entry)
            status_rows.append(status)
            completed_keys.add(key)
            n_ok += 1
            print(
                f"[{index + 1}/{len(jobs)}] ok {job['protein_key']} "
                f"{job['mutation_label']} ({status['elapsed_seconds']}s)",
                flush=True,
            )
        except Exception as exc:  # noqa: BLE001 - record and continue
            n_error += 1
            status_rows.append(
                {
                    "protein_key": job["protein_key"],
                    "mutation_label": job["mutation_label"],
                    "sequence_index": "",
                    "status": "error",
                    "elapsed_seconds": "",
                    "error_type": type(exc).__name__,
                    "error_message": str(exc)[:500],
                }
            )
            print(
                f"[{index + 1}/{len(jobs)}] ERROR {job['protein_key']} "
                f"{job['mutation_label']}: {type(exc).__name__}: {exc}",
                flush=True,
            )

        # Drop cached structure when moving to a new protein to limit RSS.
        if last_protein is not None and job["protein_key"] != last_protein:
            proteins.pop(last_protein, None)
            residue_maps.pop(last_protein, None)
        last_protein = job["protein_key"]

        if (index + 1) % 5 == 0 or index + 1 == len(jobs):
            write_tsv(status_path, status_rows, STATUS_FIELDS)
            with (output_dir / "regenerated_v3_features.partial.pickle").open("wb") as handle:
                pickle.dump(regenerated, handle, protocol=pickle.HIGHEST_PROTOCOL)
            gc.collect()
            if hasattr(torch, "cuda") and torch.cuda.is_available():
                torch.cuda.empty_cache()

    pickle_path = output_dir / "regenerated_v3_features.pickle"
    with pickle_path.open("wb") as handle:
        pickle.dump(regenerated, handle, protocol=pickle.HIGHEST_PROTOCOL)

    write_tsv(table_dir / "mutation_status.tsv", status_rows, STATUS_FIELDS)

    reference_compare = None
    if args.compare_reference and not args.skip_reference_compare:
        reference_compare = compare_to_reference(
            regenerated,
            preset.get("reference_pickle"),
        )

    summary = {
        "dataset": args.dataset,
        "n_jobs": len(jobs),
        "n_ok": sum(1 for r in status_rows if r.get("status") == "ok"),
        "n_error": sum(1 for r in status_rows if r.get("status") == "error"),
        "seed": args.seed,
        "seed_mode": args.seed_mode,
        "elapsed_seconds": time.time() - t_run,
        "mutation_table": rel_workspace(mutation_table),
        "pdb_dir": rel_workspace(pdb_dir),
        "pssm_dir": rel_workspace(pssm_dir),
        "output_pickle": rel_workspace(pickle_path),
        "tensor_fields": V3_TENSOR_FIELDS,
        "runtime": {
            "utils_path": rel_workspace(runtime.utils_path),
            "checkpoint_path": rel_workspace(runtime.checkpoint_path),
            "device": str(runtime.device),
            "num_edges": int(runtime.checkpoint["num_edges"]),
        },
        "reference_compare": reference_compare,
        "path_label": (
            "pdb+mutation_table+ProteinMPNN_v6v2_recovery→tensors→engineered+PSSM"
        ),
    }
    (json_dir / "pipeline_summary.json").write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )
    write_report(output_dir, summary)
    print(json.dumps({k: summary[k] for k in (
        "dataset", "n_jobs", "n_ok", "n_error", "elapsed_seconds", "output_pickle"
    )}, indent=2), flush=True)
    return 0 if n_error == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
