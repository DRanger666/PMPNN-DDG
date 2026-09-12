# PDB → ProteinMPNN → Features Pipeline Report

- Dataset: `Ssym`
- Jobs: `342` OK=`342` errors=`0`
- Seed mode: `per_entry` seed=`0`
- Utils: `modified_proteinmpnn/protein_mpnn_utils.py`
- Elapsed s: `499.9`

Open fidelity questions (not assumed bugs): decoder RNG, Feature B weighting,
zero-vector fallback — see MANUSCRIPT_TENSOR_EXTRACTION_FIDELITY.md.

## Optional historical pickle compare
- compared=342 top15_exact=0 log_prob_close=0
- scalars={"center_mut_wild_energy": 0, "center_entropy": 1, "V2_backward_weighted_neighbor_entropy_changes": 0, "center_neighbor_weight_check_w_m": 0, "neighbor_embedding_change_m_w": 0, "wild_pssm": 342, "alternate_pssm": 342}
