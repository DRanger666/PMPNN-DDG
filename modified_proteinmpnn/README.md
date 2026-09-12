# modified_proteinmpnn

Minimal ProteinMPNN utility fork for PMPNN-DDG feature extraction.

```text
PDB → modified_proteinmpnn (this package)
    → pmpnn_ddg extraction + features A–H
    → Random Forest
```

Point loaders at `modified_proteinmpnn/protein_mpnn_utils.py` (also exported as
`modified_proteinmpnn.UTILS_PATH`). See `MODIFICATIONS.md` for the exact
upstream diffs.
