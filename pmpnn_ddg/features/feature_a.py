"""Feature A — mutation-position log-probability ratio (manuscript §3.3).

A = (-log P_MT) - (-log P_WT) at the masked center from the center pass,
i.e. mutant_energy - wild_energy using ProteinMPNN log_probs.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from pmpnn_ddg.alphabet import AA_TO_INDEX


def compute_feature_a(
    log_prob: np.ndarray,
    mutation_label: str,
    sequence_index: int,
) -> float:
    """Return Feature A (center_mut_wild_energy) for one mutation.

    Parameters
    ----------
    log_prob:
        Center-pass ``log_probs`` with shape ``(1, L, 21)`` (or ``(L, 21)``).
    mutation_label:
        e.g. ``C191Y`` (wild + PDB residue number + mutant).
    sequence_index:
        Zero-based sequence index of the mutation center.
    """

    wild_aa = mutation_label[0]
    mutant_aa = mutation_label[-1]
    probs = np.asarray(log_prob)
    if probs.ndim == 3:
        position = probs[0, sequence_index, :]
    elif probs.ndim == 2:
        position = probs[sequence_index, :]
    else:
        raise ValueError(f"log_prob must be 2D or 3D, got shape {probs.shape}")

    wild_energy = float(-position[AA_TO_INDEX[wild_aa]])
    mutant_energy = float(-position[AA_TO_INDEX[mutant_aa]])
    return mutant_energy - wild_energy


def compute_feature_a_from_entry(entry: dict[str, Any], sequence_index: int) -> float:
    """Convenience wrapper over a V3-shaped mutation entry."""

    return compute_feature_a(entry["log_prob"], str(entry["mut"]), sequence_index)
