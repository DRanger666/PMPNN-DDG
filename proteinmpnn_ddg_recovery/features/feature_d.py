"""Feature D — neighbor embedding-change-norm summation (manuscript §3.2.3).

D = Σ_j ‖E_j^WT - E_j^MT‖
(= ``neighbor_embedding_change_m_w`` in V3 pickles).
"""

from __future__ import annotations

from typing import Any, Sequence

import numpy as np


def compute_feature_d(
    neighbor_w_embeddings: Sequence[Any],
    neighbor_m_embeddings: Sequence[Any],
    k: int = 15,
) -> float:
    total = 0.0
    for emb_w, emb_m in zip(neighbor_w_embeddings[:k], neighbor_m_embeddings[:k]):
        total += float(
            np.linalg.norm(
                np.asarray(emb_w, dtype=np.float64) - np.asarray(emb_m, dtype=np.float64)
            )
        )
    return total


def compute_feature_d_raw(
    neighbor_w_embeddings: Sequence[Any],
    neighbor_m_embeddings: Sequence[Any],
    k: int = 15,
) -> np.ndarray:
    """Per-neighbor raw difference vectors (WT - MT), shape (k, 128)."""

    rows = []
    for emb_w, emb_m in zip(neighbor_w_embeddings[:k], neighbor_m_embeddings[:k]):
        rows.append(
            np.asarray(emb_w, dtype=np.float64) - np.asarray(emb_m, dtype=np.float64)
        )
    return np.asarray(rows, dtype=np.float64)


def compute_feature_d_from_entry(entry: dict[str, Any]) -> float:
    return compute_feature_d(
        entry["neighbor_w_neighbor_embedding"],
        entry["neighbor_m_neighbor_embedding"],
    )
