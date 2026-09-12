"""Clean ProteinMPNN fork with PMPNN-DDG tensor-extraction hooks baked in."""

from __future__ import annotations

from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parent
UTILS_PATH = PACKAGE_ROOT / "protein_mpnn_utils.py"

__all__ = ["PACKAGE_ROOT", "UTILS_PATH"]
