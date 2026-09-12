# Regenerated PMPNN-DDG features/tensors vs historical V3 pickles

Date: 2026-09-12  
Branch: `reproduce-paper-results`

## Naming policy

Do **not** call today’s regenerated tensors “V3 tensors,” and avoid process
slogans in filenames.

| Name | What it is |
| --- | --- |
| **Historical V3 pickles** | Digging artifacts `*_pmppn_info_dict_V3.pickle` (2022 notebook era). Reference only. |
| **Feature pickles** | RF-ready scalars/matrices: `reproduction_inputs/pmpnn_ddg_features_2026-09-12/*_features_compact.pickle` |
| **Extraction tensor pickles** | Full intermediates for audit: `reproduction_inputs/pmpnn_ddg_extraction_tensors_2026-09-12/*_extraction_tensors.pickle` (or per-protein shards) |

Legacy `regenerated_v3_features.pickle` may remain as a compat alias only.

## Computation path

```text
ACCRE PDB (+ optional independent curated fallback)
  + mutation/DDG tables
  + ProteinMPNN v_48_020.pt
  + modified_proteinmpnn (DecLayer / forward extraction hooks)
      → extraction tensors (log_probs, messages, embeddings, neighbors, …)
      → engineered features + PSSM + A–H scalars
      → features.pickle and/or extraction_tensors.pickle
      → Random Forest / KPCA → Table 1-style metrics
```

## Save modes (`--save-mode`)

| Mode | Output emphasis | Contents |
| --- | --- | --- |
| `full` (pipeline default) | `extraction_tensors.pickle` | ProteinMPNN tensor fields + engineered + PSSM + A–H |
| `rf_compact` | `features.pickle` | RF scalars only (also promoted as `*_features_compact.pickle`) |
| `both` | full primary + compact sidecar in shards | Full + `entries_rf_compact` |

### Extraction tensor fields (intermediate)

From `V3_TENSOR_FIELDS` (historical code constant name only):

- `log_prob`
- `top_15_attention_weights`, `top_10_attention_weights`, `top_5_attention_weights`
- `top_15_neighbor_indices`, `top_10_neighbor_indices`, `top_5_neighbor_indices`
- `top_15_closest_neighbor_indices`, `top_10_closest_neighbor_indices`
- `w_n_log_prob`, `m_n_log_prob`
- `neighbor_aa_identities`
- `neighbor_w_message_vector_coming_from_center`, `neighbor_m_message_vector_coming_from_center`
- `neighbor_w_neighbor_embedding`, `neighbor_m_neighbor_embedding`

Plus engineered/PSSM/A–H fields used by RF. See also
`reproduction_inputs/pmpnn_ddg_extraction_tensors_2026-09-12/SCHEMA.md`.

## Drive / LFS

- Features (compact): Git LFS under `reproduction_inputs/pmpnn_ddg_features_2026-09-12/`
- Extraction tensors: Git LFS under `reproduction_inputs/pmpnn_ddg_extraction_tensors_2026-09-12/`
- Upload helper: `scripts/upload_pmpnn_ddg_artifacts_to_drive.sh` (rclone required; not configured on this box yet)
