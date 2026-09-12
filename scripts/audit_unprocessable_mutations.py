#!/usr/bin/env python3
"""Audit PDB→features pipeline failures into reviewer-facing TSV/JSON.

Re-checks each non-ok row in mutation_status.tsv: PDB/PSSM existence, Bio.PDB
chains, notebook-style residue-map duplicates (ICODE ignored), and historical
V3 pickle completeness. Exclusions are input/structure failures — not RF metrics.
"""
from __future__ import annotations

import argparse
import csv
import json
import pickle
import traceback
from collections import Counter
from pathlib import Path
from typing import Any

from Bio.Data.IUPACData import protein_letters_3to1
from Bio.PDB import PDBParser

WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
ACCRE = (
    WORKSPACE_ROOT
    / "drive_evidence_copy"
    / "sajidahmedprotres_drive"
    / "ACCRE_PyRun_Setup"
)
DIGGING = (
    WORKSPACE_ROOT
    / "drive_evidence_copy"
    / "sajidahmedprotres_drive"
    / "Protein_MPNN_Digging"
)

DEFAULT_DATASETS = {
    "S_2648": {
        "status_tsv": WORKSPACE_ROOT
        / "reproduction_runs/2026-09-12/pdb_to_features_s2648/tables/mutation_status.tsv",
        "summary_json": WORKSPACE_ROOT
        / "reproduction_runs/2026-09-12/pdb_to_features_s2648/json/pipeline_summary.json",
        "pdb_dir": ACCRE / "S_2648_PDB_Files",
        "pssm_dir": ACCRE / "S_2648_pssm_dir",
        "hist_pickle": DIGGING / "S_2648_pmppn_info_dict_V3.pickle",
    },
    "S_669": {
        "status_tsv": WORKSPACE_ROOT
        / "reproduction_runs/2026-09-12/pdb_to_features_s669/tables/mutation_status.tsv",
        "summary_json": WORKSPACE_ROOT
        / "reproduction_runs/2026-09-12/pdb_to_features_s669/json/pipeline_summary.json",
        "pdb_dir": ACCRE / "S_669_PDB_Files",
        "pssm_dir": ACCRE / "S_669_pssm_dir",
        "hist_pickle": DIGGING / "S_669_pmppn_info_dict_V3.pickle",
    },
    "S_921": {
        "status_tsv": WORKSPACE_ROOT
        / "reproduction_runs/2026-09-12/pdb_to_features_s921/tables/mutation_status.tsv",
        "summary_json": WORKSPACE_ROOT
        / "reproduction_runs/2026-09-12/pdb_to_features_s921/json/pipeline_summary.json",
        "pdb_dir": ACCRE / "S_921_PDB_Files",
        "pssm_dir": ACCRE / "S_921_pssm_dir",
        "hist_pickle": DIGGING / "S_921_pmppn_info_dict_V3.pickle",
    },
    "Ssym": {
        "status_tsv": WORKSPACE_ROOT
        / "reproduction_runs/2026-09-12/pdb_to_features_ssym/tables/mutation_status.tsv",
        "summary_json": WORKSPACE_ROOT
        / "reproduction_runs/2026-09-12/pdb_to_features_ssym/json/pipeline_summary.json",
        "pdb_dir": ACCRE / "Ssym_PDB_Files",
        "pssm_dir": ACCRE / "Ssym_pssm_dir",
        "hist_pickle": DIGGING / "Ssym_pmppn_info_dict_V3.pickle",
    },
}


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(WORKSPACE_ROOT))
    except ValueError:
        return str(path)


def hist_lookup(hist: dict, protein_key: str, mutation_label: str) -> dict[str, Any]:
    entries = hist.get(protein_key, [])
    exact = [e for e in entries if e.get("mut") == mutation_label]
    stripped = None
    if len(mutation_label) >= 4 and mutation_label[0].isalpha() and mutation_label[-1].isalpha():
        core = mutation_label[0]
        rest = mutation_label[1:-1]
        alt = mutation_label[-1]
        digits = "".join(ch for ch in rest if ch.isdigit())
        icode = "".join(ch for ch in rest if ch.isalpha())
        if digits and icode:
            stripped = f"{core}{digits}{alt}"
    fuzzy = [e for e in entries if stripped and e.get("mut") == stripped] if stripped else []
    chosen = exact[0] if exact else (fuzzy[0] if fuzzy else None)
    if chosen is None:
        return {
            "historical_v3_present": False,
            "historical_mut_label_matched": None,
            "historical_match_kind": "absent",
            "historical_only_ddg_mut": None,
            "historical_has_mpnn_features": None,
            "historical_n_keys": 0,
        }
    keys = sorted(chosen.keys())
    return {
        "historical_v3_present": True,
        "historical_mut_label_matched": chosen.get("mut"),
        "historical_match_kind": "exact" if exact else "icode_stripped",
        "historical_only_ddg_mut": set(keys) <= {"ddg", "mut"},
        "historical_has_mpnn_features": "center_mut_wild_energy" in chosen,
        "historical_n_keys": len(keys),
    }


def classify_and_check(
    protein_key: str,
    mutation_label: str,
    pdb_dir: Path,
    pssm_dir: Path,
) -> dict[str, Any]:
    pdb_path = pdb_dir / f"{protein_key}.pdb"
    pssm_path = pssm_dir / f"{protein_key}.pssm"
    chain_id = protein_key[-1]
    checked: list[str] = []
    checks: dict[str, Any] = {
        "pdb_path": rel(pdb_path),
        "pdb_exists": pdb_path.exists(),
        "pssm_path": rel(pssm_path),
        "pssm_exists": pssm_path.exists(),
        "expected_chain_id": chain_id,
    }
    checked.append(f"PDB path exists={pdb_path.exists()}: {rel(pdb_path)}")
    checked.append(f"PSSM path exists={pssm_path.exists()}: {rel(pssm_path)}")
    chains: list[str] = []
    icode_residues: list[dict] = []
    duplicate_labels: list[str] = []

    if not pdb_path.exists():
        alts = sorted(
            {
                p.name
                for p in list(pdb_dir.glob(f"{protein_key[:4]}*.pdb"))
                + list(pdb_dir.glob(f"{protein_key[:4].upper()}*.pdb"))
            }
        )
        checks["alternate_pdb_matches"] = alts
        checked.append(f"Alternate PDB glob for {protein_key[:4]}*: {alts or 'none'}")
        return {
            "error_class": "missing_pdb",
            "exception_type": "FileNotFoundError",
            "exception_message": f"Missing PDB: {rel(pdb_path)}",
            "justification": (
                "No ACCRE PDB file named {pk}.pdb and no alternate same-PDB-id files in the "
                "dataset PDB directory. Cannot run ProteinMPNN parse or residue mapping."
            ).format(pk=protein_key),
            "what_was_checked": checked,
            "checks": checks,
            "chains_in_pdb": chains,
            "icode_residues": icode_residues,
            "duplicate_residue_labels": duplicate_labels,
            "reproduced_worker_error": True,
        }

    try:
        parser = PDBParser(QUIET=True)
        structure = parser.get_structure(protein_key, str(pdb_path))
        model = structure[0]
        chains = list(model.child_dict.keys())
        checks["chains_in_model"] = chains
        checked.append(f"Bio.PDB model chains: {chains}")
        if chain_id not in model.child_dict:
            return {
                "error_class": "chain_parse_keyerror",
                "exception_type": "KeyError",
                "exception_message": repr(chain_id),
                "justification": (
                    f"Pipeline derives chain_id from protein_key[-1]={chain_id!r}, but the PDB "
                    f"file's model child chains are {chains}. Bio.PDB model[chain_id] raises KeyError."
                ),
                "what_was_checked": checked,
                "checks": checks,
                "chains_in_pdb": chains,
                "icode_residues": icode_residues,
                "duplicate_residue_labels": duplicate_labels,
                "reproduced_worker_error": True,
            }

        chain = model[chain_id]
        mapping: dict[str, int] = {}
        duplicates: list[str] = []
        for residue in chain:
            het, seq, icode = residue.get_id()
            if het.strip():
                continue
            residue_name = residue.get_resname().title()
            one_letter = protein_letters_3to1.get(residue_name, "X")
            key = f"{one_letter}{seq}"
            if icode.strip():
                icode_residues.append(
                    {
                        "seq": seq,
                        "icode": icode.strip(),
                        "resname": residue.get_resname().strip(),
                        "label_without_icode": key,
                    }
                )
            if key in mapping:
                duplicates.append(key)
            else:
                mapping[key] = len(mapping)
        duplicate_labels = duplicates
        checked.append(f"Residue labels with insertion codes: {len(icode_residues)}")
        checked.append(
            f"Duplicate notebook-style labels (AA+seqnum, icode ignored): {duplicates}"
        )
        if duplicates:
            return {
                "error_class": "duplicate_residue_labels",
                "exception_type": "ValueError",
                "exception_message": (
                    f"Duplicate residue labels in {pdb_path.name} chain {chain_id}: {duplicates}"
                ),
                "justification": (
                    "ACCRE PDB contains multiple residues that share the same sequence number with "
                    "different insertion codes (ICODE). The notebook residue map keys residues as "
                    "one-letter-AA + residue number and ignores ICODE; duplicates make a unique map "
                    "impossible. Historical V6_V2 skipped such proteins after ICODE warnings."
                ),
                "what_was_checked": checked,
                "checks": checks,
                "chains_in_pdb": chains,
                "icode_residues": icode_residues,
                "duplicate_residue_labels": duplicate_labels,
                "reproduced_worker_error": True,
            }

        return {
            "error_class": "other",
            "exception_type": "Unknown",
            "exception_message": "PDB map/chain OK in audit; see pipeline raw error",
            "justification": (
                "PDB exists and residue map builds without duplicate/chain errors; classify from "
                "pipeline logs or extend audit."
            ),
            "what_was_checked": checked,
            "checks": checks,
            "chains_in_pdb": chains,
            "icode_residues": icode_residues,
            "duplicate_residue_labels": duplicate_labels,
            "reproduced_worker_error": False,
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "error_class": "other",
            "exception_type": type(exc).__name__,
            "exception_message": str(exc)[:500],
            "justification": f"Unexpected exception during audit re-check: {type(exc).__name__}",
            "what_was_checked": checked + ["traceback: " + traceback.format_exc()[:800]],
            "checks": checks,
            "chains_in_pdb": chains,
            "icode_residues": icode_residues,
            "duplicate_residue_labels": duplicate_labels,
            "reproduced_worker_error": False,
        }


def audit_dataset(name: str, cfg: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if not cfg["status_tsv"].exists():
        return [], {"dataset": name, "skipped": True, "reason": f"missing {cfg['status_tsv']}"}
    status_rows = list(csv.DictReader(cfg["status_tsv"].open(), delimiter="\t"))
    summary = (
        json.loads(cfg["summary_json"].read_text())
        if cfg["summary_json"].exists()
        else {}
    )
    hist = pickle.load(cfg["hist_pickle"].open("rb")) if cfg["hist_pickle"].exists() else {}
    errors = [r for r in status_rows if r.get("status") != "ok"]
    n_ok = sum(1 for r in status_rows if r.get("status") == "ok")
    rows: list[dict[str, Any]] = []
    class_counts: Counter = Counter()
    for r in errors:
        pk = r["protein_key"]
        mut = r["mutation_label"]
        inv = classify_and_check(pk, mut, cfg["pdb_dir"], cfg["pssm_dir"])
        hist_info = hist_lookup(hist, pk, mut)
        hist_note = ""
        if name == "S_2648" and pk == "1rtpA":
            hist_note = (
                " IMPORTANT: historical V3 contains full MPNN features for 1rtpA/K80S; "
                "regeneration failed on chain-id mismatch (PDB chain '1' vs key suffix 'A'). "
                "New gap vs historical train coverage — not metric-driven."
            )
        row = {
            "dataset": name,
            "protein_key": pk,
            "mutation_label": mut,
            "pipeline_status": r.get("status"),
            "pipeline_error_type_raw": r.get("error_type"),
            "pipeline_error_message_raw": r.get("error_message"),
            "error_class": inv["error_class"],
            "exception_type": inv["exception_type"],
            "exception_message": inv["exception_message"],
            "pdb_path": inv["checks"].get("pdb_path"),
            "pdb_exists": inv["checks"].get("pdb_exists"),
            "pssm_exists": inv["checks"].get("pssm_exists"),
            "chains_in_pdb": ",".join(inv["chains_in_pdb"]) if inv["chains_in_pdb"] else "",
            "duplicate_residue_labels": ",".join(inv["duplicate_residue_labels"]),
            "icode_residue_count": len(inv["icode_residues"]),
            "what_was_checked": " | ".join(inv["what_was_checked"]),
            "justification": inv["justification"] + hist_note,
            "historical_v3_present": hist_info["historical_v3_present"],
            "historical_mut_label_matched": hist_info["historical_mut_label_matched"],
            "historical_match_kind": hist_info["historical_match_kind"],
            "historical_only_ddg_mut_stub": hist_info["historical_only_ddg_mut"],
            "historical_has_mpnn_features": hist_info["historical_has_mpnn_features"],
            "historical_n_keys": hist_info["historical_n_keys"],
            "reproduced_worker_error": inv["reproduced_worker_error"],
            "icode_residues_json": json.dumps(inv["icode_residues"]),
        }
        rows.append(row)
        class_counts[inv["error_class"]] += 1
    summary_out = {
        "dataset": name,
        "skipped": False,
        "n_jobs": len(status_rows),
        "n_ok": n_ok,
        "n_error": len(errors),
        "n_jobs_pipeline_summary": summary.get("n_jobs"),
        "n_ok_pipeline_summary": summary.get("n_ok"),
        "n_error_pipeline_summary": summary.get("n_error"),
        "elapsed_seconds": summary.get("elapsed_seconds"),
        "error_class_counts": dict(class_counts),
        "failed_proteins": sorted({r["protein_key"] for r in rows}),
        "output_pickle": summary.get("output_pickle"),
        "note": (
            "Exclusions are structure/input failures discovered before RF training; "
            "RF used only the processable subset (n_ok). Not selected by metric shopping."
        ),
    }
    return rows, summary_out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--datasets",
        nargs="+",
        default=["S_2648", "S_669", "S_921", "Ssym"],
        choices=list(DEFAULT_DATASETS.keys()),
    )
    parser.add_argument(
        "--require-complete",
        action="store_true",
        help="Exit non-zero if a requested dataset has no finished status_tsv",
    )
    args = parser.parse_args()

    all_rows: list[dict[str, Any]] = []
    dataset_summaries: dict[str, Any] = {}
    for name in args.datasets:
        rows, summary = audit_dataset(name, DEFAULT_DATASETS[name])
        dataset_summaries[name] = summary
        all_rows.extend(rows)
        if args.require_complete and summary.get("skipped"):
            raise SystemExit(f"dataset {name} incomplete: {summary}")

    out_tables = WORKSPACE_ROOT / "manuscript_codebase_mapping" / "tables"
    out_run = (
        WORKSPACE_ROOT
        / "reproduction_runs"
        / "2026-09-12"
        / "unprocessable_mutations_audit"
    )
    out_tables.mkdir(parents=True, exist_ok=True)
    out_run.mkdir(parents=True, exist_ok=True)

    fields = [
        "dataset",
        "protein_key",
        "mutation_label",
        "error_class",
        "exception_type",
        "exception_message",
        "pdb_path",
        "pdb_exists",
        "pssm_exists",
        "chains_in_pdb",
        "duplicate_residue_labels",
        "icode_residue_count",
        "what_was_checked",
        "justification",
        "historical_v3_present",
        "historical_mut_label_matched",
        "historical_match_kind",
        "historical_only_ddg_mut_stub",
        "historical_has_mpnn_features",
        "historical_n_keys",
        "pipeline_status",
        "pipeline_error_type_raw",
        "pipeline_error_message_raw",
        "reproduced_worker_error",
    ]
    payload = {
        "principle": (
            "Exclusions are not metric-driven. Failed jobs could not be featurized from ACCRE PDB "
            "inputs under notebook-faithful residue-map / chain conventions. RF used only n_ok of n_jobs."
        ),
        "datasets": dataset_summaries,
        "error_class_definitions": {
            "missing_pdb": "Expected {protein_key}.pdb absent from ACCRE PDB directory",
            "duplicate_residue_labels": "ICODE collisions under AA+seqnum map (icode ignored)",
            "chain_parse_keyerror": "protein_key chain suffix not present in Bio.PDB model chains",
            "other": "Failure not classified into the above after re-check",
        },
        "rows": all_rows,
    }
    for dest_dir in (out_tables, out_run):
        tsv_path = dest_dir / "unprocessable_mutations.tsv"
        with tsv_path.open("w", newline="") as handle:
            writer = csv.DictWriter(
                handle, fieldnames=fields, delimiter="\t", extrasaction="ignore"
            )
            writer.writeheader()
            for row in all_rows:
                writer.writerow(row)
        (dest_dir / "unprocessable_mutations.json").write_text(
            json.dumps(payload, indent=2), encoding="utf-8"
        )

    print(json.dumps(dataset_summaries, indent=2))
    print(f"n_unprocessable_rows={len(all_rows)}")
    print(f"wrote {rel(out_tables / 'unprocessable_mutations.tsv')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
