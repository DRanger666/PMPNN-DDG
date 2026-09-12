#!/usr/bin/env python3
"""Verify the manuscript Figure 6 image against notebook output and result data.

This script performs two narrow checks:

1. Hash all PNG outputs embedded in local copies of
   `Quick_Dirty_MPNN_ML_V2_VGRAPHS_V1.ipynb` and compare them with the
   standalone manuscript-side `Feature_Combinations_MultiPlot.png`.
2. Load `list_incremental_feature_result_dict.pickle` and write the exact
   S_669/Ssym total-PCC series used by the matching plotting cell.

The script is read-only with respect to historical evidence files.
"""

from __future__ import annotations

import base64
import csv
import hashlib
import json
import pickle
import struct
import zipfile
from pathlib import Path
from typing import Any
import xml.etree.ElementTree as ET


WORKSPACE = Path(__file__).resolve().parents[1]
OUTPUT_DIR = WORKSPACE / "code_inventory_analysis" / "figure6_image_verification"

MANUSCRIPT_FIGURE = (
    WORKSPACE
    / "drive_evidence_copy"
    / "sajidahmedprotres_drive"
    / "MPNN_DDG_Manuscript"
    / "Feature_Combinations_MultiPlot.png"
)

MANUSCRIPT_DOCX = (
    WORKSPACE
    / "drive_evidence_copy"
    / "sajidahmedprotres_drive"
    / "MPNN_DDG_Manuscript"
    / "SA_CEM_9_26_2022_MJ_Issue_Adressing.docx"
)

NOTEBOOKS = [
    WORKSPACE
    / "source_repos"
    / "SajidAhmeduiu_ProteinMPNN"
    / "Sajid_Additions"
    / "Quick_Dirty_MPNN_ML_V2_VGRAPHS_V1.ipynb",
    WORKSPACE
    / "drive_evidence_copy"
    / "sajidahmedprotres_drive"
    / "Colab Notebooks"
    / "Quick_Dirty_MPNN_ML_V2_VGRAPHS_V1.ipynb",
]

RESULT_PICKLE = (
    WORKSPACE
    / "drive_evidence_copy"
    / "sajidahmedprotres_drive"
    / "Protein_MPNN_Digging"
    / "list_incremental_feature_result_dict.pickle"
)

INCREMENTAL_COMBOS = [
    "A",
    "A+B",
    "A+B+C",
    "A+B+C+D",
    "A+B+C+D+E",
    "A+B+C+D+E+F",
    "A+B+C+D+E+F+G",
    "A+B+C+D+E+F+G+H",
]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def png_dimensions(data: bytes) -> tuple[int | None, int | None]:
    """Return PNG width/height from the IHDR chunk without external packages."""
    if not data.startswith(b"\x89PNG\r\n\x1a\n") or data[12:16] != b"IHDR":
        return None, None
    width, height = struct.unpack(">II", data[16:24])
    return width, height


def write_tsv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            delimiter="\t",
            fieldnames=fields,
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def decode_png_payload(payload: str | list[str]) -> bytes:
    if isinstance(payload, list):
        payload = "".join(payload)
    return base64.b64decode(payload)


def relative(path: Path) -> str:
    return str(path.relative_to(WORKSPACE))


def notebook_output_rows(manuscript_hash: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rows: list[dict[str, Any]] = []
    matches: list[dict[str, Any]] = []

    for notebook_path in NOTEBOOKS:
        if not notebook_path.exists():
            continue
        notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
        for cell_index, cell in enumerate(notebook.get("cells", [])):
            source = "".join(cell.get("source", []))
            outputs = cell.get("outputs", [])
            for output_index, output in enumerate(outputs):
                image_payload = output.get("data", {}).get("image/png")
                if not image_payload:
                    continue
                image_bytes = decode_png_payload(image_payload)
                image_hash = sha256_bytes(image_bytes)
                width, height = png_dimensions(image_bytes)
                row = {
                    "notebook_path": relative(notebook_path),
                    "cell_index": cell_index,
                    "execution_count": cell.get("execution_count"),
                    "output_index": output_index,
                    "output_sha256": image_hash,
                    "byte_length": len(image_bytes),
                    "width": width,
                    "height": height,
                    "text_plain": " ".join(output.get("data", {}).get("text/plain", [])),
                    "matches_manuscript_figure": image_hash == manuscript_hash,
                    "source_contains_s669_total_pcc": "list_S_669_total_PCC" in source,
                    "source_contains_ssym_total_pcc": "list_Ssym_total_PCC" in source,
                    "source_contains_dict_mean": "dict_mean" in source,
                }
                rows.append(row)
                if image_hash == manuscript_hash:
                    matches.append({**row, "source": source})

    return rows, matches


def docx_media_rows(manuscript_hash: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with zipfile.ZipFile(MANUSCRIPT_DOCX) as docx:
        for name in sorted(item for item in docx.namelist() if item.startswith("word/media/")):
            media_bytes = docx.read(name)
            media_hash = sha256_bytes(media_bytes)
            width, height = png_dimensions(media_bytes)
            rows.append(
                {
                    "docx_path": relative(MANUSCRIPT_DOCX),
                    "media_path": name,
                    "sha256": media_hash,
                    "byte_length": len(media_bytes),
                    "width": width,
                    "height": height,
                    "matches_standalone_manuscript_figure": media_hash == manuscript_hash,
                }
            )
    return rows


def docx_image_reference_rows() -> list[dict[str, Any]]:
    """List DOCX image references with the paragraph text around each reference."""
    ns = {
        "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
        "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
        "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    }
    rows: list[dict[str, Any]] = []

    with zipfile.ZipFile(MANUSCRIPT_DOCX) as docx:
        document = ET.fromstring(docx.read("word/document.xml"))
        rels = ET.fromstring(docx.read("word/_rels/document.xml.rels"))

    rels_map = {rel.attrib["Id"]: rel.attrib.get("Target") for rel in rels}
    paragraphs = document.findall(".//w:p", ns)

    for paragraph_index, paragraph in enumerate(paragraphs):
        paragraph_text = "".join(
            text.text or "" for text in paragraph.findall(".//w:t", ns)
        ).strip()
        if not paragraph_text:
            continue
        for blip in paragraph.findall(".//a:blip", ns):
            relationship_id = blip.attrib.get(f"{{{ns['r']}}}embed")
            target = rels_map.get(relationship_id, "")
            rows.append(
                {
                    "paragraph_index": paragraph_index,
                    "relationship_id": relationship_id,
                    "target": target,
                    "paragraph_mentions_figure6": "Figure 6" in paragraph_text,
                    "paragraph_text": paragraph_text,
                }
            )

    return rows


def dict_mean(dict_list: list[dict[str, float]]) -> dict[str, float]:
    mean_dict: dict[str, float] = {}
    for key in dict_list[0]:
        mean_dict[key] = sum(float(item[key]) for item in dict_list) / len(dict_list)
    return mean_dict


def figure_label(combo: str) -> str:
    if len(combo) == 1:
        return combo
    parts = combo.split("+")
    return f"{parts[0]}-{parts[-1]}"


def plotted_series_rows() -> list[dict[str, Any]]:
    with RESULT_PICKLE.open("rb") as handle:
        result_runs = pickle.load(handle)

    s669_dicts = [run["S_669_total_PCC"] for run in result_runs]
    ssym_dicts = [run["Ssym_total_PCC"] for run in result_runs]
    s669_mean = dict_mean(s669_dicts)
    ssym_mean = dict_mean(ssym_dicts)

    rows: list[dict[str, Any]] = []
    for combo in INCREMENTAL_COMBOS:
        rows.append(
            {
                "feature_combo": combo,
                "figure_label": figure_label(combo),
                "n_runs": len(result_runs),
                "S_669_total_PCC_mean": s669_mean[combo],
                "Ssym_total_PCC_mean": ssym_mean[combo],
                "S_669_round_2": round(s669_mean[combo], 2),
                "Ssym_round_2": round(ssym_mean[combo], 2),
            }
        )
    return rows


def write_readme(
    manuscript_hash: str,
    manuscript_width: int | None,
    manuscript_height: int | None,
    matches: list[dict[str, Any]],
    docx_figure6_targets: list[str],
    docx_exact_media_matches: int,
) -> None:
    lines = [
        "# Figure 6 Image Verification",
        "",
        "This directory is generated by `scripts/verify_figure6_image_basis.py`.",
        "",
        "## Core Result",
        "",
        f"- Manuscript figure: `{relative(MANUSCRIPT_FIGURE)}`",
        f"- Manuscript figure SHA256: `{manuscript_hash}`",
        f"- Manuscript figure dimensions: `{manuscript_width}x{manuscript_height}`",
        f"- Exact notebook-output matches found: `{len(matches)}`",
        "",
    ]

    if matches:
        match = matches[0]
        lines.extend(
            [
                "The standalone manuscript figure is byte-identical to this saved notebook output:",
                "",
                f"- notebook: `{match['notebook_path']}`",
                f"- cell index: `{match['cell_index']}`",
                f"- execution count: `{match['execution_count']}`",
                f"- output index: `{match['output_index']}`",
                f"- output SHA256: `{match['output_sha256']}`",
                "",
                "That matched cell source uses:",
                "",
                "```text",
                "S_669_PCC_vals = [i for i in dict_mean(list_S_669_total_PCC).values()]",
                "Ssym_PCC_vals = [i for i in dict_mean(list_Ssym_total_PCC).values()]",
                "```",
                "",
                "The plotted total-PCC series reconstructed from",
                "`list_incremental_feature_result_dict.pickle` is written to",
                "`figure6_plotted_total_pcc_series.tsv`.",
                "",
            ]
        )

    lines.extend(
        [
            "## DOCX Embedding Check",
            "",
            f"- DOCX file: `{relative(MANUSCRIPT_DOCX)}`",
            f"- DOCX media files byte-identical to the standalone figure: `{docx_exact_media_matches}`",
            f"- DOCX media target(s) referenced in Figure 6 paragraph(s): `{', '.join(docx_figure6_targets)}`",
            "",
            "The final DOCX references Figure 6 through its own embedded media copy.",
            "The embedded PNG does not need to be byte-identical to the standalone",
            "figure for scientific recovery. Word/DOCX embedding can preserve plotted",
            "content while changing image dimensions or bytes. The byte-level check is",
            "only an artifact-provenance shortcut when it succeeds; content and plotted",
            "numeric values are the relevant recovery criteria.",
            "",
        ]
    )

    lines.extend(
        [
            "## Files",
            "",
            "- `notebook_png_hashes.tsv`: all PNG outputs found in the checked notebooks.",
            "- `figure6_image_hash_matches.tsv`: exact hash matches to the manuscript figure.",
            "- `docx_media_hashes.tsv`: PNG media embedded in the final DOCX.",
            "- `docx_image_references.tsv`: DOCX paragraph/image relationship references.",
            "- `figure6_matched_notebook_cell_source.py.txt`: source of the matched plotting cell.",
            "- `figure6_plotted_total_pcc_series.tsv`: S_669/Ssym total-PCC series from the ten-run pickle.",
            "",
            "Scope limit: this verifies the Figure 6 image source and plotted result",
            "series. It does not prove upstream V3 pickle regeneration or direct tensor",
            "extraction.",
        ]
    )

    (OUTPUT_DIR / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    manuscript_bytes = MANUSCRIPT_FIGURE.read_bytes()
    manuscript_hash = sha256_bytes(manuscript_bytes)
    manuscript_width, manuscript_height = png_dimensions(manuscript_bytes)

    all_rows, matches = notebook_output_rows(manuscript_hash)
    match_rows = [{key: value for key, value in row.items() if key != "source"} for row in matches]
    docx_media = docx_media_rows(manuscript_hash)
    docx_references = docx_image_reference_rows()
    docx_figure6_targets = sorted(
        {
            str(row["target"])
            for row in docx_references
            if row["paragraph_mentions_figure6"] and row["target"]
        }
    )
    docx_exact_media_matches = sum(
        1 for row in docx_media if row["matches_standalone_manuscript_figure"]
    )

    write_tsv(
        OUTPUT_DIR / "notebook_png_hashes.tsv",
        all_rows,
        [
            "notebook_path",
            "cell_index",
            "execution_count",
            "output_index",
            "output_sha256",
            "byte_length",
            "width",
            "height",
            "text_plain",
            "matches_manuscript_figure",
            "source_contains_s669_total_pcc",
            "source_contains_ssym_total_pcc",
            "source_contains_dict_mean",
        ],
    )
    write_tsv(
        OUTPUT_DIR / "figure6_image_hash_matches.tsv",
        match_rows,
        [
            "notebook_path",
            "cell_index",
            "execution_count",
            "output_index",
            "output_sha256",
            "byte_length",
            "width",
            "height",
            "text_plain",
            "matches_manuscript_figure",
            "source_contains_s669_total_pcc",
            "source_contains_ssym_total_pcc",
            "source_contains_dict_mean",
        ],
    )
    write_tsv(
        OUTPUT_DIR / "docx_media_hashes.tsv",
        docx_media,
        [
            "docx_path",
            "media_path",
            "sha256",
            "byte_length",
            "width",
            "height",
            "matches_standalone_manuscript_figure",
        ],
    )
    write_tsv(
        OUTPUT_DIR / "docx_image_references.tsv",
        docx_references,
        [
            "paragraph_index",
            "relationship_id",
            "target",
            "paragraph_mentions_figure6",
            "paragraph_text",
        ],
    )
    write_tsv(
        OUTPUT_DIR / "figure6_plotted_total_pcc_series.tsv",
        plotted_series_rows(),
        [
            "feature_combo",
            "figure_label",
            "n_runs",
            "S_669_total_PCC_mean",
            "Ssym_total_PCC_mean",
            "S_669_round_2",
            "Ssym_round_2",
        ],
    )

    if matches:
        matched_source = "\n".join(
            line.rstrip() for line in matches[0]["source"].splitlines()
        )
        (OUTPUT_DIR / "figure6_matched_notebook_cell_source.py.txt").write_text(
            matched_source + "\n",
            encoding="utf-8",
        )
    else:
        (OUTPUT_DIR / "figure6_matched_notebook_cell_source.py.txt").write_text(
            "",
            encoding="utf-8",
        )

    write_readme(
        manuscript_hash,
        manuscript_width,
        manuscript_height,
        matches,
        docx_figure6_targets,
        docx_exact_media_matches,
    )

    print(f"wrote {relative(OUTPUT_DIR)}")
    print(f"exact_matches={len(matches)}")
    print(f"docx_exact_media_matches={docx_exact_media_matches}")
    print(f"docx_figure6_targets={','.join(docx_figure6_targets)}")
    for match in matches:
        print(
            "match",
            match["notebook_path"],
            f"cell={match['cell_index']}",
            f"output={match['output_index']}",
            match["output_sha256"],
        )


if __name__ == "__main__":
    main()
