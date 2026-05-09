# V3 Reproduction Prerequisite Resolution

Date: 2026-05-09

This note records the concrete resolution of the prerequisite items that were
blocking the first V3 PMPNN pickle reproduction attempt.

## S_669 Mutation/DDG CSV

The S_669 generator notebooks load:

```text
/content/drive/MyDrive/ACCRE_PyRun_Setup/Data_s669_with_predictions.csv
```

The corresponding local FUSE path exists:

```text
/home/mpr/sajidahmedprotres_drive/ACCRE_PyRun_Setup/Data_s669_with_predictions.csv
```

It was copied with archive semantics to:

```text
drive_evidence_copy/sajidahmedprotres_drive/ACCRE_PyRun_Setup/Data_s669_with_predictions.csv
```

Copy check:

```text
source size: 318618 bytes
copy size:   318618 bytes
source mtime: 2022-03-11 06:01:18 +0600
copy mtime:   2022-03-11 06:01:18 +0600
sha256: def876c7515278aa05ba29b33edaad10417aa91cfdcab68d1bebfb09f2cd2eee
rows: 669 data rows
columns: 55
```

A small tracked snapshot also exists at:

```text
reproduction_inputs/mutation_ddg_tables/S_669/Data_s669_with_predictions.csv
```

## PremPS Dataset Tables

The PremPS repository was cloned locally:

```text
source_repos/SajidAhmeduiu_PremPS
remote: https://github.com/SajidAhmeduiu/PremPS.git
commit: e9269cc678c0d14b01440e33cc6d4b3778565c42
```

`source_repos/` is ignored by Git, so the full clone is a local source cache, not
a tracked deliverable.

Small tracked snapshots were created for the three notebook-referenced PremPS
tables:

```text
reproduction_inputs/mutation_ddg_tables/S_2648/S2648.txt
reproduction_inputs/mutation_ddg_tables/S_921/S921.txt
reproduction_inputs/mutation_ddg_tables/Ssym/Ssym.txt
```

The snapshot manifest is:

```text
reproduction_inputs/mutation_ddg_tables/MANIFEST.tsv
```

## Reproduction Environment

The old `.venv_pickle_analysis` environment remains untouched. The reproduction
environment is:

```text
.venv_proteinmpnn_ddg_reproduction
```

Verification:

```text
python: 3.12.3
torch: 2.11.0+cpu
torch_cuda_available: False
biopython: 1.87
openpyxl: 3.1.5
numpy: 2.4.4
pandas: 3.0.2
scipy: 1.17.1
scikit-learn: 1.8.0
```

Matplotlib emitted a writable-config warning under the Codex sandbox because
`/home/mpr/.config/matplotlib` was not writable. That does not block the
ProteinMPNN feature-extraction work. If a script imports Matplotlib, run it with
a writable `MPLCONFIGDIR` or set that variable inside the script entrypoint.

## Remaining Variables To Test

The original 2022 Colab runtime versions and RNG state are still unknown. This
is not a reason to stop. The reproduction work should treat runtime and RNG
state as empirical variables:

- run a small ProteinMPNN extraction subset more than once;
- compare raw fields by value;
- record whether values are invariant under the current CPU environment;
- only introduce seed control if variation is observed.

The exact historical cell that saved the final V3 object is also not available
as a complete executable save point. The workaround is to reconstruct the
pipeline until the regenerated object contains all target V3 fields, then save
from that explicit reconstructed state and compare values against the 2022
target pickle.

## Next Step

Write and run the mutation-table audit and value-level pickle comparison
scripts before trusting any regenerated pickle.
