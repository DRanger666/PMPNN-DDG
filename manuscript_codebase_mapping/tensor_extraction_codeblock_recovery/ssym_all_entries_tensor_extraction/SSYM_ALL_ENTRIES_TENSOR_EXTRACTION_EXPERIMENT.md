# Ssym All-Entry Tensor Extraction Experiment

Scope: all saved Ssym V3 mutation entries, direct ProteinMPNN-derived
tensor fields only. This experiment does not stitch engineered/PSSM
features and does not claim full V3 pickle reproduction.

## Result

- Target mutation entries: `342`
- Successful entries: `342`
- Schema failures: `0`
- Runtime errors: `0`
- All selected entries passed: `True`

## Runtime

- Utils source: `drive_evidence_copy/sajidahmedprotres_drive/Protein_MPNN_Digging/ProteinMPNN/vanilla_proteinmpnn/protein_mpnn_utils.py`
- Checkpoint: `drive_evidence_copy/sajidahmedprotres_drive/Protein_MPNN_Digging/ProteinMPNN/vanilla_proteinmpnn/vanilla_model_weights/v_48_020.pt`
- Device: `cpu`
- Number of ProteinMPNN edges: `48`
- Seed base: `0`

## Tables

- `tables/ssym_all_entries_mutation_status.tsv`
- `tables/ssym_all_entries_field_schema_compare.tsv`
- `json/ssym_all_entries_tensor_extraction_summary.json`

## Boundary

Passing this experiment means the recovered Set 1 scaffold traverses the
complete selected Ssym V3 direct tensor-field surface without shape or
finite-numeric failures. It does not yet validate engineered features.
