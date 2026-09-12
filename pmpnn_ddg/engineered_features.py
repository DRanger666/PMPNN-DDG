"""Recovered ProteinMPNN-DDG V3 engineered-feature construction.

This module preserves the arithmetic from the V6_V2 notebooks after the direct
ProteinMPNN tensor fields have already been produced. It is not a cleaned-up
scientific redesign. The goal is value-level recovery of the saved V3 pickle
fields before any later refactor.

Primary source:
``colab_notebooks_inventory_analysis/git_notebook_sources/
Ssym_ProteinMPNNTesting_V6_V2.ipynb.py.txt``, especially the engineered-feature
cell after ``Ssym_pmppn_info_dict_V3.pickle`` and the following PSSM cell.
"""

from __future__ import annotations

from pathlib import Path
from string import ascii_uppercase
from typing import Any

import numpy as np
from scipy.special import expit, kl_div, softmax
from scipy.stats import entropy

from pmpnn_ddg.extraction import AA_TO_INDEX


WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SSYM_PSSM_DIR = (
    WORKSPACE_ROOT
    / "data"
    / "pdbs_pssm"
    / "Ssym_pssm_dir"
)

PSSM_AA_TO_INDEX = {
    "A": 0,
    "R": 1,
    "N": 2,
    "D": 3,
    "C": 4,
    "Q": 5,
    "E": 6,
    "G": 7,
    "H": 8,
    "I": 9,
    "L": 10,
    "K": 11,
    "M": 12,
    "F": 13,
    "P": 14,
    "S": 15,
    "T": 16,
    "W": 17,
    "Y": 18,
    "V": 19,
}

V3_ENGINEERED_TENSOR_FIELDS = [
    "center_mut_wild_energy",
    "center_mut_max_energy",
    "center_entropy",
    "weighted_neighbor_entropies",
    "weighted_neighbor_energy_changes",
    "backward_weighted_neighbor_energy_changes",
    "V2_backward_weighted_neighbor_energy_changes",
    "weighted_neighbor_forward_KL",
    "weighted_neighbor_backward_KL",
    "backward_weighted_neighbor_backward_KL",
    "V2_backward_weighted_neighbor_backward_KL",
    "weighted_neighbor_entropy_changes",
    "backward_weighted_neighbor_entropy_changes",
    "V2_backward_weighted_neighbor_entropy_changes",
    "center_neighbor_weight_check_m_w",
    "center_neighbor_weight_check_w_m",
    "neighbor_embedding_change_m_w",
    "neighbor_embedding_change_m_w_raw",
    "neighbor_message_change_m_w",
    "neighbor_message_change_m_w_raw",
    "unweighted_backward_KL",
    "unweighted_forward_KL",
]
V3_PSSM_FIELDS = ["wild_pssm", "alternate_pssm"]
V3_ENGINEERED_AND_PSSM_FIELDS = [
    *V3_ENGINEERED_TENSOR_FIELDS,
    *V3_PSSM_FIELDS,
]


def center_energy_features(entry: dict[str, Any], sequence_index: int) -> dict[str, Any]:
    """Recover the three center-position V3 scalar features."""

    mutation = str(entry["mut"])
    wild_aa = mutation[0]
    mutant_aa = mutation[-1]
    position_log_probabilities = entry["log_prob"][0, sequence_index, :]

    wild_log_probability = position_log_probabilities[AA_TO_INDEX[wild_aa]]
    mutant_log_probability = position_log_probabilities[AA_TO_INDEX[mutant_aa]]
    max_log_probability = position_log_probabilities.max()

    wild_energy = -1 * wild_log_probability
    mutant_energy = -1 * mutant_log_probability
    max_energy = -1 * max_log_probability

    return {
        "center_mut_wild_energy": mutant_energy - wild_energy,
        "center_mut_max_energy": mutant_energy - max_energy,
        "center_entropy": -1 * entropy(np.exp(position_log_probabilities)),
    }


def weighted_neighbor_entropies(entry: dict[str, Any]) -> Any:
    """Recover the weighted neighbor-position entropy feature."""

    neighbor_indices = entry["top_15_neighbor_indices"]
    neighbor_weights = entry["top_15_attention_weights"].reshape(-1, 1)
    neighbor_entropies = entropy(
        np.exp(entry["log_prob"][0, neighbor_indices, :]),
        axis=-1,
    ).reshape(-1, 1)
    return (neighbor_entropies * softmax(neighbor_weights)).sum()


def _neighbor_local_terms(entry: dict[str, Any]) -> dict[str, list[Any]]:
    """Recover per-neighbor local terms used by the V3 scalar/vector features."""

    local_neighbor_log_prob_vals = []
    local_neighbor_forward_kl_vals = []
    local_neighbor_backward_kl_vals = []
    local_neighbor_entropy_change_vals = []
    local_center_neighbor_weight_check_m_w = []
    local_center_neighbor_weight_check_w_m = []
    local_neighbor_embedding_changes = []
    local_neighbor_embedding_changes_raw = []
    local_neighbor_message_changes_raw = []
    local_center_neighbor_message_change_diff = []

    for (
        neighbor_w,
        neighbor_m,
        neighbor_aa,
        neighbor_w_message,
        neighbor_m_message,
        neighbor_w_embedding,
        neighbor_m_embedding,
    ) in zip(
        entry["w_n_log_prob"],
        entry["m_n_log_prob"],
        entry["neighbor_aa_identities"],
        entry["neighbor_w_message_vector_coming_from_center"],
        entry["neighbor_m_message_vector_coming_from_center"],
        entry["neighbor_w_neighbor_embedding"],
        entry["neighbor_m_neighbor_embedding"],
    ):
        neighbor_index = AA_TO_INDEX[neighbor_aa]
        local_neighbor_log_prob_vals.append(
            (-1 * neighbor_m[neighbor_index]) - (-1 * neighbor_w[neighbor_index])
        )
        local_neighbor_forward_kl_vals.append(
            kl_div(np.exp(neighbor_w), np.exp(neighbor_m)).sum()
        )
        local_neighbor_backward_kl_vals.append(
            kl_div(np.exp(neighbor_m), np.exp(neighbor_w)).sum()
        )
        local_neighbor_entropy_change_vals.append(
            entropy(np.exp(neighbor_m)) - entropy(np.exp(neighbor_w))
        )

        neighbor_w_message = neighbor_w_message.reshape((-1, 1))
        neighbor_m_message = neighbor_m_message.reshape((-1, 1))
        neighbor_w_message_norm = (
            np.linalg.norm(neighbor_w_message, ord=2, axis=0) + 0.00000001
        )
        neighbor_m_message_norm = (
            np.linalg.norm(neighbor_m_message, ord=2, axis=0) + 0.00000001
        )
        local_center_neighbor_weight_check_m_w.append(
            neighbor_m_message_norm / neighbor_w_message_norm
        )
        local_center_neighbor_weight_check_w_m.append(
            neighbor_w_message_norm / neighbor_m_message_norm
        )

        local_neighbor_embedding_changes.append(
            np.linalg.norm(neighbor_w_embedding - neighbor_m_embedding)
        )
        local_neighbor_embedding_changes_raw.append(
            neighbor_w_embedding - neighbor_m_embedding
        )
        local_neighbor_message_changes_raw.append(neighbor_w_message - neighbor_m_message)
        local_center_neighbor_message_change_diff.append(
            np.linalg.norm(neighbor_w_message - neighbor_m_message)
        )

    return {
        "neighbor_log_prob_vals": local_neighbor_log_prob_vals,
        "neighbor_forward_kl_vals": local_neighbor_forward_kl_vals,
        "neighbor_backward_kl_vals": local_neighbor_backward_kl_vals,
        "neighbor_entropy_change_vals": local_neighbor_entropy_change_vals,
        "center_neighbor_weight_check_m_w": local_center_neighbor_weight_check_m_w,
        "center_neighbor_weight_check_w_m": local_center_neighbor_weight_check_w_m,
        "neighbor_embedding_changes": local_neighbor_embedding_changes,
        "neighbor_embedding_changes_raw": local_neighbor_embedding_changes_raw,
        "neighbor_message_changes_raw": local_neighbor_message_changes_raw,
        "center_neighbor_message_change_diff": local_center_neighbor_message_change_diff,
    }


def neighbor_energy_kl_entropy_features(entry: dict[str, Any]) -> dict[str, Any]:
    """Recover the weighted neighbor energy, KL, and entropy-change features.

    The notebook stores message-norm ratios as one-element arrays. Multiplying a
    ``(15,)`` value array by a ``(15, 1)`` weight array broadcasts to ``(15,15)``.
    This function intentionally preserves that behavior because it matches the
    saved V3 pickle. Do not flatten the weight arrays during recovery.
    """

    terms = _neighbor_local_terms(entry)
    neighbor_weights = entry["top_15_attention_weights"].reshape(-1, 1)[0:15]
    neighbor_log_prob_vals = np.array(terms["neighbor_log_prob_vals"][0:15])
    neighbor_forward_kl_vals = np.array(terms["neighbor_forward_kl_vals"][0:15])
    neighbor_backward_kl_vals = np.array(terms["neighbor_backward_kl_vals"][0:15])
    neighbor_entropy_change_vals = np.array(
        terms["neighbor_entropy_change_vals"][0:15]
    )
    weight_check_m_w = np.array(terms["center_neighbor_weight_check_m_w"])[0:15]
    weight_check_w_m = np.array(terms["center_neighbor_weight_check_w_m"])[0:15]

    return {
        "weighted_neighbor_energy_changes": (
            neighbor_log_prob_vals * expit(neighbor_weights)
        ).sum(),
        "weighted_neighbor_forward_KL": (
            neighbor_forward_kl_vals * expit(neighbor_weights)
        ).sum(),
        "weighted_neighbor_backward_KL": (
            neighbor_backward_kl_vals * expit(neighbor_weights)
        ).sum(),
        "weighted_neighbor_entropy_changes": (
            neighbor_entropy_change_vals * expit(neighbor_weights)
        ).sum(),
        "backward_weighted_neighbor_energy_changes": (
            neighbor_log_prob_vals * expit(weight_check_m_w)
        ).sum(),
        "backward_weighted_neighbor_backward_KL": (
            neighbor_backward_kl_vals * expit(weight_check_m_w)
        ).sum(),
        "backward_weighted_neighbor_entropy_changes": (
            neighbor_entropy_change_vals * expit(weight_check_m_w)
        ).sum(),
        "center_neighbor_weight_check_m_w": np.array(weight_check_m_w).sum(),
        "center_neighbor_weight_check_w_m": np.array(weight_check_w_m).sum(),
        "V2_backward_weighted_neighbor_energy_changes": (
            neighbor_log_prob_vals * expit(weight_check_w_m)
        ).sum(),
        "V2_backward_weighted_neighbor_backward_KL": (
            neighbor_backward_kl_vals * expit(weight_check_w_m)
        ).sum(),
        "V2_backward_weighted_neighbor_entropy_changes": (
            neighbor_entropy_change_vals * expit(weight_check_w_m)
        ).sum(),
        "unweighted_backward_KL": np.array(terms["neighbor_backward_kl_vals"]).sum(),
        "unweighted_forward_KL": np.array(terms["neighbor_forward_kl_vals"]).sum(),
    }


def neighbor_embedding_message_features(entry: dict[str, Any]) -> dict[str, Any]:
    """Recover the V3 neighbor embedding-change and message-change features."""

    terms = _neighbor_local_terms(entry)
    return {
        "neighbor_embedding_change_m_w": np.array(
            terms["neighbor_embedding_changes"]
        ).sum(),
        "neighbor_embedding_change_m_w_raw": np.array(
            terms["neighbor_embedding_changes_raw"]
        ),
        "neighbor_message_change_m_w_raw": np.array(
            terms["neighbor_message_changes_raw"]
        ),
        "neighbor_message_change_m_w": np.array(
            terms["center_neighbor_message_change_diff"]
        ).sum(),
    }


def compute_v3_engineered_tensor_features(
    entry: dict[str, Any],
    sequence_index: int,
) -> dict[str, Any]:
    """Recover all non-PSSM engineered V3 fields for one mutation entry."""

    features = {}
    features.update(center_energy_features(entry, sequence_index))
    features["weighted_neighbor_entropies"] = weighted_neighbor_entropies(entry)
    features.update(neighbor_energy_kl_entropy_features(entry))
    features.update(neighbor_embedding_message_features(entry))
    return features


def convert_chain_from_alphabet_to_number(alphabet: str) -> str:
    """Notebook fallback for rare numeric-chain PSSM filenames."""

    mapping = {ch: idx + 1 for idx, ch in enumerate(ascii_uppercase)}
    return str(mapping[alphabet])


def pssm_file_path(
    pdb_id_plus_chain: str,
    pssm_dir: Path = DEFAULT_SSYM_PSSM_DIR,
    convert_upper: bool = False,
) -> Path:
    """Return the PSSM path using the V6/V6_V2 notebook filename fallback."""

    pssm_dir = Path(pssm_dir)
    first_name = (
        f"{pdb_id_plus_chain.upper()}.pssm"
        if convert_upper
        else f"{pdb_id_plus_chain}.pssm"
    )
    first_path = pssm_dir / first_name
    if first_path.exists():
        return first_path

    fallback_name = (
        f"{pdb_id_plus_chain[0:4].upper()}"
        f"{convert_chain_from_alphabet_to_number(pdb_id_plus_chain[4])}.pssm"
    )
    fallback_path = pssm_dir / fallback_name
    if fallback_path.exists():
        return fallback_path

    raise FileNotFoundError(
        f"No PSSM file for {pdb_id_plus_chain!r} in {pssm_dir}"
    )


def load_pssm_array(
    pdb_id_plus_chain: str,
    pssm_dir: Path = DEFAULT_SSYM_PSSM_DIR,
    convert_upper: bool = False,
) -> np.ndarray:
    """Load the notebook-style 20-column PSSM feature matrix."""

    path = pssm_file_path(pdb_id_plus_chain, pssm_dir, convert_upper=convert_upper)
    target_lines = [
        line.split()
        for line in path.read_text(encoding="utf-8").splitlines()
        if len(line.split()) == 44
    ]
    pssm_features = np.zeros((len(target_lines), 20))
    for index, line in enumerate(target_lines):
        pssm_features[index, :] = line[2:22]
    return pssm_features


def pssm_features_for_mutation(
    protein_key: str,
    entry: dict[str, Any],
    sequence_index: int,
    pssm_dir: Path = DEFAULT_SSYM_PSSM_DIR,
) -> dict[str, Any]:
    """Recover ``wild_pssm`` and ``alternate_pssm`` for one mutation entry."""

    mutation = str(entry["mut"])
    wild_aa = mutation[0]
    mutant_aa = mutation[-1]
    position_pssm = load_pssm_array(protein_key, pssm_dir)[sequence_index]
    return {
        "wild_pssm": position_pssm[PSSM_AA_TO_INDEX[wild_aa]],
        "alternate_pssm": position_pssm[PSSM_AA_TO_INDEX[mutant_aa]],
    }


def compute_v3_engineered_and_pssm_features(
    protein_key: str,
    entry: dict[str, Any],
    sequence_index: int,
    pssm_dir: Path = DEFAULT_SSYM_PSSM_DIR,
) -> dict[str, Any]:
    """Recover all engineered/PSSM V3 fields for one mutation entry."""

    features = compute_v3_engineered_tensor_features(entry, sequence_index)
    features.update(pssm_features_for_mutation(protein_key, entry, sequence_index, pssm_dir))
    return features
