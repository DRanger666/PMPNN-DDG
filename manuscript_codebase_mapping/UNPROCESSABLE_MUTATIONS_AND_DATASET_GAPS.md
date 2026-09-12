# Unprocessable Mutations and Dataset Gaps (PDB → features)

Date: 2026-09-12 (updated after independent PDB re-download + parser fixes)  
Branch: `reproduce-paper-results`  
Machine-readable companions:

- `manuscript_codebase_mapping/tables/unprocessable_mutations.tsv`
- `manuscript_codebase_mapping/tables/unprocessable_mutations.json`
- Copy under `reproduction_runs/2026-09-12/unprocessable_mutations_audit/`
- Independent PDBs: `reproduction_inputs/independent_pdb_fetches/`

## Non-negotiable framing (reviewer-facing)

**Exclusions are not metric-driven.**

1. Failures were discovered during PDB → modified ProteinMPNN → feature extraction, **before** RF.
2. No mutation was dropped because it hurt correlation, RMSE, or Table 1 match.
3. RF uses only the processable subset (`n_ok`).
4. Every prior failure was re-investigated with an **independent RCSB/PDBe download** and improved parsing before being marked unprocessable.

## S_2648 recovery of the original 29 errors

| Quantity | Value |
| --- | ---: |
| Prior `n_error` (first regen) | 29 |
| Recovered after re-download + parser fixes | **28** |
| Remaining genuinely unprocessable | **1** |
| Current `n_ok` / `n_jobs` | **2647** / 2648 |

### Recovered (28)

| Protein | n | Prior class | Fix |
| --- | ---: | --- | --- |
| `1lveA` | 17 | duplicate_residue_labels (ICODE) | PremPS ICODE-aware residue map; ACCRE≡RCSB seq |
| `2immA` | 10 | duplicate_residue_labels (ICODE) | same |
| `1rtpA` | 1 | chain_parse_keyerror (`1` vs `A`) | alphabet→number chain resolve + key remap |

Independent downloads for `1lve`/`2imm`/`1rtp` matched ACCRE polymer sequences (not corrupt snapshots). Failures were **parser limitations** in our code.

### Remaining (1)

| Protein | Mutation | Class | Justification |
| --- | --- | --- | --- |
| `2a01A` | `L141R` | `missing_pssm` | ACCRE PDB absent; RCSB curated chain A loads and residue map builds (`L141` present). Historical ACCRE PSSM also absent; not regenerated. Historical V3 was ddg+mut stub only. |

## Current remaining failures by dataset

### S_2648 (1 errors)

| Class | Count | Proteins |
| --- | ---: | --- |
| `missing_pssm` | 1 | 2a01A |

### S_669 (31 errors; 638/669 ok)

| Class | Count | Proteins |
| --- | ---: | --- |
| `missing_pssm` | 31 | 3dv0I |

All 31 S_669 failures are `3dv0I`: ACCRE PDB/PSSM missing historically; independent RCSB `3DV0` chain `I` curated extract parses (43-residue fragment; all mutation sites present). Residual blocker: **missing PSSM**.

### S_921 / Ssym

- S_921 (partial status while regen continues): n_ok=120, n_error=0
- Ssym: n_ok=342, n_error=0 (zero unprocessable)

## Code changes (PDB processing)

1. **ICODE-aware `build_residue_index_map`**: keys `{AA}{seqnum}{icode}` when ICODE non-blank (PremPS `V27BL` → `V27B`).
2. **`resolve_pdb_chain_id`**: exact match → alphabet-to-number (`A`→`1`) → sole polymer chain; remap ProteinMPNN seq/coords keys to logical chain.
3. **`resolve_pdb_path` + `--pdb-fallback-dir`**: use `reproduction_inputs/independent_pdb_fetches/curated/` when ACCRE lacks the file.
4. **Fetch script**: `scripts/fetch_independent_problem_pdbs.py`.

## Investigation method (per remaining failure)

1. Independent RCSB/PDBe download → curated single-chain extract + MANIFEST checksums.
2. Compare ACCRE vs independent polymer sequence when both exist.
3. Build ICODE-aware residue map with chain resolution.
4. Confirm PSSM presence/absence.
5. Only then mark unprocessable with written justification.

## What we did *not* do

- Invent PSSM scores for `2a01A` / `3dv0I`.
- Drop mutations to improve RF metrics.
- Leave `1rtpA` as a silent new gap (recovered via chain remap).

## RF implication

Regenerated S_2648 train matrix after recovery: **2647** forward examples (was 2619 before recovery). Re-run RF with the updated pickle for Table 1 comparison.
