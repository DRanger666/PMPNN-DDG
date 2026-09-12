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

## Remaining blockers (honest)

1. **PDB → V3 direct tensors** value-level match (attended neighbors, log_probs).
2. **Feature E** not bit-identical to 2022 Colab (unseeded KPCA subsample); seeded
   re-fit is protocol-aligned and sufficient for current RF metrics.
3. **S_669 / S_2648 incomplete engineered entries** skipped (31 + 28); same class
   of gaps as historical notebooks (e.g. `3dv0I`, `1lveA`).
4. Large historical model pickles (`feature_combo_model_dict.pickle`, etc.) not
   in the narrowly promoted LFS set — not required for this RF retrain.
5. Regenerating features from V6_V2 on PDB (step B of the pivot) not yet wired
   into the RF loop; primary path uses saved V3 matrices.

## Next experiments (ordered)

1. Optional: longer `manuscript_unweighted` Feature B run (10×) if wording
   debate needs tighter CI — not blocking.
2. Wire regenerated engineered features (from saved tensors via
   `proteinmpnn_ddg_recovery.engineered_features`, already proven on Ssym) into
   the same RF script for non-Ssym sets.
3. Only if needed for claims beyond RF-from-saved-features: resume V3 tensor
   regeneration with manuscript-fidelity framing (not bit-exact obsession).

## Key paths

| Item | Path |
| --- | --- |
| RF script | `scripts/train_eval_rf_from_v3_features.py` |
| Primary metrics | `reproduction_runs/2026-09-12/rf_from_v3_features/` |
| Feature B diagnostic | `reproduction_runs/2026-09-12/rf_from_v3_features_manuscript_B/` |
| Fidelity checklist | `manuscript_codebase_mapping/MANUSCRIPT_TENSOR_EXTRACTION_FIDELITY.md` |
| Results-layer runner | `scripts/run_results_layer_reproduction.sh` |
