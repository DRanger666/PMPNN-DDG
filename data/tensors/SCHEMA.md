# Extraction / feature schema (BioRxiv §§3.1–3.3)

Date: 2026-09-12  
Code: `pmpnn_ddg/extraction_tensor_schema.py`

Canonical Python keys name the **scientific objects** in the method text.
Legacy Digging/notebook keys are dual-written as aliases for RF compatibility.

## Artifact files

| File | Role |
| --- | --- |
| `{Dataset}_extraction_tensors.pickle` | Full §3.1 intermediates + §3.2–3.3 features (audit / transparency) |
| `{Dataset}_features.pickle` | RF-ready feature subset (may symlink to `*_features_rf.pickle`) |
| `shards/{Dataset}/{protein}.out.pkl` | Per-protein full shards if the aggregate pickle is too large |

Datasets: `Ssym`, `S2648`, `S669`, `S921`.

Top-level layout: `{ protein_key: [entry, …], … }`.

---

## §3.1 Center-masked pass

Mutation site is the sole designable position. Decoder yields masked-center
probabilities and neighbor→center messages.

| Canonical key | Legacy alias | Shape | Manuscript meaning |
| --- | --- | --- | --- |
| `center_masked_log_probs` | `log_prob` | `float[1,L,21]` | Masked-center AA log-probs; feeds **Feature A** |
| `neighbor_to_center_message_l2_norms_top15` | `top_15_attention_weights` | `float[15]` | L2 norms used to rank “most attended” neighbors (**not** attention) |
| `neighbor_to_center_message_l2_norms_top10` | `top_10_attention_weights` | `float[10]` | K=10 |
| `neighbor_to_center_message_l2_norms_top5` | `top_5_attention_weights` | `float[5]` | K=5 |
| `most_attended_neighbor_indices_top15` | `top_15_neighbor_indices` | `int[15]` | Top-K neighbor residue indices by message L2 norm |
| `most_attended_neighbor_indices_top10` | `top_10_neighbor_indices` | `int[10]` | |
| `most_attended_neighbor_indices_top5` | `top_5_neighbor_indices` | `int[5]` | |
| `spatial_nearest_neighbor_indices_top15` | `top_15_closest_neighbor_indices` | `int[15]` | Geometric nearest among local CA neighbors |
| `spatial_nearest_neighbor_indices_top10` | `top_10_closest_neighbor_indices` | `int[10]` | |

---

## §3.1 Neighbor-masked passes

For each most-attended neighbor *j*, that neighbor is designable; the mutation
center is set to **WT** then **MT**.

| Canonical key | Legacy alias | Shape | Manuscript symbol |
| --- | --- | --- | --- |
| `neighbor_log_probs_wt` | `w_n_log_prob` | `list[15]×float[21]` | \(P_j^{\mathrm{WT}}\) (stored as log-probs) |
| `neighbor_log_probs_mt` | `m_n_log_prob` | `list[15]×float[21]` | \(P_j^{\mathrm{MT}}\) |
| `neighbor_aa_identities` | *(same)* | `list[15]×str` | WT AA identities at neighbors |
| `center_to_neighbor_messages_wt` | `neighbor_w_message_vector_coming_from_center` | `list[15]×float[128]` | \(M_j^{\mathrm{WT}}\) |
| `center_to_neighbor_messages_mt` | `neighbor_m_message_vector_coming_from_center` | `list[15]×float[128]` | \(M_j^{\mathrm{MT}}\) |
| `neighbor_embeddings_wt` | `neighbor_w_neighbor_embedding` | `list[15]×float[128]` | \(E_j^{\mathrm{WT}}\) |
| `neighbor_embeddings_mt` | `neighbor_m_neighbor_embedding` | `list[15]×float[128]` | \(E_j^{\mathrm{MT}}\) |

---

## §3.2–3.3 / §4 Feature layer

| Canonical key | Legacy / dual name | Meaning |
| --- | --- | --- |
| `feature_A` | — | Mutation-position log-probability ratio |
| `feature_B_entropy_change_sum_unweighted` | `feature_B_manuscript_unweighted` | Eq.1 unweighted neighbor entropy-change sum |
| `feature_B_entropy_change_sum_weighted` | `feature_B_historical_weighted` | Historical RF weighted entropy-change sum |
| `feature_C` | — | Message-norm-ratio sum |
| `feature_D` | — | Neighbor embedding-change-norm sum |
| `feature_E_message_change_matrix` / KPCA | — | Message-change matrix → KPCA components for RF |
| `feature_F`, `feature_G`, `feature_H` | — | PSSM evolutionary terms |

Identity fields on every entry: `mut`, `ddg`, `protein_key`, `sequence_index`,
`artifact_kind="pmpnn_ddg_extraction"`.

---

## Alias policy

`with_legacy_aliases(..., primary="canonical")` dual-writes:

1. Digging/notebook keys (`log_prob`, `top_15_attention_weights`, …)
2. Short-lived branch names (`message_norm_top15_weights`, …) if encountered

RF training may read either naming generation.
