# Manuscript → variable naming

Date: 2026-09-12  
Source: BioRxiv PMPNN-DDG §§3.1–3.3 (DOI `10.64898/2026.08.23.746499`)  
Machine-readable aliases: `proteinmpnn_ddg_recovery/extraction_tensor_schema.py`  
Full shapes + dual-write policy: `proteinmpnn_ddg_recovery/SCHEMA.md`

This table is the human-facing map from method-text objects to Python storage
keys. Prefer the **canonical** names in new code and saved pickles. Legacy
Digging/notebook keys remain dual-written as aliases so RF scripts keep working.

## §3.1 Center-masked pass

| Manuscript language | Symbol / role | Canonical variable |
| --- | --- | --- |
| Masked-center probability / log-probs (feeds Feature A) | center masked decode | `center_masked_log_probs` |
| L2 norms of neighbor→center messages (rank Top-K / “most attended”) | **not** attention | `neighbor_to_center_message_l2_norms_top15` |
| Top-K / most-attended neighbor residue indices | K=15 | `most_attended_neighbor_indices_top15` |
| Geometrically nearest local neighbors | CA neighborhood | `spatial_nearest_neighbor_indices_top15` |

(Also `…_top10` / `…_top5` where retained.)

## §3.1 Neighbor-masked passes (center WT then MT)

| Manuscript language | Symbol | Canonical variable |
| --- | --- | --- |
| Neighbor probability distributions | \(P_j^{\mathrm{WT}}\), \(P_j^{\mathrm{MT}}\) | `neighbor_log_probs_wt`, `neighbor_log_probs_mt` |
| Center→neighbor message vectors | \(M_j^{\mathrm{WT}}\), \(M_j^{\mathrm{MT}}\) | `center_to_neighbor_messages_wt`, `center_to_neighbor_messages_mt` |
| Neighbor embedding vectors | \(E_j^{\mathrm{WT}}\), \(E_j^{\mathrm{MT}}\) | `neighbor_embeddings_wt`, `neighbor_embeddings_mt` |
| Neighbor AA identities | — | `neighbor_aa_identities` |

## §3.2–3.3 / §4 Features

| Manuscript | Canonical variable |
| --- | --- |
| Feature A (mutation-position log-probability ratio) | `feature_A` |
| Feature B Eq.1 (unweighted entropy-change sum) | `feature_B_entropy_change_sum_unweighted` |
| Feature B (historical weighted RF field) | `feature_B_entropy_change_sum_weighted` |
| Feature C (message-norm-ratio sum) | `feature_C` |
| Feature D (neighbor embedding-change-norm sum) | `feature_D` |
| Feature E (message-change KPCA) | `feature_E_kpca_components` / matrix helpers |
| Evolutionary F, G, H (PSSM) | `feature_F`, `feature_G`, `feature_H` |

## Artifact filenames

| Contents | Filename pattern |
| --- | --- |
| Full §3.1 intermediates (+ features) | `{Dataset}_extraction_tensors.pickle` |
| RF feature subset | `{Dataset}_features.pickle` |

Datasets: `Ssym`, `S2648`, `S669`, `S921`.

## Legacy aliases (examples)

| Canonical | Legacy notebook / Digging |
| --- | --- |
| `center_masked_log_probs` | `log_prob` |
| `neighbor_to_center_message_l2_norms_top15` | `top_15_attention_weights` |
| `most_attended_neighbor_indices_top15` | `top_15_neighbor_indices` |
| `center_to_neighbor_messages_wt` | `neighbor_w_message_vector_coming_from_center` |
| `neighbor_embeddings_mt` | `neighbor_m_neighbor_embedding` |

## RF packing: neighbor-embedding ΔE vs message ΔM (71 → 41)

Never call these vague “emb” / “m” columns. Scientific objects:

| Object | Manuscript | Role in packing |
| --- | --- | --- |
| Neighbor embedding change ΔE_j | §3.2.3 Feature D uses Σ‖ΔE_j‖; raw (K,128) also PCA/KPCA’d | **Not** Feature E |
| Center→neighbor message change ΔM_j | §3.2.4 Feature E = Σ RBF₁₋₅(ΔM_j) | Feature E = first 5 message-change KPCA comps |

Module: `proteinmpnn_ddg_recovery/features/rf_feature_matrix_packing.py`

- **71-col dual-direction row** — one mutation; scalars + forward/reverse projection blocks for ΔE and ΔM side-by-side. Feature E indices: `46:51`.
- **41-col F+R row** — after augmentation; two rows per mutation. Feature E indices: `31:36`.

Do **not** apply augmented E indices to the dual-direction matrix (that bug selected neighbor-embedding-change KPCA and broke Figs 4–5).
