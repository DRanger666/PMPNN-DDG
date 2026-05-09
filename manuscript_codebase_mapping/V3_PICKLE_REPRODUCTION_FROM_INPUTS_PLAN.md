# V3 Pickle Reproduction From Inputs Plan

Date: 2026-05-09

## Goal

Reconstruct the code path that can regenerate the manuscript-used V3 PMPNN
pickle dictionaries from raw-ish inputs:

```text
mutation/DDG table
+ dataset-specific PDB files
+ dataset-specific PSSM files
+ ProteinMPNN model code and weights
-> regenerated V3 PMPNN pickle
-> value-level comparison against the 2022 V3 pickle
```

The first target is not a cleaned final pipeline. The first target is a
faithful stitched pipeline that reproduces the existing 2022 pickle values as
closely and explicitly as possible.

## Target Pickles

Primary targets:

```text
drive_evidence_copy/sajidahmedprotres_drive/Protein_MPNN_Digging/S_2648_pmppn_info_dict_V3.pickle
drive_evidence_copy/sajidahmedprotres_drive/Protein_MPNN_Digging/S_921_pmppn_info_dict_V3.pickle
drive_evidence_copy/sajidahmedprotres_drive/Protein_MPNN_Digging/S_669_pmppn_info_dict_V3.pickle
drive_evidence_copy/sajidahmedprotres_drive/Protein_MPNN_Digging/Ssym_pmppn_info_dict_V3.pickle
```

These are the first reproduction targets because the downstream RF notebooks
load the V3 family for manuscript-level evaluation.

## Current Local Inputs

The old copied ACCRE input directories are present locally:

```text
drive_evidence_copy/sajidahmedprotres_drive/ACCRE_PyRun_Setup/S_2648_PDB_Files  131 files
drive_evidence_copy/sajidahmedprotres_drive/ACCRE_PyRun_Setup/S_2648_pssm_dir    131 files
drive_evidence_copy/sajidahmedprotres_drive/ACCRE_PyRun_Setup/S_921_PDB_Files   195 files
drive_evidence_copy/sajidahmedprotres_drive/ACCRE_PyRun_Setup/S_921_pssm_dir     195 files
drive_evidence_copy/sajidahmedprotres_drive/ACCRE_PyRun_Setup/S_669_PDB_Files    93 files
drive_evidence_copy/sajidahmedprotres_drive/ACCRE_PyRun_Setup/S_669_pssm_dir     93 files
drive_evidence_copy/sajidahmedprotres_drive/ACCRE_PyRun_Setup/Ssym_PDB_Files    357 files
drive_evidence_copy/sajidahmedprotres_drive/ACCRE_PyRun_Setup/Ssym_pssm_dir      357 files
```

The ProteinMPNN code and model weights are present in the cloned old fork:

```text
source_repos/SajidAhmeduiu_ProteinMPNN/vanilla_proteinmpnn/
source_repos/SajidAhmeduiu_ProteinMPNN/vanilla_proteinmpnn/vanilla_model_weights/v_48_020.pt
```

The strongest generator-code family is:

```text
colab_notebooks_inventory_analysis/git_notebook_sources/ProteinMPNNTesting_V6_V2.ipynb.py.txt
colab_notebooks_inventory_analysis/git_notebook_sources/S921_ProteinMPNNTesting_V6_V2.ipynb.py.txt
colab_notebooks_inventory_analysis/git_notebook_sources/S669_ProteinMPNNTesting_V6_V2.ipynb.py.txt
colab_notebooks_inventory_analysis/git_notebook_sources/Ssym_ProteinMPNNTesting_V6_V2.ipynb.py.txt
```

## Mutation/DDG Table Sources

The generator notebooks point to these mutation/DDG sources:

```text
S_2648: https://raw.githubusercontent.com/SajidAhmeduiu/PremPS/main/Datasets/S2648/S2648.txt
S_921:  https://raw.githubusercontent.com/SajidAhmeduiu/PremPS/main/Datasets/S921/S921.txt
Ssym:   https://raw.githubusercontent.com/SajidAhmeduiu/PremPS/main/Datasets/Eight%20test%20sets/Ssym.txt
S_669:  /content/drive/MyDrive/ACCRE_PyRun_Setup/Data_s669_with_predictions.csv
```

The mutation/DDG input tables now have local snapshots:

```text
reproduction_inputs/mutation_ddg_tables/S_2648/S2648.txt
reproduction_inputs/mutation_ddg_tables/S_921/S921.txt
reproduction_inputs/mutation_ddg_tables/Ssym/Ssym.txt
reproduction_inputs/mutation_ddg_tables/S_669/Data_s669_with_predictions.csv
```

The three PremPS files were snapshotted from:

```text
source_repos/SajidAhmeduiu_PremPS
remote: https://github.com/SajidAhmeduiu/PremPS.git
commit: e9269cc678c0d14b01440e33cc6d4b3778565c42
```

The S_669 CSV was recovered from the local FUSE mount and copied into the local
evidence tree with size and mtime preserved:

```text
source: /home/mpr/sajidahmedprotres_drive/ACCRE_PyRun_Setup/Data_s669_with_predictions.csv
copy:   drive_evidence_copy/sajidahmedprotres_drive/ACCRE_PyRun_Setup/Data_s669_with_predictions.csv
size:   318618 bytes
mtime:  2022-03-11 06:01:18 +0600
sha256: def876c7515278aa05ba29b33edaad10417aa91cfdcab68d1bebfb09f2cd2eee
```

For temporary code stitching, the `mut` and `ddg` entries already inside the
target pickles can be used as a scaffold. That is useful for debugging the
pipeline, but it is not independent raw-input provenance evidence. The first
independent mutation/DDG table prerequisite is now satisfied by the local
snapshots above.

## What Must Match

Do not use byte-identical pickle files as the primary criterion. Pickle byte
streams can differ while representing the same values.

Use value-level comparison:

- top-level protein keys match
- mutation-list order per protein matches
- scalar fields match exactly where possible
- NumPy arrays match by dtype, shape, and element values
- missing-instance entries match intentionally, not accidentally
- report any floating-point differences with max absolute difference and field
  location

The comparison script should produce:

```text
protein_key
mutation_index
mutation_label
field
status
target_summary
regenerated_summary
```

## Pipeline Stages

### 1. Freeze Target Manifests

Create immutable manifests for the target V3 pickles, PDB inputs, PSSM inputs,
generator notebook source files, and model weights.

Record:

- path
- size
- mtime
- SHA256
- dataset assignment

This prevents later confusion about which evidence version was used.

### 2. Reproduce Initial Mutation Dictionaries

Build the initial `two_level_dict` from mutation/DDG tables only.

Expected fields at this stage:

```text
mut
ddg
```

Checks:

- protein-key set against target V3 pickle
- entry count per protein
- mutation labels and order
- DDG values

Resolved prerequisite:

- `Data_s669_with_predictions.csv` is now available locally from the copied
  Drive evidence and from the tracked reproduction-input snapshot.

### 3. Reproduce PDB Mapping and Skip Behavior

Recreate:

```text
mapping_dict
proteins_to_skip
```

from the copied PDB input directories, using the same residue iteration logic
as the notebooks.

Checks:

- sequence index assigned to each `wild+position` key
- proteins skipped for duplicate residue keys or insertion-code behavior
- proteins absent from PDB/PSSM directories
- mutation entries retained as label-only records because their PDB/PSSM inputs
  were not processed

Known instance-level absence cases:

- S_2648: `1lveA`, `2a01A`, `2immA` entries lack ProteinMPNN-derived feature
  records in the target V3 pickle.
- S_669: `3dv0I` entries lack ProteinMPNN-derived feature records in the target
  V3 pickle.

For the first stitching phase, reproduce the old target behavior. Do not force
these missing instances into the regenerated pickle yet.

### 4. Reproduce the ProteinMPNN-DDG V3 Tensor-Extraction Segment

Overall target: reproduce the ProteinMPNN-DDG V3 pickle objects. The
ProteinMPNN-derived tensor extraction is only one upstream segment of that V3
pickle pipeline; it is not a standalone goal.

Primary ProteinMPNN-derived tensor fields:

```text
log_prob
top_15_attention_weights
top_10_attention_weights
top_5_attention_weights
top_15_neighbor_indices
top_10_neighbor_indices
top_5_neighbor_indices
top_15_closest_neighbor_indices
top_10_closest_neighbor_indices
w_n_log_prob
m_n_log_prob
neighbor_aa_identities
neighbor_w_message_vector_coming_from_center
neighbor_m_message_vector_coming_from_center
neighbor_w_neighbor_embedding
neighbor_m_neighbor_embedding
```

Start order:

1. Ssym, because it has complete V3 per-entry feature records and saved
   execution-trace coverage.
2. S_921, because it has complete V3 per-entry feature records but lacks saved
   execution-trace coverage.
3. S_2648 and S_669, because they include known instance-level absence cases.

Important determinism issue:

The notebooks call `torch.randn(...)` before ProteinMPNN forward passes. The
model is in `eval()` mode and `backbone_noise=0.00`, but the random tensor is
used in ProteinMPNN decoding-order logic. We must empirically test whether the
outputs are invariant to that random tensor under the single-designable-position
setup used here.

If outputs are not invariant, exact value-level reproduction may require the
original RNG state and original file-processing order. That information is not
currently known.

### 5. Reproduce Engineered/PSSM Fields Added After Tensor Extraction

The target V3 pickles contain more than the direct ProteinMPNN-derived tensor
fields. They also contain scalar engineered fields and PSSM fields, including:

```text
center_mut_wild_energy
center_mut_max_energy
center_entropy
weighted_neighbor_entropies
weighted_neighbor_energy_changes
weighted_neighbor_forward_KL
weighted_neighbor_backward_KL
backward_weighted_neighbor_energy_changes
backward_weighted_neighbor_backward_KL
backward_weighted_neighbor_entropy_changes
V2_backward_weighted_neighbor_energy_changes
V2_backward_weighted_neighbor_backward_KL
V2_backward_weighted_neighbor_entropy_changes
center_neighbor_weight_check_m_w
center_neighbor_weight_check_w_m
neighbor_embedding_change_m_w
neighbor_embedding_change_m_w_raw
neighbor_message_change_m_w
neighbor_message_change_m_w_raw
unweighted_backward_KL
unweighted_forward_KL
wild_pssm
alternate_pssm
```

This means the ProteinMPNN-DDG V3 pickle reproduction pipeline cannot stop at
the commented `with open(..., "wb")` save cell near the tensor-extraction
block. The regenerated object must run the later feature-construction cells
before the V3 value-level comparison.

Open evidence issue:

- The extracted notebook source shows the V3 save line near the
  ProteinMPNN-derived tensor-extraction block, but the target V3 pickles contain
  later engineered and PSSM fields. Therefore, the exact historical save timing
  is not fully represented by the visible commented save cell. The practical
  reproduction pipeline should save after all fields present in the target V3
  pickle have been reconstructed.

### 6. Compare Incrementally

Do not wait for a full four-dataset run before checking.

Compare in this order:

1. one protein, one mutation, ProteinMPNN-derived tensor fields
2. one protein, all mutations, ProteinMPNN-derived tensor fields
3. one dataset, ProteinMPNN-derived tensor fields
4. one dataset, engineered fields
5. one dataset, full V3 pickle
6. all four datasets

Each comparison should write machine-readable tables and a short markdown
summary.

### 7. Only After Matching the Old Pickles, Rerun Missing Instances

The first goal is to reproduce the existing 2022 target pickles, including
their instance-level absence behavior.

Only after that should we create a separate rerun branch/artifact that attempts
to include:

- S_669 `3dv0I`
- S_2648 `1lveA`
- S_2648 `2a01A`
- S_2648 `2immA`

Those reruns are new analysis, not evidence of what the 2022 manuscript numbers
used.

## Required Code Work

The required code is mostly present, but not in a clean runnable form.

Needed scripts:

```text
scripts/build_initial_mutation_dicts.py
scripts/reproduce_v3_pmpnn_pickle.py
scripts/compare_regenerated_v3_pickle.py
scripts/audit_pdb_pssm_input_coverage.py
```

The first implementation should reuse the notebook logic directly and change as
little as possible. Cleanup can come after matching.

## Resolved Inputs And Remaining Requirements

Resolved on 2026-05-09:

- local independent copy of `Data_s669_with_predictions.csv`
- local commit-pinned snapshots of the PremPS dataset text files used for
  S_2648, S_921, and Ssym
- runnable CPU reproduction environment named
  `.venv_proteinmpnn_ddg_reproduction`, with PyTorch, Biopython, pandas, NumPy,
  SciPy, scikit-learn, openpyxl, tqdm, and Matplotlib installed

Still unresolved, but not blockers:

- exact original Python/PyTorch/Biopython runtime versions from the 2022 Colab
  run
- exact original RNG state, if ProteinMPNN outputs are not invariant to the
  `torch.randn(...)` decoding-order tensor
- exact historical save timing for the final V3 object after later engineered
  fields and PSSM fields were added

Working rule for the unresolved items:

- test runtime and RNG effects empirically on small controlled subsets;
- reconstruct a clear final save point after all target V3 fields are present;
- compare regenerated objects to the 2022 target pickles by value, not by
  pickle bytes.

Available:

- old PDB/PSSM input directory pairs for all four datasets, with known
  instance-level absence cases
- old ProteinMPNN fork code and `v_48_020.pt` model weight
- notebook-derived generator code for all four datasets
- target V3 pickles for all four datasets
- existing fingerprint and instance-coverage reports

## First Concrete Execution Plan

1. Write the comparison script first. It will define the value-level truth
   criterion before any regeneration code is trusted.
2. Write a mutation-table audit script. It should load the local mutation/DDG
   table snapshots and report whether the initial dictionary matches the target.
3. Reproduce Ssym initial dictionary, PDB mapping, ProteinMPNN-derived tensor
   fields, and final engineered/PSSM fields.
4. If Ssym matches, repeat for S_921.
5. Then handle S_2648 and S_669 with explicit expected absence reports.
6. Only then start the separate rerun effort for the missing instances.
