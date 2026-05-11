# ProteinMPNN Checkpoint Inputs

This directory contains curated, tracked checkpoint inputs needed by current
ProteinMPNN-DDG recovery code.

## `vanilla_model_weights/v_48_020.pt`

- Source evidence path:
  `drive_evidence_copy/sajidahmedprotres_drive/Protein_MPNN_Digging/ProteinMPNN/vanilla_proteinmpnn/vanilla_model_weights/v_48_020.pt`
- Copy method: `rsync -a`, preserving file mtime.
- Size: `6681301` bytes.
- Historical mtime: `2022-07-28 23:05:32.400000000 +0600`.
- SHA256:
  `c9cb4a671d79604111231f8dbfc7c590e06f1197453b7a6854ac6661a642f5bd`.
- Storage: Git LFS.

The original file lives inside a nested historical ProteinMPNN Git checkout.
This curated copy exists so the parent workspace repo can track the required
checkpoint without tracking the nested `.git` directory or treating the nested
checkout as normal parent-repo source.
