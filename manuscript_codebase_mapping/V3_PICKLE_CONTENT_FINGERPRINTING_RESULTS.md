# V3 Pickle Content-Fingerprinting Results

Date: 2026-05-09

Script:

```text
scripts/fingerprint_v3_pickles.py
```

Primary outputs:

```text
pickle_analysis/v3_fingerprinting/tables/
pickle_analysis/v3_fingerprinting/json/v3_pickle_fingerprints.json
```

## Scope

This pass used only the workspace-local copied evidence under:

```text
drive_evidence_copy/sajidahmedprotres_drive/Protein_MPNN_Digging/
```

It did not read the live FUSE mount and did not execute notebooks.

The pass fingerprinted base, V2, and V3 PMPNN pickle dictionaries for:

- `S_2648`
- `S_921`
- `S_669`
- `Ssym`

## Short Result

All twelve target pickles loaded with the restricted audit unpickler. All V3
pickles contain the expected ProteinMPNN-derived generator fields in their field
union, and the candidate `*_ProteinMPNNTesting_V6_V2` notebook family assigns
all seven expected fields:

- `w_n_log_prob`
- `m_n_log_prob`
- `neighbor_aa_identities`
- `neighbor_w_message_vector_coming_from_center`
- `neighbor_m_message_vector_coming_from_center`
- `neighbor_w_neighbor_embedding`
- `neighbor_m_neighbor_embedding`

The downstream RF notebook family has un-commented `rb` loads of the V3 pickle
family. The candidate generator save references exist, but the V3
`with open(..., "wb")` save statements are commented in the `.ipynb.py.txt`
code-cell text files inspected here.

That does not imply that these notebooks did not generate the V3 pickle files.
It is compatible with saving the pickle files once and commenting the save
statements later to avoid accidental overwrites.

## Evidence Status

| Dataset | Status | Main reason |
| --- | --- | --- |
| `Ssym` | `proven` | V3 expected fields cover all 342 entries, saved execution trace covers all 15 proteins and all 342 mutation entries, and downstream V3 RF loads exist. |
| `S_921` | `strong_candidate` | V3 expected fields cover all 921 entries and downstream V3 RF loads exist, but no saved execution trace matched the `Took ... forward-mutations` pattern. |
| `S_2648` | `strong_candidate` | V3 expected fields exist, but 28 mutation entries lack the ProteinMPNN-derived feature-record fields. The best saved execution trace also covers 129/132 proteins and 2620/2648 mutation entries. |
| `S_669` | `strong_candidate` | V3 expected fields exist, but 31 `3dv0I` mutation entries lack the ProteinMPNN-derived feature-record fields, and no saved execution trace matched the `Took ... forward-mutations` pattern. |

The authoritative status table is:

```text
pickle_analysis/v3_fingerprinting/tables/v3_dataset_evidence_status.tsv
```

## Instance-Level Missing ProteinMPNN Feature Records

The V3 field-union match is not the same thing as per-mutation-instance
completeness. The issue below is not a partly populated field schema. These are
mutation entries that retain dataset labels but do not have the
ProteinMPNN-derived feature record needed by the RF feature assembly.

For `S_2648`, 28 mutation entries lack the expected ProteinMPNN-derived feature
record fields across three proteins:

- `1lveA`: 17 entries
- `2a01A`: 1 entry
- `2immA`: 10 entries

For `S_669`, 31 mutation entries lack the expected ProteinMPNN-derived feature
record fields, all under:

- `3dv0I`: 31 entries

The entry-level evidence table is:

```text
pickle_analysis/v3_fingerprinting/tables/v3_missing_expected_fields_by_entry.tsv
```

This matters for the manuscript-to-code map. The RF feature assembly requires
these fields. If one of these mutation entries reached the mutation-level
feature-extraction loop, the notebook would fail rather than evaluate that
entry. Therefore the operational question is where those mutation entries were
excluded, most likely at protein-level mapping/skip logic before the
mutation-level loop.

For the targeted `S_669` check, see:

```text
pickle_analysis/s669_instance_coverage/tables/
```

That check confirms that the 31 `3dv0I` entries contain only `ddg` and `mut` in
both `S_669_pmppn_info_dict_V3.pickle` and the matching
`S_669_full_feature_dict.pickle` entries. No PSSM fields remain for these
entries in those inspected dictionaries.

## Version-Lineage Finding

The base pickle family already contains log-probability, neighbor-identity, and
center-to-neighbor message-vector fields, but it lacks the neighbor embedding
fields.

The V2 family adds the larger engineered-feature set, including neighbor
embeddings and scalar engineered features. The V3 family adds exactly one field
relative to V2 across all four datasets:

```text
neighbor_message_change_m_w_raw
```

That V3-only raw field has shape `[15, 128, 1]` where present. The related
scalar field is:

```text
neighbor_message_change_m_w
```

This supports treating message-change and neighbor-embedding-change as distinct
engineered feature families, but the final RF feature-column mapping still needs
to be traced before the manuscript feature labels are rewritten.

## Next Mapping Step

The next reliable step is downstream, not further pickle discovery:

```text
V3 PMPNN pickle dictionary
-> RF feature-matrix assembly
-> exact RF evaluation rows and feature-column blocks
```

For `S_2648` and `S_669`, specifically trace the protein-level skip/mapping
logic that excluded the entries listed in
`v3_missing_expected_fields_by_entry.tsv`. For `S_921`, look for an alternate
saved output or notebook copy that contains the missing ProteinMPNN execution
trace; the currently inspected V3 pickle itself has complete per-entry
ProteinMPNN-derived feature records. For `Ssym`, the Stage 5
generator-to-pickle edge is currently proven under the written rule.

Later reproducibility work should reconstruct or rerun the ProteinMPNN feature
extraction for the excluded `S_669` `3dv0I` instances and the excluded `S_2648`
instances. The goal is to identify whether the original issue was missing PDB
input, residue/ICODE mapping, ProteinMPNN extraction failure, or another
upstream condition. Current manuscript numbers should not be described as
covering those excluded mutation instances unless that is separately proven.
