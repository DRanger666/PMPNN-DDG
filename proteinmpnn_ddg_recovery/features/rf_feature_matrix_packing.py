"""RF feature-matrix packing: scalars + neighbor-embedding / message-change projections.

Manuscript objects (BioRxiv §§3.2.3–3.2.4)
------------------------------------------
* Neighbor embedding vectors ``E_j^{WT}``, ``E_j^{MT}``
  → Feature D = Σ_j ‖E_j^{WT} − E_j^{MT}‖₂
  → raw per-neighbor difference matrix also projected (PCA/KPCA) in the 2022
    notebook; those projection columns are **not** manuscript Feature E.
* Center→neighbor message vectors ``M_j^{WT}``, ``M_j^{MT}``
  → Feature E = Σ_j RBF_{1..5}(M_j^{WT} − M_j^{MT})  (RBF KernelPCA)
  → Feature C uses message-norm ratios of the same messages.

Why 71 columns then 41?
-----------------------
The Digging notebook built **one intermediate vector per mutation** that stored
*both* forward and reverse projection blocks side-by-side (71 floats), then
expanded each mutation into **two training rows** (forward ΔΔG and reverse
−ΔΔG), each keeping only one direction’s blocks (41 floats). That is packing /
F+R augmentation, not “71 manuscript features.”

Layout of the intermediate (71) vector after ``project_dual_direction_row``
--------------------------------------------------------------------------
 indices   width   contents
  0:11      11     scalar pack (see SCALAR_*)
 11:16       5     neighbor-embedding-change PCA  (forward, from ΔE)
 16:26      10     neighbor-embedding-change KPCA (forward)
 26:31       5     neighbor-embedding-change PCA  (reverse, from −ΔE)
 31:41      10     neighbor-embedding-change KPCA (reverse)
 41:46       5     center→neighbor message-change PCA  (forward, from ΔM)
 46:56      10     center→neighbor message-change KPCA (forward)  ← Feature E = [:5]
 56:61       5     center→neighbor message-change PCA  (reverse, from −ΔM)
 61:71      10     center→neighbor message-change KPCA (reverse)

Layout of one F+R-augmented (41) row
------------------------------------
 indices   width   contents
  0:11      11     scalars (reverse row remaps signs / swaps PSSM fields)
 11:16       5     neighbor-embedding-change PCA  (this direction)
 16:26      10     neighbor-embedding-change KPCA (this direction)
 26:31       5     message-change PCA             (this direction)
 31:41      10     message-change KPCA            (this direction)
                   → manuscript Feature E = columns 31:36 (first 5 of 10)

Legacy Digging field names often use ``m_w`` (= MT−WT ordering in the stored
difference). Feature D’s L2 sum is sign-invariant; KernelPCA component *signs*
are not — keep the stored orientation when fitting projections.
"""

from __future__ import annotations

from typing import Any, Sequence

import numpy as np
from sklearn.decomposition import KernelPCA, PCA
from sklearn.preprocessing import StandardScaler

# --- dimensions (notebook / Table-1 path) ---------------------------------
N_SCALARS = 11
NEIGHBOR_EMBEDDING_CHANGE_PCA_N = 5
NEIGHBOR_EMBEDDING_CHANGE_KPCA_N = 10  # reduced_dimension + 5
MESSAGE_CHANGE_PCA_N = 5
MESSAGE_CHANGE_KPCA_N = 10
FEATURE_E_N_COMPONENTS = 5  # first 5 of message-change KPCA

DUAL_DIRECTION_ROW_WIDTH = 71  # intermediate, both directions packed
AUGMENTED_ROW_WIDTH = 41  # one F or R training row

# Intermediate (71) slices — prefer these names over magic integers.
SLICE_SCALARS = slice(0, 11)
SLICE_NEIGHBOR_EMBEDDING_CHANGE_PCA_FWD = slice(11, 16)
SLICE_NEIGHBOR_EMBEDDING_CHANGE_KPCA_FWD = slice(16, 26)
SLICE_NEIGHBOR_EMBEDDING_CHANGE_PCA_REV = slice(26, 31)
SLICE_NEIGHBOR_EMBEDDING_CHANGE_KPCA_REV = slice(31, 41)
SLICE_MESSAGE_CHANGE_PCA_FWD = slice(41, 46)
SLICE_MESSAGE_CHANGE_KPCA_FWD = slice(46, 56)
SLICE_MESSAGE_CHANGE_PCA_REV = slice(56, 61)
SLICE_MESSAGE_CHANGE_KPCA_REV = slice(61, 71)

# Feature E on the *intermediate* 71-vector = first 5 of message-change KPCA fwd.
FEATURE_E_COLS_ON_DUAL_DIRECTION_ROW = (46, 47, 48, 49, 50)

# Feature E on an *augmented* 41-col forward/reverse row.
FEATURE_E_COLS_ON_AUGMENTED_ROW = (31, 32, 33, 34, 35)

# Scalar positions inside the 11-pack (Digging / VGRAPHS map).
SCALAR_INDEX = {
    "feature_A_center_log_prob_ratio": 0,  # center_mut_wild_energy
    "center_entropy": 1,
    "weighted_neighbor_energy_change": 2,
    "weighted_neighbor_forward_KL": 3,
    "weighted_neighbor_backward_KL": 4,
    "feature_F_pssm_wt_minus_mt": 5,
    "feature_B_entropy_change": 6,  # historical weighted or manuscript unweighted
    "feature_C_message_norm_ratio": 7,
    "feature_D_neighbor_embedding_change_norm": 8,
    "feature_G_pssm_wt": 9,
    "feature_H_pssm_mt": 10,
}

# Manuscript A–H → column index on the *augmented* 41-col matrix.
MANUSCRIPT_AH_TO_AUGMENTED_INDEX = {
    "A": 0,
    "B": 6,
    "C": 7,
    "D": 8,
    "E": list(FEATURE_E_COLS_ON_AUGMENTED_ROW),
    "F": 5,
    "G": 9,
    "H": 10,
}


def fit_neighbor_change_projections(
    neighbor_embedding_change_matrices: Sequence[np.ndarray],
    center_to_neighbor_message_change_matrices: Sequence[np.ndarray],
    kpca_sample_size: int,
    rng: np.random.Generator,
) -> dict[str, Any]:
    """Fit StandardScaler + PCA + RBF KernelPCA on S2648 neighbor-change rows.

    Parameters
    ----------
    neighbor_embedding_change_matrices
        Per-mutation arrays shaped (K, 128) — ΔE_j (stored Digging orientation).
    center_to_neighbor_message_change_matrices
        Per-mutation arrays shaped (K, 128) — ΔM_j (stored Digging orientation).
    """
    full_embedding = np.concatenate(
        [np.asarray(m, dtype=np.float64) for m in neighbor_embedding_change_matrices],
        axis=0,
    )
    full_message = np.concatenate(
        [
            np.asarray(m, dtype=np.float64)
            for m in center_to_neighbor_message_change_matrices
        ],
        axis=0,
    )

    def _fit_pair(full: np.ndarray) -> tuple[StandardScaler, PCA, KernelPCA]:
        n_sample = min(kpca_sample_size, full.shape[0])
        indices = rng.choice(full.shape[0], size=n_sample, replace=False)
        scaling = StandardScaler()
        scaling.fit(full)
        pca = PCA(n_components=NEIGHBOR_EMBEDDING_CHANGE_PCA_N)
        kpca = KernelPCA(
            n_components=NEIGHBOR_EMBEDDING_CHANGE_KPCA_N, kernel="rbf"
        )
        scaled_sample = scaling.transform(full[indices, :])
        pca.fit(scaled_sample)
        kpca.fit(scaled_sample)
        return scaling, pca, kpca

    emb_scaling, emb_pca, emb_kpca = _fit_pair(full_embedding)
    msg_scaling, msg_pca, msg_kpca = _fit_pair(full_message)
    return {
        "neighbor_embedding_change_scaler": emb_scaling,
        "neighbor_embedding_change_pca": emb_pca,
        "neighbor_embedding_change_kpca": emb_kpca,
        "message_change_scaler": msg_scaling,
        "message_change_pca": msg_pca,
        "message_change_kpca": msg_kpca,
        # legacy aliases (old train_eval keys)
        "e_scaling": emb_scaling,
        "e_pca": emb_pca,
        "e_kpca": emb_kpca,
        "m_scaling": msg_scaling,
        "m_pca": msg_pca,
        "m_kpca": msg_kpca,
        "full_neighbor_embedding_change_shape": list(full_embedding.shape),
        "full_message_change_shape": list(full_message.shape),
    }


def _sum_project(
    matrix: np.ndarray, scaler: StandardScaler, model: PCA | KernelPCA
) -> np.ndarray:
    return model.transform(scaler.transform(matrix)).sum(axis=0)


def project_dual_direction_row(
    scalars_11: Sequence[float],
    neighbor_embedding_change_matrix: np.ndarray,
    center_to_neighbor_message_change_matrix: np.ndarray,
    proj: dict[str, Any],
) -> list[float]:
    """Build the 71-float intermediate row (forward + reverse projection blocks)."""
    emb = np.asarray(neighbor_embedding_change_matrix, dtype=np.float64)
    msg = np.asarray(center_to_neighbor_message_change_matrix, dtype=np.float64)
    emb_rev = -1.0 * emb
    msg_rev = -1.0 * msg

    emb_s = proj["neighbor_embedding_change_scaler"]
    emb_pca = proj["neighbor_embedding_change_pca"]
    emb_kpca = proj["neighbor_embedding_change_kpca"]
    msg_s = proj["message_change_scaler"]
    msg_pca = proj["message_change_pca"]
    msg_kpca = proj["message_change_kpca"]

    flat: list[float] = [float(v) for v in scalars_11]
    assert len(flat) == N_SCALARS
    flat.extend(_sum_project(emb, emb_s, emb_pca).tolist())
    flat.extend(_sum_project(emb, emb_s, emb_kpca).tolist())
    flat.extend(_sum_project(emb_rev, emb_s, emb_pca).tolist())
    flat.extend(_sum_project(emb_rev, emb_s, emb_kpca).tolist())
    flat.extend(_sum_project(msg, msg_s, msg_pca).tolist())
    flat.extend(_sum_project(msg, msg_s, msg_kpca).tolist())
    flat.extend(_sum_project(msg_rev, msg_s, msg_pca).tolist())
    flat.extend(_sum_project(msg_rev, msg_s, msg_kpca).tolist())
    assert len(flat) == DUAL_DIRECTION_ROW_WIDTH
    return flat


def feature_E_from_dual_direction_row(row: Sequence[float]) -> np.ndarray:
    """Manuscript Feature E (5 comps) from a 71-col intermediate row."""
    return np.asarray(
        [row[i] for i in FEATURE_E_COLS_ON_DUAL_DIRECTION_ROW], dtype=np.float64
    )


def augment_forward_reverse(
    dual_direction_rows: np.ndarray, labels: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """Expand 71-col intermediate rows → interleaved F/R 41-col training matrix."""
    X_aug: list[np.ndarray] = []
    y_aug: list[float] = []
    for row, label in zip(dual_direction_rows, labels):
        forward = np.concatenate(
            [
                row[SLICE_SCALARS],
                row[SLICE_NEIGHBOR_EMBEDDING_CHANGE_PCA_FWD],
                row[SLICE_NEIGHBOR_EMBEDDING_CHANGE_KPCA_FWD],
                row[SLICE_MESSAGE_CHANGE_PCA_FWD],
                row[SLICE_MESSAGE_CHANGE_KPCA_FWD],
            ]
        )
        assert forward.shape[0] == AUGMENTED_ROW_WIDTH

        rev = np.zeros_like(forward)
        rev[0] = -1.0 * row[0]
        rev[1] = row[1]
        rev[2] = -1.0 * row[2]
        rev[3] = row[4]
        rev[4] = row[3]
        rev[5] = -1.0 * row[5]
        rev[6] = -1.0 * row[6]
        # Feature C reverse shortcut: 1/Σ_j r_j  (r_j = ‖M_j^WT‖/‖M_j^MT‖).
        # Algebraically exact reverse C would be Σ_j 1/r_j = Σ_j ‖M_j^MT‖/‖M_j^WT‖.
        # Notebook / Digging used the reciprocal-of-sum; we keep that for Table 1
        # fidelity (see MANUSCRIPT_TENSOR_EXTRACTION_FIDELITY Item H).
        denom = row[7]
        rev[7] = 1.0 / denom if abs(denom) > 1e-12 else 0.0
        rev[8] = row[8]
        rev[9] = row[10]
        rev[10] = row[9]
        rev[11:16] = row[SLICE_NEIGHBOR_EMBEDDING_CHANGE_PCA_REV]
        rev[16:26] = row[SLICE_NEIGHBOR_EMBEDDING_CHANGE_KPCA_REV]
        rev[26:31] = row[SLICE_MESSAGE_CHANGE_PCA_REV]
        rev[31:41] = row[SLICE_MESSAGE_CHANGE_KPCA_REV]

        X_aug.append(forward)
        X_aug.append(rev)
        y_aug.append(float(label))
        y_aug.append(-1.0 * float(label))
    return np.asarray(X_aug, dtype=np.float64), np.asarray(y_aug, dtype=np.float64)


def manuscript_combo_indices(combo: tuple[str, ...]) -> list[int]:
    idxs: list[int] = []
    for label in combo:
        mapped = MANUSCRIPT_AH_TO_AUGMENTED_INDEX[label]
        if isinstance(mapped, list):
            idxs.extend(mapped)
        else:
            idxs.append(mapped)
    return idxs
