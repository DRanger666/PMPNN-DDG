# Ssym Tensor Extraction Smoke Test

Scope: one-entry smoke test for the recovered V6_V2 ProteinMPNN tensor
extraction module. This does not stitch engineered/PSSM features and does
not claim full V3 pickle reproduction.

## Target

- Protein key: `1amqA`
- Mutation: `C191Y`
- Zero-based sequence index from PDB residue map: `179`

## Result

- All V3 tensor-field shapes match target entry: `True`
- All generated numeric tensors are finite: `True`
- Numeric values are recorded as diagnostics only. Exact equality is not
  expected at this stage because the historical RNG state and runtime stack
  are not recovered.

## Runtime

- Utils source: `drive_evidence_copy/sajidahmedprotres_drive/Protein_MPNN_Digging/ProteinMPNN/vanilla_proteinmpnn/protein_mpnn_utils.py`
- Checkpoint: `drive_evidence_copy/sajidahmedprotres_drive/Protein_MPNN_Digging/ProteinMPNN/vanilla_proteinmpnn/vanilla_model_weights/v_48_020.pt`
- Device: `cpu`
- Number of ProteinMPNN edges: `48`

## Tables

- `tables/ssym_tensor_field_schema_compare.tsv`
- `json/ssym_tensor_extraction_smoke_summary.json`
