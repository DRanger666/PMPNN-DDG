"""Extraction-tensor field names grounded in BioRxiv method §§3.1–3.3.

Canonical keys name the scientific objects from the manuscript. Legacy
notebook / Digging keys are dual-written as aliases for RF and engineered-
feature code.
"""
from __future__ import annotations

from typing import Any

# ---------------------------------------------------------------------------
# Canonical (BioRxiv language) -> legacy notebook key
# ---------------------------------------------------------------------------
EXTRACTION_FIELD_ALIASES: dict[str, str] = {
    # §3.1 Center-masked pass (designable = mutation site)
    "center_masked_log_probs": "log_prob",
    # L2 norms of neighbor→center decoder messages used to rank "most attended"
    # Top-K neighbors — NOT true attention weights:
    "neighbor_to_center_message_l2_norms_top15": "top_15_attention_weights",
    "neighbor_to_center_message_l2_norms_top10": "top_10_attention_weights",
    "neighbor_to_center_message_l2_norms_top5": "top_5_attention_weights",
    "most_attended_neighbor_indices_top15": "top_15_neighbor_indices",
    "most_attended_neighbor_indices_top10": "top_10_neighbor_indices",
    "most_attended_neighbor_indices_top5": "top_5_neighbor_indices",
    "spatial_nearest_neighbor_indices_top15": "top_15_closest_neighbor_indices",
    "spatial_nearest_neighbor_indices_top10": "top_10_closest_neighbor_indices",
    # §3.1 Neighbor-masked passes (each top-K neighbor designable; center WT then MT)
    "neighbor_log_probs_wt": "w_n_log_prob",
    "neighbor_log_probs_mt": "m_n_log_prob",
    "neighbor_aa_identities": "neighbor_aa_identities",  # already descriptive
    "center_to_neighbor_messages_wt": "neighbor_w_message_vector_coming_from_center",
    "center_to_neighbor_messages_mt": "neighbor_m_message_vector_coming_from_center",
    "neighbor_embeddings_wt": "neighbor_w_neighbor_embedding",
    "neighbor_embeddings_mt": "neighbor_m_neighbor_embedding",
}

# Intermediate names briefly used on this branch (also aliased from canonical)
BRANCH_INTERMEDIATE_ALIASES: dict[str, str] = {
    "neighbor_to_center_message_l2_norms_top15": "message_norm_top15_weights",
    "neighbor_to_center_message_l2_norms_top10": "message_norm_top10_weights",
    "neighbor_to_center_message_l2_norms_top5": "message_norm_top5_weights",
    "most_attended_neighbor_indices_top15": "message_norm_top15_residue_indices",
    "most_attended_neighbor_indices_top10": "message_norm_top10_residue_indices",
    "most_attended_neighbor_indices_top5": "message_norm_top5_residue_indices",
    "spatial_nearest_neighbor_indices_top15": "spatial_nearest_top15_residue_indices",
    "spatial_nearest_neighbor_indices_top10": "spatial_nearest_top10_residue_indices",
    "neighbor_log_probs_wt": "neighbor_log_probs_center_wt",
    "neighbor_log_probs_mt": "neighbor_log_probs_center_mt",
    "center_to_neighbor_messages_wt": "center_to_neighbor_messages_center_wt",
    "center_to_neighbor_messages_mt": "center_to_neighbor_messages_center_mt",
    "neighbor_embeddings_wt": "neighbor_embeddings_center_wt",
    "neighbor_embeddings_mt": "neighbor_embeddings_center_mt",
}

# §3.2–3.3 / §4 feature-layer aliases
FEATURE_FIELD_ALIASES: dict[str, str] = {
    "feature_B_entropy_change_sum_weighted": "feature_B_historical_weighted",
    "feature_B_entropy_change_sum_unweighted": "feature_B_manuscript_unweighted",
}

LEGACY_TO_CANONICAL = {legacy: canon for canon, legacy in EXTRACTION_FIELD_ALIASES.items()}
EXTRACTION_TENSOR_FIELDS = list(EXTRACTION_FIELD_ALIASES.keys())
V3_TENSOR_FIELDS_LEGACY = [
    legacy for legacy in EXTRACTION_FIELD_ALIASES.values()
    if legacy != "neighbor_aa_identities" or True
]
# Unique legacy list preserving order
_seen = set()
V3_TENSOR_FIELDS_LEGACY = []
for legacy in EXTRACTION_FIELD_ALIASES.values():
    if legacy not in _seen:
        V3_TENSOR_FIELDS_LEGACY.append(legacy)
        _seen.add(legacy)

FIELD_SHAPES_DOC: dict[str, str] = {
    "center_masked_log_probs": (
        "float[1, L, 21] — §3.1 center-masked decode log-softmax; feeds Feature A "
        "(mutation-position log-probability ratio)"
    ),
    "neighbor_to_center_message_l2_norms_top15": (
        "float[15] — §3.1 L2 norms of decoder messages used to rank most-attended "
        "neighbors (NOT attention weights)"
    ),
    "neighbor_to_center_message_l2_norms_top10": "float[10] — same, K=10",
    "neighbor_to_center_message_l2_norms_top5": "float[5] — same, K=5",
    "most_attended_neighbor_indices_top15": (
        "int[15] — §3.1 Top-K neighbor residue indices by message L2 norm (K=15)"
    ),
    "most_attended_neighbor_indices_top10": "int[10]",
    "most_attended_neighbor_indices_top5": "int[5]",
    "spatial_nearest_neighbor_indices_top15": (
        "int[15] — §3.1 geometrically nearest residues on the local CA neighborhood graph"
    ),
    "spatial_nearest_neighbor_indices_top10": "int[10]",
    "neighbor_log_probs_wt": (
        "list[15]×float[21] — §3.1 PjWT: neighbor-site log-probs with center fixed WT"
    ),
    "neighbor_log_probs_mt": (
        "list[15]×float[21] — §3.1 PjMT: neighbor-site log-probs with center fixed MT"
    ),
    "neighbor_aa_identities": "list[15]×str — WT one-letter AA at each most-attended neighbor",
    "center_to_neighbor_messages_wt": (
        "list[15]×float[128] — §3.1 MjWT: message vector at neighbor from center slot, WT"
    ),
    "center_to_neighbor_messages_mt": (
        "list[15]×float[128] — §3.1 MjMT: same with center=MT"
    ),
    "neighbor_embeddings_wt": (
        "list[15]×float[128] — §3.1 EjWT: neighbor node embedding, center=WT"
    ),
    "neighbor_embeddings_mt": (
        "list[15]×float[128] — §3.1 EjMT: neighbor node embedding, center=MT"
    ),
    "feature_A": "scalar — §3.2 mutation-position log-probability ratio",
    "feature_B_entropy_change_sum_unweighted": "scalar — §3.2 Eq.1 unweighted neighbor entropy-change sum",
    "feature_B_entropy_change_sum_weighted": "scalar — historical RF weighted entropy-change sum",
    "feature_C": "scalar — §3.2 message-norm-ratio sum",
    "feature_D": "scalar — §3.2 neighbor embedding-change-norm sum",
    "feature_E_kpca_components": "float[5] — §3.2 KPCA components of message-change matrix (or feature_E_1..5)",
    "feature_F": "scalar — §3.3 / §4 PSSM evolutionary (wild)",
    "feature_G": "scalar — §3.3 / §4 PSSM evolutionary",
    "feature_H": "scalar — §3.3 / §4 PSSM evolutionary",
}


def with_legacy_aliases(fields: dict[str, Any], *, primary: str = "canonical") -> dict[str, Any]:
    """Dual-write canonical, legacy notebook, and short-lived branch names."""

    out = dict(fields)
    if primary == "canonical":
        for canon, legacy in EXTRACTION_FIELD_ALIASES.items():
            if canon in out and legacy not in out:
                out[legacy] = out[canon]
        for canon, mid in BRANCH_INTERMEDIATE_ALIASES.items():
            if canon in out and mid not in out:
                out[mid] = out[canon]
        for canon, legacy in FEATURE_FIELD_ALIASES.items():
            if canon in out and legacy not in out:
                out[legacy] = out[canon]
            if legacy in out and canon not in out:
                out[canon] = out[legacy]
    elif primary == "legacy":
        for canon, legacy in EXTRACTION_FIELD_ALIASES.items():
            if legacy in out and canon not in out:
                out[canon] = out[legacy]
        for canon, legacy in FEATURE_FIELD_ALIASES.items():
            if legacy in out and canon not in out:
                out[canon] = out[legacy]
    else:
        raise ValueError(f"Unknown primary={primary!r}")
    return out


def get_tensor_field(entry: dict[str, Any], canonical_name: str) -> Any:
    """Fetch by canonical name, then legacy / branch aliases."""

    if canonical_name in entry:
        return entry[canonical_name]
    legacy = EXTRACTION_FIELD_ALIASES.get(canonical_name)
    if legacy is not None and legacy in entry:
        return entry[legacy]
    mid = BRANCH_INTERMEDIATE_ALIASES.get(canonical_name)
    if mid is not None and mid in entry:
        return entry[mid]
    feat = FEATURE_FIELD_ALIASES.get(canonical_name)
    if feat is not None and feat in entry:
        return entry[feat]
    raise KeyError(canonical_name)
