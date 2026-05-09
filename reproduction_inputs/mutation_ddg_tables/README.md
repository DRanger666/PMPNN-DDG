# Mutation/DDG Table Snapshots

Date created: 2026-05-09

This directory contains small local snapshots of the mutation/DDG input tables
needed for the V3 PMPNN pickle reproduction work.

These snapshots are intentionally separate from the larger ignored source and
evidence trees:

- `source_repos/` contains full cloned repositories and is ignored.
- `drive_evidence_copy/sajidahmedprotres_drive/` contains copied Drive evidence
  and is ignored.
- this directory contains the small reproduction inputs that should remain easy
  to track and inspect.

## Sources

`S_2648/S2648.txt`, `S_921/S921.txt`, and `Ssym/Ssym.txt` come from:

```text
source_repos/SajidAhmeduiu_PremPS
remote: https://github.com/SajidAhmeduiu/PremPS.git
commit: e9269cc678c0d14b01440e33cc6d4b3778565c42
```

`S_669/Data_s669_with_predictions.csv` comes from the local read-only Drive
mount source:

```text
/home/mpr/sajidahmedprotres_drive/ACCRE_PyRun_Setup/Data_s669_with_predictions.csv
```

It was first copied into the local evidence tree with archive semantics:

```text
drive_evidence_copy/sajidahmedprotres_drive/ACCRE_PyRun_Setup/Data_s669_with_predictions.csv
```

The copied S_669 evidence file preserved the source file size and mtime:

```text
size: 318618 bytes
mtime: 2022-03-11 06:01:18 +0600
```

## Manifest

See `MANIFEST.tsv` for SHA256 hashes, line counts, source paths, and provenance
notes.
