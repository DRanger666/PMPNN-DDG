"""Canonical extraction-tensor field names (scientific objects).

New full saves use descriptive keys. Legacy notebook/V3-era keys remain as
backward-compatible aliases pointing at the same arrays so engineered-feature
and RF code keep working unchanged.
"""
from __future__ import annotations

from typing import Any

# canonical_name -> legacy_alias (historical pickle / notebook key)
EXTRACTION_FIELD_ALIASES: dict[str, str] = {
    # Center-masked pass
    "center_masked_log_probs": "log_prob",
    # Message L2 norms used to rank neighbors (NOT attention weights)
    "message_norm_top15_weights": "top_15_attention_weights",
    "message_norm_top10_weights": "top_10_attention_weights",
    "message_norm_top5_weights": "top_5_attention_weights",
    "message_norm_top15_residue_indices": "top_15_neighbor_indices",
    "message_norm_top10_residue_indices": "top_10_neighbor_indices",
    "message_norm_top5_residue_indices": "top_5_neighbor_indices",
    "spatial_nearest_top15_residue_indices": "top_15_closest_neighbor_indices",
    "spatial_nearest_top10_residue_indices": "top_10_closest_neighbor_indices",
    # Neighbor-masked passes (WT vs MT center identity)
    "neighbor_log_probs_center_wt": "w_n_log_prob",
    "neighbor_log_probs_center_mt": "m_n_log_prob",
    "neighbor_residue_aa_ids": "neighbor_aa_identities",
    "center_to_neighbor_messages_center_wt": "neighbor_w_message_vector_coming_from_center",
    "center_to_neighbor_messages_center_mt": "neighbor_m_message_vector_coming_from_center",
    "neighbor_embeddings_center_wt": "neighbor_w_neighbor_embedding",
    "neighbor_embeddings_center_mt": "neighbor_m_neighbor_embedding",
}

LEGACY_TO_CANONICAL = {legacy: canon for canon, legacy in EXTRACTION_FIELD_ALIASES.items()}

EXTRACTION_TENSOR_FIELDS = list(EXTRACTION_FIELD_ALIASES.keys())
# Historical constant name retained for imports
V3_TENSOR_FIELDS_LEGACY = list(EXTRACTION_FIELD_ALIASES.values())

FIELD_SHAPES_DOC = {
    "center_masked_log_probs": "float[1, L, 21] — log-softmax AA probs from center-masked decode",
    "message_norm_top15_weights": "float[15] — L2 norms of center→neighbor decoder messages (ranking scores)",
    "message_norm_top10_weights": "float[10]",
    "message_norm_top5_weights": "float[5]",
    "message_norm_top15_residue_indices": "int[15] — residue indices ranked by message L2 norm",
    "message_norm_top10_residue_indices": "int[10]",
    "message_norm_top5_residue_indices": "int[5]",
    "spatial_nearest_top15_residue_indices": "int[15] — spatially nearest residues (CA distance graph)",
    "spatial_nearest_top10_residue_indices": "int[10]",
    "neighbor_log_probs_center_wt": "list[15] of float[21] — neighbor-site log-probs, center=WT",
    "neighbor_log_probs_center_mt": "list[15] of float[21] — neighbor-site log-probs, center=MT",
    "neighbor_residue_aa_ids": "list[15] of str — one-letter AA at each ranked neighbor",
    "center_to_neighbor_messages_center_wt": "list[15] of float[128] — message vector center→neighbor, WT center",
    "center_to_neighbor_messages_center_mt": "list[15] of float[128] — message vector center→neighbor, MT center",
    "neighbor_embeddings_center_wt": "list[15] of float[128] — neighbor node embedding, WT center",
    "neighbor_embeddings_center_mt": "list[15] of float[128] — neighbor node embedding, MT center",
}


def with_legacy_aliases(fields: dict[str, Any], *, primary: str = "canonical") -> dict[str, Any]:
    """Return a dict containing both canonical and legacy keys.

    ``primary`` selects which name set must already be present in ``fields``:
    - ``canonical``: expect new names; add legacy aliases
    - ``legacy``: expect old names; add canonical aliases
    """

    out = dict(fields)
    if primary == "canonical":
        for canon, legacy in EXTRACTION_FIELD_ALIASES.items():
            if canon in out and legacy not in out:
                out[legacy] = out[canon]
    elif primary == "legacy":
        for canon, legacy in EXTRACTION_FIELD_ALIASES.items():
            if legacy in out and canon not in out:
                out[canon] = out[legacy]
    else:
        raise ValueError(f"Unknown primary={primary!r}")
    return out


def get_tensor_field(entry: dict[str, Any], canonical_name: str) -> Any:
    """Fetch a tensor by canonical name, falling back to legacy alias."""

    if canonical_name in entry:
        return entry[canonical_name]
    legacy = EXTRACTION_FIELD_ALIASES.get(canonical_name)
    if legacy is not None and legacy in entry:
        return entry[legacy]
    raise KeyError(canonical_name)
