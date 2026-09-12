# Fallback PDBs

Independently fetched RCSB/PDBe structures used when a dataset PDB directory
is missing the file. `scripts/extract.py` defaults `--pdb-fallback-dir` here.

| Path | Purpose |
| --- | --- |
| `MANIFEST.tsv` / `MANIFEST.json` | Checksums and chain mapping |
| `curated/{protein_key}.pdb` | Single-chain polymer extracts |

| protein_key | PDB | Why a fallback exists |
| --- | --- | --- |
| `1lveA` | 1lve | ICODE residue labels |
| `2immA` | 2imm | ICODE residue labels |
| `1rtpA` | 1rtp | Numeric chain `1` vs key suffix `A` |
| `2a01A` | 2a01 | Missing from the S2648 PDB dir (also missing PSSM) |
| `3dv0I` | 3dv0 | Missing from the S669 PDB dir |
