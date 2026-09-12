# PDB → ProteinMPNN → Features Pipeline Report

Clean reproduction path: local PDBs + mutation table + checkpoint +
recovered V6_V2 tensor extraction → engineered/PSSM features.

## Run

- Dataset: `Ssym`
- Jobs requested: `16`
- OK: `16`
- Errors: `0`
- Seed mode: `continuous` (seed=0)
- Device: `cpu`
- Elapsed seconds: `25.2`

## Artifacts

- `regenerated_v3_features.pickle`
- `tables/mutation_status.tsv`
- `json/pipeline_summary.json`

## Open fidelity questions (not assumed bugs)

- Decoder RNG / order among fixed residues (Item A)
- Feature B weighted vs manuscript unweighted wording (Item B)
- Zero-vector fallback for non-reciprocal edges (Item C)

See `manuscript_codebase_mapping/MANUSCRIPT_TENSOR_EXTRACTION_FIDELITY.md`.

## Optional historical pickle compare (diagnostic)

- Compared entries: `16`
- top_15_neighbor exact: `0`
- log_prob allclose: `0`
- scalar allclose: `{"center_mut_wild_energy": 0, "center_entropy": 0, "V2_backward_weighted_neighbor_entropy_changes": 0, "center_neighbor_weight_check_w_m": 0, "neighbor_embedding_change_m_w": 0, "wild_pssm": 16, "alternate_pssm": 16}`
