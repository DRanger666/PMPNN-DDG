# Reproduction Status (`reproduce-paper-results`)

Date: 2026-09-12  
Machine run directory: `reproduction_runs/2026-09-12/`  
Runtime: `.venv_proteinmpnn_ddg_reproduction/` (Python 3.12, CPU torch 2.6.0+cpu)

## Strategy pivot (active)

**Stop** treating bit-exact historical V3 pickle regeneration as the success
criterion.

**Path forward**

1. Use best-available features aligned with the BioRxiv method (saved V3
   engineered fields + V6_V2 / recovered package for regeneration when needed).
2. Train Random Forest as in the paper / Table 1 notebooks.
3. Evaluate on independent S_669, Ssym, S_921 and compare to published metrics.

V3 tensor diagnostics remain useful background; do not burn more time on pickle
matching unless it directly improves feature generation for RF.

Fidelity questions (Feature B weighting, decoder RNG, zero-vector fallback,
etc.) are tracked skeptically in
`manuscript_codebase_mapping/MANUSCRIPT_TENSOR_EXTRACTION_FIDELITY.md` — conflict
vs shorthand vs unused alternate vs unresolved — not assumed bugs.

## Clean PDB → modified ProteinMPNN → features path (active)

**Primary deliverable on this branch:** runnable extraction from local PDBs.

```text
ACCRE_*_PDB_Files + mutation_ddg_tables + v_48_020.pt
  → modified_proteinmpnn/ (baked-in DecLayer + forward hooks)
  → proteinmpnn_ddg_recovery.features (A–H callables)
  → regenerated V3-shaped pickle
  → train_eval_rf_from_v3_features.py (--v3-pickle-override)
```

| Piece | Path |
| --- | --- |
| Clean MPNN fork | `modified_proteinmpnn/` (`MODIFICATIONS.md`) |
| Feature A–H API | `proteinmpnn_ddg_recovery/features/` |
| Pipeline entrypoint | `scripts/run_pdb_to_features_pipeline.py` |
| Architecture note | `manuscript_codebase_mapping/CLEAN_MODIFIED_PROTEINMPNN_AND_FEATURES.md` |
| Slice smoke (16) | `reproduction_runs/2026-09-12/pdb_to_features_ssym_slice16/` |

Slice-16 diagnostic vs historical Ssym V3: PSSM 16/16; ProteinMPNN-derived
scalars/tensors not bit-exact (expected under open RNG/order questions). Runtime
utils path confirmed: `modified_proteinmpnn/protein_mpnn_utils.py`.

```bash
.venv_proteinmpnn_ddg_reproduction/bin/python scripts/run_pdb_to_features_pipeline.py \
  --dataset Ssym --seed-mode continuous --compare-reference \
  --output-dir reproduction_runs/2026-09-12/pdb_to_features_ssym
```

---

## Honest scope

```text
Saved historical V3 engineered features (+ re-fit KPCA E)
  → RF train on S_2648 (F+R aug) → eval S_669/Ssym/S_921
```

is **working** and close to Table 1 (see below).

```text
PDB + ProteinMPNN → V3 direct tensors (value-level) → …
```

is **still blocked** (`log_prob` / attended neighbors). Not required for the
RF-from-saved-features milestone.

Results-layer verification from the saved ten-run pickle (Table 1 21/21, Fig 6)
remains available via `./scripts/run_results_layer_reproduction.sh`.

---

## RF retrain vs Table 1 (measured)

**Script:** `scripts/train_eval_rf_from_v3_features.py`  
**Primary artifact:** `reproduction_runs/2026-09-12/rf_from_v3_features/`  
**Feature source:** saved historical V3 engineered + re-fit KPCA Feature E  
**Feature B (primary):** `historical_weighted`  
**S_669:** ΔΔG sign flip applied (notebook protocol)

### Hyperparams

| Label | Settings | Role |
| --- | --- | --- |
| `manuscript_literal` | `n_estimators=500`, `max_samples=0.5`, other sklearn defaults | Primary vs BioRxiv wording |
| `notebook_table1` | + `max_features="sqrt"`, `min_samples_split=2` | Matches VGRAPHS / ten-run pickle cell |
| `notebook_early` (optional CLI) | 300 / 0.2 / min_samples_split=5 / sqrt | Early notebooks; not run in primary table |

### Command (primary 10-run)

```bash
.venv_proteinmpnn_ddg_reproduction/bin/python scripts/train_eval_rf_from_v3_features.py \
  --output-dir reproduction_runs/2026-09-12/rf_from_v3_features \
  --n-runs 10 --full-ah-only \
  --configs manuscript_literal notebook_table1 \
  --feature-b-mode historical_weighted --kpca-seed 0
```

### Ours vs paper (full A–H, ten-run means)

Paper targets from Table 1 PMPNN-DDG rows.

#### `notebook_table1` (closest to historical pickle protocol)

| Dataset | Metric | Ours | Paper | Δ round |
| --- | --- | ---: | ---: | ---: |
| S_669 | rF+R | 0.6443 → **0.64** | 0.64 | 0.00 |
| S_669 | rmsF+R | 1.4517 → **1.45** | 1.45 | 0.00 |
| S_669 | rF-R | -0.9940 → **-0.99** | -0.99 | 0.00 |
| Ssym | rF+R | 0.8108 → **0.81** | 0.81 | 0.00 |
| Ssym | rmsF+R | 1.1039 → **1.10** | 1.10 | 0.00 |
| Ssym | rF-R | -0.9954 → -1.00 | -0.99 | 0.01 |
| S_921 | rF+R | 0.7954 → 0.80 | 0.79 | 0.01 |
| S_921 | rmsF+R | 1.4915 → **1.49** | 1.49 | 0.00 |
| S_921 | rF-R | -0.9962 → **-1.00** | -1.00 | 0.00 |

Most other Table 1 columns (`rF`, `rR`, `rmsF`, `rmsR`) also match rounded paper
values under this config; see `ours_vs_paper_table1.tsv`.

#### `manuscript_literal`

| Dataset | rF+R ours→round | Paper | rmsF+R ours→round | Paper |
| --- | ---: | ---: | ---: | ---: |
| S_669 | 0.6375 → 0.64 | 0.64 | 1.4627 → 1.46 | 1.45 |
| Ssym | 0.8037 → 0.80 | 0.81 | 1.1078 → 1.11 | 1.10 |
| S_921 | 0.7936 → 0.79 | 0.79 | 1.4708 → 1.47 | 1.49 |

### Feature B diagnostic (not primary)

`reproduction_runs/2026-09-12/rf_from_v3_features_manuscript_B/` — 3 runs,
`notebook_table1`, `--feature-b-mode manuscript_unweighted`. rF+R still rounds
to paper on S_669/Ssym/S_921. Supports leaving Feature B weighting as an open
wording/fidelity question rather than a confirmed metric blocker.

### Call

**Manuscript-method RF reproduction from saved V3 features is promising.**
Rounded Table 1 targets are recovered under notebook_table1 settings; manuscript
literal hyperparams are within ~0.01–0.02 on key cells.

---

## Prior milestones (still valid)

### Table 1 results layer — SUCCESS (saved pickle, not retrain)

`./scripts/run_results_layer_reproduction.sh` → **21/21** cells from
`list_incremental_feature_result_dict.pickle` + notebook `rF-R`.

### Figure 6 results layer — SUCCESS

Incremental PCC series + PNG byte-match path; see
`reproduction_runs/2026-09-12/figure6_image_verification/`.

### Ssym engineered/PSSM from saved tensors — SUCCESS

342/342 entries; engineered/PSSM fields allclose. Proves saved-tensor → features
only.

### V3 direct-tensor slice diagnostics — still failing value match

Neighbor replay lifts identity fields; `log_prob` remains 0/6. Continuous RNG
alone does not help. Details:
`reproduction_runs/2026-09-12/v3_ssym_slice_diagnostics/`.

---


## PDB → clean MPNN → manuscript-path features → RF (measured)

### Naming: historical V3 vs manuscript-path

Today’s regenerated tensors/features are **manuscript-path artifacts**, not “V3
tensors.” V3 refers to historical Digging pickles
(`*_pmppn_info_dict_V3.pickle`). See
`manuscript_codebase_mapping/MANUSCRIPT_PATH_VS_HISTORICAL_V3.md`.

Preferred pickle name: `manuscript_path_features.pickle`  
Compat alias: `regenerated_v3_features.pickle` (symlink on existing runs)  
Umbrella: `reproduction_runs/2026-09-12/manuscript_path_tensors/{S_2648,…}`  
Save modes: `--save-mode full|both|rf_compact` (default **full**; prior runs used
`rf_compact` via `--compact-for-rf`). Full extraction tensors are the durable
artifact; RF-compact alone is insufficient for long-term storage.

**Drive interim store:** `scripts/upload_manuscript_path_tensors_to_drive.sh`  
**Blocker:** rclone not installed / no remotes on this box — parent must auth.


### Integrity audit (unprocessable mutations)

**Exclusions are not metric-driven.** Every failed PDB→features job is listed with
error class, PDB path, checks performed, justification, and historical V3
stub-vs-full comparison:

- `manuscript_codebase_mapping/UNPROCESSABLE_MUTATIONS_AND_DATASET_GAPS.md`
- `manuscript_codebase_mapping/tables/unprocessable_mutations.tsv`
- `manuscript_codebase_mapping/tables/unprocessable_mutations.json`
- Regenerator: `scripts/audit_unprocessable_mutations.py`

S_2648: **2647/2648** ok; **1** remaining (`2a01A/L141R` `missing_pssm` after
independent RCSB PDB fetch + ICODE/chain parser fixes). **28/29** prior errors
recovered (`1lveA` 17 + `2immA` 10 + `1rtpA` 1). ACCRE vs RCSB sequences matched
for the ICODE/chain cases (parser bugs, not corrupt snapshots).
S_669: **638/669** ok; **31** remaining (`3dv0I` `missing_pssm` after independent
`3DV0` chain I fetch — PDB parses; PSSM absent).
Ssym: **342/342** (zero unprocessable). S_921 regen in progress with `--resume`.

### Regenerated pickles

| Dataset | Status | Artifact | Notes |
| --- | --- | --- | --- |
| Ssym | **done** 342/342 (~500s) | `reproduction_runs/2026-09-12/pdb_to_features_ssym/regenerated_v3_features.pickle` | PSSM exact vs hist; MPNN tensors not bit-exact |
| S_2648 (train) | **done** 2647/2648 (recovered 28/29) | `reproduction_runs/2026-09-12/pdb_to_features_s2648/regenerated_v3_features.pickle` | Remaining: `2a01A/L141R` missing_pssm; see integrity doc |
| S_669 | **done** 638/669 | `reproduction_runs/2026-09-12/pdb_to_features_s669/regenerated_v3_features.pickle` | 31× `3dv0I` missing_pssm after independent PDB |
| S_921 | in progress (`--resume`) | `reproduction_runs/2026-09-12/pdb_to_features_s921/` | |

Always: `--by-protein-subprocess --compact-for-rf --seed-mode per_entry` (+ `--resume`).

### Full-train E2E RF (regenerated S_2648 + regenerated Ssym)

**Artifact:** `reproduction_runs/2026-09-12/rf_from_regenerated_s2648_ssym/`  
**Overrides:** S_2648 + Ssym regenerated; S_669 / S_921 still saved historical V3.  
**Protocol:** 10-run, `full-ah-only`, `historical_weighted` Feature B, `kpca-seed 0`.  
**Coverage (pre-recovery RF):** train kept 2619. **Post-recovery:** retrain with 2647 S_2648 examples (see `rf_from_regenerated_s2648_ssym_post_recovery/`). S_669 still skips 31 `3dv0I` (missing_pssm).

#### `notebook_table1` (primary vs Table 1)

| Dataset | Metric | Ours | Paper | Δ round |
| --- | --- | ---: | ---: | ---: |
| S_669 | rF+R | 0.6421 → **0.64** | 0.64 | 0.00 |
| S_669 | rmsF+R | 1.4551 → 1.46 | 1.45 | 0.01 |
| Ssym | rF+R | 0.8141 → **0.81** | 0.81 | 0.00 |
| Ssym | rmsF+R | 1.0972 → **1.10** | 1.10 | 0.00 |
| S_921 | rF+R | 0.7950 → **0.79** | 0.79 | 0.00 |
| S_921 | rmsF+R | 1.4925 → **1.49** | 1.49 | 0.00 |

Most other Table 1 cells also match under this config; see
`ours_vs_paper_table1.tsv`.

#### `manuscript_literal`

| Dataset | rF+R ours→round | Paper | rmsF+R ours→round | Paper |
| --- | ---: | ---: | ---: | ---: |
| S_669 | 0.6376 → 0.64 | 0.64 | 1.4625 → 1.46 | 1.45 |
| Ssym | 0.8086 → **0.81** | 0.81 | 1.0981 → **1.10** | 1.10 |
| S_921 | 0.7935 → 0.79 | 0.79 | 1.4700 → 1.47 | 1.49 |

### Earlier partial E2E (saved train, regenerated Ssym only)

3-run `notebook_table1`: Ssym rF+R 0.8134 → 0.81 / rms 1.0983 → 1.10
(`rf_from_regenerated_ssym/`).

### Commands

```bash
.venv_proteinmpnn_ddg_reproduction/bin/python scripts/run_pdb_to_features_pipeline.py \
  --dataset S_2648 --seed-mode per_entry \
  --by-protein-subprocess --compact-for-rf --resume --compare-reference \
  --output-dir reproduction_runs/2026-09-12/pdb_to_features_s2648

.venv_proteinmpnn_ddg_reproduction/bin/python scripts/train_eval_rf_from_v3_features.py \
  --v3-pickle-override S_2648=reproduction_runs/2026-09-12/pdb_to_features_s2648/regenerated_v3_features.pickle \
  --v3-pickle-override Ssym=reproduction_runs/2026-09-12/pdb_to_features_ssym/regenerated_v3_features.pickle \
  --output-dir reproduction_runs/2026-09-12/rf_from_regenerated_s2648_ssym \
  --n-runs 10 --full-ah-only --configs notebook_table1 manuscript_literal \
  --feature-b-mode historical_weighted --kpca-seed 0
```

**Call:** regenerating the **training** set from PDB does not break Table 1
alignment under `notebook_table1`. Remaining gap for all-regenerated eval is
S_669 / S_921 PDB→features (S_669 kicked off with `--resume`).


## Remaining blockers (honest)

1. **PDB → V3 direct tensors** value-level match (attended neighbors, log_probs).
2. **Feature E** not bit-identical to 2022 Colab (unseeded KPCA subsample); seeded
   re-fit is protocol-aligned and sufficient for current RF metrics.
3. **S_669 / S_2648 gaps:** saved path skips 31 on S_669; regenerated S_2648 had
   29 audited failures (see `UNPROCESSABLE_MUTATIONS_AND_DATASET_GAPS.md`). 28
   align with historical `ddg`+`mut` stubs; `1rtpA` is a new regen-only chain-id
   gap vs a historically complete entry.
4. Large historical model pickles (`feature_combo_model_dict.pickle`, etc.) not
   in the narrowly promoted LFS set — not required for this RF retrain.
5. S_669 / S_921 regenerated pickles not yet folded into RF (S_669 running).

## Next experiments (ordered)

1. Finish S_669 (+ optional S_921) PDB→features; re-run RF with all four
   `--v3-pickle-override`s (`READY_COMMANDS_remaining_datasets.sh`).
2. Optional: longer `manuscript_unweighted` Feature B run (10×) if wording
   debate needs tighter CI — not blocking.
3. Only if needed for claims beyond RF-from-features: resume V3 tensor
   regeneration with manuscript-fidelity framing (not bit-exact obsession).

## Key paths

| Item | Path |
| --- | --- |
| RF script | `scripts/train_eval_rf_from_v3_features.py` |
| PDB→features pipeline | `scripts/run_pdb_to_features_pipeline.py` (`--resume`) |
| Saved-V3 RF metrics | `reproduction_runs/2026-09-12/rf_from_v3_features/` |
| Regenerated-train RF | `reproduction_runs/2026-09-12/rf_from_regenerated_s2648_ssym/` |
| Regenerated S_2648 pickle | `reproduction_runs/2026-09-12/pdb_to_features_s2648/regenerated_v3_features.pickle` |
| Regenerated Ssym pickle | `reproduction_runs/2026-09-12/pdb_to_features_ssym/regenerated_v3_features.pickle` |
| Feature B diagnostic | `reproduction_runs/2026-09-12/rf_from_v3_features_manuscript_B/` |
| Ready commands | `reproduction_runs/2026-09-12/logs/READY_COMMANDS_remaining_datasets.sh` |
| Fidelity checklist | `manuscript_codebase_mapping/MANUSCRIPT_TENSOR_EXTRACTION_FIDELITY.md` |
| Results-layer runner | `scripts/run_results_layer_reproduction.sh` |
