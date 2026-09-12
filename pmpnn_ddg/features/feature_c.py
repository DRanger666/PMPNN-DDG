"""Feature C — center→neighbor message-norm-ratio summation (manuscript §3.2.2).

NR form used in final RF: Σ_j ‖M_j^WT‖ / ‖M_j^MT‖
(= ``center_neighbor_weight_check_w_m`` in V3 pickles).
"""

from __future__ import annotations

from typing import Any, Sequence

import numpy as np


def compute_feature_c(
    neighbor_w_messages: Sequence[Any],
    neighbor_m_messages: Sequence[Any],
    k: int = 15,
) -> float:
    total = 0.0
    for msg_w, msg_m in zip(neighbor_w_messages[:k], neighbor_m_messages[:k]):
        w_norm = float(np.linalg.norm(np.asarray(msg_w, dtype=np.float64))) + 1e-8
        m_norm = float(np.linalg.norm(np.asarray(msg_m, dtype=np.float64))) + 1e-8
        total += w_norm / m_norm
    return total


def compute_feature_c_from_entry(entry: dict[str, Any]) -> float:
    return compute_feature_c(
        entry["neighbor_w_message_vector_coming_from_center"],
        entry["neighbor_m_message_vector_coming_from_center"],
    )
