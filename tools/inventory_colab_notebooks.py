#!/usr/bin/env python3
"""Inventory copied 2022 Google Drive Colab notebooks.

This script reads notebook JSON and text metadata only. It does not execute
notebooks and does not unpickle old result artifacts.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


WORKSPACE = Path("/home/mpr/github_account_history_porting_2022_continuation")
COLAB_DIR = WORKSPACE / "drive_evidence_copy/sajidahmedprotres_drive/Colab Notebooks"
GIT_NOTEBOOK_DIR = WORKSPACE / "source_repos/SajidAhmeduiu_ProteinMPNN/Sajid_Additions"
DRIVE_DIGGING_ROOT = WORKSPACE / "drive_evidence_copy/sajidahmedprotres_drive/Protein_MPNN_Digging"
OUT = WORKSPACE / "colab_notebooks_inventory_analysis"

DATASET_RE = re.compile(
    r"(?<![A-Za-z0-9])(?:S_2648|S2648|S_669|S669|S_921|S921|Ssym|PREMPS|ProTherm|ThermoMutDB|FireProtDB)(?![A-Za-z0-9])",
    re.I,
)
ARTIFACT_RE = re.compile(
    r"(?P<artifact>[\w./~$:{}\\ ()-]+?"
    r"(?:\.pickle|\.pkl|\.xlsx|\.png|\.txt|\.csv|\.pdb|\.json|\.npz|\.pt|\.fa|\.fasta))"
)
PATH_RE = re.compile(r"(?:/content/drive/MyDrive|/content/|/home/mpr|ACCRE_PyRun_Setup)[^\s'\",)\\]*")
IMPORT_RE = re.compile(r"^\s*(?:import\s+[\w.]+|from\s+[\w.]+\s+import\s+.+)", re.M)
DEF_RE = re.compile(r"^\s*def\s+([A-Za-z_]\w*)\s*\(", re.M)
CLASS_RE = re.compile(r"^\s*class\s+([A-Za-z_]\w*)\s*[:(]", re.M)
TOKEN_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]{2,}")


@dataclass
class NotebookDoc:
    label: str
    path: Path
    rel_path: str
    valid: bool
    error: str
    cells: list[dict]
    source_text: str
    code_text: str
    output_text: str
    file_sha256: str
    source_sha256: str
    code_sha256: str
    tokens: set[str]


def write_tsv(path: Path, rows: Iterable[dict], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def iso_mtime(path: Path) -> str:
    import datetime as dt

    return dt.datetime.fromtimestamp(path.stat().st_mtime).isoformat(timespec="seconds")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", "replace")).hexdigest()


def read_source(cell: dict) -> str:
    source = cell.get("source", "")
    return "".join(source) if isinstance(source, list) else str(source)


def one_line(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def load_notebook(path: Path, label: str, root: Path) -> NotebookDoc:
    rel_path = path.relative_to(root).as_posix()
    file_hash = sha256_file(path)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        cells = data.get("cells", [])
        if not isinstance(cells, list):
            raise ValueError("notebook cells is not a list")
        source_chunks = [read_source(cell) for cell in cells]
        code_chunks = [read_source(cell) for cell in cells if cell.get("cell_type") == "code"]
        output_chunks: list[str] = []
        for cell in cells:
            for output in cell.get("outputs", []) or []:
                output_chunks.append(output_to_text(output))
        source_text = "\n".join(source_chunks)
        code_text = "\n".join(code_chunks)
        output_text = "\n".join(output_chunks)
        return NotebookDoc(
            label=label,
            path=path,
            rel_path=rel_path,
            valid=True,
            error="",
            cells=cells,
            source_text=source_text,
            code_text=code_text,
            output_text=output_text,
            file_sha256=file_hash,
            source_sha256=sha256_text(source_text),
            code_sha256=sha256_text(code_text),
            tokens={tok.lower() for tok in TOKEN_RE.findall(source_text)},
        )
    except Exception as exc:
        return NotebookDoc(
            label=label,
            path=path,
            rel_path=rel_path,
            valid=False,
            error=repr(exc),
            cells=[],
            source_text="",
            code_text="",
            output_text="",
            file_sha256=file_hash,
            source_sha256="",
            code_sha256="",
            tokens=set(),
        )


def output_to_text(output: dict) -> str:
    out_type = output.get("output_type", "")
    if out_type == "stream":
        text = output.get("text", "")
        return "".join(text) if isinstance(text, list) else str(text)
    if out_type == "error":
        traceback = output.get("traceback", [])
        return "\n".join([str(output.get("ename", "")), str(output.get("evalue", "")), *map(str, traceback)])
    data = output.get("data", {}) if isinstance(output.get("data", {}), dict) else {}
    chunks: list[str] = []
    for key in ["text/plain", "text/html", "text/markdown"]:
        if key in data:
            value = data[key]
            chunks.append("".join(value) if isinstance(value, list) else str(value))
    return "\n".join(chunks)


def output_mime_summary(output: dict) -> tuple[str, str, int]:
    out_type = output.get("output_type", "")
    data = output.get("data", {}) if isinstance(output.get("data", {}), dict) else {}
    mime_keys = ",".join(sorted(data.keys()))
    text = output_to_text(output)
    image_bytes = 0
    for key, value in data.items():
        if key.startswith("image/"):
            image_bytes += len("".join(value) if isinstance(value, list) else str(value))
    return out_type, mime_keys, image_bytes


def clean_artifact(text: str) -> str:
    text = text.strip().strip("'\"")
    text = text.replace("\\/", "/")
    text = re.sub(r"^[^A-Za-z0-9_./~$:{}/() -]+", "", text)
    return text


def classify_cell_for_artifact(cell_text: str, artifact: str) -> str:
    active_lines: list[str] = []
    commented_lines: list[str] = []
    for line in cell_text.splitlines():
        if line.lstrip().startswith("#"):
            commented_lines.append(line)
        else:
            active_lines.append(line)
    active_lower = "\n".join(active_lines).lower()
    commented_lower = "\n".join(commented_lines).lower()
    name = artifact.lower()
    producer_terms = [
        "pickle.dump",
        ".dump(",
        "to_pickle",
        "to_csv",
        "to_excel",
        "savefig",
        "\"wb\"",
        "'wb'",
        "\"w\"",
        "'w'",
    ]
    consumer_terms = [
        "pickle.load",
        "read_pickle",
        "read_csv",
        "read_excel",
        "open(",
        "\"rb\"",
        "'rb'",
        "plt.imread",
    ]

    def classify_text(lower: str, prefix: str = "") -> str:
        if name not in lower:
            return ""
        producer = any(term in lower for term in producer_terms)
        consumer = any(term in lower for term in consumer_terms)
        if producer and consumer:
            return f"{prefix}producer_or_consumer"
        if producer:
            return f"{prefix}producer"
        if consumer:
            return f"{prefix}consumer"
        return f"{prefix}mention"

    active_classification = classify_text(active_lower)
    if active_classification:
        return active_classification
    return classify_text(commented_lower, "commented_")


def export_source(doc: NotebookDoc, out_dir: str = "notebook_sources") -> None:
    if not doc.valid:
        return
    out_path = OUT / out_dir / f"{doc.rel_path}.py.txt"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as handle:
        handle.write(f"# Source export for {doc.label} notebook: {doc.rel_path}\n")
        handle.write("# Generated from notebook cell sources only; outputs are omitted.\n\n")
        for idx, cell in enumerate(doc.cells):
            text = read_source(cell)
            handle.write(f"\n# %% cell {idx} [{cell.get('cell_type', '')}]\n")
            handle.write(text)
            if text and not text.endswith("\n"):
                handle.write("\n")


def export_outputs(doc: NotebookDoc, out_dir: str = "notebook_outputs") -> None:
    if not doc.valid:
        return
    out_path = OUT / out_dir / f"{doc.rel_path}.outputs.txt"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as handle:
        handle.write(f"# Output export for {doc.label} notebook: {doc.rel_path}\n")
        handle.write("# Generated from notebook outputs; image payloads are summarized, not embedded.\n\n")
        for idx, cell in enumerate(doc.cells):
            outputs = cell.get("outputs", []) or []
            if not outputs:
                continue
            handle.write(f"\n# %% cell {idx} [{cell.get('cell_type', '')}] execution_count={cell.get('execution_count', '')}\n")
            for out_idx, output in enumerate(outputs):
                out_type, mime_keys, image_bytes = output_mime_summary(output)
                text = output_to_text(output)
                handle.write(
                    f"\n## output {out_idx} type={out_type} mime={mime_keys or '-'} image_data_chars={image_bytes}\n"
                )
                if image_bytes and not text:
                    handle.write("[image output omitted]\n")
                elif text:
                    handle.write(text)
                    if not text.endswith("\n"):
                        handle.write("\n")


def load_docs() -> tuple[list[NotebookDoc], list[NotebookDoc]]:
    colab_paths = sorted(p for p in COLAB_DIR.iterdir() if p.is_file())
    git_paths = sorted(GIT_NOTEBOOK_DIR.glob("*.ipynb")) if GIT_NOTEBOOK_DIR.exists() else []
    colab_docs = [load_notebook(path, "colab_drive_copy", COLAB_DIR) for path in colab_paths]
    git_docs = [load_notebook(path, "git_sajid_additions", GIT_NOTEBOOK_DIR) for path in git_paths]
    for doc in colab_docs:
        export_source(doc)
        export_outputs(doc)
    for doc in git_docs:
        export_source(doc, "git_notebook_sources")
        export_outputs(doc, "git_notebook_outputs")
    return colab_docs, git_docs


def notebook_inventory(docs: list[NotebookDoc], prefix: str = "colab") -> None:
    rows: list[dict] = []
    cell_rows: list[dict] = []
    output_rows: list[dict] = []
    feature_rows: list[dict] = []
    mention_rows: list[dict] = []
    for doc in docs:
        path = doc.path
        code_cells = [c for c in doc.cells if c.get("cell_type") == "code"]
        markdown_cells = [c for c in doc.cells if c.get("cell_type") == "markdown"]
        outputs = [out for cell in code_cells for out in (cell.get("outputs", []) or [])]
        output_cells = sum(1 for c in code_cells if c.get("outputs"))
        executed_cells = sum(1 for c in code_cells if c.get("execution_count") is not None)
        image_outputs = 0
        error_outputs = 0
        text_output_records = 0
        output_image_bytes = 0
        for cell_idx, cell in enumerate(doc.cells):
            for out_idx, output in enumerate(cell.get("outputs", []) or []):
                out_type, mime_keys, image_bytes = output_mime_summary(output)
                text = output_to_text(output)
                if image_bytes:
                    image_outputs += 1
                    output_image_bytes += image_bytes
                if out_type == "error":
                    error_outputs += 1
                if text:
                    text_output_records += 1
                output_rows.append(
                    {
                        "notebook": doc.rel_path,
                        "cell_index": cell_idx,
                        "execution_count": cell.get("execution_count", ""),
                        "output_index": out_idx,
                        "output_type": out_type,
                        "mime_keys": mime_keys,
                        "image_data_chars": image_bytes,
                        "text_snippet": one_line(text)[:1500],
                    }
                )
        datasets = sorted(set(DATASET_RE.findall(doc.source_text)))
        artifact_mentions = sorted(set(clean_artifact(m.group("artifact")) for m in ARTIFACT_RE.finditer(doc.source_text)))
        hard_paths = sorted(set(PATH_RE.findall(doc.source_text)))
        imports = sorted(set(m.group(0).strip() for m in IMPORT_RE.finditer(doc.source_text)))
        defs = sorted(set(DEF_RE.findall(doc.source_text)))
        classes = sorted(set(CLASS_RE.findall(doc.source_text)))
        rows.append(
            {
                "filename": path.name,
                "valid_notebook_json": doc.valid,
                "error": doc.error,
                "size_bytes": path.stat().st_size,
                "mtime_iso": iso_mtime(path),
                "cells": len(doc.cells),
                "code_cells": len(code_cells),
                "markdown_cells": len(markdown_cells),
                "executed_code_cells": executed_cells,
                "code_cells_with_outputs": output_cells,
                "output_records": len(outputs),
                "text_output_records": text_output_records,
                "image_output_records": image_outputs,
                "image_output_data_chars": output_image_bytes,
                "error_output_records": error_outputs,
                "file_sha256": doc.file_sha256,
                "source_sha256": doc.source_sha256,
                "code_sha256": doc.code_sha256,
                "datasets_mentioned": ",".join(datasets),
                "artifact_mentions_count": len(artifact_mentions),
                "hardcoded_paths_count": len(hard_paths),
                "pickle_load_count": doc.source_text.count("pickle.load"),
                "pickle_dump_count": doc.source_text.count("pickle.dump"),
                "savefig_count": doc.source_text.count("savefig"),
                "read_csv_count": doc.source_text.count("read_csv"),
                "read_excel_count": doc.source_text.count("read_excel"),
                "imports": " | ".join(imports[:40]),
                "defs": ",".join(defs[:80]),
                "classes": ",".join(classes[:80]),
            }
        )
        for dataset in datasets:
            mention_rows.append({"notebook": doc.rel_path, "mention_type": "dataset", "mention": dataset, "cell_index": ""})
        for artifact in artifact_mentions:
            mention_rows.append({"notebook": doc.rel_path, "mention_type": "artifact", "mention": artifact, "cell_index": ""})
        for hard_path in hard_paths:
            mention_rows.append({"notebook": doc.rel_path, "mention_type": "hardcoded_path", "mention": hard_path, "cell_index": ""})
        for idx, cell in enumerate(doc.cells):
            text = read_source(cell)
            cell_outputs = cell.get("outputs", []) or []
            cell_output_text = "\n".join(output_to_text(output) for output in cell_outputs)
            cell_image_outputs = 0
            cell_error_outputs = 0
            cell_image_chars = 0
            for output in cell_outputs:
                out_type, _, image_bytes = output_mime_summary(output)
                if image_bytes:
                    cell_image_outputs += 1
                    cell_image_chars += image_bytes
                if out_type == "error":
                    cell_error_outputs += 1
            cell_rows.append(
                {
                    "notebook": doc.rel_path,
                    "cell_index": idx,
                    "cell_type": cell.get("cell_type", ""),
                    "execution_count": cell.get("execution_count", ""),
                    "source_lines": len(text.splitlines()),
                    "source_chars": len(text),
                    "source_sha256": sha256_text(text),
                    "output_records": len(cell_outputs),
                    "text_output_chars": len(cell_output_text),
                    "image_output_records": cell_image_outputs,
                    "image_output_data_chars": cell_image_chars,
                    "error_output_records": cell_error_outputs,
                    "output_sha256": sha256_text(cell_output_text),
                    "source_snippet": one_line(text)[:1200],
                    "output_snippet": one_line(cell_output_text)[:1200],
                }
            )
            if re.search(r"feature|PCC|RMSE|RandomForest|ExtraTrees|GradientBoost|DDG|ddg|pickle|savefig|Table|Figure|corr", text, re.I):
                feature_rows.append(
                    {
                        "notebook": doc.rel_path,
                        "cell_index": idx,
                        "cell_type": cell.get("cell_type", ""),
                        "execution_count": cell.get("execution_count", ""),
                        "has_outputs": bool(cell.get("outputs")),
                        "snippet": one_line(text)[:1600],
                    }
                )
    write_tsv(
        OUT / f"{prefix}_notebook_inventory.tsv",
        rows,
        [
            "filename",
            "valid_notebook_json",
            "error",
            "size_bytes",
            "mtime_iso",
            "cells",
            "code_cells",
            "markdown_cells",
            "executed_code_cells",
            "code_cells_with_outputs",
            "output_records",
            "text_output_records",
            "image_output_records",
            "image_output_data_chars",
            "error_output_records",
            "file_sha256",
            "source_sha256",
            "code_sha256",
            "datasets_mentioned",
            "artifact_mentions_count",
            "hardcoded_paths_count",
            "pickle_load_count",
            "pickle_dump_count",
            "savefig_count",
            "read_csv_count",
            "read_excel_count",
            "imports",
            "defs",
            "classes",
        ],
    )
    write_tsv(
        OUT / f"{prefix}_notebook_cell_index.tsv",
        cell_rows,
        [
            "notebook",
            "cell_index",
            "cell_type",
            "execution_count",
            "source_lines",
            "source_chars",
            "source_sha256",
            "output_records",
            "text_output_chars",
            "image_output_records",
            "image_output_data_chars",
            "error_output_records",
            "output_sha256",
            "source_snippet",
            "output_snippet",
        ],
    )
    write_tsv(
        OUT / f"{prefix}_notebook_output_cells.tsv",
        output_rows,
        [
            "notebook",
            "cell_index",
            "execution_count",
            "output_index",
            "output_type",
            "mime_keys",
            "image_data_chars",
            "text_snippet",
        ],
    )
    write_tsv(
        OUT / f"{prefix}_notebook_feature_result_cells.tsv",
        feature_rows,
        ["notebook", "cell_index", "cell_type", "execution_count", "has_outputs", "snippet"],
    )
    write_tsv(
        OUT / f"{prefix}_notebook_mentions.tsv",
        mention_rows,
        ["notebook", "mention_type", "mention", "cell_index"],
    )


def compare_colab_to_git(colab_docs: list[NotebookDoc], git_docs: list[NotebookDoc]) -> None:
    git_by_name = {doc.path.name: doc for doc in git_docs}
    rows: list[dict] = []
    for doc in colab_docs:
        git_doc = git_by_name.get(doc.path.name)
        rows.append(
            {
                "filename": doc.path.name,
                "git_same_filename_exists": bool(git_doc),
                "file_sha256_equal": bool(git_doc and doc.file_sha256 == git_doc.file_sha256),
                "source_sha256_equal": bool(git_doc and doc.source_sha256 == git_doc.source_sha256),
                "code_sha256_equal": bool(git_doc and doc.code_sha256 == git_doc.code_sha256),
                "colab_size_bytes": doc.path.stat().st_size,
                "git_size_bytes": git_doc.path.stat().st_size if git_doc else "",
                "colab_mtime_iso": iso_mtime(doc.path),
                "colab_code_cells": sum(1 for c in doc.cells if c.get("cell_type") == "code"),
                "git_code_cells": sum(1 for c in git_doc.cells if c.get("cell_type") == "code") if git_doc else "",
                "colab_code_cells_with_outputs": sum(
                    1 for c in doc.cells if c.get("cell_type") == "code" and c.get("outputs")
                ),
                "git_code_cells_with_outputs": sum(
                    1 for c in git_doc.cells if c.get("cell_type") == "code" and c.get("outputs")
                )
                if git_doc
                else "",
                "colab_source_sha256": doc.source_sha256,
                "git_source_sha256": git_doc.source_sha256 if git_doc else "",
            }
        )
    for git_doc in git_docs:
        if git_doc.path.name not in {doc.path.name for doc in colab_docs}:
            rows.append(
                {
                    "filename": git_doc.path.name,
                    "git_same_filename_exists": True,
                    "file_sha256_equal": "",
                    "source_sha256_equal": "",
                    "code_sha256_equal": "",
                    "colab_size_bytes": "",
                    "git_size_bytes": git_doc.path.stat().st_size,
                    "colab_mtime_iso": "",
                    "colab_code_cells": "",
                    "git_code_cells": sum(1 for c in git_doc.cells if c.get("cell_type") == "code"),
                    "colab_code_cells_with_outputs": "",
                    "git_code_cells_with_outputs": sum(
                        1 for c in git_doc.cells if c.get("cell_type") == "code" and c.get("outputs")
                    ),
                    "colab_source_sha256": "",
                    "git_source_sha256": git_doc.source_sha256,
                }
            )
    write_tsv(
        OUT / "colab_vs_git_notebooks_by_filename.tsv",
        rows,
        [
            "filename",
            "git_same_filename_exists",
            "file_sha256_equal",
            "source_sha256_equal",
            "code_sha256_equal",
            "colab_size_bytes",
            "git_size_bytes",
            "colab_mtime_iso",
            "colab_code_cells",
            "git_code_cells",
            "colab_code_cells_with_outputs",
            "git_code_cells_with_outputs",
            "colab_source_sha256",
            "git_source_sha256",
        ],
    )
    similarity_rows: list[dict] = []
    for colab_doc in colab_docs:
        if not colab_doc.tokens:
            continue
        for git_doc in git_docs:
            if not git_doc.tokens:
                continue
            inter = len(colab_doc.tokens & git_doc.tokens)
            union = len(colab_doc.tokens | git_doc.tokens)
            smaller = min(len(colab_doc.tokens), len(git_doc.tokens))
            similarity_rows.append(
                {
                    "colab_notebook": colab_doc.rel_path,
                    "git_notebook": git_doc.rel_path,
                    "same_filename": colab_doc.path.name == git_doc.path.name,
                    "jaccard": f"{inter / union:.4f}",
                    "containment_smaller": f"{inter / smaller:.4f}",
                    "shared_tokens": inter,
                    "colab_tokens": len(colab_doc.tokens),
                    "git_tokens": len(git_doc.tokens),
                }
            )
    similarity_rows.sort(
        key=lambda row: (
            row["same_filename"],
            float(row["containment_smaller"]),
            float(row["jaccard"]),
        ),
        reverse=True,
    )
    write_tsv(
        OUT / "colab_vs_git_notebook_similarity.tsv",
        similarity_rows,
        [
            "colab_notebook",
            "git_notebook",
            "same_filename",
            "jaccard",
            "containment_smaller",
            "shared_tokens",
            "colab_tokens",
            "git_tokens",
        ],
    )


def colab_internal_similarity(colab_docs: list[NotebookDoc]) -> None:
    rows: list[dict] = []
    for i, doc_a in enumerate(colab_docs):
        if not doc_a.tokens:
            continue
        for doc_b in colab_docs[i + 1 :]:
            if not doc_b.tokens:
                continue
            inter = len(doc_a.tokens & doc_b.tokens)
            union = len(doc_a.tokens | doc_b.tokens)
            smaller = min(len(doc_a.tokens), len(doc_b.tokens))
            rows.append(
                {
                    "notebook_a": doc_a.rel_path,
                    "notebook_b": doc_b.rel_path,
                    "jaccard": f"{inter / union:.4f}",
                    "containment_smaller": f"{inter / smaller:.4f}",
                    "shared_tokens": inter,
                    "tokens_a": len(doc_a.tokens),
                    "tokens_b": len(doc_b.tokens),
                }
            )
    rows.sort(key=lambda row: (float(row["containment_smaller"]), float(row["jaccard"])), reverse=True)
    write_tsv(
        OUT / "colab_notebook_internal_similarity.tsv",
        rows,
        ["notebook_a", "notebook_b", "jaccard", "containment_smaller", "shared_tokens", "tokens_a", "tokens_b"],
    )


def artifact_mentions(docs: list[NotebookDoc], prefix: str = "colab") -> None:
    artifact_paths = sorted(path for path in DRIVE_DIGGING_ROOT.iterdir() if path.is_file()) if DRIVE_DIGGING_ROOT.exists() else []
    mention_rows: list[dict] = []
    artifact_rows: list[dict] = []
    for artifact_path in artifact_paths:
        name = artifact_path.name
        matches: list[str] = []
        producer_matches: list[str] = []
        consumer_matches: list[str] = []
        commented_matches: list[str] = []
        for doc in docs:
            if not doc.valid:
                continue
            for idx, cell in enumerate(doc.cells):
                text = read_source(cell)
                classification = classify_cell_for_artifact(text, name)
                if not classification:
                    continue
                row_key = f"{doc.rel_path}:cell{idx}:{classification}"
                matches.append(row_key)
                if classification.startswith("commented_"):
                    commented_matches.append(row_key)
                if classification in {"producer", "producer_or_consumer"}:
                    producer_matches.append(row_key)
                if classification in {"consumer", "producer_or_consumer"}:
                    consumer_matches.append(row_key)
                mention_rows.append(
                    {
                        "artifact": name,
                        "artifact_size_bytes": artifact_path.stat().st_size,
                        "artifact_mtime_iso": iso_mtime(artifact_path),
                        "notebook": doc.rel_path,
                        "cell_index": idx,
                        "classification": classification,
                        "cell_has_outputs": bool(cell.get("outputs")),
                        "execution_count": cell.get("execution_count", ""),
                        "snippet": one_line(text)[:1600],
                    }
                )
        artifact_rows.append(
            {
                "artifact": name,
                "artifact_size_bytes": artifact_path.stat().st_size,
                "artifact_mtime_iso": iso_mtime(artifact_path),
                f"mentioned_in_{prefix}_count": len(matches),
                "producer_candidate_count": len(producer_matches),
                "consumer_candidate_count": len(consumer_matches),
                "commented_candidate_count": len(commented_matches),
                "producer_candidates": " | ".join(producer_matches[:20]),
                "consumer_candidates": " | ".join(consumer_matches[:20]),
                "commented_candidates": " | ".join(commented_matches[:20]),
                "all_candidates": " | ".join(matches[:30]),
            }
        )
    write_tsv(
        OUT / f"protein_mpnn_digging_artifact_to_{prefix}_candidates.tsv",
        artifact_rows,
        [
            "artifact",
            "artifact_size_bytes",
            "artifact_mtime_iso",
            f"mentioned_in_{prefix}_count",
            "producer_candidate_count",
            "consumer_candidate_count",
            "commented_candidate_count",
            "producer_candidates",
            "consumer_candidates",
            "commented_candidates",
            "all_candidates",
        ],
    )
    write_tsv(
        OUT / f"{prefix}_artifact_mentions_by_cell.tsv",
        mention_rows,
        [
            "artifact",
            "artifact_size_bytes",
            "artifact_mtime_iso",
            "notebook",
            "cell_index",
            "classification",
            "cell_has_outputs",
            "execution_count",
            "snippet",
        ],
    )


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    colab_docs, git_docs = load_docs()
    notebook_inventory(colab_docs)
    notebook_inventory(git_docs, "git")
    compare_colab_to_git(colab_docs, git_docs)
    colab_internal_similarity(colab_docs)
    artifact_mentions(colab_docs)
    artifact_mentions(git_docs, "git")


if __name__ == "__main__":
    main()
