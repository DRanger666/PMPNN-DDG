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

The exact original cause for `3dv0I` is not yet proven in this workspace because
the old `ACCRE_PyRun_Setup/S_669_PDB_Files` directory and a local `3dv0I` PDB
copy have not been found in the copied evidence.

## Later Rerun Requirement

When the pipeline is reconstructed, rerun or reconstruct the ProteinMPNN feature
extraction for `3dv0I` and include these 31 mutation instances deliberately.

The rerun should determine whether the original exclusion was caused by missing
PDB input, residue/ICODE mapping, ProteinMPNN extraction failure, or another
upstream condition. The same class of check is needed for the excluded `S_2648`
instances.
