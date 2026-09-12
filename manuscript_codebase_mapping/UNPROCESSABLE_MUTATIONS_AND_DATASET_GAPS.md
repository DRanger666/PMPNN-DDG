# Unprocessable Mutations and Dataset Gaps (PDB → features)

Date: 2026-09-12  
Branch: `reproduce-paper-results`  
Machine-readable companions:

- `manuscript_codebase_mapping/tables/unprocessable_mutations.tsv`
- `manuscript_codebase_mapping/tables/unprocessable_mutations.json`
- Copy under `reproduction_runs/2026-09-12/unprocessable_mutations_audit/`

Related prior instance-level notes (historical saved V3 stubs, not this regen
audit):

- `manuscript_codebase_mapping/S2648_INSTANCE_LEVEL_FEATURE_ABSENCE.md`
- `manuscript_codebase_mapping/S669_3DV0I_INSTANCE_LEVEL_FEATURE_ABSENCE.md`

## Non-negotiable framing (reviewer-facing)

**Exclusions are not metric-driven.**

1. Failures were discovered during PDB → modified ProteinMPNN → feature
   extraction, **before** Random Forest training/evaluation.
2. No mutation was dropped because it hurt correlation, RMSE, or Table 1 match.
3. RF used only the **processable subset** produced by the pipeline (`n_ok` of
   `n_jobs`). Regenerated-train metrics in `REPRODUCTION_STATUS.md` must be read
   with those denominators.
4. Where the historical V3 pickle also lacked ProteinMPNN-derived fields for the
   same instances, that is recorded explicitly. Where historical V3 **had**
   features but this regeneration failed, that is also recorded explicitly
   (see `1rtpA` below) — nothing is papered over.

## Regeneration coverage (S_2648)

| Quantity | Value |
| --- | ---: |
| `n_jobs` (mutation-table rows / pipeline jobs) | 2648 |
| `n_ok` (featurized) | 2619 |
| `n_error` (unprocessable in this run) | 29 |
| Wall time | ~3480 s |

Artifact:
`reproduction_runs/2026-09-12/pdb_to_features_s2648/regenerated_v3_features.pickle`

RF override run (`rf_from_regenerated_s2648_ssym`) kept **2619** S_2648 forward
entries (`skipped_incomplete=0` among regenerated rows). Saved-path historical
RF previously skipped **28** incomplete stubs (`1lveA`+`2immA`+`2a01A`); this
regeneration additionally could not process **`1rtpA/K80S`** (see below), so
train `n_ok` is 2619 rather than 2620.

## Error-class counts (S_2648, 29 jobs)

| Error class | Count | Proteins |
| --- | ---: | --- |
| `duplicate_residue_labels` | 27 | `1lveA` (17), `2immA` (10) |
| `chain_parse_keyerror` | 1 | `1rtpA` |
| `missing_pdb` | 1 | `2a01A` |
| `other` | 0 | — |

### Class definitions

| Class | Meaning |
| --- | --- |
| `missing_pdb` | Expected `{protein_key}.pdb` absent from ACCRE PDB directory (no alternate same-id file). |
| `duplicate_residue_labels` | Multiple residues share AA+seqnum when ICODE is ignored (notebook-faithful map). |
| `chain_parse_keyerror` | `protein_key[-1]` chain suffix not present in Bio.PDB model chains. |
| `other` | Re-check did not fall into the above (none for S_2648). |

## Investigation method

For every failed job in
`reproduction_runs/2026-09-12/pdb_to_features_s2648/tables/mutation_status.tsv`:

1. Re-ran `scripts/_pdb_to_features_one_protein.py` with stderr capture.
2. Checked PDB/PSSM path existence under
   `drive_evidence_copy/.../ACCRE_PyRun_Setup/S_2648_*`.
3. Parsed the PDB with Bio.PDB: listed chains; rebuilt the notebook-style
   residue map (`{one_letter}{seqnum}`, **ICODE ignored**) matching
   `build_residue_index_map` in `proteinmpnn_ddg_recovery/recovered_v6v2.py`.
4. Compared each mutation to `S_2648_pmppn_info_dict_V3.pickle` (exact mut label
   and ICODE-stripped fuzzy match for PremPS labels like `V27BL` → `V27L`).

## Per-protein findings

### `1lveA` — 17 jobs — `duplicate_residue_labels`

- **PDB:** `.../S_2648_PDB_Files/1lveA.pdb` (exists); PSSM exists.
- **Worker error:** `ValueError: Duplicate residue labels in 1lveA.pdb chain A: ['S27', 'S27']`
  (reproduced).
- **Checked:** Chain `A` present. Sequence number **27** has residues with
  ICODEs ` ` (Gln), `A`–`F` (Ser, Val, Leu, Tyr, Ser, Ser). Notebook map keys
  collide on `*27`.
- **Mutation table:** PremPS labels encode ICODE for some sites (`V27BL`,
  `L27CQ`, `L27CN`, `Y27DD`); others are ordinary labels on the same protein.
  Protein-level map failure blocks **all** mutations for this PDB.
- **Historical V3:** All 17 entries exist as **`ddg`+`mut` stubs only** (no
  ProteinMPNN-derived fields). Saved V6_V2 trace documents ICODE skip for
  `1lveA:S27` (see `S2648_INSTANCE_LEVEL_FEATURE_ABSENCE.md`).
- **Justification:** Unprocessable under ICODE-ignoring residue map; same skip
  class as the historical run. Not metric-driven.

### `2immA` — 10 jobs — `duplicate_residue_labels`

- **PDB/PSSM:** present (`2immA.pdb`).
- **Worker error:** `ValueError: Duplicate residue labels in 2immA.pdb chain A: ['N31', 'N31']`
  (reproduced).
- **Checked:** Seq **31** has ICODEs ` ` (Asn) plus `A`–`F`. Collides on `N31`
  (and other AA+31 keys as map enumeration hits duplicates).
- **Historical V3:** All 10 entries are **`ddg`+`mut` stubs only**. Saved trace
  ICODE warning `2immA:N31`.
- **Justification:** Same ICODE / duplicate-label class as historical skip.

### `2a01A` — 1 job (`L141R`) — `missing_pdb`

- **PDB path checked:**
  `drive_evidence_copy/.../ACCRE_PyRun_Setup/S_2648_PDB_Files/2a01A.pdb` —
  **absent**. Glob `2a01*` / `2A01*` in that directory: **none**. PSSM absent.
- **Worker error:** `FileNotFoundError` (reproduced).
- **Historical V3:** Entry present as **`ddg`+`mut` stub only** (no MPNN
  features). Prior analysis: absent from saved execution PDB-directory trace
  (`S2648_INSTANCE_LEVEL_FEATURE_ABSENCE.md`).
- **Justification:** No local structure file to featurize. Not metric-driven.

### `1rtpA` — 1 job (`K80S`) — `chain_parse_keyerror` (**honesty flag**)

- **PDB/PSSM:** present (`1rtpA.pdb`).
- **Worker error:** `KeyError: 'A'` in `build_residue_index_map` (reproduced).
- **Checked:** Bio.PDB model chains are **`['1']`** only (ATOM column 22 is
  digit `1`). Pipeline sets `chain_id = protein_key[-1]` → `'A'` from key
  `1rtpA` / mutation-table chain column `A`. Chain `A` is not in the file.
- **Historical V3:** Entry **`K80S` has full ProteinMPNN-derived features**
  (`historical_has_mpnn_features=true`, 43 keys). So the **historical** run
  successfully featurized this mutation (likely different chain handling or
  file), while **this** regeneration did not.
- **Justification for exclusion in *this* run:** Current clean pipeline cannot
  open chain `A` in the ACCRE file as shipped. Recovery would require an
  explicit chain-remapping policy (e.g. treat lone chain `1` as the intended
  chain) — **not applied** in the 2026-09-12 regeneration. Exclusion is still
  input/parser constraint, not RF metric selection — but it is a **new gap
  versus historical train coverage** and must not be conflated with the 28
  historical stubs.

## Per-job machine-readable rows

Every failed job has one row in
`manuscript_codebase_mapping/tables/unprocessable_mutations.tsv` with:

dataset, protein, mutation, error_class, exception, PDB path, existence flags,
chains, duplicate labels, what_was_checked, justification, historical V3
presence / stub-vs-full features.

Do not summarize away individual mutations when discussing integrity: use the
TSV/JSON as the canonical list.

## S_669 / S_921

As of this document’s S_2648 audit freeze, S_669 regeneration was still running
and S_921 had not finished. When those pipelines complete, re-run the audit
generator (or extend this file) so **every** failed job receives the same
per-mutation treatment. Historical S_669 gap `3dv0I` (31 stubs) is already
documented in `S669_3DV0I_INSTANCE_LEVEL_FEATURE_ABSENCE.md`; regen may surface
the same or different classes — both must be listed.

## What we did *not* do

- We did not delete mutations from the mutation tables to improve scores.
- We did not silently coerce ICODE maps or chain IDs to force a higher `n_ok`
  without documenting the policy change.
- We did not claim bit-exact historical tensor match for processable rows
  (PSSM matched; MPNN tensors remain non-bit-exact under open RNG questions).

## RF implication (explicit)

Regenerated S_2648 train matrix: **2619** forward examples.  
Paper Table 1 comparisons under `--v3-pickle-override` use that subset plus
processable eval sets. Metrics are reported honestly against paper numbers; the
denominator difference vs a hypothetical 2620-example historical train
(`1rtpA` included historically) is small but **not zero** and is called out
here so reviewers are not misled.
