#!/usr/bin/env python3
"""Build read-only inventory tables for the 2022 ProteinMPNN code evidence.

This deliberately avoids unpickling old result artifacts. Pickle files are
inventoried by path, size, mtime, and notebook mentions only.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


WORKSPACE = Path("/home/mpr/github_account_history_porting_2022_continuation")
SOURCE_REPO = WORKSPACE / "source_repos/SajidAhmeduiu_ProteinMPNN"
SAJID_ADDITIONS = SOURCE_REPO / "Sajid_Additions"
DRIVE_ROOT = WORKSPACE / "drive_evidence_copy/sajidahmedprotres_drive/Protein_MPNN_Digging"
DRIVE_REPO = DRIVE_ROOT / "ProteinMPNN"
OUT = WORKSPACE / "code_inventory_analysis"

DATASET_RE = re.compile(r"(?<![A-Za-z0-9])(?:S_2648|S_669|S_921|Ssym)(?![A-Za-z0-9])")
ARTIFACT_RE = re.compile(
    r"(?P<artifact>[\w./~$:{}\\ -]+?"
    r"(?:\.pickle|\.pkl|\.xlsx|\.png|\.txt|\.csv|\.pdb|\.jsonl|\.npz|\.pt))"
)
PATH_RE = re.compile(r"(?:/content/drive/MyDrive|/home/mpr|ACCRE_PyRun_Setup)[^\s'\",)\\]*")
IMPORT_RE = re.compile(r"^\s*(?:import\s+[\w.]+|from\s+[\w.]+\s+import\s+.+)", re.M)
DEF_RE = re.compile(r"^\s*def\s+([A-Za-z_]\w*)\s*\(", re.M)
CLASS_RE = re.compile(r"^\s*class\s+([A-Za-z_]\w*)\s*[:(]", re.M)
TOKEN_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]{2,}")


@dataclass(frozen=True)
class RootSpec:
    label: str
    path: Path


ROOTS = [
    RootSpec("git_sajid_additions", SAJID_ADDITIONS),
    RootSpec("drive_evidence_root", DRIVE_ROOT),
    RootSpec("drive_nested_proteinmpnn", DRIVE_REPO),
]


def write_tsv(path: Path, rows: Iterable[dict], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def sha256_file(path: Path, limit_mb: int | None = None) -> str:
    if limit_mb is not None and path.stat().st_size > limit_mb * 1024 * 1024:
        return f"[skipped_gt_{limit_mb}MB]"
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def file_inventory() -> None:
    rows: list[dict] = []
    for spec in ROOTS:
        if not spec.path.exists():
            continue
        for path in sorted(spec.path.rglob("*")):
            if ".git" in path.parts:
                continue
            st = path.lstat()
            rows.append(
                {
                    "root": spec.label,
                    "relative_path": rel(path, spec.path),
                    "kind": "dir" if path.is_dir() else "file",
                    "extension": path.suffix.lower() if path.is_file() else "",
                    "size_bytes": st.st_size if path.is_file() else "",
                    "mtime_iso": iso_mtime(st.st_mtime),
                }
            )
    write_tsv(
        OUT / "file_inventory.tsv",
        rows,
        ["root", "relative_path", "kind", "extension", "size_bytes", "mtime_iso"],
    )


def iso_mtime(ts: float) -> str:
    import datetime as _dt

    return _dt.datetime.fromtimestamp(ts).isoformat(timespec="seconds")


def load_notebook(path: Path) -> tuple[str, list[dict]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    cells = data.get("cells", [])
    chunks: list[str] = []
    for cell in cells:
        source = cell.get("source", "")
        if isinstance(source, list):
            chunks.append("".join(source))
        else:
            chunks.append(str(source))
    return "\n".join(chunks), cells


def notebook_inventory() -> None:
    nb_paths = sorted(SAJID_ADDITIONS.glob("*.ipynb")) + sorted(DRIVE_REPO.rglob("*.ipynb"))
    rows: list[dict] = []
    mention_rows: list[dict] = []
    feature_rows: list[dict] = []
    for path in nb_paths:
        root_label = "git_sajid_additions" if SAJID_ADDITIONS in path.parents else "drive_nested_proteinmpnn"
        root_path = SAJID_ADDITIONS if root_label == "git_sajid_additions" else DRIVE_REPO
        try:
            source_text, cells = load_notebook(path)
        except Exception as exc:
            rows.append(
                {
                    "root": root_label,
                    "relative_path": rel(path, root_path),
                    "error": repr(exc),
                }
            )
            continue
        export_notebook_source(path, root_label, root_path, cells)
        code_cells = [c for c in cells if c.get("cell_type") == "code"]
        markdown_cells = [c for c in cells if c.get("cell_type") == "markdown"]
        output_cells = sum(1 for c in code_cells if c.get("outputs"))
        imports = sorted(set(m.group(0).strip() for m in IMPORT_RE.finditer(source_text)))
        defs = sorted(set(DEF_RE.findall(source_text)))
        classes = sorted(set(CLASS_RE.findall(source_text)))
        datasets = sorted(set(DATASET_RE.findall(source_text)))
        artifacts = sorted(set(clean_artifact(m.group("artifact")) for m in ARTIFACT_RE.finditer(source_text)))
        hard_paths = sorted(set(PATH_RE.findall(source_text)))
        source_hash = hashlib.sha256(source_text.encode("utf-8", "replace")).hexdigest()
        rows.append(
            {
                "root": root_label,
                "relative_path": rel(path, root_path),
                "size_bytes": path.stat().st_size,
                "mtime_iso": iso_mtime(path.stat().st_mtime),
                "cells": len(cells),
                "code_cells": len(code_cells),
                "markdown_cells": len(markdown_cells),
                "code_cells_with_outputs": output_cells,
                "source_sha256": source_hash,
                "datasets_mentioned": ",".join(datasets),
                "artifact_mentions_count": len(artifacts),
                "hardcoded_paths_count": len(hard_paths),
                "imports": " | ".join(imports[:30]),
                "defs": ",".join(defs[:50]),
                "classes": ",".join(classes[:50]),
                "error": "",
            }
        )
        for dataset in datasets:
            mention_rows.append(
                {
                    "notebook": rel(path, root_path),
                    "root": root_label,
                    "mention_type": "dataset",
                    "mention": dataset,
                }
            )
        for artifact in artifacts:
            mention_rows.append(
                {
                    "notebook": rel(path, root_path),
                    "root": root_label,
                    "mention_type": "artifact",
                    "mention": artifact,
                }
            )
        for hard_path in hard_paths:
            mention_rows.append(
                {
                    "notebook": rel(path, root_path),
                    "root": root_label,
                    "mention_type": "hardcoded_path",
                    "mention": hard_path,
                }
            )
        for cell_idx, cell in enumerate(cells):
            source = cell.get("source", "")
            text = "".join(source) if isinstance(source, list) else str(source)
            if re.search(r"feature|PCC|RMSE|RandomForest|ExtraTrees|GradientBoost|DDG|ddg", text, re.I):
                snippet = one_line(text)
                feature_rows.append(
                    {
                        "root": root_label,
                        "notebook": rel(path, root_path),
                        "cell_index": cell_idx,
                        "cell_type": cell.get("cell_type", ""),
                        "snippet": snippet[:1200],
                    }
                )
    write_tsv(
        OUT / "notebook_inventory.tsv",
        rows,
        [
            "root",
            "relative_path",
            "size_bytes",
            "mtime_iso",
            "cells",
            "code_cells",
            "markdown_cells",
            "code_cells_with_outputs",
            "source_sha256",
            "datasets_mentioned",
            "artifact_mentions_count",
            "hardcoded_paths_count",
            "imports",
            "defs",
            "classes",
            "error",
        ],
    )
    write_tsv(
        OUT / "notebook_mentions.tsv",
        mention_rows,
        ["root", "notebook", "mention_type", "mention"],
    )
    write_tsv(
        OUT / "notebook_feature_result_cells.tsv",
        feature_rows,
        ["root", "notebook", "cell_index", "cell_type", "snippet"],
    )
    notebook_similarity(nb_paths)


def export_notebook_source(path: Path, root_label: str, root_path: Path, cells: list[dict]) -> None:
    out_path = OUT / "notebook_sources" / root_label / f"{rel(path, root_path)}.py.txt"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as handle:
        handle.write(f"# Source export for {root_label}:{rel(path, root_path)}\n")
        handle.write("# Generated from notebook cell sources only; outputs are omitted.\n\n")
        for idx, cell in enumerate(cells):
            source = cell.get("source", "")
            text = "".join(source) if isinstance(source, list) else str(source)
            handle.write(f"\n# %% cell {idx} [{cell.get('cell_type', '')}]\n")
            handle.write(text)
            if text and not text.endswith("\n"):
                handle.write("\n")


def clean_artifact(text: str) -> str:
    text = text.strip().strip("'\"")
    text = text.replace("\\/", "/")
    text = re.sub(r"^[^A-Za-z0-9_./~$:{}/-]+", "", text)
    return text


def one_line(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def notebook_similarity(nb_paths: list[Path]) -> None:
    docs: list[tuple[str, str, set[str]]] = []
    for path in nb_paths:
        if not path.exists():
            continue
        root_label = "git_sajid_additions" if SAJID_ADDITIONS in path.parents else "drive_nested_proteinmpnn"
        root_path = SAJID_ADDITIONS if root_label == "git_sajid_additions" else DRIVE_REPO
        try:
            source_text, _ = load_notebook(path)
        except Exception:
            continue
        tokens = {t.lower() for t in TOKEN_RE.findall(source_text)}
        docs.append((root_label, rel(path, root_path), tokens))
    rows: list[dict] = []
    for i in range(len(docs)):
        root_a, path_a, tok_a = docs[i]
        for j in range(i + 1, len(docs)):
            root_b, path_b, tok_b = docs[j]
            if not tok_a or not tok_b:
                continue
            inter = len(tok_a & tok_b)
            union = len(tok_a | tok_b)
            smaller = min(len(tok_a), len(tok_b))
            rows.append(
                {
                    "root_a": root_a,
                    "path_a": path_a,
                    "root_b": root_b,
                    "path_b": path_b,
                    "jaccard": f"{inter / union:.4f}",
                    "containment_smaller": f"{inter / smaller:.4f}",
                    "shared_tokens": inter,
                    "tokens_a": len(tok_a),
                    "tokens_b": len(tok_b),
                }
            )
    rows.sort(key=lambda r: (float(r["containment_smaller"]), float(r["jaccard"])), reverse=True)
    write_tsv(
        OUT / "notebook_source_similarity.tsv",
        rows,
        [
            "root_a",
            "path_a",
            "root_b",
            "path_b",
            "jaccard",
            "containment_smaller",
            "shared_tokens",
            "tokens_a",
            "tokens_b",
        ],
    )


def git_files(repo: Path) -> list[str]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=repo,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return [line for line in result.stdout.splitlines() if line]


def tree_comparison() -> None:
    source_files = set(git_files(SOURCE_REPO))
    drive_files = set(git_files(DRIVE_REPO))
    rows: list[dict] = []
    for file in sorted(source_files | drive_files):
        in_source = file in source_files
        in_drive = file in drive_files
        source_path = SOURCE_REPO / file
        drive_path = DRIVE_REPO / file
        if in_source and in_drive:
            source_hash = sha256_file(source_path, limit_mb=200)
            drive_hash = sha256_file(drive_path, limit_mb=200)
            status = "same_hash" if source_hash == drive_hash else "different_hash"
        elif in_source:
            source_hash = sha256_file(source_path, limit_mb=200)
            drive_hash = ""
            status = "source_only"
        else:
            source_hash = ""
            drive_hash = sha256_file(drive_path, limit_mb=200)
            status = "drive_only"
        rows.append(
            {
                "relative_path": file,
                "status": status,
                "in_source_repo": in_source,
                "in_drive_nested_repo": in_drive,
                "source_size": source_path.stat().st_size if in_source else "",
                "drive_size": drive_path.stat().st_size if in_drive else "",
                "source_sha256": source_hash,
                "drive_sha256": drive_hash,
            }
        )
    write_tsv(
        OUT / "source_repo_vs_drive_nested_repo.tsv",
        rows,
        [
            "relative_path",
            "status",
            "in_source_repo",
            "in_drive_nested_repo",
            "source_size",
            "drive_size",
            "source_sha256",
            "drive_sha256",
        ],
    )


def drive_top_level_artifacts() -> None:
    rows: list[dict] = []
    for path in sorted(DRIVE_ROOT.iterdir()):
        if not path.is_file():
            continue
        rows.append(
            {
                "filename": path.name,
                "extension": path.suffix.lower(),
                "size_bytes": path.stat().st_size,
                "mtime_iso": iso_mtime(path.stat().st_mtime),
                "dataset_hint": ",".join(sorted(set(DATASET_RE.findall(path.name)))),
                "role_hint": role_hint(path.name),
                "sha256": sha256_file(path, limit_mb=20),
            }
        )
    write_tsv(
        OUT / "drive_top_level_artifacts.tsv",
        rows,
        ["filename", "extension", "size_bytes", "mtime_iso", "dataset_hint", "role_hint", "sha256"],
    )


def role_hint(name: str) -> str:
    lower = name.lower()
    if "pmppn_info" in lower or "mpnn_info" in lower:
        return "ProteinMPNN intermediate info dict"
    if "full_feature" in lower:
        return "assembled feature dict"
    if "feature_combo_model" in lower:
        return "trained feature-combination models"
    if "feature_combo_result" in lower:
        return "feature-combination result summary"
    if "incremental_feature" in lower:
        return "incremental-feature result summary"
    if lower.endswith(".xlsx"):
        return "spreadsheet data"
    if lower.endswith(".png"):
        return "figure/image output"
    if lower == "res_dict.pickle":
        return "early result dict"
    return ""


def git_history() -> None:
    rows: list[dict] = []
    files = sorted(git_files(SOURCE_REPO))
    for file in files:
        if not file.startswith("Sajid_Additions/"):
            continue
        result = subprocess.run(
            ["git", "log", "--follow", "--format=%H%x09%ad%x09%an%x09%ae%x09%s", "--date=iso-strict", "--", file],
            cwd=SOURCE_REPO,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        for line in result.stdout.splitlines():
            parts = line.split("\t", 4)
            if len(parts) != 5:
                continue
            commit, date, author, email, subject = parts
            rows.append(
                {
                    "relative_path": file,
                    "commit": commit,
                    "date": date,
                    "author": author,
                    "email": email,
                    "subject": subject,
                }
            )
    write_tsv(
        OUT / "git_sajid_additions_file_history.tsv",
        rows,
        ["relative_path", "commit", "date", "author", "email", "subject"],
    )


def drive_repo_state() -> None:
    rows: list[dict] = []
    for label, repo in [("source_repo", SOURCE_REPO), ("drive_nested_repo", DRIVE_REPO)]:
        for args, key in [
            (["rev-parse", "HEAD"], "head"),
            (["status", "--short"], "status_short"),
            (["remote", "-v"], "remote_v"),
            (["log", "--oneline", "--decorate", "--max-count=12"], "recent_log"),
        ]:
            result = subprocess.run(
                ["git", *args],
                cwd=repo,
                check=True,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            rows.append({"repo": label, "field": key, "value": result.stdout.strip()})
    write_tsv(OUT / "git_repo_states.tsv", rows, ["repo", "field", "value"])


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    file_inventory()
    notebook_inventory()
    tree_comparison()
    drive_top_level_artifacts()
    git_history()
    drive_repo_state()


if __name__ == "__main__":
    main()
