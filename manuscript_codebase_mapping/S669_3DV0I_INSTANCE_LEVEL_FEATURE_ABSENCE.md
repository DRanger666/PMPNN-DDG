# S_669 3dv0I Instance-Level ProteinMPNN Feature Absence

Date: 2026-05-09

## Correct Terminology

This is not a "field gap" in the sense of a partially populated feature schema.

For `S_669`, the issue is instance-level absence of ProteinMPNN-derived feature
records for one protein:

- `3dv0I`: 31 mutation entries

Each affected mutation entry exists as a mutation/DDG record, but it does not
contain the ProteinMPNN-derived fields needed by the RF feature assembly.

## Direct Pickle Finding

Script:

```text
scripts/inspect_s669_instance_coverage.py
```

Tables:

```text
pickle_analysis/s669_instance_coverage/tables/
```

The `3dv0I` entries in `S_669_pmppn_info_dict_V3.pickle` contain only:

- `ddg`
- `mut`

The matching `3dv0I` entries in `S_669_full_feature_dict.pickle` also contain
only:

- `ddg`
- `mut`

Therefore, PSSM features do not remain for these entries in the inspected V3 or
full-feature dictionaries.

## ACCRE Input Directory Finding

After copying the dataset-specific ACCRE input directories from the Drive mount,
the local evidence copy contains:

```text
drive_evidence_copy/sajidahmedprotres_drive/ACCRE_PyRun_Setup/S_669_PDB_Files
drive_evidence_copy/sajidahmedprotres_drive/ACCRE_PyRun_Setup/S_669_pssm_dir
```

Both directories contain 93 files. The V3 pickle has 94 protein keys.

The only V3 protein key absent from both copied S_669 input directories is:

- `3dv0I`

This means the current evidence for `3dv0I` is stronger than before: the
mutation/DDG records exist in the V3 and full-feature dictionaries, but the
corresponding PDB and PSSM input files are absent from the copied old S_669
input directories.

## RF Implication

The downstream RF feature assembly requires ProteinMPNN-derived fields and PSSM
fields. The `3dv0I` mutation entries could not have been evaluated from this V3
pickle by the inspected RF feature-assembly code.

If these entries reached the mutation-level feature extraction loop, the code
would fail when it accessed missing fields. The plausible exclusion point is
before that loop, at protein-level mapping/skip logic.

The inspected RF notebook code has two relevant protein-level exclusion routes:

- skip proteins already listed in `proteins_to_skip`
- skip proteins that are absent from `mapping_dict`

For `3dv0I`, the current best-supported cause is absence from the old S_669
PDB/PSSM input directory. This is distinct from the direct ICODE-warning pattern
seen for S_2648 `1lveA` and `2immA`. The saved S_669 notebook output shows a
`0/93` PDB-directory progress total, but no saved ICODE warning for `3dv0I` and
no per-protein `Took ... forward-mutations` trace.

## Later Rerun Requirement

When the pipeline is reconstructed, rerun or reconstruct the ProteinMPNN feature
extraction for `3dv0I` and include these 31 mutation instances deliberately.

The rerun should determine whether adding the missing `3dv0I` PDB/PSSM inputs
is sufficient, or whether residue mapping, chain handling, ProteinMPNN parsing,
or another upstream issue also appears once those inputs are restored. The same
class of check is needed for the excluded `S_2648` instances.
