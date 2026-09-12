# PDB → ProteinMPNN → Features Pipeline Report

- Dataset: `S_669`
- Jobs: `669` OK=`638` errors=`31`
- Seed mode: `per_entry` seed=`0`
- Utils: `modified_proteinmpnn/protein_mpnn_utils.py`
- Elapsed s: `2.0`

Open fidelity questions (not assumed bugs): decoder RNG, Feature B weighting,
zero-vector fallback — see MANUSCRIPT_TENSOR_EXTRACTION_FIDELITY.md.

## Optional historical pickle compare
- compared=638 top15_exact=0 log_prob_close=0
- scalars={"center_mut_wild_energy": 0, "center_entropy": 0, "V2_backward_weighted_neighbor_entropy_changes": 0, "center_neighbor_weight_check_w_m": 0, "neighbor_embedding_change_m_w": 0, "wild_pssm": 638, "alternate_pssm": 638}
