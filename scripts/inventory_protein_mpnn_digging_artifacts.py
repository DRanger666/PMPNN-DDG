#!/usr/bin/env python3
"""Build a complete registry for the copied Protein_MPNN_Digging evidence tree.

The copied directory is historical evidence. This script treats it as read-only
and writes derived inventory tables under code_inventory_analysis/.

The output is meant to support storage decisions, dependency mapping, and the
ProteinMPNN checkpoint/source pinning question without relying on the current
state of the upstream ProteinMPNN repository.
"""

from __future__ import annotations

import csv
import hashlib
import os
import re
import subprocess
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


WORKSPACE = Path(__file__).resolve().parents[1]
EVIDENCE_ROOT = (
    WORKSPACE
    / "drive_evidence_copy"
    / "sajidahmedprotres_drive"
    / "Protein_MPNN_Digging"
)
NESTED_PROTEINMPNN = EVIDENCE_ROOT / "ProteinMPNN"
SOURCE_REPO = WORKSPACE / "source_repos" / "SajidAhmeduiu_ProteinMPNN"
OUTPUT_DIR = WORKSPACE / "code_inventory_analysis" / "protein_mpnn_digging_artifact_registry"

TEXT_SUFFIXES = {
    ".csv",
    ".ipynb",
    ".json",
    ".jsonl",
    ".md",
    ".py",
    ".sh",
    ".tsv",
    ".txt",
    ".yml",
    ".yaml",
}

COMMON_FALSE_POSITIVE_NAMES = {
    ".gitignore",
    "LICENSE",
    "README.md",
}

CHECKPOINT_TERMS = [
    "v_48_002",
    "v_48_010",
    "v_48_020",
    "v_48_030",
    "model_name",
    "checkpoint_path",
    "weights_path",
    "vanilla_model_weights",
    "ca_model_weights",
    "ProteinMPNN(",
    "protein_mpnn_utils",
]

SCAN_ROOTS = [
    WORKSPACE / "colab_notebooks_inventory_analysis" / "notebook_sources",
    WORKSPACE / "colab_notebooks_inventory_analysis" / "git_notebook_sources",
    WORKSPACE / "code_inventory_analysis" / "notebook_sources",
    WORKSPACE / "drive_evidence_copy" / "sajidahmedprotres_drive" / "Colab Notebooks",
    WORKSPACE / "manuscript_codebase_mapping",
    WORKSPACE / "pickle_analysis" / "README.md",
    WORKSPACE / "pickle_analysis" / "reports",
    WORKSPACE / "proteinmpnn_ddg_recovery",
    WORKSPACE / "reproduction_inputs",
    WORKSPACE / "scripts",
    WORKSPACE / "workspace_operations",
]


@dataclass(frozen=True)
class Artifact:
    rel_path: str
    abs_path: Path
    basename: str
    suffix: str
    size_bytes: int
    mtime_epoch: float
    mtime_utc: str
    sha256: str
    artifact_class: str
    dataset_hint: str
    role_hint: str
    storage_route: str
    storage_reason: str
    git_tracked_now: str


def write_tsv(path: Path, rows: Iterable[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fields,
            delimiter="\t",
            lineterminator="\n",
            extrasaction="ignore",
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def rel_workspace(path: Path) -> str:
    return path.relative_to(WORKSPACE).as_posix()


def rel_evidence(path: Path) -> str:
    return path.relative_to(EVIDENCE_ROOT).as_posix()


def iso_utc(ts: float) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def git_ls_files() -> set[str]:
    proc = subprocess.run(
        ["git", "ls-files"],
        cwd=WORKSPACE,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return set(proc.stdout.splitlines())


def dataset_hint(path: str) -> str:
    for name in ("S_2648", "S_921", "S_669", "Ssym"):
        if name in path:
            return name
    return ""


def classify_artifact(rel_path: str, suffix: str, size_bytes: int) -> tuple[str, str, str, str]:
    name = Path(rel_path).name
    in_nested = rel_path.startswith("ProteinMPNN/")
    in_nested_git = rel_path.startswith("ProteinMPNN/.git/")

    if in_nested_git:
        return (
            "nested_proteinmpnn_git_history",
            "Nested ProteinMPNN Git metadata preserved by the copied evidence tree.",
            "preserve_as_evidence_archive_not_regular_git",
            "Do not track a nested .git directory directly inside the workspace repo; preserve via bundle/archive or documented source commit.",
        )

    if suffix == ".pyc" or "__pycache__" in rel_path:
        return (
            "runtime_cache",
            "Python bytecode cache from historical/local execution.",
            "do_not_track",
            "Rebuildable runtime cache; not scientific or provenance evidence.",
        )

    if in_nested and suffix == ".pt":
        return (
            "proteinmpnn_checkpoint_weight",
            "ProteinMPNN model checkpoint weight file inside the copied nested source checkout.",
            "git_lfs_candidate_required_if_used",
            "Binary checkpoint is required if a historical run depends on this exact weight file; regular Git is not appropriate.",
        )

    if in_nested and suffix in {".py", ".sh", ".md", ".jsonl", ".json", ".npz", ".fa", ".pdb", ".sample", ".idx", ".out"}:
        return (
            "nested_proteinmpnn_source_or_example",
            "File from the copied nested ProteinMPNN checkout or its bundled examples.",
            "regular_git_or_source_snapshot_decision",
            "Source files may be tracked as a curated snapshot or represented by a pinned commit plus patch; examples/outputs need separate relevance checks.",
        )

    if suffix == ".ipynb":
        return (
            "notebook_artifact",
            "Notebook artifact inside Protein_MPNN_Digging.",
            "regular_git_if_provenance_relevant",
            "Notebook files are code/provenance evidence when they explain generation or analysis steps.",
        )

    if suffix == ".pt":
        return (
            "model_checkpoint_or_weight",
            "Binary model checkpoint or weight file.",
            "git_lfs_candidate_required_if_used",
            "Binary model weights should not be regular Git files; use LFS or an external release/artifact store if needed.",
        )

    if name.endswith("_pmppn_info_dict_V3.pickle"):
        return (
            "v3_pmpnn_info_pickle",
            "Final V3 ProteinMPNN-DDG intermediate dictionary used by final RF notebooks.",
            "git_lfs_candidate_required_for_recovery",
            "High-priority binary evidence for V3 pickle-level reproduction; too large for regular Git.",
        )

    if name.endswith("_pmppn_info_dict_V2.pickle"):
        return (
            "v2_pmpnn_info_pickle",
            "V2 ProteinMPNN-DDG intermediate dictionary from the feature-schema evolution trail.",
            "git_lfs_candidate_if_needed_for_lineage",
            "Binary lineage evidence; track only if needed for reproducibility/history comparison.",
        )

    if name.endswith("_pmppn_info_dict.pickle"):
        return (
            "base_pmpnn_info_pickle",
            "Early ProteinMPNN-DDG intermediate dictionary from the feature-schema evolution trail.",
            "git_lfs_candidate_if_needed_for_lineage",
            "Binary lineage evidence; track only if needed for reproducibility/history comparison.",
        )

    if name.endswith("_full_feature_dict.pickle"):
        return (
            "full_feature_pickle",
            "Assembled scalar feature dictionary.",
            "git_lfs_candidate_if_needed_for_scalar_feature_lineage",
            "Binary feature evidence; useful for validating scalar feature construction and schema evolution.",
        )

    if name in {"feature_combo_model_dict.pickle", "S_669_feature_combo_model_dict.pickle"}:
        return (
            "trained_feature_combo_model_pickle",
            "Saved trained feature-combination model dictionary from historical RF/ML experiments.",
            "git_lfs_candidate_after_deep_inspection",
            "Large trained-model artifact; inspect content before deciding whether it is indispensable or rerunnable.",
        )

    if name.endswith("_feature_combo_result_dict.pickle") or name in {
        "feature_combo_result_dict.pickle",
        "incremental_feature_result_dict.pickle",
        "list_incremental_feature_result_dict.pickle",
        "res_dict.pickle",
    }:
        return (
            "ml_result_summary_pickle",
            "Saved result-summary dictionary from historical ML experiments.",
            "git_lfs_candidate_if_needed_for_number_provenance",
            "Binary result evidence; may help tie manuscript numbers to saved outputs.",
        )

    if suffix == ".pickle":
        return (
            "other_pickle",
            "Pickle artifact requiring separate inspection.",
            "git_lfs_candidate_after_role_assignment",
            "Binary artifact; do not track blindly without dependency and role evidence.",
        )

    if suffix in {".xlsx", ".png", ".npz"}:
        return (
            "binary_analysis_artifact",
            "Binary analysis artifact, figure, spreadsheet, or array file.",
            "git_lfs_or_regular_git_case_by_case",
            "Small binary evidence can be tracked normally only when stable and useful; otherwise use LFS or regenerate.",
        )

    if suffix in {".py", ".sh", ".md", ".txt", ".csv"}:
        return (
            "small_text_or_source_artifact",
            "Small text/source artifact from the copied evidence tree.",
            "regular_git_candidate_if_relevant",
            "Text/source files are suitable for regular Git if they are real evidence rather than generated residue.",
        )

    if size_bytes > 100 * 1024 * 1024:
        return (
            "large_unknown_binary_or_data",
            "Large artifact that needs a specific role assignment.",
            "git_lfs_or_external_artifact_store_required",
            "Large files are not suitable for ordinary Git tracking.",
        )

    return (
        "uncategorized_small_artifact",
        "Small artifact requiring role assignment.",
        "decide_after_dependency_review",
        "Small size alone is not enough; track only if it supports evidence, reproducibility, or maintained code.",
    )


def collect_artifacts() -> list[Artifact]:
    if not EVIDENCE_ROOT.exists():
        raise FileNotFoundError(f"Missing evidence root: {EVIDENCE_ROOT}")

    tracked = git_ls_files()
    artifacts: list[Artifact] = []
    for path in sorted(EVIDENCE_ROOT.rglob("*")):
        if not path.is_file():
            continue
        st = path.stat()
        rel_path = rel_evidence(path)
        artifact_class, role_hint, storage_route, storage_reason = classify_artifact(
            rel_path, path.suffix.lower(), st.st_size
        )
        artifacts.append(
            Artifact(
                rel_path=rel_path,
                abs_path=path,
                basename=path.name,
                suffix=path.suffix.lower(),
                size_bytes=st.st_size,
                mtime_epoch=st.st_mtime,
                mtime_utc=iso_utc(st.st_mtime),
                sha256=sha256_file(path),
                artifact_class=artifact_class,
                dataset_hint=dataset_hint(rel_path),
                role_hint=role_hint,
                storage_route=storage_route,
                storage_reason=storage_reason,
                git_tracked_now="yes" if rel_workspace(path) in tracked else "no",
            )
        )
    return artifacts


def should_scan_text_file(path: Path) -> bool:
    if not path.is_file():
        return False
    if OUTPUT_DIR in path.parents:
        return False
    if EVIDENCE_ROOT in path.parents:
        return False
    if ".git" in path.parts:
        return False
    if ".venv" in "".join(path.parts):
        return False
    return path.suffix.lower() in TEXT_SUFFIXES


def source_group(path: Path) -> str:
    rel = rel_workspace(path)
    if rel.startswith("colab_notebooks_inventory_analysis/") and "notebook_sources" in rel:
        return "historical_notebook_source_export"
    if rel.startswith("code_inventory_analysis/") and "notebook_sources" in rel:
        return "historical_notebook_source_export"
    if rel.startswith("drive_evidence_copy/sajidahmedprotres_drive/Colab Notebooks/"):
        return "raw_colab_notebook_copy"
    if rel.startswith("proteinmpnn_ddg_recovery/") or rel.startswith("scripts/"):
        return "current_recovery_code"
    if rel.startswith("manuscript_codebase_mapping/"):
        return "manuscript_codebase_mapping_note"
    if rel.startswith("pickle_analysis/"):
        return "pickle_analysis_output_or_note"
    if rel.startswith("workspace_operations/"):
        return "workspace_operations_note"
    if rel.startswith("reproduction_inputs/"):
        return "reproduction_input_note_or_data"
    if rel.startswith("code_inventory_analysis/"):
        return "generated_code_inventory"
    return "other_workspace_text"


def iter_scan_files() -> Iterable[Path]:
    seen: set[Path] = set()
    for root in SCAN_ROOTS:
        if not root.exists():
            continue
        candidates = [root] if root.is_file() else sorted(root.rglob("*"))
        for path in candidates:
            if path in seen:
                continue
            seen.add(path)
            if should_scan_text_file(path):
                yield path


def reference_state(line: str, group: str) -> str:
    stripped = line.lstrip()
    if stripped.startswith("#") or stripped.startswith("//"):
        return "commented"
    if group.endswith("_note") or group in {"generated_code_inventory", "pickle_analysis_output_or_note"}:
        return "note_or_generated_inventory"
    return "active_or_text"


def scan_dependency_references(artifacts: list[Artifact]) -> list[dict[str, object]]:
    basename_to_artifacts: dict[str, list[Artifact]] = defaultdict(list)
    rel_to_artifact = {
        artifact.rel_path: artifact
        for artifact in artifacts
        if artifact.artifact_class != "nested_proteinmpnn_git_history"
    }
    for artifact in artifacts:
        if artifact.artifact_class == "nested_proteinmpnn_git_history":
            continue
        if artifact.basename in COMMON_FALSE_POSITIVE_NAMES:
            continue
        if not artifact.suffix:
            continue
        if len(artifact.basename) < 8:
            continue
        basename_to_artifacts[artifact.basename].append(artifact)

    rows: list[dict[str, object]] = []
    basename_names = sorted(basename_to_artifacts, key=len, reverse=True)
    for scan_path in iter_scan_files():
        group = source_group(scan_path)
        try:
            text = scan_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = scan_path.read_text(encoding="utf-8", errors="replace")
        for line_number, line in enumerate(text.splitlines(), start=1):
            matched: set[str] = set()

            for rel_path, artifact in rel_to_artifact.items():
                if rel_path in line:
                    matched.add(artifact.rel_path)
                else:
                    prefixed = f"Protein_MPNN_Digging/{rel_path}"
                    if prefixed in line:
                        matched.add(artifact.rel_path)

            for basename in basename_names:
                if basename in line:
                    for artifact in basename_to_artifacts[basename]:
                        matched.add(artifact.rel_path)

            if not matched:
                continue

            state = reference_state(line, group)
            for artifact_rel_path in sorted(matched):
                rows.append(
                    {
                        "artifact_relative_path": artifact_rel_path,
                        "artifact_basename": Path(artifact_rel_path).name,
                        "source_file": rel_workspace(scan_path),
                        "source_group": group,
                        "line_number": line_number,
                        "reference_state": state,
                        "line_text": line.strip()[:500],
                    }
                )
    return rows


def scan_checkpoint_usage() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for scan_path in iter_scan_files():
        group = source_group(scan_path)
        try:
            text = scan_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = scan_path.read_text(encoding="utf-8", errors="replace")
        for line_number, line in enumerate(text.splitlines(), start=1):
            hits = [term for term in CHECKPOINT_TERMS if term in line]
            if not hits:
                continue
            rows.append(
                {
                    "source_file": rel_workspace(scan_path),
                    "source_group": group,
                    "line_number": line_number,
                    "terms": ",".join(hits),
                    "reference_state": reference_state(line, group),
                    "line_text": line.strip()[:700],
                }
            )
    return rows


def run_git(args: list[str], cwd: Path) -> tuple[str, str, int]:
    proc = subprocess.run(
        ["git", *args],
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return proc.stdout.strip(), proc.stderr.strip(), proc.returncode


def nested_source_state_rows() -> list[dict[str, object]]:
    repos = [
        ("drive_nested_proteinmpnn", NESTED_PROTEINMPNN),
        ("sajidahmeduiu_source_repo", SOURCE_REPO),
    ]
    rows: list[dict[str, object]] = []
    for label, repo in repos:
        if not repo.exists():
            rows.append(
                {
                    "repo_label": label,
                    "repo_path": rel_workspace(repo) if repo.is_relative_to(WORKSPACE) else str(repo),
                    "field": "exists",
                    "value": "no",
                    "stderr": "NA",
                    "returncode": "NA",
                }
            )
            continue
        for field, args in [
            ("head_commit", ["rev-parse", "HEAD"]),
            ("current_branch", ["branch", "--show-current"]),
            ("remote_verbose", ["remote", "-v"]),
            ("status_short", ["status", "--short"]),
            ("diff_stat", ["diff", "--stat"]),
        ]:
            stdout, stderr, returncode = run_git(args, repo)
            rows.append(
                {
                    "repo_label": label,
                    "repo_path": rel_workspace(repo) if repo.is_relative_to(WORKSPACE) else str(repo),
                    "field": field,
                    "value": stdout.replace("\n", " | "),
                    "stderr": stderr.replace("\n", " | "),
                    "returncode": returncode,
                }
            )

    key_files = [
        "vanilla_proteinmpnn/protein_mpnn_utils.py",
        "vanilla_proteinmpnn/protein_mpnn_run.py",
        "vanilla_proteinmpnn/vanilla_model_weights/v_48_020.pt",
        "ca_proteinmpnn/protein_mpnn_utils.py",
        "ca_proteinmpnn/ca_model_weights/v_48_020.pt",
    ]
    for relative in key_files:
        for label, repo in repos:
            path = repo / relative
            value = ""
            if path.exists() and path.is_file():
                value = f"size={path.stat().st_size};sha256={sha256_file(path)}"
            elif path.exists():
                value = "exists_non_file"
            else:
                value = "missing"
            rows.append(
                {
                    "repo_label": label,
                    "repo_path": rel_workspace(repo) if repo.is_relative_to(WORKSPACE) else str(repo),
                    "field": f"key_file:{relative}",
                    "value": value,
                    "stderr": "NA",
                    "returncode": "NA",
                }
            )
    return rows


def artifact_reference_counts(reference_rows: list[dict[str, object]]) -> dict[str, Counter[str]]:
    counts: dict[str, Counter[str]] = defaultdict(Counter)
    for row in reference_rows:
        artifact = str(row["artifact_relative_path"])
        counts[artifact]["total"] += 1
        counts[artifact][str(row["reference_state"])] += 1
        counts[artifact][str(row["source_group"])] += 1
    return counts


def artifact_rows(
    artifacts: list[Artifact],
    reference_rows: list[dict[str, object]],
) -> list[dict[str, object]]:
    counts = artifact_reference_counts(reference_rows)
    rows: list[dict[str, object]] = []
    for artifact in artifacts:
        counter = counts.get(artifact.rel_path, Counter())
        rows.append(
            {
                "relative_path": artifact.rel_path,
                "basename": artifact.basename,
                "extension": artifact.suffix,
                "size_bytes": artifact.size_bytes,
                "mtime_epoch": f"{artifact.mtime_epoch:.6f}",
                "mtime_utc": artifact.mtime_utc,
                "sha256": artifact.sha256,
                "artifact_class": artifact.artifact_class,
                "dataset_hint": artifact.dataset_hint,
                "role_hint": artifact.role_hint,
                "git_tracked_now": artifact.git_tracked_now,
                "recommended_storage_route": artifact.storage_route,
                "storage_reason": artifact.storage_reason,
                "dependency_reference_count": counter["total"],
                "active_or_text_reference_count": counter["active_or_text"],
                "commented_reference_count": counter["commented"],
                "note_or_generated_reference_count": counter["note_or_generated_inventory"],
                "current_recovery_code_reference_count": counter["current_recovery_code"],
                "historical_notebook_reference_count": counter["historical_notebook_source_export"]
                + counter["raw_colab_notebook_copy"],
            }
        )
    return rows


def class_summary_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    summary: dict[tuple[str, str], Counter[str]] = defaultdict(Counter)
    for row in rows:
        key = (str(row["artifact_class"]), str(row["recommended_storage_route"]))
        summary[key]["file_count"] += 1
        summary[key]["size_bytes"] += int(row["size_bytes"])
        summary[key]["tracked"] += 1 if row["git_tracked_now"] == "yes" else 0
        summary[key]["referenced"] += 1 if int(row["dependency_reference_count"]) > 0 else 0

    out = []
    for (artifact_class, route), counter in sorted(summary.items()):
        out.append(
            {
                "artifact_class": artifact_class,
                "recommended_storage_route": route,
                "file_count": counter["file_count"],
                "tracked_file_count": counter["tracked"],
                "referenced_file_count": counter["referenced"],
                "size_bytes": counter["size_bytes"],
            }
        )
    return out


def write_markdown_summary(
    artifact_table: list[dict[str, object]],
    reference_rows: list[dict[str, object]],
    checkpoint_rows: list[dict[str, object]],
    source_rows: list[dict[str, object]],
) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    total_files = len(artifact_table)
    total_bytes = sum(int(row["size_bytes"]) for row in artifact_table)
    class_counts = Counter(str(row["artifact_class"]) for row in artifact_table)
    route_counts = Counter(str(row["recommended_storage_route"]) for row in artifact_table)
    largest = sorted(artifact_table, key=lambda row: int(row["size_bytes"]), reverse=True)[:12]
    referenced = [row for row in artifact_table if int(row["dependency_reference_count"]) > 0]

    v48_020_rows = [
        row
        for row in checkpoint_rows
        if "v_48_020" in str(row["line_text"]) or "v_48_020" in str(row["terms"])
    ]
    nested_head = next(
        (
            row["value"]
            for row in source_rows
            if row["repo_label"] == "drive_nested_proteinmpnn"
            and row["field"] == "head_commit"
        ),
        "",
    )
    nested_status = next(
        (
            row["value"]
            for row in source_rows
            if row["repo_label"] == "drive_nested_proteinmpnn"
            and row["field"] == "status_short"
        ),
        "",
    )

    lines = [
        "# Protein_MPNN_Digging Artifact Registry",
        "",
        "This report is generated from the copied local evidence tree:",
        "",
        f"- Evidence root: `{rel_workspace(EVIDENCE_ROOT)}`",
        f"- Generated at: `{datetime.now(timezone.utc).isoformat()}`",
        f"- File count: `{total_files}`",
        f"- Total bytes: `{total_bytes}`",
        "",
        "## Main Findings",
        "",
        "- The copied `Protein_MPNN_Digging` tree is only partially tracked by the workspace Git repository; promoted files are represented in `artifact_registry.tsv` with `git_tracked_now=yes`.",
        "- The V3 `*_pmppn_info_dict_V3.pickle` files, trained model pickles, and ProteinMPNN `.pt` checkpoints are binary artifacts; they need Git LFS or an external artifact-store decision before promotion.",
        "- The nested `ProteinMPNN/.git` metadata should not be committed as a nested Git directory. Preserve the source state by pinned commit, patch/diff, or an archive/bundle decision.",
        f"- The nested copied ProteinMPNN checkout HEAD is `{nested_head}` with status `{nested_status or 'clean'}`.",
        f"- Checkpoint usage lines mentioning `v_48_020` were found: `{len(v48_020_rows)}`.",
        "",
        "## Artifact Classes",
        "",
    ]

    for artifact_class, count in sorted(class_counts.items()):
        lines.append(f"- `{artifact_class}`: `{count}` files")

    lines.extend(["", "## Storage Route Counts", ""])
    for route, count in sorted(route_counts.items()):
        lines.append(f"- `{route}`: `{count}` files")

    lines.extend(["", "## Largest Artifacts", ""])
    for row in largest:
        lines.append(
            f"- `{row['relative_path']}`: `{row['size_bytes']}` bytes, class `{row['artifact_class']}`, sha256 `{row['sha256']}`"
        )

    lines.extend(
        [
            "",
            "## Dependency Map",
            "",
            f"- Dependency/reference rows written: `{len(reference_rows)}`",
            f"- Referenced artifacts: `{len(referenced)}`",
            "- Reference states are intentionally simple: `active_or_text`, `commented`, and `note_or_generated_inventory`.",
            "",
            "## Generated Tables",
            "",
            "- `artifact_registry.tsv`",
            "- `artifact_class_summary.tsv`",
            "- `dependency_references.tsv`",
            "- `proteinmpnn_checkpoint_usage.tsv`",
            "- `nested_proteinmpnn_source_state.tsv`",
            "",
            "## Storage Decision Rule",
            "",
            "Promote artifacts by class, not by accident. For each class, decide whether it is:",
            "",
            "- core reproducibility evidence that must be portable,",
            "- lineage evidence useful for historical comparison,",
            "- rerunnable/generated output,",
            "- runtime residue that should stay untracked, or",
            "- nested upstream source state that should be represented by commit/diff/archive rather than a nested `.git` directory.",
            "",
        ]
    )
    (OUTPUT_DIR / "README.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    artifacts = collect_artifacts()
    reference_rows = scan_dependency_references(artifacts)
    checkpoint_rows = scan_checkpoint_usage()
    source_rows = nested_source_state_rows()
    registry_rows = artifact_rows(artifacts, reference_rows)
    summary_rows = class_summary_rows(registry_rows)

    write_tsv(
        OUTPUT_DIR / "artifact_registry.tsv",
        registry_rows,
        [
            "relative_path",
            "basename",
            "extension",
            "size_bytes",
            "mtime_epoch",
            "mtime_utc",
            "sha256",
            "artifact_class",
            "dataset_hint",
            "role_hint",
            "git_tracked_now",
            "recommended_storage_route",
            "storage_reason",
            "dependency_reference_count",
            "active_or_text_reference_count",
            "commented_reference_count",
            "note_or_generated_reference_count",
            "current_recovery_code_reference_count",
            "historical_notebook_reference_count",
        ],
    )
    write_tsv(
        OUTPUT_DIR / "artifact_class_summary.tsv",
        summary_rows,
        [
            "artifact_class",
            "recommended_storage_route",
            "file_count",
            "tracked_file_count",
            "referenced_file_count",
            "size_bytes",
        ],
    )
    write_tsv(
        OUTPUT_DIR / "dependency_references.tsv",
        reference_rows,
        [
            "artifact_relative_path",
            "artifact_basename",
            "source_file",
            "source_group",
            "line_number",
            "reference_state",
            "line_text",
        ],
    )
    write_tsv(
        OUTPUT_DIR / "proteinmpnn_checkpoint_usage.tsv",
        checkpoint_rows,
        [
            "source_file",
            "source_group",
            "line_number",
            "terms",
            "reference_state",
            "line_text",
        ],
    )
    write_tsv(
        OUTPUT_DIR / "nested_proteinmpnn_source_state.tsv",
        source_rows,
        ["repo_label", "repo_path", "field", "value", "stderr", "returncode"],
    )
    write_markdown_summary(registry_rows, reference_rows, checkpoint_rows, source_rows)


if __name__ == "__main__":
    main()
