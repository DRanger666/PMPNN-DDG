"""Recovered V6_V2 ProteinMPNN tensor-extraction behavior.

This module is intentionally narrow. It does not implement the full
ProteinMPNN-DDG V3 pickle pipeline. It only recovers the ProteinMPNN inference
changes used to expose tensors that later fed the V3 feature-construction code.

Evidence source:
``colab_notebooks_inventory_analysis/git_notebook_sources/*_ProteinMPNNTesting_V6_V2.ipynb.py.txt``

Design choice:
Default utils path is ``modified_proteinmpnn/protein_mpnn_utils.py`` — a clean
dauparas-based fork with the two V6_V2 extraction hooks baked in:

1. ``DecLayer.forward`` returns the scaled decoder message tensor.
2. ``ProteinMPNN.forward`` returns ``log_probs``, ``decoder_messages``, and
   final node embeddings ``h_V``.

If a vanilla (unpatched) utils path is supplied, the same hooks are applied via
``patch_utils_for_v6v2_tensor_returns`` for backward compatibility.
"""

from __future__ import annotations

import copy
import importlib.util
import types
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import torch
from Bio.Data.IUPACData import protein_letters_3to1
from Bio.PDB import PDBParser


WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
# Clean fork with baked-in DecLayer / forward extraction hooks.
# (Not the Digging nested annotated utils — those lack the V6_V2 returns.)
DEFAULT_UTILS_PATH = (
    WORKSPACE_ROOT / "modified_proteinmpnn" / "protein_mpnn_utils.py"
)
LEGACY_DIGGING_UTILS_PATH = (
    WORKSPACE_ROOT
    / "drive_evidence_copy"
    / "sajidahmedprotres_drive"
    / "Protein_MPNN_Digging"
    / "ProteinMPNN"
    / "vanilla_proteinmpnn"
    / "protein_mpnn_utils.py"
)
DEFAULT_CHECKPOINT_PATH = (
    WORKSPACE_ROOT
    / "reproduction_inputs"
    / "proteinmpnn_checkpoints"
    / "vanilla_model_weights"
    / "v_48_020.pt"
)
DEFAULT_SSYM_PDB_DIR = (
    WORKSPACE_ROOT
    / "drive_evidence_copy"
    / "sajidahmedprotres_drive"
    / "ACCRE_PyRun_Setup"
    / "Ssym_PDB_Files"
)

ALPHABET = "ACDEFGHIKLMNPQRSTVWYX"
AA_TO_INDEX = {aa: index for index, aa in enumerate(ALPHABET)}
V3_TENSOR_FIELDS = [
    "log_prob",
    "top_15_attention_weights",
    "top_10_attention_weights",
    "top_5_attention_weights",
    "top_15_neighbor_indices",
    "top_10_neighbor_indices",
    "top_5_neighbor_indices",
    "top_15_closest_neighbor_indices",
    "top_10_closest_neighbor_indices",
    "w_n_log_prob",
    "m_n_log_prob",
    "neighbor_aa_identities",
    "neighbor_w_message_vector_coming_from_center",
    "neighbor_m_message_vector_coming_from_center",
    "neighbor_w_neighbor_embedding",
    "neighbor_m_neighbor_embedding",
]


@dataclass(frozen=True)
class ProteinMPNNRuntime:
    """Loaded ProteinMPNN runtime with V6_V2 tensor-return patches applied."""

    utils: types.ModuleType
    model: torch.nn.Module
    checkpoint: dict[str, Any]
    device: torch.device
    utils_path: Path
    checkpoint_path: Path


@dataclass(frozen=True)
class FeaturizedInputs:
    """Subset of ``tied_featurize`` outputs used by V6_V2 tensor extraction."""

    X: torch.Tensor
    S: torch.Tensor
    mask: torch.Tensor
    chain_M: torch.Tensor
    chain_M_pos: torch.Tensor
    residue_idx: torch.Tensor
    chain_encoding_all: torch.Tensor


@dataclass(frozen=True)
class MutationTensorExtraction:
    """Recovered ProteinMPNN-derived V3 tensor fields for one mutation."""

    protein_key: str
    chain_id: str
    mutation_label: str
    sequence_index: int
    fields: dict[str, Any]


def load_proteinmpnn_utils(utils_path: Path = DEFAULT_UTILS_PATH) -> types.ModuleType:
    """Load the recovered ProteinMPNN utility source from a path."""

    utils_path = Path(utils_path)
    if not utils_path.exists():
        raise FileNotFoundError(f"ProteinMPNN utility source not found: {utils_path}")

    module_name = "proteinmpnn_ddg_recovery_recovered_v6v2_utils"
    spec = importlib.util.spec_from_file_location(module_name, utils_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not create import spec for {utils_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def patch_utils_for_v6v2_tensor_returns(utils: types.ModuleType) -> None:
    """Apply the V6_V2 tensor-return behavior to a loaded ProteinMPNN module."""

    def dec_layer_forward(self, h_V, h_E, mask_V=None, mask_attend=None):
        h_V_expand = h_V.unsqueeze(-2).expand(-1, -1, h_E.size(-2), -1)
        h_EV = torch.cat([h_V_expand, h_E], -1)

        h_message = self.W3(self.act(self.W2(self.act(self.W1(h_EV)))))
        if mask_attend is not None:
            h_message = mask_attend.unsqueeze(-1) * h_message
        dh = torch.sum(h_message, -2) / self.scale

        h_V = self.norm1(h_V + self.dropout1(dh))
        dh = self.dense(h_V)
        h_V = self.norm2(h_V + self.dropout2(dh))

        if mask_V is not None:
            h_V = mask_V.unsqueeze(-1) * h_V

        return h_V, (h_message / self.scale)

    def protein_mpnn_forward(
        self,
        X,
        S,
        mask,
        chain_M,
        residue_idx,
        chain_encoding_all,
        randn,
        use_input_decoding_order=False,
        decoding_order=None,
    ):
        device = X.device

        E, E_idx = self.features(X, mask, residue_idx, chain_encoding_all)
        h_V = torch.zeros((E.shape[0], E.shape[1], E.shape[-1]), device=E.device)
        h_E = self.W_e(E)

        mask_attend = utils.gather_nodes(mask.unsqueeze(-1), E_idx).squeeze(-1)
        mask_attend = mask.unsqueeze(-1) * mask_attend
        for layer in self.encoder_layers:
            h_V, h_E = layer(h_V, h_E, E_idx, mask, mask_attend)

        h_S = self.W_s(S)
        h_ES = utils.cat_neighbors_nodes(h_S, h_E, E_idx)
        h_EX_encoder = utils.cat_neighbors_nodes(torch.zeros_like(h_S), h_E, E_idx)
        h_EXV_encoder = utils.cat_neighbors_nodes(h_V, h_EX_encoder, E_idx)

        chain_M = chain_M * mask
        if not use_input_decoding_order:
            decoding_order = torch.argsort((chain_M + 0.0001) * (torch.abs(randn)))

        mask_size = E_idx.shape[1]
        permutation_matrix_reverse = torch.nn.functional.one_hot(
            decoding_order,
            num_classes=mask_size,
        ).float()
        order_mask_backward = torch.einsum(
            "ij, biq, bjp->bqp",
            (1 - torch.triu(torch.ones(mask_size, mask_size, device=device))),
            permutation_matrix_reverse,
            permutation_matrix_reverse,
        )
        mask_attend = torch.gather(order_mask_backward, 2, E_idx).unsqueeze(-1)
        mask_1D = mask.view([mask.size(0), mask.size(1), 1, 1])
        mask_bw = mask_1D * mask_attend
        mask_fw = mask_1D * (1.0 - mask_attend)

        h_EXV_encoder_fw = mask_fw * h_EXV_encoder
        decoder_messages = None
        for layer in self.decoder_layers:
            h_ESV = utils.cat_neighbors_nodes(h_V, h_ES, E_idx)
            h_ESV = mask_bw * h_ESV + h_EXV_encoder_fw
            h_V, decoder_messages = layer(h_V, h_ESV, mask)

        logits = self.W_out(h_V)
        log_probs = torch.nn.functional.log_softmax(logits, dim=-1)
        return log_probs, decoder_messages, h_V

    utils.DecLayer.forward = dec_layer_forward
    utils.ProteinMPNN.forward = protein_mpnn_forward


def load_runtime(
    utils_path: Path = DEFAULT_UTILS_PATH,
    checkpoint_path: Path = DEFAULT_CHECKPOINT_PATH,
    device: str | torch.device = "cpu",
) -> ProteinMPNNRuntime:
    """Load ProteinMPNN with the recovered V6_V2 tensor-return patch."""

    device = torch.device(device)
    utils = load_proteinmpnn_utils(utils_path)
    # Clean modified_proteinmpnn already returns messages; only patch vanilla.
    if getattr(utils, "PMPNN_DDG_EXTRACTION_HOOKS", False):
        pass  # clean modified_proteinmpnn (or previously patched)
    else:
        needs_patch = True
        try:
            import inspect

            src = inspect.getsource(utils.DecLayer.forward)
            if "h_message / self.scale" in src or "h_message/self.scale" in src:
                needs_patch = False
        except (OSError, TypeError):
            needs_patch = True
        if needs_patch:
            patch_utils_for_v6v2_tensor_returns(utils)
        utils.PMPNN_DDG_EXTRACTION_HOOKS = True

    checkpoint_path = Path(checkpoint_path)
    checkpoint = torch.load(checkpoint_path, map_location=device)
    model = utils.ProteinMPNN(
        num_letters=21,
        node_features=128,
        edge_features=128,
        hidden_dim=128,
        num_encoder_layers=3,
        num_decoder_layers=3,
        augment_eps=0.0,
        k_neighbors=checkpoint["num_edges"],
    )
    model.to(device)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    return ProteinMPNNRuntime(
        utils=utils,
        model=model,
        checkpoint=checkpoint,
        device=device,
        utils_path=Path(utils_path),
        checkpoint_path=checkpoint_path,
    )


def distance_func_local(
    X: torch.Tensor,
    mask: torch.Tensor,
    num_edges: int,
    eps: float = 1e-6,
) -> tuple[torch.Tensor, torch.Tensor]:
    """Notebook V6_V2 nearest-neighbor distance helper."""

    mask_2D = torch.unsqueeze(mask, 1) * torch.unsqueeze(mask, 2)
    dX = torch.unsqueeze(X, 1) - torch.unsqueeze(X, 2)
    D = mask_2D * torch.sqrt(torch.sum(dX**2, 3) + eps)
    D_max, _ = torch.max(D, -1, keepdim=True)
    D_adjust = D + (1.0 - mask_2D) * D_max
    top_k = min(int(num_edges), int(X.shape[1]))
    return torch.topk(D_adjust, top_k, dim=-1, largest=False)


def return_neighbor_info(
    X: torch.Tensor,
    mask: torch.Tensor,
    num_edges: int,
) -> tuple[torch.Tensor, torch.Tensor]:
    """Return nearest-neighbor distances and residue indices from CA atoms."""

    ca_coordinates = X[:, :, 1, :]
    return distance_func_local(ca_coordinates, mask, num_edges=num_edges)



def resolve_pdb_path(
    protein_key: str,
    pdb_dir: Path,
    fallback_dirs: list[Path] | None = None,
) -> Path:
    """Locate ``{protein_key}.pdb`` in ``pdb_dir`` or optional fallback dirs."""

    primary = Path(pdb_dir) / f"{protein_key}.pdb"
    if primary.exists():
        return primary
    for directory in fallback_dirs or []:
        if directory is None:
            continue
        candidate = Path(directory) / f"{protein_key}.pdb"
        if candidate.exists():
            return candidate
    raise FileNotFoundError(f"Missing PDB: {primary}")


def list_polymer_chain_ids(pdb_path: Path) -> list[str]:
    """Return Bio.PDB chain IDs that contain at least one standard polymer residue."""

    parser = PDBParser(QUIET=True)
    structure = parser.get_structure(id=Path(pdb_path).stem, file=str(pdb_path))
    model = structure[0]
    chain_ids: list[str] = []
    for chain in model:
        if any(residue.id[0] == " " for residue in chain):
            chain_ids.append(chain.id)
    return chain_ids


def alphabet_chain_to_numeric(chain_id: str) -> str | None:
    """Map A→1 … Z→26 (notebook PSSM fallback convention)."""

    if len(chain_id) == 1 and chain_id.isalpha():
        return str(ord(chain_id.upper()) - ord("A") + 1)
    return None


def resolve_pdb_chain_id(pdb_path: Path, requested_chain_id: str) -> tuple[str, str]:
    """Resolve the on-disk chain id for a protein_key chain suffix.

    Returns ``(parse_chain_id, logical_chain_id)``. ``logical_chain_id`` is always
    ``requested_chain_id`` (the protein_key suffix) so downstream dict keys stay
    stable. ``parse_chain_id`` is the chain letter/digit actually present in the
    PDB file.

    Resolution order:
    1. Exact match for ``requested_chain_id``
    2. Alphabet→number fallback (``A``→``1``) when that chain exists
    3. Sole polymer chain in the file (common for single-chain ACCRE extracts)
    """

    available = list_polymer_chain_ids(pdb_path)
    if not available:
        raise ValueError(f"No polymer chains found in {pdb_path}")
    if requested_chain_id in available:
        return requested_chain_id, requested_chain_id
    numeric = alphabet_chain_to_numeric(requested_chain_id)
    if numeric is not None and numeric in available:
        return numeric, requested_chain_id
    if len(available) == 1:
        return available[0], requested_chain_id
    raise KeyError(
        f"Chain {requested_chain_id!r} not in {pdb_path.name}; available={available}"
    )


def remap_protein_chain_keys(
    protein: dict[str, Any],
    from_chain_id: str,
    to_chain_id: str,
) -> dict[str, Any]:
    """Rename seq/coords keys from the parsed chain id to the logical chain id."""

    if from_chain_id == to_chain_id:
        return protein
    remapped = copy.deepcopy(protein)
    seq_from = f"seq_chain_{from_chain_id}"
    seq_to = f"seq_chain_{to_chain_id}"
    coords_from = f"coords_chain_{from_chain_id}"
    coords_to = f"coords_chain_{to_chain_id}"
    if seq_from not in remapped:
        raise KeyError(f"Missing {seq_from} while remapping to {to_chain_id}")
    remapped[seq_to] = remapped.pop(seq_from)
    coords = remapped.pop(coords_from)
    new_coords = {}
    for atom in ["N", "CA", "C", "O"]:
        old_key = f"{atom}_chain_{from_chain_id}"
        new_key = f"{atom}_chain_{to_chain_id}"
        new_coords[new_key] = coords[old_key]
    remapped[coords_to] = new_coords
    return remapped


def load_single_chain_protein(
    runtime: ProteinMPNNRuntime,
    pdb_path: Path,
    chain_id: str,
) -> dict[str, Any]:
    """Parse one PDB chain and apply the V6_V2 gap-removal step.

    ``chain_id`` is the logical id from ``protein_key[-1]``. If the PDB uses a
    different id (numeric chains, sole-chain extracts), the structure is parsed
    under the on-disk id and keys are remapped back to ``chain_id``.
    """

    parse_chain_id, logical_chain_id = resolve_pdb_chain_id(pdb_path, chain_id)
    pdb_dict_list = runtime.utils.parse_PDB(
        str(pdb_path), input_chain_list=[parse_chain_id]
    )
    if not pdb_dict_list:
        raise ValueError(f"No parseable chain {parse_chain_id!r} found in {pdb_path}")
    protein0 = pdb_dict_list[0]
    if int(protein0.get("num_of_chains", 0)) < 1 or not protein0.get(
        f"seq_chain_{parse_chain_id}", ""
    ):
        raise ValueError(
            f"parse_PDB returned empty chain {parse_chain_id!r} for {pdb_path}"
        )

    dataset = runtime.utils.StructureDatasetPDB(
        pdb_dict_list,
        truncate=None,
        max_length=20000,
    )
    if len(dataset) != 1:
        raise ValueError(f"Expected one parsed protein from {pdb_path}, found {len(dataset)}")

    protein = copy.deepcopy(dataset[0])
    protein = remap_protein_chain_keys(protein, parse_chain_id, logical_chain_id)
    return remove_gaps_from_single_chain_protein(protein, logical_chain_id)


def remove_gaps_from_single_chain_protein(
    protein: dict[str, Any],
    chain_id: str,
) -> dict[str, Any]:
    """Match the V6_V2 single-chain gap-removal step before featurization."""

    seq_chain_key = f"seq_chain_{chain_id}"
    coords_chain_key = f"coords_chain_{chain_id}"
    seq_chain = protein[seq_chain_key]
    keep_indices = [index for index, aa in enumerate(seq_chain) if aa != "-"]
    if len(keep_indices) == len(seq_chain):
        return protein

    coordinates = protein[coords_chain_key]
    for atom in ["N", "CA", "C", "O"]:
        key = f"{atom}_chain_{chain_id}"
        coordinates[key] = [coordinates[key][index] for index in keep_indices]

    protein[seq_chain_key] = "".join(seq_chain[index] for index in keep_indices)
    protein["seq"] = "".join(protein["seq"][index] for index in keep_indices)
    protein[coords_chain_key] = coordinates
    return protein


def build_residue_index_map(pdb_path: Path, chain_id: str) -> dict[str, int]:
    """Build residue-label → zero-based index map (PremPS / ICODE-aware).

    Labels match mutation-table prefixes (``mut[:-1]``):
    - blank ICODE → ``{AA}{seqnum}`` (e.g. ``M4``)
    - non-blank ICODE → ``{AA}{seqnum}{icode}`` (e.g. ``V27B`` for PremPS ``V27BL``)

    Polymer residues only (``hetflag == " "``), in Bio.PDB chain order, which
    matches ProteinMPNN ``parse_PDB`` sequence order after gap removal for the
    ACCRE single-chain extracts used here.

    ``chain_id`` is the logical protein_key suffix; on-disk chain ids are
    resolved via :func:`resolve_pdb_chain_id`.
    """

    parse_chain_id, _logical = resolve_pdb_chain_id(pdb_path, chain_id)
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure(id=Path(pdb_path).stem, file=str(pdb_path))
    model = structure[0]
    chain = model[parse_chain_id]

    mapping: dict[str, int] = {}
    duplicates: list[str] = []
    index = 0
    for residue in chain:
        hetflag, seqnum, icode = residue.get_id()
        if hetflag != " ":
            continue
        residue_name = residue.get_resname().title()
        one_letter = protein_letters_3to1.get(residue_name, "X")
        icode_s = icode.strip()
        key = f"{one_letter}{seqnum}{icode_s}" if icode_s else f"{one_letter}{seqnum}"
        if key in mapping:
            duplicates.append(key)
        else:
            mapping[key] = index
        index += 1
    if duplicates:
        raise ValueError(
            f"Duplicate residue labels in {pdb_path.name} chain {parse_chain_id}: {duplicates}"
        )
    return mapping


def fixed_positions_dict_for_one_designable_position(
    protein_name: str,
    chain_id: str,
    sequence_length: int,
    designable_zero_index: int,
) -> dict[str, dict[str, list[int]]]:
    """Create V6_V2-style fixed-position dictionary for one designable site."""

    designable_one_index = designable_zero_index + 1
    fixed_positions = [
        position
        for position in range(1, sequence_length + 1)
        if position != designable_one_index
    ]
    return {protein_name: {chain_id: fixed_positions}}


def featurize_for_one_designable_position(
    runtime: ProteinMPNNRuntime,
    protein: dict[str, Any],
    chain_id: str,
    designable_zero_index: int,
) -> FeaturizedInputs:
    """Run ``tied_featurize`` with exactly one designable chain position."""

    seq_chain = protein[f"seq_chain_{chain_id}"]
    fixed_positions_dict = fixed_positions_dict_for_one_designable_position(
        protein_name=protein["name"],
        chain_id=chain_id,
        sequence_length=len(seq_chain),
        designable_zero_index=designable_zero_index,
    )
    chain_id_dict = {protein["name"]: ([chain_id], [])}
    batch_clones = [copy.deepcopy(protein)]

    outputs = runtime.utils.tied_featurize(
        batch_clones,
        runtime.device,
        chain_id_dict,
        fixed_positions_dict,
        None,
        None,
        None,
        None,
    )
    (
        X,
        S,
        mask,
        _lengths,
        chain_M,
        chain_encoding_all,
        _chain_list_list,
        _visible_list_list,
        _masked_list_list,
        _masked_chain_length_list_list,
        chain_M_pos,
        _omit_AA_mask,
        residue_idx,
        *_unused,
    ) = outputs

    return FeaturizedInputs(
        X=X,
        S=S,
        mask=mask,
        chain_M=chain_M,
        chain_M_pos=chain_M_pos,
        residue_idx=residue_idx,
        chain_encoding_all=chain_encoding_all,
    )


def run_v6v2_forward(
    runtime: ProteinMPNNRuntime,
    featurized: FeaturizedInputs,
    alternate_aa: str | None = None,
    mutation_zero_index: int | None = None,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """Run the patched V6_V2 forward pass and return the three exposed tensors."""

    S = featurized.S.clone()
    if alternate_aa is not None:
        if mutation_zero_index is None:
            raise ValueError("mutation_zero_index is required when alternate_aa is set")
        S[0, mutation_zero_index] = AA_TO_INDEX[alternate_aa]

    randn = torch.randn(featurized.chain_M.shape, device=featurized.X.device)
    with torch.inference_mode():
        return runtime.model(
            featurized.X,
            S,
            featurized.mask,
            featurized.chain_M * featurized.chain_M_pos,
            featurized.residue_idx,
            featurized.chain_encoding_all,
            randn,
        )


def extract_mutation_tensor_fields(
    runtime: ProteinMPNNRuntime,
    protein: dict[str, Any],
    protein_key: str,
    mutation_label: str,
    sequence_index: int,
    neighbor_indices_override: list[int] | None = None,
) -> MutationTensorExtraction:
    """Recover V6_V2 ProteinMPNN-derived tensor fields for one mutation.

    Optional ``neighbor_indices_override`` replays a saved
    ``top_15_neighbor_indices`` list instead of ranking center-pass message
    norms. This is a diagnostic mode for V3 reconciliation, not a claim that
    historical extraction used an external neighbor list.
    """

    chain_id = protein_key[-1]
    alternate_aa = mutation_label[-1]
    seq_chain = protein[f"seq_chain_{chain_id}"]

    center_inputs = featurize_for_one_designable_position(
        runtime,
        protein,
        chain_id,
        sequence_index,
    )
    log_probs, decoder_messages, _node_embedding_info = run_v6v2_forward(
        runtime,
        center_inputs,
    )

    local_distances, local_neighbors = return_neighbor_info(
        center_inputs.X,
        center_inputs.mask,
        runtime.checkpoint["num_edges"],
    )
    message_norms = torch.linalg.vector_norm(
        decoder_messages[0, sequence_index, :, :],
        ord=2,
        dim=1,
    )

    top_15_attention_vals, top_15_local_indices = torch.topk(message_norms, k=15)
    top_10_attention_vals, top_10_local_indices = torch.topk(message_norms, k=10)
    top_5_attention_vals, top_5_local_indices = torch.topk(message_norms, k=5)

    top_15_neighbor_indices = local_neighbors[0, sequence_index, top_15_local_indices]
    top_10_neighbor_indices = local_neighbors[0, sequence_index, top_10_local_indices]
    top_5_neighbor_indices = local_neighbors[0, sequence_index, top_5_local_indices]
    top_15_closest_neighbor_indices = local_neighbors[0, sequence_index, 1:16]
    top_10_closest_neighbor_indices = local_neighbors[0, sequence_index, 1:11]

    if neighbor_indices_override is not None:
        if len(neighbor_indices_override) != 15:
            raise ValueError(
                f"neighbor_indices_override must have length 15, got {len(neighbor_indices_override)}"
            )
        override = torch.tensor(
            neighbor_indices_override,
            dtype=top_15_neighbor_indices.dtype,
            device=top_15_neighbor_indices.device,
        )
        top_15_neighbor_indices = override
        top_10_neighbor_indices = override[:10]
        top_5_neighbor_indices = override[:5]
        # Attention weights remain from the center-pass ranking; neighbor
        # identity fields are forced to the saved indices for downstream replay.

    fields: dict[str, Any] = {
        "log_prob": log_probs.cpu().numpy(),
        "top_15_attention_weights": top_15_attention_vals.cpu().numpy(),
        "top_10_attention_weights": top_10_attention_vals.cpu().numpy(),
        "top_5_attention_weights": top_5_attention_vals.cpu().numpy(),
        "top_15_neighbor_indices": top_15_neighbor_indices.cpu().numpy(),
        "top_10_neighbor_indices": top_10_neighbor_indices.cpu().numpy(),
        "top_5_neighbor_indices": top_5_neighbor_indices.cpu().numpy(),
        "top_15_closest_neighbor_indices": top_15_closest_neighbor_indices.cpu().numpy(),
        "top_10_closest_neighbor_indices": top_10_closest_neighbor_indices.cpu().numpy(),
    }

    neighbor_w_log_probs = []
    neighbor_m_log_probs = []
    neighbor_aa_identities = []
    neighbor_w_messages = []
    neighbor_m_messages = []
    neighbor_w_embeddings = []
    neighbor_m_embeddings = []

    for neighbor_index_value in fields["top_15_neighbor_indices"]:
        neighbor_index = int(neighbor_index_value)
        neighbor_aa_identities.append(seq_chain[neighbor_index])

        neighbor_inputs = featurize_for_one_designable_position(
            runtime,
            protein,
            chain_id,
            neighbor_index,
        )
        _neighbor_distances, neighbor_neighbors = return_neighbor_info(
            neighbor_inputs.X,
            neighbor_inputs.mask,
            runtime.checkpoint["num_edges"],
        )
        matches = (neighbor_neighbors[0, neighbor_index, :] == sequence_index).nonzero(
            as_tuple=False
        )
        center_neighbor_slot = int(matches[0][0].item()) if len(matches) == 1 else -1

        wild_log_probs, wild_messages, wild_embeddings = run_v6v2_forward(
            runtime,
            neighbor_inputs,
        )
        mutant_log_probs, mutant_messages, mutant_embeddings = run_v6v2_forward(
            runtime,
            neighbor_inputs,
            alternate_aa=alternate_aa,
            mutation_zero_index=sequence_index,
        )

        neighbor_w_log_probs.append(wild_log_probs[0, neighbor_index, :].cpu().numpy())
        neighbor_m_log_probs.append(mutant_log_probs[0, neighbor_index, :].cpu().numpy())
        neighbor_w_embeddings.append(wild_embeddings[0, neighbor_index, :].cpu().numpy())
        neighbor_m_embeddings.append(mutant_embeddings[0, neighbor_index, :].cpu().numpy())

        if center_neighbor_slot >= 0:
            neighbor_w_messages.append(
                wild_messages[0, neighbor_index, center_neighbor_slot, :].cpu().numpy()
            )
            neighbor_m_messages.append(
                mutant_messages[0, neighbor_index, center_neighbor_slot, :].cpu().numpy()
            )
        else:
            neighbor_w_messages.append(np.zeros(128))
            neighbor_m_messages.append(np.zeros(128))

    fields.update(
        {
            "w_n_log_prob": neighbor_w_log_probs,
            "m_n_log_prob": neighbor_m_log_probs,
            "neighbor_aa_identities": neighbor_aa_identities,
            "neighbor_w_message_vector_coming_from_center": neighbor_w_messages,
            "neighbor_m_message_vector_coming_from_center": neighbor_m_messages,
            "neighbor_w_neighbor_embedding": neighbor_w_embeddings,
            "neighbor_m_neighbor_embedding": neighbor_m_embeddings,
        }
    )

    return MutationTensorExtraction(
        protein_key=protein_key,
        chain_id=chain_id,
        mutation_label=mutation_label,
        sequence_index=sequence_index,
        fields=fields,
    )
