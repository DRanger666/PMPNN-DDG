# V3 Pickle Content-Fingerprinting Plan

This note records the next planned Stage 5 move: test whether the V3 PMPNN
pickle dictionaries match the candidate generator notebooks at content level.

## Goal

Establish the evidence edge:

```text
ProteinMPNN feature-extraction notebook/code
-> V3 PMPNN pickle dictionary
-> RF feature matrix assembly
-> manuscript table/figure output
```

The immediate target is the first edge. Filename matches and nearby save cells
are not enough, because the candidate save cells appear commented in the
extracted notebook state.

## Target Pickles

Use only the local copied evidence files under:

```text
drive_evidence_copy/sajidahmedprotres_drive/Protein_MPNN_Digging/
```

Initial V3 targets:

- `S_2648_pmppn_info_dict_V3.pickle`
- `S_921_pmppn_info_dict_V3.pickle`
- `S_669_pmppn_info_dict_V3.pickle`
- `Ssym_pmppn_info_dict_V3.pickle`

V2 and base versions should be analyzed as controls for lineage comparison.

## Candidate Generator Notebooks

Current strongest candidate generator family:

- `ProteinMPNNTesting_V6_V2.ipynb.py.txt` for `S_2648`
- `S921_ProteinMPNNTesting_V6_V2.ipynb.py.txt` for `S_921`
- `S669_ProteinMPNNTesting_V6_V2.ipynb.py.txt` for `S_669`
- `Ssym_ProteinMPNNTesting_V6_V2.ipynb.py.txt` for `Ssym`

These extracts should be treated as candidate generation code until content
matching and execution traces strengthen the edge.

## Planned Evidence Passes

1. Freeze file identity for each target pickle:
   size, preserved mtime, SHA256, object type, and top-level counts.
2. Build structural fingerprints:
   top-level keys, protein/mutation counts, nested field names, array/list
   shapes, dtypes, and compact numeric summaries.
3. Extract the expected schema from generator notebooks:
   fields assigned into `two_level_dict` and `mut`, including ProteinMPNN
   log-probability, neighbor-identity, decoder-message, and embedding fields.
4. Compare V2 and V3:
   identify which fields or shapes were added or changed in V3 and whether
   those additions correspond to the V6_V2 generator code.
5. Search saved notebook outputs for execution traces:
   especially `Took ... for ... with ... forward-mutations` messages, then
   compare those counts against pickle mutation counts.
6. Verify downstream consumption:
   confirm that the RF notebooks that support manuscript evidence load the same
   V3 filenames and consume fields actually present in those V3 pickles.
7. Assign evidence status per dataset:
   `proven`, `strong candidate`, or `unresolved`.

## Evidence Status Rules

- `proven`: saved execution trace, schema match, count match, and downstream
  RF-load evidence all align.
- `strong candidate`: filename, schema, count, and timeline evidence align, but
  one of execution trace or direct saved-state evidence is missing.
- `unresolved`: field/schema/count mismatch, ambiguous notebook version, or
  incompatible downstream load evidence.

## Expected Deliverables

- A clean script under `scripts/` for V3 pickle fingerprinting.
- TSV/JSON outputs under `pickle_analysis/`.
- A concise mapping note under `manuscript_codebase_mapping/` summarizing the
  evidence status for each dataset.

