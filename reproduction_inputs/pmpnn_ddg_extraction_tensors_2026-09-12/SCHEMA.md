# Extraction tensor schema (canonical keys)

Date: 2026-09-12  
Code: `proteinmpnn_ddg_recovery/extraction_tensor_schema.py`

New full saves store **canonical** scientific names below. The same arrays are
also written under **legacy** notebook keys (parentheses) so engineered-feature
/ RF code can read either.

## Files

| File | Contents |
| --- | --- |
| `{Dataset}_extraction_tensors.pickle` | Full intermediates + engineered/A–H (audit asset) |
| `shards/{Dataset}/{protein}.out.pkl` | Per-protein full shards if aggregate is too large |
| `../pmpnn_ddg_features_2026-09-12/{Dataset}_features_rf.pickle` | RF-ready subset only |

Datasets: `Ssym`, `S2648`, `S669`, `S921`.

## Top-level layout

```text
{ "<protein_key>": [ entry, ... ], ... }
```

## Center-masked pass (designable = mutation site)

| Canonical key | Legacy alias | Shape / type | Meaning |
| --- | --- | --- | --- |
| `center_masked_log_probs` | `log_prob` | `float[1, L, 21]` | Log-softmax AA probs; center residue masked/designable |
| `message_norm_top15_weights` | `top_15_attention_weights` | `float[15]` | **L2 norms of decoder messages** used to rank neighbors (not attention) |
| `message_norm_top10_weights` | `top_10_attention_weights` | `float[10]` | same, top-10 |
| `message_norm_top5_weights` | `top_5_attention_weights` | `float[5]` | same, top-5 |
| `message_norm_top15_residue_indices` | `top_15_neighbor_indices` | `int[15]` | Residue indices ranked by message L2 norm |
| `message_norm_top10_residue_indices` | `top_10_neighbor_indices` | `int[10]` | |
| `message_norm_top5_residue_indices` | `top_5_neighbor_indices` | `int[5]` | |
| `spatial_nearest_top15_residue_indices` | `top_15_closest_neighbor_indices` | `int[15]` | Spatially nearest residues on the CA kNN graph |
| `spatial_nearest_top10_residue_indices` | `top_10_closest_neighbor_indices` | `int[10]` | |

## Neighbor-masked passes (each of 15 ranked neighbors designable)

Center identity toggled WT vs MT at the mutation index.

| Canonical key | Legacy alias | Shape / type | Meaning |
| --- | --- | --- | --- |
| `neighbor_log_probs_center_wt` | `w_n_log_prob` | `list[15]×float[21]` | Neighbor-site log-probs with center=WT |
| `neighbor_log_probs_center_mt` | `m_n_log_prob` | `list[15]×float[21]` | Neighbor-site log-probs with center=MT |
| `neighbor_residue_aa_ids` | `neighbor_aa_identities` | `list[15]×str` | WT one-letter AA at each neighbor |
| `center_to_neighbor_messages_center_wt` | `neighbor_w_message_vector_coming_from_center` | `list[15]×float[128]` | Message vector at neighbor from center slot, WT |
| `center_to_neighbor_messages_center_mt` | `neighbor_m_message_vector_coming_from_center` | `list[15]×float[128]` | Same, MT center |
| `neighbor_embeddings_center_wt` | `neighbor_w_neighbor_embedding` | `list[15]×float[128]` | Neighbor node embedding, WT center |
| `neighbor_embeddings_center_mt` | `neighbor_m_neighbor_embedding` | `list[15]×float[128]` | Neighbor node embedding, MT center |

## Feature layer (also present on full entries)

| Key | Notes |
| --- | --- |
| `feature_A` … `feature_H` | Manuscript feature callables |
| `feature_B_historical_weighted` | Primary B used in Table 1 RF |
| `feature_B_manuscript_unweighted` | Diagnostic unweighted B |
| `center_mut_wild_energy`, `center_entropy`, … | Engineered scalars |
| `wild_pssm`, `alternate_pssm` | PSSM lookups |
| `mut`, `ddg`, `protein_key`, `sequence_index` | Identity |
| `artifact_kind` | `"pmpnn_ddg_extraction"` on full saves |

## RF-only subset

`{Dataset}_features_rf.pickle` keeps identity + engineered/PSSM/A–H scalars needed
for training (see `RF_KEEP_FIELDS` in the pipeline). It does **not** replace
extraction tensor pickles for audit/transparency.
