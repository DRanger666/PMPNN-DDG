"""Feature E — center→neighbor message-change Kernel-PCA projection (manuscript §3.2.4).

E is five scalars: for a fitted RBF KernelPCA (10 comps on S_2648 message-change
rows), sum the projected neighbor rows and take the first 5 components.

Fitting is dataset-level (train on S_2648); this module provides the per-mutation
message-change matrix and a project helper given a fitted KPCA + scaler.
"""

from __future__ import annotations

from typing import Any, Sequence

import numpy as np


def build_message_change_matrix(
    neighbor_w_messages: Sequence[Any],
    neighbor_m_messages: Sequence[Any],
    k: int = 15,
) -> np.ndarray:
    """Return (k, 128) matrix of (M_WT - M_MT) per neighbor (squeezed)."""

    rows = []
    for msg_w, msg_m in zip(neighbor_w_messages[:k], neighbor_m_messages[:k]):
        diff = np.asarray(msg_w, dtype=np.float64) - np.asarray(msg_m, dtype=np.float64)
        rows.append(np.asarray(diff).reshape(-1))
    return np.asarray(rows, dtype=np.float64)


def project_feature_e(
    message_change_matrix: np.ndarray,
    scaler: Any,
    kpca: Any,
    n_take: int = 5,
) -> np.ndarray:
    """Project neighbor message-change rows and sum → first ``n_take`` comps."""

    scaled = scaler.transform(message_change_matrix)
    projected = kpca.transform(scaled)
    summed = projected.sum(axis=0)
    return np.asarray(summed[:n_take], dtype=np.float64)


def build_message_change_matrix_from_entry(entry: dict[str, Any]) -> np.ndarray:
    return build_message_change_matrix(
        entry["neighbor_w_message_vector_coming_from_center"],
        entry["neighbor_m_message_vector_coming_from_center"],
    )
