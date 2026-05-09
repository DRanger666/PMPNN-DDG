# Ssym Engineered/PSSM Feature Reconstruction

Scope: recompute the saved Ssym V3 engineered and PSSM fields from
the saved direct tensor fields plus the copied local Ssym PSSM files.
This is the feature-construction segment only; it does not rerun
ProteinMPNN tensor extraction and does not write a replacement pickle.

## Result

- Target mutation entries: `342`
- Successful entries: `342`
- Mismatch entries: `0`
- Runtime errors: `0`
- Field comparisons: `8208`
- Exact field matches: `6621`
- Allclose field matches at `atol=1e-6, rtol=1e-6`: `8208`
- All selected entries passed: `True`
- Maximum absolute difference: `5.32375236162e-06`

## Inputs

- Target pickle: `drive_evidence_copy/sajidahmedprotres_drive/Protein_MPNN_Digging/Ssym_pmppn_info_dict_V3.pickle`
- PDB directory used for residue-index mapping: `drive_evidence_copy/sajidahmedprotres_drive/ACCRE_PyRun_Setup/Ssym_PDB_Files`
- PSSM directory: `drive_evidence_copy/sajidahmedprotres_drive/ACCRE_PyRun_Setup/Ssym_pssm_dir`

## Important Recovery Detail

The old notebook stores message-norm ratio weights as one-element arrays.
For several weighted neighbor scalar features, NumPy therefore broadcasts
a `(15,)` value vector against a `(15, 1)` weight vector. The recovery
module preserves that behavior because flattening the weights changes the
saved V3 values.

## Tables

- `tables/ssym_engineered_pssm_mutation_status.tsv`
- `tables/ssym_engineered_pssm_field_compare.tsv`
- `json/ssym_engineered_pssm_feature_reconstruction_summary.json`
