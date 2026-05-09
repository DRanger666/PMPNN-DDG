#!/usr/bin/env python3
"""Check S_669 3dv0I mutation positions against a downloaded RCSB 3DV0 PDB.

This script intentionally checks only the current downloaded reference
structure. It does not prove what was present in the old 2022 ACCRE input
directory.
"""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path


THREE_TO_ONE = {
    "ALA": "A",
    "ARG": "R",
    "ASN": "N",
    "ASP": "D",
    "CYS": "C",
    "GLN": "Q",
    "GLU": "E",
    "GLY": "G",
    "HIS": "H",
    "ILE": "I",
    "LEU": "L",
    "LYS": "K",
    "MET": "M",
    "PHE": "F",
    "PRO": "P",
    "SER": "S",
    "THR": "T",
    "TRP": "W",
    "TYR": "Y",
    "VAL": "V",
    "MSE": "M",
    "SEC": "U",
    "PYL": "O",
}


def read_unique_mutations(path: Path) -> list[str]:
    """Read unique mutations from the S_669 remaining-fields table."""

    mutations: list[str] = []
    seen: set[str] = set()
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        for row in reader:
            mutation = row["mut"].strip()
            if mutation and mutation not in seen:
                mutations.append(mutation)
                seen.add(mutation)
    return mutations


def parse_pdb(path: Path):
    """Collect residue identities, atoms, insertion codes, and altlocs."""

    residues: dict[tuple[str, int, str], str] = {}
    atoms: dict[tuple[str, int, str], set[str]] = defaultdict(set)
    altlocs: dict[tuple[str, int, str], set[str]] = defaultdict(set)
    insertion_codes: dict[tuple[str, int], set[str]] = defaultdict(set)
    missing_atoms: dict[tuple[str, int], list[str]] = defaultdict(list)

    for line in path.read_text(errors="replace").splitlines():
        if line.startswith("ATOM  "):
            chain = line[21].strip() or " "
            resseq = int(line[22:26])
            icode = line[26].strip()
            altloc = line[16].strip()
            resname = line[17:20].strip()
            atom = line[12:16].strip()
            key = (chain, resseq, icode)

            residues[key] = resname
            atoms[key].add(atom)
            if altloc:
                altlocs[key].add(altloc)
            if icode:
                insertion_codes[(chain, resseq)].add(icode)

        if line.startswith("REMARK 470"):
            parts = line.split()
            if len(parts) >= 6 and len(parts[3]) == 1:
                try:
                    resseq = int(parts[4])
                except ValueError:
                    continue
                missing_atoms[(parts[3], resseq)].extend(parts[5:])

    return residues, atoms, insertion_codes, altlocs, missing_atoms


def check_mutations(
    mutations: list[str],
    chain_id: str,
    residues: dict[tuple[str, int, str], str],
    atoms: dict[tuple[str, int, str], set[str]],
    insertion_codes: dict[tuple[str, int], set[str]],
    altlocs: dict[tuple[str, int, str], set[str]],
    missing_atoms: dict[tuple[str, int], list[str]],
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for mutation in mutations:
        wt = mutation[0]
        position = int(mutation[1:-1])
        matches = [
            (key, residues[key])
            for key in sorted(residues)
            if key[0] == chain_id and key[1] == position
        ]

        if not matches:
            rows.append(
                {
                    "mutation": mutation,
                    "chain_position_status": "absent",
                    "pdb_resname": "-",
                    "pdb_one_letter": "-",
                    "wt_check": "NO_ATOM_RESIDUE",
                    "atom_count": "0",
                    "insertion_codes": "-",
                    "altlocs": "-",
                    "missing_atoms_remark470": "-",
                }
            )
            continue

        key, resname = matches[0]
        one_letter = THREE_TO_ONE.get(resname, "?")
        rows.append(
            {
                "mutation": mutation,
                "chain_position_status": "present",
                "pdb_resname": resname,
                "pdb_one_letter": one_letter,
                "wt_check": "WT_MATCH" if one_letter == wt else "WT_MISMATCH",
                "atom_count": str(len(atoms[key])),
                "insertion_codes": ",".join(sorted(insertion_codes.get((chain_id, position), [])))
                or "-",
                "altlocs": ",".join(sorted(altlocs.get(key, []))) or "-",
                "missing_atoms_remark470": ",".join(missing_atoms.get((chain_id, position), []))
                or "-",
            }
        )

    return rows


def write_tsv(path: Path, rows: list[dict[str, str]]) -> None:
    fieldnames = [
        "mutation",
        "chain_position_status",
        "pdb_resname",
        "pdb_one_letter",
        "wt_check",
        "atom_count",
        "insertion_codes",
        "altlocs",
        "missing_atoms_remark470",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            delimiter="\t",
            fieldnames=fieldnames,
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--pdb",
        type=Path,
        default=Path("external_reference_structures/rcsb/3DV0/3DV0.pdb"),
    )
    parser.add_argument(
        "--mutations",
        type=Path,
        default=Path(
            "pickle_analysis/s669_instance_coverage/tables/"
            "s669_3dv0i_v3_remaining_fields.tsv"
        ),
    )
    parser.add_argument("--chain", default="I")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "external_reference_structures/rcsb/3DV0/"
            "s669_3dv0I_mutation_position_check.tsv"
        ),
    )
    args = parser.parse_args()

    mutations = read_unique_mutations(args.mutations)
    residues, atoms, insertion_codes, altlocs, missing_atoms = parse_pdb(args.pdb)
    rows = check_mutations(
        mutations,
        args.chain,
        residues,
        atoms,
        insertion_codes,
        altlocs,
        missing_atoms,
    )
    write_tsv(args.output, rows)

    present = sum(row["chain_position_status"] == "present" for row in rows)
    wt_match = sum(row["wt_check"] == "WT_MATCH" for row in rows)
    with_missing_atoms = [
        row for row in rows if row["missing_atoms_remark470"] != "-"
    ]
    print(f"mutations={len(rows)} present={present} wt_match={wt_match}")
    print(f"rows_with_remark470_missing_atoms={len(with_missing_atoms)}")
    for row in with_missing_atoms:
        print(
            row["mutation"],
            row["pdb_resname"],
            row["missing_atoms_remark470"],
            sep="\t",
        )


if __name__ == "__main__":
    main()
