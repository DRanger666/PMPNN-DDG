# Clean Modified ProteinMPNN + Per-Feature API

Date: 2026-09-12  
Branch: `reproduce-paper-results`

## Architecture (intended reproduction path)

```text
ACCRE PDB dirs + mutation_ddg_tables + v_48_020.pt
  → modified_proteinmpnn (baked-in extraction hooks)
  → proteinmpnn_ddg_recovery.recovered_v6v2.extract_mutation_tensor_fields
  → proteinmpnn_ddg_recovery.features.{feature_a…feature_fgh}
  → V3-shaped pickle / RF via train_eval_rf_from_v3_features.py
```

## Inventory vs upstream

| Source | Role |
| --- | --- |
| `source_repos/dauparas_ProteinMPNN/.../protein_mpnn_utils.py` | Clean upstream base (md5 = Digging nested) |
| Digging nested utils | Annotated / incomplete `return_neighbor_info`; **no** DecLayer message return |
| `SajidAhmeduiu_ProteinMPNN` utils | Comment-heavy + incomplete helper; not the V6_V2 return hooks |
| V6_V2 notebooks | Authoritative hook behavior for messages / triple return |
| `modified_proteinmpnn/` | **This branch’s clean fork** with only those hooks |

See `modified_proteinmpnn/MODIFICATIONS.md` and
`NESTED_PROTEINMPNN_DIRTY_UTILS_AUDIT.md`.

## Per-feature modules

| Feature | Module | Notes |
| --- | --- | --- |
| A | `features/feature_a.py` | Center log-prob energy difference |
| B | `features/feature_b.py` | `historical_weighted` + `manuscript_unweighted` (open wording Q) |
| C | `features/feature_c.py` | Message-norm ratio sum (NR) |
| D | `features/feature_d.py` | Embedding change-norm sum + raw matrix |
| E | `features/feature_e.py` | Message-change matrix; KPCA project helper (fit at train set) |
| F/G/H | `features/feature_fgh.py` | PSSM delta / WT / MT |

`features/compute_bundle.py` builds labeled A–H fields and a full V3-shaped entry
(including historical engineered scalars for RF pickle compatibility).

## Open questions (not assumed bugs)

Unchanged skeptical framing in `MANUSCRIPT_TENSOR_EXTRACTION_FIDELITY.md`:
decoder RNG, Feature B weighting wording, zero-vector fallback.

## Commands

```bash
.venv_proteinmpnn_ddg_reproduction/bin/python scripts/run_pdb_to_features_pipeline.py \
  --dataset Ssym --limit 16 --seed-mode continuous --compare-reference \
  --output-dir reproduction_runs/2026-09-12/pdb_to_features_ssym_slice16

.venv_proteinmpnn_ddg_reproduction/bin/python scripts/train_eval_rf_from_v3_features.py \
  --v3-pickle-override Ssym=reproduction_runs/2026-09-12/pdb_to_features_ssym/regenerated_v3_features.pickle \
  --output-dir reproduction_runs/2026-09-12/rf_from_regenerated_ssym \
  --n-runs 3 --full-ah-only --configs notebook_table1
```

## Measured (2026-09-12)

- Full Ssym PDB→features: **342/342** via `--by-protein-subprocess --compact-for-rf`.
- RF (saved S_2648 train, regenerated Ssym eval, 3× notebook_table1): Ssym rF+R **0.81**, rmsF+R **1.10** (paper match) despite non-bit-exact tensors vs historical V3.
