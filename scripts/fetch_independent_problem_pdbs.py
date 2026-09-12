#!/usr/bin/env python3
"""Download RCSB/PDBe PDBs for historically unprocessable protein keys.

Writes:
  reproduction_inputs/independent_pdb_fetches/raw/{pdb_id}.pdb
  reproduction_inputs/independent_pdb_fetches/curated/{protein_key}.pdb
  reproduction_inputs/independent_pdb_fetches/MANIFEST.{tsv,json}

Large raw multi-chain depositions are gitignored; curated single-chain polymer
extracts for the problem set are intended to be tracked (small).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from Bio.Data.IUPACData import protein_letters_3to1
from Bio.PDB import PDBIO, PDBParser, Select

WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = WORKSPACE_ROOT / "reproduction_inputs" / "independent_pdb_fetches"

# protein_key → (pdb_id, source_chain, rewrite_chain_or_None)
PROBLEM_SPECS = [
    ("1lveA", "1lve", "A", None),
    ("2immA", "2imm", "A", None),
    ("1rtpA", "1rtp", "1", "A"),
    ("2a01A", "2a01", "A", None),
    ("3dv0I", "3dv0", "I", None),
]


class ChainSelect(Select):
    def __init__(self, chain_id: str):
        self.chain_id = chain_id

    def accept_chain(self, chain):
        return chain.id == self.chain_id

    def accept_residue(self, residue):
        return residue.id[0] == " "

    def accept_atom(self, atom):
        return (not atom.is_disordered()) or atom.get_altloc() in (" ", "A")


def download(pdb_id: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    urls = [
        f"https://files.rcsb.org/download/{pdb_id}.pdb",
        f"https://www.ebi.ac.uk/pdbe/entry-files/download/pdb{pdb_id.lower()}.ent",
    ]
    last_err: Exception | None = None
    for url in urls:
        try:
            urllib.request.urlretrieve(url, dest)
            return
        except Exception as exc:  # noqa: BLE001
            last_err = exc
    raise RuntimeError(f"Failed to download {pdb_id}: {last_err}")


def curate(
    raw_path: Path,
    protein_key: str,
    source_chain: str,
    rewrite_chain: str | None,
    out_path: Path,
) -> dict:
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure(protein_key, str(raw_path))
    for model in list(structure.get_models())[1:]:
        structure.detach_child(model.id)
    model = structure[0]
    select_chain = source_chain
    if rewrite_chain and rewrite_chain != source_chain:
        model[source_chain].id = rewrite_chain
        select_chain = rewrite_chain
    out_path.parent.mkdir(parents=True, exist_ok=True)
    io = PDBIO()
    io.set_structure(structure)
    io.save(str(out_path), ChainSelect(select_chain))
    data = out_path.read_bytes()
    s2 = PDBParser(QUIET=True).get_structure("c", str(out_path))[0]
    chain = next(s2.get_chains())
    seq = "".join(
        protein_letters_3to1.get(r.get_resname().title(), "X")
        for r in chain
        if r.id[0] == " "
    )
    return {
        "protein_key": protein_key,
        "source": "RCSB/PDBe",
        "source_url": f"https://files.rcsb.org/download/{raw_path.stem}.pdb",
        "raw_path": str(raw_path.relative_to(WORKSPACE_ROOT)),
        "curated_path": str(out_path.relative_to(WORKSPACE_ROOT)),
        "source_chain": source_chain,
        "curated_chain": select_chain,
        "n_polymer_residues": len(seq),
        "sequence_sha256": hashlib.sha256(seq.encode()).hexdigest()[:16],
        "size_bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "fetched_utc": datetime.now(timezone.utc).isoformat(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-root", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    raw_dir = args.out_root / "raw"
    curated_dir = args.out_root / "curated"
    rows = []
    for protein_key, pdb_id, source_chain, rewrite in PROBLEM_SPECS:
        raw_path = raw_dir / f"{pdb_id}.pdb"
        if args.force or not raw_path.exists():
            print(f"download {pdb_id} → {raw_path}")
            download(pdb_id, raw_path)
        else:
            print(f"reuse raw {raw_path}")
        out_path = curated_dir / f"{protein_key}.pdb"
        row = curate(raw_path, protein_key, source_chain, rewrite, out_path)
        rows.append(row)
        print(
            f"  curated {protein_key}: nres={row['n_polymer_residues']} "
            f"sha={row['sha256'][:12]}"
        )
    man_json = args.out_root / "MANIFEST.json"
    man_tsv = args.out_root / "MANIFEST.tsv"
    man_json.write_text(json.dumps({"fetched": rows}, indent=2) + "\n")
    cols = [
        "protein_key",
        "source_url",
        "curated_path",
        "source_chain",
        "curated_chain",
        "n_polymer_residues",
        "size_bytes",
        "sha256",
    ]
    with man_tsv.open("w", encoding="utf-8") as handle:
        handle.write("\t".join(cols) + "\n")
        for row in rows:
            handle.write("\t".join(str(row[c]) for c in cols) + "\n")
    print(f"wrote {man_json} and {man_tsv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
