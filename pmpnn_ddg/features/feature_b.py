"""Feature B — neighbor entropy-change summation (manuscript §3.2.1).

Manuscript Eq.1 (OCR): unweighted Σ_j (H(P_j^WT) - H(P_j^MT)).

Historical Table 1 / Fig 6 RF column uses the V2 backward-weighted field
``V2_backward_weighted_neighbor_entropy_changes`` (message-norm-ratio weights;
per-neighbor term H_MT - H_WT before weighting — sign convention of the
notebook cell).

Both are exposed; neither is declared a bug. See fidelity checklist Item B.
"""

from __future__ import annotations

from typing import Any, Sequence

import numpy as np
from scipy.special import expit
from scipy.stats import entropy


def compute_feature_b_manuscript_unweighted(
    w_n_log_prob: Sequence[Any],
    m_n_log_prob: Sequence[Any],
    k: int = 15,
) -> float:
    """Manuscript Eq.1-style: Σ_j (H_WT - H_MT) over top-K neighbors."""

    total = 0.0
    for neighbor_w, neighbor_m in zip(w_n_log_prob[:k], m_n_log_prob[:k]):
        h_wt = float(entropy(np.exp(np.asarray(neighbor_w, dtype=np.float64))))
        h_mt = float(entropy(np.exp(np.asarray(neighbor_m, dtype=np.float64))))
        total += h_wt - h_mt
    return total


def compute_feature_b_historical_weighted(
    w_n_log_prob: Sequence[Any],
    m_n_log_prob: Sequence[Any],
    neighbor_w_messages: Sequence[Any],
    neighbor_m_messages: Sequence[Any],
    k: int = 15,
) -> float:
    """Historical V2 backward-weighted Feature B used in Table 1 RF.

    Matches ``engineered_features.neighbor_energy_kl_entropy_features`` field
    ``V2_backward_weighted_neighbor_entropy_changes``: per-neighbor
    ``H_MT - H_WT``, weighted by ``expit(‖M_WT‖ / ‖M_MT‖)``, with the notebook
    broadcast quirk preserved via the shared engineered_features path when
    building full V3 entries. This function uses an explicit per-neighbor sum
    (no (15,15) broadcast) that is numerically equivalent when weights are
    length-1 arrays.
    """

    total = 0.0
    for neighbor_w, neighbor_m, msg_w, msg_m in zip(
        w_n_log_prob[:k],
        m_n_log_prob[:k],
        neighbor_w_messages[:k],
        neighbor_m_messages[:k],
    ):
        h_change = float(
            entropy(np.exp(np.asarray(neighbor_m, dtype=np.float64)))
            - entropy(np.exp(np.asarray(neighbor_w, dtype=np.float64)))
        )
        w_norm = float(np.linalg.norm(np.asarray(msg_w, dtype=np.float64))) + 1e-8
        m_norm = float(np.linalg.norm(np.asarray(msg_m, dtype=np.float64))) + 1e-8
        weight = float(expit(w_norm / m_norm))
        total += h_change * weight
    return total


def compute_feature_b_from_entry(
    entry: dict[str, Any],
    mode: str = "historical_weighted",
) -> float:
    if mode == "manuscript_unweighted":
        return compute_feature_b_manuscript_unweighted(
            entry["w_n_log_prob"],
            entry["m_n_log_prob"],
        )
    if mode == "historical_weighted":
        return compute_feature_b_historical_weighted(
            entry["w_n_log_prob"],
            entry["m_n_log_prob"],
            entry["neighbor_w_message_vector_coming_from_center"],
            entry["neighbor_m_message_vector_coming_from_center"],
        )
    raise ValueError(f"Unknown Feature B mode {mode!r}")
