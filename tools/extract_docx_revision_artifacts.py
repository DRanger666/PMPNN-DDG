#!/usr/bin/env python3
"""Extract DOCX comments and tracked-change summaries.

The script reads copied evidence DOCX files as ZIP/XML packages and writes TSV
summaries. It does not modify the DOCX files.
"""

from __future__ import annotations

import argparse
import re
import zipfile
from collections import defaultdict
from pathlib import Path
from xml.etree import ElementTree as ET


NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
TEXT_TAGS = {
    f"{{{NS['w']}}}t",
    f"{{{NS['w']}}}delText",
    f"{{{NS['w']}}}instrText",
}
CHANGE_TAGS = {
    f"{{{NS['w']}}}ins": "insertion",
    f"{{{NS['w']}}}del": "deletion",
    f"{{{NS['w']}}}moveFrom": "move_from",
    f"{{{NS['w']}}}moveTo": "move_to",
}
WORD_RE = re.compile(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)?")


def clean_cell(value: str | None) -> str:
    if not value:
        return ""
    return re.sub(r"\s+", " ", value).strip().replace("\t", " ")


def text_from_element(element: ET.Element) -> str:
    pieces: list[str] = []
    for child in element.iter():
        if child.tag in TEXT_TAGS and child.text:
            pieces.append(child.text)
    return clean_cell(" ".join(pieces))


def words(text: str) -> int:
    return len(WORD_RE.findall(text))


def read_xml(zf: zipfile.ZipFile, name: str) -> ET.Element | None:
    try:
        with zf.open(name) as f:
            return ET.parse(f).getroot()
    except KeyError:
        return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--docx-dir", required=True)
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()

    docx_dir = Path(args.docx_dir)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    comments_rows: list[list[str]] = []
    change_rows: list[list[str]] = []
    file_summary_rows: list[list[str]] = []
    summary_rows: list[list[str]] = []

    for docx in sorted(docx_dir.glob("*.docx")):
        by_type_author_date: dict[tuple[str, str, str], dict[str, int | str]] = defaultdict(
            lambda: {"count": 0, "chars": 0, "words": 0, "example": ""}
        )
        comment_count = 0
        change_count = 0

        with zipfile.ZipFile(docx) as zf:
            comments_root = read_xml(zf, "word/comments.xml")
            if comments_root is not None:
                for comment in comments_root.findall("w:comment", NS):
                    comment_count += 1
                    text = text_from_element(comment)
                    comments_rows.append(
                        [
                            docx.name,
                            clean_cell(comment.get(f"{{{NS['w']}}}id")),
                            clean_cell(comment.get(f"{{{NS['w']}}}author")),
                            clean_cell(comment.get(f"{{{NS['w']}}}date")),
                            text,
                        ]
                    )

            document_root = read_xml(zf, "word/document.xml")
            if document_root is not None:
                for element in document_root.iter():
                    change_type = CHANGE_TAGS.get(element.tag)
                    if change_type is None:
                        continue
                    change_count += 1
                    author = clean_cell(element.get(f"{{{NS['w']}}}author"))
                    date = clean_cell(element.get(f"{{{NS['w']}}}date"))
                    text = text_from_element(element)
                    change_rows.append([docx.name, change_type, author, date, text])
                    key = (change_type, author, date)
                    rec = by_type_author_date[key]
                    rec["count"] = int(rec["count"]) + 1
                    rec["chars"] = int(rec["chars"]) + len(text)
                    rec["words"] = int(rec["words"]) + words(text)
                    if not rec["example"] and text:
                        rec["example"] = text[:180]

        change_type_counts = defaultdict(int)
        authors = set()
        for (change_type, author, _date), rec in by_type_author_date.items():
            change_type_counts[change_type] += int(rec["count"])
            if author:
                authors.add(author)
        file_summary_rows.append(
            [
                docx.name,
                str(comment_count),
                str(change_count),
                str(change_type_counts["insertion"]),
                str(change_type_counts["deletion"]),
                str(change_type_counts["move_from"]),
                str(change_type_counts["move_to"]),
                "; ".join(sorted(authors)),
            ]
        )
        for (change_type, author, date), rec in sorted(by_type_author_date.items()):
            summary_rows.append(
                [
                    docx.name,
                    "",
                    "",
                    change_type,
                    author,
                    date,
                    str(rec["count"]),
                    str(rec["words"]),
                    str(rec["chars"]),
                    clean_cell(str(rec["example"])),
                ]
            )

    with (out_dir / "docx_comments.tsv").open("w", encoding="utf-8") as f:
        f.write("file\tcomment_id\tauthor\tdate\ttext\n")
        for row in comments_rows:
            f.write("\t".join(row) + "\n")

    with (out_dir / "docx_tracked_changes.tsv").open("w", encoding="utf-8") as f:
        f.write("file\tchange_type\tauthor\tdate\ttext\n")
        for row in change_rows:
            f.write("\t".join(row) + "\n")

    with (out_dir / "docx_revision_artifact_file_summary.tsv").open(
        "w", encoding="utf-8"
    ) as f:
        f.write(
            "file\tcomment_count\tchange_count\tinsertion_count\t"
            "deletion_count\tmove_from_count\tmove_to_count\tchange_authors\n"
        )
        for row in file_summary_rows:
            f.write("\t".join(row) + "\n")

    with (out_dir / "docx_revision_artifact_summary.tsv").open(
        "w", encoding="utf-8"
    ) as f:
        f.write(
            "file\tcomment_count\tchange_count\tchange_type\tauthor\tdate\t"
            "count\twords\tchars\texample\n"
        )
        for row in summary_rows:
            f.write("\t".join(row) + "\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
