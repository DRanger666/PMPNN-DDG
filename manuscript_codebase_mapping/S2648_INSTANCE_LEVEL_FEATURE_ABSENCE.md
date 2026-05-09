# S_2648 Instance-Level ProteinMPNN Feature Absence

Date: 2026-05-09

## Correct Framing

For `S_2648`, the issue is instance-level absence of ProteinMPNN-derived feature
records for 28 mutation entries. It is not a partially populated feature schema.

Affected proteins:

- `1lveA`: 17 mutation entries
- `2a01A`: 1 mutation entry
- `2immA`: 10 mutation entries

Each affected mutation entry exists as a mutation/DDG record, but it does not
contain the ProteinMPNN-derived fields needed by the RF feature assembly.

## Direct Pickle Finding

Script:

```text
scripts/inspect_s2648_instance_coverage.py
```

Tables:

```text
pickle_analysis/s2648_instance_coverage/tables/
```

The affected entries in `S_2648_pmppn_info_dict_V3.pickle` contain only:

- `ddg`
- `mut`

The matching affected entries in `S_2648_full_feature_dict.pickle` also contain
only:

- `ddg`
- `mut`

Therefore, PSSM features do not remain for these entries in the inspected V3 or
full-feature dictionaries.

## Saved Trace Finding

The saved `ProteinMPNNTesting_V6_V2.ipynb` output contains:

- `v3_protein_count`: 132
- `saved_trace_processed_protein_count`: 129
- `saved_trace_forward_mutation_sum`: 2620
- `saved_trace_pdb_directory_tqdm_total`: 131
- `saved_icode_warning_proteins`: `1lveA`, `2immA`

This separates the 28 affected entries into two evidence classes.

### ICODE Skip Evidence

`1lveA` and `2immA` have direct saved ICODE warning evidence:

- `1lveA:S27`
- `2immA:N31`

The old notebook source builds `proteins_to_skip` when duplicate residue-position
keys occur in the PDB-derived residue map, and the saved output shows those two
proteins triggering that path. Their feature absence is therefore currently
explained by the deliberate ICODE-related protein-level skip.

### 2a01A Is Different

`2a01A` has one affected mutation:

- `L141R`

It is absent from the saved execution trace and has no saved ICODE warning in the
inspected output. The trace reports 131 PDB-directory entries, while the V3
pickle has 132 proteins. The 129 processed proteins plus the two ICODE-skipped
proteins account for those 131 traced PDB-directory entries.

The best current explanation is that `2a01A` was present in the mutation/DDG
dictionary but was not present in the PDB directory used by that saved
ProteinMPNN feature-extraction run. This is not yet proven because the original
`ACCRE_PyRun_Setup/S_2648_PDB_Files` directory has not been recovered in the
workspace-local copied evidence.

## RF Implication

The downstream RF feature assembly requires ProteinMPNN-derived fields and PSSM
fields. These 28 mutation entries could not have been evaluated from this V3
pickle by the inspected RF feature-assembly code.

If these entries reached the mutation-level feature extraction loop, the code
would fail when it accessed missing fields. The evidence instead points to
protein-level exclusion before mutation-level feature extraction:

- `1lveA` and `2immA`: explicit ICODE skip path
- `2a01A`: likely absent from the PDB directory used by the saved run, pending
  direct directory evidence

## Later Rerun Requirement

When the pipeline is reconstructed, rerun or reconstruct ProteinMPNN feature
extraction for:

- all 17 `1lveA` mutation entries
- the one `2a01A` mutation entry
- all 10 `2immA` mutation entries

The rerun should determine whether `1lveA:S27` and `2immA:N31` can be handled
with explicit insertion-code-aware residue mapping, and whether `2a01A` only
needs the missing PDB input restored or has a separate structural/mapping issue.
