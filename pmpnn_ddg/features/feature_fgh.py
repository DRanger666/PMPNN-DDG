"""Features F, G, H — PSSM evolutionary features (manuscript §3.4 family).

G = wild_pssm, H = alternate_pssm, F = G - H at the mutation sequence index.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pmpnn_ddg.engineered_features import (
    DEFAULT_SSYM_PSSM_DIR,
    pssm_features_for_mutation,
)


def compute_features_fgh(
    protein_key: str,
    mutation_label: str,
    sequence_index: int,
    pssm_dir: Path = DEFAULT_SSYM_PSSM_DIR,
) -> dict[str, float]:
    """Return ``{\"F\", \"G\", \"H\"}`` PSSM features for one mutation."""

    entry = {"mut": mutation_label}
    raw = pssm_features_for_mutation(protein_key, entry, sequence_index, pssm_dir)
    g = float(raw["wild_pssm"])
    h = float(raw["alternate_pssm"])
    return {"F": g - h, "G": g, "H": h}


def compute_features_fgh_from_entry(
    protein_key: str,
    entry: dict[str, Any],
    sequence_index: int,
    pssm_dir: Path = DEFAULT_SSYM_PSSM_DIR,
) -> dict[str, float]:
    return compute_features_fgh(
        protein_key,
        str(entry["mut"]),
        sequence_index,
        pssm_dir=pssm_dir,
    )
