#!/usr/bin/env python3
"""Analyze extracted manuscript text files for draft relationships.

Inputs are plain-text files generated from DOCX/PDF sources. Outputs are TSV
tables that help distinguish exact exports, small revisions, and separate
documents without modifying the preserved evidence copy.
"""

from __future__ import annotations

import argparse
import difflib
import re
from collections import Counter
from pathlib import Path


WORD_RE = re.compile(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)?")


def normalized_words(text: str) -> list[str]:
    return [m.group(0).lower() for m in WORD_RE.finditer(text)]


def normalized_lines(text: str) -> list[str]:
    lines = []
    for line in text.splitlines():
        line = re.sub(r"\s+", " ", line).strip()
        if line:
            lines.append(line)
    return lines


def ngrams(words: list[str], n: int = 7) -> set[tuple[str, ...]]:
    if len(words) < n:
        return set()
    return {tuple(words[i : i + n]) for i in range(len(words) - n + 1)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--docx-text-dir", required=True)
    parser.add_argument("--pdf-text-dir", required=True)
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    files: list[tuple[str, str, Path]] = []
    for kind, root in [
        ("docx", Path(args.docx_text_dir)),
        ("pdf", Path(args.pdf_text_dir)),
    ]:
        for path in sorted(root.glob("*.txt")):
            files.append((kind, path.stem, path))

    records = {}
    for kind, stem, path in files:
        text = path.read_text(errors="replace")
        words = normalized_words(text)
        lines = normalized_lines(text)
        records[(kind, stem)] = {
            "kind": kind,
            "stem": stem,
            "path": path,
            "text": text,
            "words": words,
            "word_counts": Counter(words),
            "lines": lines,
            "ngrams7": ngrams(words, 7),
        }

    stats_path = out_dir / "text_stats.tsv"
    with stats_path.open("w") as f:
        f.write("kind\tstem\twords\tunique_words\tlines\tchars\tpath\n")
        for key, rec in sorted(records.items()):
            f.write(
                "{kind}\t{stem}\t{words}\t{unique}\t{lines}\t{chars}\t{path}\n".format(
                    kind=rec["kind"],
                    stem=rec["stem"],
                    words=len(rec["words"]),
                    unique=len(rec["word_counts"]),
                    lines=len(rec["lines"]),
                    chars=len(rec["text"]),
                    path=rec["path"],
                )
            )

    containment_path = out_dir / "ngram7_containment.tsv"
    with containment_path.open("w") as f:
        f.write(
            "source_kind\tsource\tcandidate_kind\tcandidate\t"
            "source_words\tcandidate_words\tsource_ngrams\tcandidate_ngrams\t"
            "source_ngrams_in_candidate_pct\tcandidate_ngrams_in_source_pct\t"
            "line_sequence_ratio\n"
        )
        for skey, srec in sorted(records.items()):
            for ckey, crec in sorted(records.items()):
                if skey == ckey:
                    continue
                sgrams = srec["ngrams7"]
                cgrams = crec["ngrams7"]
                source_in_candidate = (
                    100.0 * len(sgrams & cgrams) / len(sgrams) if sgrams else 0.0
                )
                candidate_in_source = (
                    100.0 * len(sgrams & cgrams) / len(cgrams) if cgrams else 0.0
                )
                ratio = difflib.SequenceMatcher(
                    None, srec["lines"], crec["lines"], autojunk=False
                ).ratio()
                f.write(
                    "{sk}\t{s}\t{ck}\t{c}\t{sw}\t{cw}\t{sg}\t{cg}\t"
                    "{sic:.2f}\t{cis:.2f}\t{ratio:.4f}\n".format(
                        sk=srec["kind"],
                        s=srec["stem"],
                        ck=crec["kind"],
                        c=crec["stem"],
                        sw=len(srec["words"]),
                        cw=len(crec["words"]),
                        sg=len(sgrams),
                        cg=len(cgrams),
                        sic=source_in_candidate,
                        cis=candidate_in_source,
                        ratio=ratio,
                    )
                )

    near_duplicates_path = out_dir / "near_duplicates.tsv"
    with near_duplicates_path.open("w") as f:
        f.write(
            "a_kind\ta\tb_kind\tb\ta_words\tb_words\t"
            "a_in_b_pct\tb_in_a_pct\tline_sequence_ratio\n"
        )
        seen = set()
        for akey, arec in sorted(records.items()):
            for bkey, brec in sorted(records.items()):
                if akey == bkey or (bkey, akey) in seen:
                    continue
                seen.add((akey, bkey))
                agrams = arec["ngrams7"]
                bgrams = brec["ngrams7"]
                if not agrams or not bgrams:
                    continue
                a_in_b = 100.0 * len(agrams & bgrams) / len(agrams)
                b_in_a = 100.0 * len(agrams & bgrams) / len(bgrams)
                ratio = difflib.SequenceMatcher(
                    None, arec["lines"], brec["lines"], autojunk=False
                ).ratio()
                if max(a_in_b, b_in_a) >= 80 or ratio >= 0.80:
                    f.write(
                        "{ak}\t{a}\t{bk}\t{b}\t{aw}\t{bw}\t"
                        "{aib:.2f}\t{bia:.2f}\t{ratio:.4f}\n".format(
                            ak=arec["kind"],
                            a=arec["stem"],
                            bk=brec["kind"],
                            b=brec["stem"],
                            aw=len(arec["words"]),
                            bw=len(brec["words"]),
                            aib=a_in_b,
                            bia=b_in_a,
                            ratio=ratio,
                        )
                    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
