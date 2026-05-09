#!/usr/bin/env python3
"""Recover ProteinMPNN-DDG tensor-extraction codeblock evidence.

This script performs the Set 1 recovery pass described in
``manuscript_codebase_mapping/V3_PICKLE_REPRODUCTION_FROM_INPUTS_PLAN.md``.

It scans source text only. It does not execute notebooks, import ProteinMPNN,
load pickle files, or read the live Google Drive FUSE mount. The goal is to
identify where the old code exposed ProteinMPNN intermediate values that later
fed ProteinMPNN-DDG V3 pickle feature construction.
"""

from __future__ import annotations

import csv
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = (
    WORKSPACE_ROOT
    / "manuscript_codebase_mapping"
    / "tensor_extraction_codeblock_recovery"
)
TABLE_DIR = OUTPUT_DIR / "tables"

SOURCE_GROUPS = [
    (
        "git_exported_notebook_source",
        WORKSPACE_ROOT / "colab_notebooks_inventory_analysis" / "git_notebook_sources",
        "*.py.txt",
    ),
    (
        "drive_exported_notebook_source",
        WORKSPACE_ROOT / "colab_notebooks_inventory_analysis" / "notebook_sources",
        "*.py.txt",
    ),
    (
        "old_fork_python_source",
        WORKSPACE_ROOT / "source_repos" / "SajidAhmeduiu_ProteinMPNN",
        "*.py",
    ),
]

OLD_FORK_REPO = WORKSPACE_ROOT / "source_repos" / "SajidAhmeduiu_ProteinMPNN"
OLD_FORK_PROTEINMPNN_PATHS = [
    "vanilla_proteinmpnn/protein_mpnn_utils.py",
    "vanilla_proteinmpnn/protein_mpnn_run.py",
    "ca_proteinmpnn/protein_mpnn_utils.py",
    "ca_proteinmpnn/protein_mpnn_run.py",
]

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

PRIMARY_V6_V2_NOTEBOOKS = [
    "ProteinMPNNTesting_V6_V2.ipynb.py.txt",
    "S921_ProteinMPNNTesting_V6_V2.ipynb.py.txt",
    "S669_ProteinMPNNTesting_V6_V2.ipynb.py.txt",
    "Ssym_ProteinMPNNTesting_V6_V2.ipynb.py.txt",
]


@dataclass(frozen=True)
class CodePattern:
    evidence_kind: str
    symbol: str
    regex: re.Pattern[str]
    confidence: str
    note: str


CODE_PATTERNS = [
    CodePattern(
        evidence_kind="modified_declayer_message_return",
        symbol="decoder message tensor",
        regex=re.compile(r"return\s+h_V,\s*\(h_message\s*/\s*self\.scale\)"),
        confidence="direct",
        note="DecLayer.forward returns per-edge decoder messages together with updated node state.",
    ),
    CodePattern(
        evidence_kind="modified_forward_return_log_probs_messages_embeddings",
        symbol="log_probs, decoder_messages, h_V",
        regex=re.compile(r"return\s+log_probs,\s*decoder_messages,\s*h_V\b"),
        confidence="direct",
        note="ProteinMPNN.forward returns log probabilities, decoder messages, and final node embeddings.",
    ),
    CodePattern(
        evidence_kind="modified_forward_return_log_probs_messages_only",
        symbol="log_probs, decoder_messages",
        regex=re.compile(r"return\s+log_probs,\s*decoder_messages\b(?!\s*,)"),
        confidence="direct",
        note="Earlier notebook variant returns log probabilities and decoder messages, but not node embeddings.",
    ),
    CodePattern(
        evidence_kind="neighbor_index_function_definition",
        symbol="return_neighbor_info",
        regex=re.compile(r"^def\s+return_neighbor_info\s*\("),
        confidence="direct",
        note="Notebook-side helper exposes nearest-neighbor distances and residue indices from coordinates.",
    ),
    CodePattern(
        evidence_kind="neighbor_index_function_call",
        symbol="return_neighbor_info(X, mask)",
        regex=re.compile(r"return_neighbor_info\s*\(\s*X\s*,\s*mask\s*\)"),
        confidence="direct",
        note="Feature-generation code asks for local neighbor distances and indices for the current featurized structure.",
    ),
    CodePattern(
        evidence_kind="center_forward_tuple_unpack",
        symbol="mpnn_model forward tuple",
        regex=re.compile(
            r"log_probs,\s*decoder_messages,\s*node_embedding_info\s*=\s*mpnn_model\s*\("
        ),
        confidence="direct",
        note="Main center-position call consumes all three modified forward outputs.",
    ),
    CodePattern(
        evidence_kind="center_log_prob_storage",
        symbol='mut["log_prob"]',
        regex=re.compile(r'mut\["log_prob"\]\s*=\s*log_probs\.cpu\(\)\.data\.numpy\(\)'),
        confidence="direct",
        note="Center-position log probabilities are stored into the mutation dictionary.",
    ),
    CodePattern(
        evidence_kind="decoder_message_norm_for_neighbor_ranking",
        symbol="message_norms",
        regex=re.compile(r"torch\.linalg\.vector_norm\s*\(\s*decoder_messages"),
        confidence="direct",
        note="Decoder-message vectors from the mutated center are converted to norms for neighbor ranking.",
    ),
    CodePattern(
        evidence_kind="topk_message_neighbor_selection",
        symbol="torch.topk(message_norms)",
        regex=re.compile(r"torch\.topk\s*\(\s*message_norms"),
        confidence="direct",
        note="Highest-norm center-to-neighbor message edges are selected.",
    ),
    CodePattern(
        evidence_kind="center_sequence_mutation",
        symbol="S[0,seq_index]",
        regex=re.compile(r"S\[0,\s*seq_index\]\s*=\s*aa_1_N\[alternate_aa\]"),
        confidence="direct",
        note="The sequence tensor is edited at the center mutation before mutant neighbor tensors are extracted.",
    ),
    CodePattern(
        evidence_kind="neighbor_log_prob_tensor_access",
        symbol="mpnn_model(...)[0]",
        regex=re.compile(r"mpnn_model\s*\([^\n]*\)\[0\]\[0,\s*n_ind,\s*:\]"),
        confidence="direct",
        note="Neighbor residue log-probability vector is extracted from modified forward output index 0.",
    ),
    CodePattern(
        evidence_kind="neighbor_message_tensor_access",
        symbol="mpnn_model(...)[1]",
        regex=re.compile(
            r"mpnn_model\s*\([^\n]*\)\[1\]\[0,\s*n_ind,\s*neighbor_neighbor_index,\s*:\]"
        ),
        confidence="direct",
        note="Center-to-neighbor message vector is extracted from modified forward output index 1.",
    ),
    CodePattern(
        evidence_kind="neighbor_embedding_tensor_access",
        symbol="mpnn_model(...)[2]",
        regex=re.compile(r"mpnn_model\s*\([^\n]*\)\[2\]\[0,\s*n_ind,\s*:\]"),
        confidence="direct",
        note="Neighbor node embedding is extracted from modified forward output index 2.",
    ),
    CodePattern(
        evidence_kind="neighbor_identity_storage",
        symbol="neighbor_aa_identities",
        regex=re.compile(r'neighbor_aa_identities\.append\s*\(\s*seq_chain\[n_ind\]\s*\)'),
        confidence="direct",
        note="Neighbor amino-acid identity is taken from the sequence string by global neighbor index.",
    ),
    CodePattern(
        evidence_kind="v3_field_storage",
        symbol="V3 mutation-dictionary field",
        regex=re.compile(r'mut\["(?:' + "|".join(re.escape(f) for f in V3_TENSOR_FIELDS) + r')"\]\s*='),
        confidence="direct",
        note="One of the ProteinMPNN-derived V3 fields is stored in the mutation dictionary.",
    ),
]


FIELD_LOGIC = {
    "log_prob": (
        "log_probs returned by modified ProteinMPNN.forward",
        'mut["log_prob"] = log_probs.cpu().data.numpy()',
    ),
    "top_15_attention_weights": (
        "L2 norms of decoder_messages for the mutated center position",
        'mut["top_15_attention_weights"] = top_15_attention_weights.cpu().data.numpy()',
    ),
    "top_10_attention_weights": (
        "L2 norms of decoder_messages for the mutated center position",
        'mut["top_10_attention_weights"] = top_10_attention_weights.cpu().data.numpy()',
    ),
    "top_5_attention_weights": (
        "L2 norms of decoder_messages for the mutated center position",
        'mut["top_5_attention_weights"] = top_5_attention_weights.cpu().data.numpy()',
    ),
    "top_15_neighbor_indices": (
        "top message-norm local neighbor slots mapped through return_neighbor_info E_idx",
        'mut["top_15_neighbor_indices"] = top_15_attended_neighbor_indices.cpu().data.numpy()',
    ),
    "top_10_neighbor_indices": (
        "top message-norm local neighbor slots mapped through return_neighbor_info E_idx",
        'mut["top_10_neighbor_indices"] = top_10_attended_neighbor_indices.cpu().data.numpy()',
    ),
    "top_5_neighbor_indices": (
        "top message-norm local neighbor slots mapped through return_neighbor_info E_idx",
        'mut["top_5_neighbor_indices"] = top_5_attended_neighbor_indices.cpu().data.numpy()',
    ),
    "top_15_closest_neighbor_indices": (
        "nearest-neighbor residue indices returned by return_neighbor_info for the center residue",
        'mut["top_15_closest_neighbor_indices"] = local_neighbors[0,seq_index,1:16].cpu().data.numpy()',
    ),
    "top_10_closest_neighbor_indices": (
        "nearest-neighbor residue indices returned by return_neighbor_info for the center residue",
        'mut["top_10_closest_neighbor_indices"] = local_neighbors[0,seq_index,1:11].cpu().data.numpy()',
    ),
    "w_n_log_prob": (
        "neighbor log-probability vectors from modified forward output index 0 before center mutation",
        'mut["w_n_log_prob"] = neighbor_w_log_probs',
    ),
    "m_n_log_prob": (
        "neighbor log-probability vectors from modified forward output index 0 after center mutation",
        'mut["m_n_log_prob"] = neighbor_m_log_probs',
    ),
    "neighbor_aa_identities": (
        "sequence character at each selected neighbor index",
        'mut["neighbor_aa_identities"] = neighbor_aa_identities',
    ),
    "neighbor_w_message_vector_coming_from_center": (
        "center-to-neighbor decoder-message vector from modified forward output index 1 before center mutation",
        'mut["neighbor_w_message_vector_coming_from_center"] = neighbor_w_message_vector_coming_from_center',
    ),
    "neighbor_m_message_vector_coming_from_center": (
        "center-to-neighbor decoder-message vector from modified forward output index 1 after center mutation",
        'mut["neighbor_m_message_vector_coming_from_center"] = neighbor_m_message_vector_coming_from_center',
    ),
    "neighbor_w_neighbor_embedding": (
        "neighbor node embedding from modified forward output index 2 before center mutation",
        'mut["neighbor_w_neighbor_embedding"] = neighbor_w_embedding_info',
    ),
    "neighbor_m_neighbor_embedding": (
        "neighbor node embedding from modified forward output index 2 after center mutation",
        'mut["neighbor_m_neighbor_embedding"] = neighbor_m_embedding_info',
    ),
}


def ensure_dirs() -> None:
    TABLE_DIR.mkdir(parents=True, exist_ok=True)


def rel(path: Path) -> str:
    return str(path.relative_to(WORKSPACE_ROOT))


def write_tsv(path: Path, rows: Iterable[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            delimiter="\t",
            fieldnames=fieldnames,
            lineterminator="\n",
        )
        writer.writeheader()
        for row in rows:
            cleaned_row = {}
            for field in fieldnames:
                value = row.get(field, "NA")
                text = str(value).rstrip()
                cleaned_row[field] = text if text else "NA"
            writer.writerow(cleaned_row)


def source_files() -> list[tuple[str, Path]]:
    files: list[tuple[str, Path]] = []
    for group, root, glob_pattern in SOURCE_GROUPS:
        if not root.exists():
            continue
        for path in sorted(root.rglob(glob_pattern)):
            if ".ipynb_checkpoints" in path.parts:
                continue
            files.append((group, path))
    return files


def clean_snippet(lines: list[str], line_index: int, radius: int = 2) -> str:
    start = max(0, line_index - radius)
    end = min(len(lines), line_index + radius + 1)
    numbered = []
    for offset, line in enumerate(lines[start:end]):
        line_number = start + offset + 1
        content = line.rstrip()
        numbered.append(f"{line_number}: {content}" if content else f"{line_number}:")
    return "\\n".join(numbered)


def cell_for_line(lines: list[str], line_number: int) -> str:
    current = ""
    for index, line in enumerate(lines, start=1):
        if index > line_number:
            break
        if line.startswith("# %% cell "):
            current = line.strip("# ").strip()
    return current


def dataset_hint(path: Path) -> str:
    name = path.name
    if name.startswith("S921"):
        return "S_921"
    if name.startswith("S669"):
        return "S_669"
    if name.startswith("Ssym"):
        return "Ssym"
    if name.startswith("ProteinMPNNTesting"):
        return "S_2648_or_general_training_notebook"
    if name.startswith("Quick_Dirty"):
        return "RF_or_feature_consumer"
    return ""


def scan_codeblock_hits(files: list[tuple[str, Path]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for group, path in files:
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        lines = text.splitlines()
        for pattern in CODE_PATTERNS:
            for line_index, line in enumerate(lines):
                if not pattern.regex.search(line):
                    continue
                line_number = line_index + 1
                rows.append(
                    {
                        "source_group": group,
                        "source_file": rel(path),
                        "dataset_hint": dataset_hint(path),
                        "cell_marker": cell_for_line(lines, line_number),
                        "line_number": line_number,
                        "evidence_kind": pattern.evidence_kind,
                        "symbol": pattern.symbol,
                        "confidence": pattern.confidence,
                        "note": pattern.note,
                        "snippet": clean_snippet(lines, line_index),
                    }
                )
    return rows


def has_regex(text: str, pattern: str) -> bool:
    return re.search(pattern, text) is not None


def source_version_summary(files: list[tuple[str, Path]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    interesting_name = re.compile(
        r"(ProteinMPNNTesting|S921_ProteinMPNNTesting|S669_ProteinMPNNTesting|Ssym_ProteinMPNNTesting|protein_mpnn_utils|protein_mpnn_run)"
    )
    for group, path in files:
        if not interesting_name.search(path.name):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        field_count = sum(f'mut["{field}"]' in text for field in V3_TENSOR_FIELDS)
        has_v3_complete = all(f'mut["{field}"]' in text for field in V3_TENSOR_FIELDS)
        rows.append(
            {
                "source_group": group,
                "source_file": rel(path),
                "dataset_hint": dataset_hint(path),
                "has_modified_declayer_message_return": has_regex(
                    text, r"return\s+h_V,\s*\(h_message\s*/\s*self\.scale\)"
                ),
                "has_forward_return_log_probs_decoder_messages_h_v": has_regex(
                    text, r"return\s+log_probs,\s*decoder_messages,\s*h_V\b"
                ),
                "has_forward_return_log_probs_decoder_messages_only": has_regex(
                    text, r"return\s+log_probs,\s*decoder_messages\b(?!\s*,)"
                ),
                "has_return_neighbor_info_def": "def return_neighbor_info(" in text,
                "has_center_forward_tuple_unpack": (
                    "log_probs, decoder_messages, node_embedding_info = mpnn_model("
                    in text
                ),
                "has_decoder_message_topk": (
                    has_regex(text, r"torch\.linalg\.vector_norm\s*\([^\n]*decoder_messages")
                    and has_regex(text, r"torch\.topk\s*\(\s*message_norms")
                ),
                "has_neighbor_log_prob_fields": (
                    'mut["w_n_log_prob"]' in text and 'mut["m_n_log_prob"]' in text
                ),
                "has_neighbor_message_vector_fields": (
                    'mut["neighbor_w_message_vector_coming_from_center"]' in text
                    and 'mut["neighbor_m_message_vector_coming_from_center"]' in text
                ),
                "has_neighbor_embedding_fields": (
                    'mut["neighbor_w_neighbor_embedding"]' in text
                    and 'mut["neighbor_m_neighbor_embedding"]' in text
                ),
                "v3_tensor_field_assignment_count": field_count,
                "has_all_v3_tensor_field_assignments": has_v3_complete,
                "probable_role": probable_role(text, path),
            }
        )
    return rows


def probable_role(text: str, path: Path) -> str:
    if (
        "return log_probs, decoder_messages, h_V" in text
        and 'mut["neighbor_w_neighbor_embedding"]' in text
        and 'mut["neighbor_m_neighbor_embedding"]' in text
    ):
        return "primary V3 tensor-extraction candidate"
    if "return log_probs, decoder_messages" in text and 'mut["w_n_log_prob"]' in text:
        return "earlier message/log-probability extraction candidate"
    if path.name == "protein_mpnn_utils.py" and "def return_neighbor_info" in text:
        return "old fork source contains neighbor-info history, not complete V6_V2 tensor returns"
    if path.name.startswith("Quick_Dirty"):
        return "downstream RF or feature consumer"
    return ""


def first_line_refs_for_term(
    files: list[tuple[str, Path]],
    term: str,
    limit: int = 8,
    primary_only: bool = True,
) -> list[str]:
    refs: list[str] = []
    for group, path in files:
        if primary_only and (
            group != "git_exported_notebook_source"
            or path.name not in PRIMARY_V6_V2_NOTEBOOKS
        ):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if term not in text:
            continue
        for index, line in enumerate(text.splitlines(), start=1):
            if term in line:
                refs.append(f"{rel(path)}:{index}")
                break
        if len(refs) >= limit:
            break
    return refs


def field_to_extraction_rows(files: list[tuple[str, Path]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for field in V3_TENSOR_FIELDS:
        produced_from, storage_expression = FIELD_LOGIC[field]
        direct_storage_refs = first_line_refs_for_term(files, f'mut["{field}"]')
        status = "direct storage evidence in primary V6_V2 notebooks" if direct_storage_refs else "not found"
        rows.append(
            {
                "v3_pickle_field": field,
                "produced_from_code_value": produced_from,
                "storage_expression": storage_expression,
                "primary_evidence_refs": "; ".join(direct_storage_refs),
                "status": status,
            }
        )
    return rows


def old_fork_history_rows() -> list[dict[str, object]]:
    if not (OLD_FORK_REPO / ".git").exists():
        return []

    command = [
        "git",
        "-C",
        str(OLD_FORK_REPO),
        "log",
        "--format=%H%x09%h%x09%ad%x09%an%x09%ae%x09%s",
        "--date=iso-strict",
        "--",
        *OLD_FORK_PROTEINMPNN_PATHS,
    ]
    result = subprocess.run(command, check=False, text=True, capture_output=True)
    if result.returncode != 0:
        return [
            {
                "commit": "",
                "short_commit": "",
                "date": "",
                "author": "",
                "author_email": "",
                "subject": "",
                "note": result.stderr.strip(),
            }
        ]

    rows: list[dict[str, object]] = []
    for line in result.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) != 6:
            continue
        commit, short_commit, date, author, author_email, subject = parts
        note = ""
        if short_commit == "7dd03b9":
            note = (
                "Important clue: commit subject says neighbor extraction was added to "
                "ProteinFeatures, but V6_V2 tensor extraction uses notebook-side helpers "
                "and copied class definitions."
            )
        rows.append(
            {
                "commit": commit,
                "short_commit": short_commit,
                "date": date,
                "author": author,
                "author_email": author_email,
                "subject": subject,
                "note": note,
            }
        )
    return rows


def refs_for_pattern(
    hits: list[dict[str, object]],
    evidence_kind: str,
    dataset_filter: str | None = None,
    limit: int = 6,
) -> list[str]:
    refs: list[str] = []
    for hit in hits:
        if hit["evidence_kind"] != evidence_kind:
            continue
        if dataset_filter and hit["dataset_hint"] != dataset_filter:
            continue
        refs.append(f"{hit['source_file']}:{hit['line_number']}")
        if len(refs) >= limit:
            break
    return refs


def write_report(
    hits: list[dict[str, object]],
    version_rows: list[dict[str, object]],
    field_rows: list[dict[str, object]],
    history_rows: list[dict[str, object]],
) -> None:
    primary_rows = [
        row
        for row in version_rows
        if row["source_group"] == "git_exported_notebook_source"
        and Path(str(row["source_file"])).name in PRIMARY_V6_V2_NOTEBOOKS
    ]
    all_primary_have_v3 = all(row["has_all_v3_tensor_field_assignments"] for row in primary_rows)

    message_refs = refs_for_pattern(hits, "modified_declayer_message_return")
    forward_refs = refs_for_pattern(
        hits, "modified_forward_return_log_probs_messages_embeddings"
    )
    neighbor_refs = refs_for_pattern(hits, "neighbor_index_function_definition")
    topk_refs = refs_for_pattern(hits, "decoder_message_norm_for_neighbor_ranking")
    mutation_refs = refs_for_pattern(hits, "center_sequence_mutation")
    embedding_refs = refs_for_pattern(hits, "neighbor_embedding_tensor_access")
    source_history = next(
        (row for row in history_rows if row["short_commit"] == "7dd03b9"),
        None,
    )

    lines = [
        "# Tensor Extraction Codeblock Recovery",
        "",
        "Scope: Set 1 recovery for ProteinMPNN-DDG V3 pickle-level reproduction.",
        "This report identifies codeblocks that expose ProteinMPNN intermediate tensors.",
        "It does not cover the later engineered/PSSM feature-construction codeblocks.",
        "",
        "## Main Finding",
        "",
        "The strongest current evidence points to notebook-side copied ProteinMPNN",
        "class/function definitions as the effective tensor-extraction source for the",
        "V3 pickle generation notebooks. The checked-out old fork Python source is",
        "useful history, but it does not by itself contain the complete V6_V2 behavior.",
        "",
        f"Primary V6_V2 notebooks with all direct V3 tensor-field assignments: {all_primary_have_v3}.",
        "",
        "Primary candidate notebooks:",
        "",
    ]
    for row in primary_rows:
        lines.append(
            f"- `{row['source_file']}`: {row['probable_role']}; "
            f"field assignments={row['v3_tensor_field_assignment_count']}."
        )

    lines.extend(
        [
            "",
            "## Direct Answers",
            "",
            "Which files/cells modified or wrapped ProteinMPNN inference?",
            "",
            "- The V6_V2 notebook source exports redefine `DecLayer.forward` and",
            "  `ProteinMPNN.forward` in notebook code. These are copied definitions, not",
            "  just calls into the checked-out Python source.",
            "- Earlier V4/V5/V6 notebook variants expose decoder messages; V6_V2 adds",
            "  final node embeddings by returning `h_V` from `ProteinMPNN.forward`.",
            "",
            "Where were message tensors exposed?",
            "",
            f"- `DecLayer.forward` returns `h_message/self.scale`: {format_refs(message_refs)}.",
            f"- `ProteinMPNN.forward` returns `decoder_messages`: {format_refs(forward_refs)}.",
            "",
            "Where were neighbor embeddings exposed?",
            "",
            f"- V6_V2 returns `h_V`, and the neighbor loop reads `mpnn_model(...)[2][0,n_ind,:]`: {format_refs(embedding_refs)}.",
            "",
            "Where were neighbor indices and identities exposed?",
            "",
            f"- `return_neighbor_info(X, mask)` exposes nearest-neighbor residue indices: {format_refs(neighbor_refs)}.",
            "- Neighbor amino-acid identity is stored from `seq_chain[n_ind]`; see the",
            "  `neighbor_aa_identities` row in `tables/v3_field_to_tensor_extraction_evidence.tsv`.",
            "",
            "Where were wild-type vs mutant log-probabilities extracted?",
            "",
            "- The center-position log-probability tensor is stored in `mut[\"log_prob\"]`.",
            "- Neighbor wild-type and mutant log-probability vectors come from modified",
            "  forward output index 0 before and after `S[0,seq_index]` is edited.",
            f"- Center mutation assignment evidence: {format_refs(mutation_refs)}.",
            "",
            "Which exposed tensors correspond to each V3 pickle field?",
            "",
            "- See `tables/v3_field_to_tensor_extraction_evidence.tsv`.",
            "",
            "Were tensors produced by edited source files, monkeypatching, copied",
            "functions, or plain call-site extraction?",
            "",
            "- Current evidence: copied notebook-side class/function definitions plus",
            "  call-site extraction. The old fork Python source contains neighbor-info",
            "  history, but the complete V6_V2 three-output `ProteinMPNN.forward` is in",
            "  notebook source exports.",
            "",
            "## Old Fork History Clue",
            "",
        ]
    )
    if source_history:
        lines.extend(
            [
                f"- `{source_history['short_commit']}` `{source_history['subject']}`",
                f"  by {source_history['author']} <{source_history['author_email']}> on {source_history['date']}.",
                "- This supports the history of neighbor extraction work, but the direct",
                "  V3 tensor-extraction evidence is still the V6_V2 notebook source.",
            ]
        )
    else:
        lines.append("- No old-fork ProteinMPNN source history rows were recovered.")

    lines.extend(
        [
            "",
            "## Evidence Tables",
            "",
            "- `tables/tensor_extraction_codeblock_hits.tsv`: line-level hits for tensor",
            "  exposure, neighbor mapping, mutation editing, and V3 field storage.",
            "- `tables/tensor_extraction_source_versions.tsv`: source-file version summary",
            "  showing which notebooks contain message, embedding, and V3 storage code.",
            "- `tables/v3_field_to_tensor_extraction_evidence.tsv`: field-by-field mapping",
            "  from V3 pickle field to exposed tensor or direct code value.",
            "- `tables/old_fork_proteinmpnn_history.tsv`: commits touching old fork",
            "  ProteinMPNN source files.",
            "",
            "## Next Step",
            "",
            "Extract the V6_V2 tensor-extraction codeblocks into a small reproduction",
            "module without changing behavior, then test that module on Ssym first.",
            "Only after those exposed tensors are reproduced should the engineered/PSSM",
            "feature-construction codeblocks be stitched into the V3 pickle reproduction",
            "pipeline.",
            "",
        ]
    )

    (OUTPUT_DIR / "TENSOR_EXTRACTION_CODEBLOCK_RECOVERY.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )


def format_refs(refs: list[str]) -> str:
    if not refs:
        return "not found"
    return "; ".join(f"`{ref}`" for ref in refs[:6])


def main() -> None:
    ensure_dirs()
    files = source_files()
    hits = scan_codeblock_hits(files)
    version_rows = source_version_summary(files)
    field_rows = field_to_extraction_rows(files)
    history_rows = old_fork_history_rows()

    write_tsv(
        TABLE_DIR / "tensor_extraction_codeblock_hits.tsv",
        hits,
        [
            "source_group",
            "source_file",
            "dataset_hint",
            "cell_marker",
            "line_number",
            "evidence_kind",
            "symbol",
            "confidence",
            "note",
            "snippet",
        ],
    )
    write_tsv(
        TABLE_DIR / "tensor_extraction_source_versions.tsv",
        version_rows,
        [
            "source_group",
            "source_file",
            "dataset_hint",
            "has_modified_declayer_message_return",
            "has_forward_return_log_probs_decoder_messages_h_v",
            "has_forward_return_log_probs_decoder_messages_only",
            "has_return_neighbor_info_def",
            "has_center_forward_tuple_unpack",
            "has_decoder_message_topk",
            "has_neighbor_log_prob_fields",
            "has_neighbor_message_vector_fields",
            "has_neighbor_embedding_fields",
            "v3_tensor_field_assignment_count",
            "has_all_v3_tensor_field_assignments",
            "probable_role",
        ],
    )
    write_tsv(
        TABLE_DIR / "v3_field_to_tensor_extraction_evidence.tsv",
        field_rows,
        [
            "v3_pickle_field",
            "produced_from_code_value",
            "storage_expression",
            "primary_evidence_refs",
            "status",
        ],
    )
    write_tsv(
        TABLE_DIR / "old_fork_proteinmpnn_history.tsv",
        history_rows,
        [
            "commit",
            "short_commit",
            "date",
            "author",
            "author_email",
            "subject",
            "note",
        ],
    )
    write_report(hits, version_rows, field_rows, history_rows)

    print(f"Wrote {len(hits)} codeblock hits")
    print(f"Wrote {len(version_rows)} source-version rows")
    print(f"Wrote {len(field_rows)} V3 field mapping rows")
    print(f"Wrote {len(history_rows)} old-fork history rows")
    print(rel(OUTPUT_DIR / "TENSOR_EXTRACTION_CODEBLOCK_RECOVERY.md"))


if __name__ == "__main__":
    main()
