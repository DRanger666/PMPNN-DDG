# S_669 3dv0I RCSB Reference Check

Date: 2026-05-09

## Scope

This note checks a freshly downloaded current RCSB reference structure for
`3DV0`, chain `I`, because `3dv0I` is the only S_669 protein key absent from
the copied old S_669 PDB/PSSM input directories.

This is not old 2022 input evidence. The downloaded PDB has later RCSB revision
records, including an ATOM-record revision on 2023-11-15, so it should be used
only as a current reference for structural plausibility checks.

Downloaded files:

```text
external_reference_structures/rcsb/3DV0/3DV0_core_entry.json
external_reference_structures/rcsb/3DV0/3DV0.pdb
```

Mutation-position check:

```text
scripts/check_s669_3dv0_rcsb_reference.py
external_reference_structures/rcsb/3DV0/s669_3dv0I_mutation_position_check.tsv
```

## RCSB Structure Summary

`3DV0` is an X-ray diffraction structure at 2.50 A resolution:

```text
SNAPSHOTS OF CATALYSIS IN THE E1 SUBUNIT OF THE PYRUVATE DEHYDROGENASE
MULTI-ENZYME COMPLEX
```

The PDB `COMPND` records assign chains `I` and `J` to the
dihydrolipoyllysine-residue acetyltransferase component of pyruvate
dehydrogenase complex, also named E2.

For chain `I`, the ATOM records contain only 43 residues:

```text
127-169
RRVIAMPSVRKYAREKGVDIRLVQGTGKNGRVLKEDIDAFLAG
```

The PDB has no insertion codes and no alternate locations for chain `I` ATOM
residues.

## Missing-Residue and Missing-Atom Findings

The current RCSB PDB records chain `I` residues `1-126` and `170-428` as missing
from the experiment. Therefore, chain `I` is a short resolved fragment rather
than a full-length chain.

The PDB also records missing atoms for some chain `I` residues:

```text
ARG 127: CG CD NE CZ NH1 NH2
ARG 128: CA C O CB CG CD NE CZ NH1 NH2
VAL 129: N
ARG 140: CG CD NE CZ NH1 NH2
LYS 154: CB CG CD CE NZ
ASN 155: CG OD1 ND2
LYS 160: CB CG CD CE NZ
```

Only one S_669 mutation position is affected by these missing-atom records:
`V129A` and `V129G` are at VAL 129, where the backbone `N` atom is missing.

## S_669 Mutation Position Check

All 31 S_669 `3dv0I` mutation positions are present in the current RCSB chain
`I` ATOM records. All 31 wild-type residue letters match the PDB residue
identities. None of the mutation positions has an insertion code or alternate
location.

Summary from the generated TSV:

```text
mutations=31
present=31
wt_match=31
mutation_rows_with_remark470_missing_atoms=2, both at position 129
```

## Interpretation

The current RCSB reference file does not show an obvious inherent residue-number
or chain-identifier problem for the S_669 `3dv0I` mutation list. It is not like
the direct insertion-code warning pattern seen for S_2648 `1lveA` and `2immA`.

The main structural concern is different: chain `I` is a very short observed
fragment of a much longer protein, with most residues missing from the
experiment. That could plausibly explain why the old dataset-input preparation
step skipped or failed to carry `3dv0I` into the S_669 PDB/PSSM input
directories, but this side-check does not prove that mechanism.

## Next Check

When reconstructing the upstream pipeline, create or recover the exact
`3dv0I.pdb` input that the 2022 scripts expected, then run the chain-extraction,
PSSM, and ProteinMPNN feature-extraction steps deliberately for these 31
mutations. The key question is whether the short chain-I fragment is sufficient
for the old feature-extraction code, or whether the input-preparation step had a
rule that excluded it.
