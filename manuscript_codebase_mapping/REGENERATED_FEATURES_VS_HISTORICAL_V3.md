# Regenerated PMPNN-DDG features/tensors vs historical V3 pickles

Date: 2026-09-12  
Branch: `reproduce-paper-results`

## Naming policy

Do **not** call regenerated tensors “V3.” Prefer scientific names from BioRxiv
§§3.1–3.3 (see `proteinmpnn_ddg_recovery/SCHEMA.md`).

| Artifact | Path pattern |
| --- | --- |
| Historical Digging V3 | `*_pmppn_info_dict_V3.pickle` (reference only) |
| RF features | `reproduction_inputs/pmpnn_ddg_features_2026-09-12/{Dataset}_features.pickle` |
| Full extraction tensors | `reproduction_inputs/pmpnn_ddg_extraction_tensors_2026-09-12/{Dataset}_extraction_tensors.pickle` |

## Computation path

```text
PDB (+ fallback) + mutation table + v_48_020.pt
  → modified ProteinMPNN (§3.1 center- / neighbor-masked passes)
  → extraction tensors (canonical keys + legacy aliases)
  → features A–H (§3.2–3.3)
  → RF / KPCA → Table 1 metrics
```

## Save modes

| `--save-mode` | Emphasizes |
| --- | --- |
| `full` | `{Dataset}_extraction_tensors.pickle` (intermediates + features) |
| `rf_compact` | RF subset only |
| `both` | Full primary + compact sidecar in shards |

Legacy notebook keys (`log_prob`, `top_15_attention_weights`, …) remain as
aliases. Note: “attention” legacy names are **message L2 norms**, not attention.
