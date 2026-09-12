"""Assemble manuscript Features A–H (and V3 engineered companions) for one mutation.

Primary path:
  extract_mutation_tensor_fields (clean modified ProteinMPNN)
  → compute_feature_a / b / c / d / fgh
  → message-change matrix for Feature E (projected later at dataset level)
  → also fill full V3 engineered/PSSM fields via engineered_features for RF pickle
    compatibility.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from proteinmpnn_ddg_recovery.engineered_features import (
    DEFAULT_SSYM_PSSM_DIR,
    compute_v3_engineered_and_pssm_features,
)
from proteinmpnn_ddg_recovery.features.feature_a import compute_feature_a
from proteinmpnn_ddg_recovery.features.feature_b import (
    compute_feature_b_historical_weighted,
    compute_feature_b_manuscript_unweighted,
)
from proteinmpnn_ddg_recovery.features.feature_c import compute_feature_c
from proteinmpnn_ddg_recovery.features.feature_d import (
    compute_feature_d,
    compute_feature_d_raw,
)
from proteinmpnn_ddg_recovery.features.feature_e import build_message_change_matrix
from proteinmpnn_ddg_recovery.features.feature_fgh import compute_features_fgh
from proteinmpnn_ddg_recovery.recovered_v6v2 import MutationTensorExtraction


def compute_ah_from_tensors(
    extraction: MutationTensorExtraction,
    *,
    pssm_dir: Path = DEFAULT_SSYM_PSSM_DIR,
    feature_b_mode: str = "historical_weighted",
) -> dict[str, Any]:
    """Compute Features A–H (E as raw message-change matrix) from one extraction."""

    fields = extraction.fields
    mutation_label = extraction.mutation_label
    sequence_index = extraction.sequence_index
    protein_key = extraction.protein_key

    a = compute_feature_a(fields["log_prob"], mutation_label, sequence_index)
    if feature_b_mode == "manuscript_unweighted":
        b = compute_feature_b_manuscript_unweighted(
            fields["w_n_log_prob"],
            fields["m_n_log_prob"],
        )
    else:
        b = compute_feature_b_historical_weighted(
            fields["w_n_log_prob"],
            fields["m_n_log_prob"],
            fields["neighbor_w_message_vector_coming_from_center"],
            fields["neighbor_m_message_vector_coming_from_center"],
        )
    c = compute_feature_c(
        fields["neighbor_w_message_vector_coming_from_center"],
        fields["neighbor_m_message_vector_coming_from_center"],
    )
    d = compute_feature_d(
        fields["neighbor_w_neighbor_embedding"],
        fields["neighbor_m_neighbor_embedding"],
    )
    e_matrix = build_message_change_matrix(
        fields["neighbor_w_message_vector_coming_from_center"],
        fields["neighbor_m_message_vector_coming_from_center"],
    )
    fgh = compute_features_fgh(
        protein_key,
        mutation_label,
        sequence_index,
        pssm_dir=pssm_dir,
    )
    return {
        "A": a,
        "B": b,
        "B_mode": feature_b_mode,
        "C": c,
        "D": d,
        "E_message_change_matrix": e_matrix,
        "D_raw": compute_feature_d_raw(
            fields["neighbor_w_neighbor_embedding"],
            fields["neighbor_m_neighbor_embedding"],
        ),
        "F": fgh["F"],
        "G": fgh["G"],
        "H": fgh["H"],
    }


def build_v3_entry_from_extraction(
    extraction: MutationTensorExtraction,
    ddg: float,
    *,
    pssm_dir: Path = DEFAULT_SSYM_PSSM_DIR,
) -> dict[str, Any]:
    """Build a V3-shaped pickle entry (tensors + engineered + PSSM + ddg)."""

    entry: dict[str, Any] = {
        "mut": extraction.mutation_label,
        "ddg": float(ddg),
    }
    entry.update(extraction.fields)
    entry.update(
        compute_v3_engineered_and_pssm_features(
            extraction.protein_key,
            entry,
            extraction.sequence_index,
            pssm_dir=pssm_dir,
        )
    )
    # Attach labeled A–H scalars for the clean API (Feature E deferred).
    ah = compute_ah_from_tensors(extraction, pssm_dir=pssm_dir)
    entry["feature_A"] = ah["A"]
    entry["feature_B_historical_weighted"] = compute_feature_b_historical_weighted(
        extraction.fields["w_n_log_prob"],
        extraction.fields["m_n_log_prob"],
        extraction.fields["neighbor_w_message_vector_coming_from_center"],
        extraction.fields["neighbor_m_message_vector_coming_from_center"],
    )
    entry["feature_B_manuscript_unweighted"] = compute_feature_b_manuscript_unweighted(
        extraction.fields["w_n_log_prob"],
        extraction.fields["m_n_log_prob"],
    )
    entry["feature_B_entropy_change_sum_weighted"] = entry["feature_B_historical_weighted"]
    entry["feature_B_entropy_change_sum_unweighted"] = entry["feature_B_manuscript_unweighted"]
    entry["feature_C"] = ah["C"]
    entry["feature_D"] = ah["D"]
    entry["feature_F"] = ah["F"]
    entry["feature_G"] = ah["G"]
    entry["feature_H"] = ah["H"]
    entry["feature_E_message_change_matrix"] = ah["E_message_change_matrix"]
    return entry
