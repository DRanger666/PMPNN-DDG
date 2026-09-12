#!/usr/bin/env python3
"""PDB + mutation table + ProteinMPNN → V3 tensors → engineered/PSSM features.

Clean reproduction path:

  ACCRE PDB dirs + mutation_ddg_tables + v_48_020.pt
    → modified_proteinmpnn (baked-in extraction hooks)
    → proteinmpnn_ddg_recovery.features (A–H)
    → regenerated V3-shaped pickle under reproduction_runs/

Prefer --by-protein-subprocess --compact-for-rf for full datasets (isolates RSS).
"""

from __future__ import annotations

import argparse
import csv
import gc
import json
import pickle
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
import torch

WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))


def rel_workspace(path: Path) -> str:
    path = Path(path)
    try:
        return str(path.resolve().relative_to(WORKSPACE_ROOT))
    except ValueError:
        return str(path)


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

RF_KEEP_FIELDS = [
    "mut",
    "ddg",
    "center_mut_wild_energy",
    "center_entropy",
    "V2_backward_weighted_neighbor_energy_changes",
    "weighted_neighbor_forward_KL",
    "V2_backward_weighted_neighbor_backward_KL",
    "wild_pssm",
    "alternate_pssm",
    "V2_backward_weighted_neighbor_entropy_changes",
    "center_neighbor_weight_check_w_m",
    "neighbor_embedding_change_m_w",
    "neighbor_embedding_change_m_w_raw",
    "neighbor_message_change_m_w_raw",
    "feature_A",
    "feature_B_historical_weighted",
    "feature_B_manuscript_unweighted",
    "feature_C",
    "feature_D",
    "feature_F",
    "feature_G",
    "feature_H",
]

STATUS_FIELDS = [
    "protein_key",
    "mutation_label",
    "sequence_index",
    "status",
    "elapsed_seconds",
    "error_type",
    "error_message",
]


def compact_entry_for_rf(entry: dict[str, Any]) -> dict[str, Any]:
    return {key: entry[key] for key in RF_KEEP_FIELDS if key in entry}


def load_mutation_jobs(
    table_path: Path,
    table_kind: str,
    forward_only: bool,
    protein_key_filter: str | None,
    limit: int | None,
) -> list[dict[str, Any]]:
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
                {"protein_key": protein_key, "mutation_label": mutation, "ddg": ddg}
            )
            if limit is not None and len(jobs) >= limit:
                return jobs
        return jobs

    if table_kind == "s669_csv":
        with table_path.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        for row in rows:
            protein = str(row["Protein"])
            pdb_wild = str(row.get("PDB_wild", protein[:4])).lower()
            chain = protein[4:] if len(protein) > 4 else "A"
            protein_key = f"{pdb_wild}{chain}"
            mutation = str(row["PDB_Mut"])
            ddg = float(row["DDG_checked_dir"])
            if protein_key_filter is not None and protein_key != protein_key_filter:
                continue
            jobs.append(
                {"protein_key": protein_key, "mutation_label": mutation, "ddg": ddg}
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
    sequence_index = residue_map[mutation_label[:-1]]
    extracted = extract_mutation_tensor_fields(
        runtime,
        proteins[protein_key],
        protein_key,
        mutation_label,
        sequence_index,
    )
    entry = build_v3_entry_from_extraction(
        extracted, float(job["ddg"]), pssm_dir=pssm_dir
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
            if "top_15_neighbor_indices" in entry and "top_15_neighbor_indices" in ref:
                if np.array_equal(
                    np.asarray(entry["top_15_neighbor_indices"]),
                    np.asarray(ref["top_15_neighbor_indices"]),
                ):
                    n_top15_exact += 1
            if "log_prob" in entry and "log_prob" in ref:
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


def write_report(output_dir: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# PDB → ProteinMPNN → Features Pipeline Report",
        "",
        f"- Dataset: `{summary['dataset']}`",
        f"- Jobs: `{summary['n_jobs']}` OK=`{summary['n_ok']}` errors=`{summary['n_error']}`",
        f"- Seed mode: `{summary['seed_mode']}` seed=`{summary['seed']}`",
        f"- Utils: `{summary['runtime']['utils_path']}`",
        f"- Elapsed s: `{summary['elapsed_seconds']:.1f}`",
        "",
        "Open fidelity questions (not assumed bugs): decoder RNG, Feature B weighting,",
        "zero-vector fallback — see MANUSCRIPT_TENSOR_EXTRACTION_FIDELITY.md.",
        "",
    ]
    if summary.get("reference_compare"):
        cmp_ = summary["reference_compare"]
        lines.extend(
            [
                "## Optional historical pickle compare",
                f"- compared={cmp_['n_compared']} top15_exact={cmp_['top15_neighbor_exact']} "
                f"log_prob_close={cmp_['log_prob_allclose']}",
                f"- scalars={json.dumps(cmp_['scalar_allclose'])}",
                "",
            ]
        )
    (output_dir / "PIPELINE_REPORT.md").write_text("\n".join(lines), encoding="utf-8")


def run_by_protein_subprocess(
    jobs: list[dict[str, Any]],
    *,
    pdb_dir: Path,
    pssm_dir: Path,
    checkpoint: Path,
    utils_path: Path,
    device: str,
    seed: int,
    seed_mode: str,
    compact_for_rf: bool,
    output_dir: Path,
) -> tuple[dict[str, list[dict[str, Any]]], list[dict[str, Any]]]:
    worker = WORKSPACE_ROOT / "scripts" / "_pdb_to_features_one_protein.py"
    shard_dir = output_dir / "shards"
    table_dir = output_dir / "tables"
    shard_dir.mkdir(parents=True, exist_ok=True)
    table_dir.mkdir(parents=True, exist_ok=True)

    by_protein: dict[str, list[dict[str, Any]]] = {}
    for job in jobs:
        by_protein.setdefault(job["protein_key"], []).append(job)

    regenerated: dict[str, list[dict[str, Any]]] = {}
    status_rows: list[dict[str, Any]] = []
    global_index = 0
    python = sys.executable

    for protein_i, (protein_key, protein_jobs) in enumerate(by_protein.items(), start=1):
        jobs_path = shard_dir / f"{protein_key}.jobs.pkl"
        out_path = shard_dir / f"{protein_key}.out.pkl"
        with jobs_path.open("wb") as handle:
            pickle.dump(protein_jobs, handle)
        cmd = [
            python,
            str(worker),
            "--protein-key",
            protein_key,
            "--jobs-pickle",
            str(jobs_path),
            "--out-pickle",
            str(out_path),
            "--pdb-dir",
            str(pdb_dir),
            "--pssm-dir",
            str(pssm_dir),
            "--checkpoint",
            str(checkpoint),
            "--utils-path",
            str(utils_path),
            "--device",
            device,
            "--seed",
            str(seed),
            "--seed-mode",
            seed_mode,
            "--global-index-base",
            str(global_index),
        ]
        if compact_for_rf:
            cmd.append("--compact-for-rf")
        print(
            f"[protein {protein_i}/{len(by_protein)}] {protein_key} "
            f"n_mut={len(protein_jobs)}",
            flush=True,
        )
        completed = subprocess.run(cmd, check=False)
        if completed.returncode != 0 or not out_path.exists():
            for job in protein_jobs:
                status_rows.append(
                    {
                        "protein_key": protein_key,
                        "mutation_label": job["mutation_label"],
                        "sequence_index": "",
                        "status": "error",
                        "elapsed_seconds": "",
                        "error_type": "WorkerFailed",
                        "error_message": f"returncode={completed.returncode}",
                    }
                )
            global_index += len(protein_jobs)
            continue
        payload = pickle.load(out_path.open("rb"))
        regenerated[protein_key] = payload["entries"]
        status_rows.extend(payload["statuses"])
        global_index += len(protein_jobs)
        with (output_dir / "regenerated_v3_features.partial.pickle").open("wb") as handle:
            pickle.dump(regenerated, handle, protocol=pickle.HIGHEST_PROTOCOL)
        write_tsv(table_dir / "mutation_status.tsv", status_rows, STATUS_FIELDS)
        gc.collect()
    return regenerated, status_rows


def run_inprocess(
    jobs: list[dict[str, Any]],
    *,
    runtime: Any,
    pdb_dir: Path,
    pssm_dir: Path,
    seed: int,
    seed_mode: str,
    compact_for_rf: bool,
    output_dir: Path,
) -> tuple[dict[str, list[dict[str, Any]]], list[dict[str, Any]]]:
    regenerated: dict[str, list[dict[str, Any]]] = {}
    status_rows: list[dict[str, Any]] = []
    residue_maps: dict[str, dict[str, int]] = {}
    proteins: dict[str, dict[str, Any]] = {}
    last_protein = None
    table_dir = output_dir / "tables"
    table_dir.mkdir(parents=True, exist_ok=True)

    for index, job in enumerate(jobs):
        maybe_seed(seed, seed_mode, index)
        try:
            entry, status = process_job(
                runtime, job, pdb_dir, pssm_dir, residue_maps, proteins
            )
            if compact_for_rf:
                entry = compact_entry_for_rf(entry)
            regenerated.setdefault(job["protein_key"], []).append(entry)
            status_rows.append(status)
            print(
                f"[{index + 1}/{len(jobs)}] ok {job['protein_key']} "
                f"{job['mutation_label']} ({status['elapsed_seconds']}s)",
                flush=True,
            )
        except Exception as exc:  # noqa: BLE001
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
        if last_protein is not None and job["protein_key"] != last_protein:
            proteins.pop(last_protein, None)
            residue_maps.pop(last_protein, None)
        last_protein = job["protein_key"]
        gc.collect()
        if (index + 1) % 5 == 0 or index + 1 == len(jobs):
            write_tsv(table_dir / "mutation_status.tsv", status_rows, STATUS_FIELDS)
            with (output_dir / "regenerated_v3_features.partial.pickle").open("wb") as handle:
                pickle.dump(regenerated, handle, protocol=pickle.HIGHEST_PROTOCOL)
    return regenerated, status_rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", choices=list(DATASET_PRESETS.keys()), default="Ssym")
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
    )
    parser.add_argument("--protein-key", default=None)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=WORKSPACE_ROOT / "reproduction_runs" / "2026-09-12" / "pdb_to_features_ssym",
    )
    parser.add_argument("--compare-reference", action="store_true")
    parser.add_argument("--by-protein-subprocess", action="store_true")
    parser.add_argument("--compact-for-rf", action="store_true")
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
        f"seed_mode={args.seed_mode} seed={args.seed} "
        f"subprocess={args.by_protein_subprocess} compact={args.compact_for_rf}",
        flush=True,
    )

    t_run = time.time()
    if args.by_protein_subprocess:
        regenerated, status_rows = run_by_protein_subprocess(
            jobs,
            pdb_dir=pdb_dir,
            pssm_dir=pssm_dir,
            checkpoint=args.checkpoint,
            utils_path=args.utils_path,
            device=args.device,
            seed=args.seed,
            seed_mode=args.seed_mode,
            compact_for_rf=args.compact_for_rf,
            output_dir=output_dir,
        )
        runtime = load_runtime(
            utils_path=args.utils_path,
            checkpoint_path=args.checkpoint,
            device=args.device,
        )
    else:
        runtime = load_runtime(
            utils_path=args.utils_path,
            checkpoint_path=args.checkpoint,
            device=args.device,
        )
        regenerated, status_rows = run_inprocess(
            jobs,
            runtime=runtime,
            pdb_dir=pdb_dir,
            pssm_dir=pssm_dir,
            seed=args.seed,
            seed_mode=args.seed_mode,
            compact_for_rf=args.compact_for_rf,
            output_dir=output_dir,
        )

    pickle_path = output_dir / "regenerated_v3_features.pickle"
    with pickle_path.open("wb") as handle:
        pickle.dump(regenerated, handle, protocol=pickle.HIGHEST_PROTOCOL)
    write_tsv(table_dir / "mutation_status.tsv", status_rows, STATUS_FIELDS)

    reference_compare = None
    if args.compare_reference:
        reference_compare = compare_to_reference(
            regenerated, preset.get("reference_pickle")
        )

    n_ok = sum(1 for r in status_rows if r.get("status") == "ok")
    n_error = sum(1 for r in status_rows if r.get("status") == "error")
    summary = {
        "dataset": args.dataset,
        "n_jobs": len(jobs),
        "n_ok": n_ok,
        "n_error": n_error,
        "seed": args.seed,
        "seed_mode": args.seed_mode,
        "by_protein_subprocess": args.by_protein_subprocess,
        "compact_for_rf": args.compact_for_rf,
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
            "pdb+mutation_table+modified_proteinmpnn→features_A-H→pickle"
        ),
    }
    (json_dir / "pipeline_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    write_report(output_dir, summary)
    print(
        json.dumps(
            {
                k: summary[k]
                for k in (
                    "dataset",
                    "n_jobs",
                    "n_ok",
                    "n_error",
                    "elapsed_seconds",
                    "output_pickle",
                )
            },
            indent=2,
        ),
        flush=True,
    )
    return 0 if n_error == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
