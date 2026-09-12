# Independent PDB fetches (unprocessable-mutation recovery)

Date: 2026-09-12  
Branch: `reproduce-paper-results`

This directory holds **independently downloaded** RCSB/PDBe structures used to
isolate whether S_2648 / S_669 pipeline failures were caused by missing/corrupt
ACCRE snapshots versus parser limitations in our code.

## Layout

| Path | Tracked? | Purpose |
| --- | --- | --- |
| `MANIFEST.tsv` / `MANIFEST.json` | yes | Checksums, chain mapping, residue counts |
| `curated/{protein_key}.pdb` | yes (small) | Single-chain polymer extracts |
| `raw/{pdb_id}.pdb` | no (gitignore) | Full depositions; re-fetch via script |
| `../scripts/fetch_independent_problem_pdbs.py` | yes | Re-download + curate |

## Problem set

| protein_key | RCSB | Issue under audit |
| --- | --- | --- |
| `1lveA` | 1lve | ICODE residue labels (PremPS) |
| `2immA` | 2imm | ICODE residue labels (PremPS) |
| `1rtpA` | 1rtp | Numeric chain `1` vs key suffix `A` |
| `2a01A` | 2a01 | Missing from ACCRE PDB dir |
| `3dv0I` | 3dv0 | Missing from ACCRE S_669 PDB dir |

## Re-fetch

```bash
python scripts/fetch_independent_problem_pdbs.py
# or
python scripts/fetch_independent_problem_pdbs.py --force
```

The PDB→features pipeline defaults `--pdb-fallback-dir` to `curated/`.
