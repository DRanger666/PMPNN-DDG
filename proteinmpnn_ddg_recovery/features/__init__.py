"""Per-feature PMPNN-DDG callables (manuscript A–H).

Each module exposes a clear ``compute_*`` function. Structural features A–E use
tensors from the clean modified ProteinMPNN extraction path. Evolutionary
features F–H use PSSM rows at the mutation position.
"""

from proteinmpnn_ddg_recovery.features.feature_a import compute_feature_a
from proteinmpnn_ddg_recovery.features.feature_b import (
    compute_feature_b_historical_weighted,
    compute_feature_b_manuscript_unweighted,
)
from proteinmpnn_ddg_recovery.features.feature_c import compute_feature_c
from proteinmpnn_ddg_recovery.features.feature_d import compute_feature_d
from proteinmpnn_ddg_recovery.features.feature_e import (
    build_message_change_matrix,
    project_feature_e,
)
from proteinmpnn_ddg_recovery.features.feature_fgh import compute_features_fgh

__all__ = [
    "compute_feature_a",
    "compute_feature_b_historical_weighted",
    "compute_feature_b_manuscript_unweighted",
    "compute_feature_c",
    "compute_feature_d",
    "build_message_change_matrix",
    "project_feature_e",
    "compute_features_fgh",
]

# RF dual-direction / F+R packing (neighbor-embedding ΔE vs message ΔM)
from proteinmpnn_ddg_recovery.features import rf_feature_matrix_packing

