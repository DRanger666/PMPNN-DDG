# MPNN DDG Manuscript Folder Content Inventory

Working evidence root:

`drive_evidence_copy/sajidahmedprotres_drive/MPNN_DDG_Manuscript`

This inventory is based on the copied evidence directory, not the mounted
Drive source. The mounted source was not modified.

## Executive Finding

The manuscript folder contains one main PMPNN-DDG manuscript lineage, several
PDF exports/snapshots of that lineage, figure assets, one separate long
physics/concept note, and a small CFTR-related figure side folder.

The latest broad manuscript evidence package is
`SA_CEM_9_26_2022_MJ_Issue_Adressing.docx`, but it is not a clean final
manuscript. It still contains Jens Meiler comments and tracked changes, plus
Sajid-authored tracked insertions from 2022-10-17 that appear to address or
push back on parts of the MJ revision. Treat it as the latest annotated
revision state, not as a ready-to-revive base.

The safest clean pre-MJ manuscript base is `SA_CEM_9_26_2022.docx`.
`SA_9_23_2022_CEM.docx` and `SA_CEM_9_26_2022.docx` are text-equivalent by
7-gram comparison and line sequence comparison; the 2022-09-26 file is the
later save/export event.

`some_soul_wrenching_physics.docx` is a separate long conceptual document. It
does not subsume the PMPNN-DDG manuscript.

## Evidence Generated

Primary analysis outputs:

| Path | Purpose |
| --- | --- |
| `manuscript_inventory_analysis/metadata/file_timeline.tsv` | mtime-sorted source file timeline |
| `manuscript_inventory_analysis/metadata/document_metadata.txt` | ExifTool metadata for DOCX/PDF/image files |
| `manuscript_inventory_analysis/metadata/image_dimensions.tsv` | image dimensions and file sizes |
| `manuscript_inventory_analysis/metadata/docx_comments.tsv` | extracted DOCX comments |
| `manuscript_inventory_analysis/metadata/docx_revision_artifact_file_summary.tsv` | compact DOCX comments/tracked-change counts |
| `manuscript_inventory_analysis/metadata/docx_tracked_changes.tsv` | extracted tracked-change text |
| `manuscript_inventory_analysis/comparisons/text_stats.tsv` | extracted text size stats |
| `manuscript_inventory_analysis/comparisons/near_duplicates.tsv` | pairwise containment and near-duplicate signals |
| `manuscript_inventory_analysis/extracted/docx_text/` | `docx2txt` extraction |
| `manuscript_inventory_analysis/extracted/docx_markdown_accept/` | Pandoc extraction with tracked changes accepted |
| `manuscript_inventory_analysis/extracted/docx_markdown_reject/` | Pandoc extraction with tracked changes rejected |
| `manuscript_inventory_analysis/extracted/docx_markdown_track_all/` | Pandoc extraction preserving tracked changes/comments |
| `manuscript_inventory_analysis/extracted/pdf_text/` | `pdftotext -layout` extraction |

Toolchain verified after installation:

| Tool | Version / status |
| --- | --- |
| `pandoc` | `pandoc 3.1.3` |
| `docx2txt` | available at `/usr/bin/docx2txt` |
| `exiftool` | `12.76` |
| `pdftotext` | `24.02.0` |

## Main Manuscript Lineage

| Order | File | Extracted words | Metadata modify time | Role |
| ---: | --- | ---: | --- | --- |
| 1 | `V1_CEM.docx` | 1,855 | 2022-09-08 10:17:38Z | short early skeleton with reviewer comments |
| 2 | `V1.docx` | 6,109 | 2022-09-20 19:13:00Z | first full manuscript-shaped draft |
| 3 | `SA_9_20_2022.docx` | 6,528 | 2022-09-21 01:07:00Z | fuller draft with system diagram material |
| 4 | `SA_9_20_2022_Equation_Update_Attempt.docx` | 6,565 | 2022-09-21 18:27:00Z | near-copy with equation/conclusion work |
| 5 | `SA_9_21_2022.docx` | 6,764 | 2022-09-21 21:58:00Z | near-superset of equation-update draft |
| 6 | `SA_9_23_2022_CEM.docx` | 6,771 | 2022-09-26 17:13:00Z | title/author and CEM-stage polished draft |
| 7 | `SA_CEM_9_26_2022.docx` | 6,771 | 2022-09-26 22:19:00Z | text-equivalent later save of prior file |
| 8 | `SA_CEM_9_26_2022_MJ.docx` | 6,776 | 2022-09-28 12:59:00Z | Jens Meiler commented/tracked-change revision |
| 9 | `SA_CEM_9_26_2022_MJ_Issue_Adressing.docx` | 7,182 | 2022-11-20 00:50:00Z | latest annotated issue-addressing state |

Notes:

- The extracted word counts above come from `docx2txt`. For the MJ-family
  documents, the more precise interpretation requires Pandoc accept/reject/
  track-all views because those DOCX files contain unresolved tracked changes.
- Word's internal word-count metadata is much larger than extracted visible text
  for several files, likely because it counts document fields, revision state,
  hidden parts, or layout artifacts differently. Use extracted text stats for
  textual comparison and DOCX metadata for provenance.

## Subsumption and Difference Summary

| Relationship | Evidence | Interpretation |
| --- | --- | --- |
| `V1_CEM.docx` -> `V1.docx` | 82.56% of `V1_CEM` 7-grams appear in `V1`, but only 27.04% of `V1` appears in `V1_CEM` | `V1_CEM` is an early skeleton/partial draft, not a full predecessor that preserves all later content |
| `V1.docx` -> `SA_9_20_2022.docx` | 97.05% of `V1` 7-grams appear in `SA_9_20_2022`; reverse containment is 91.49% | `SA_9_20_2022` largely subsumes `V1` and adds content |
| `SA_9_20_2022.docx` -> `SA_9_20_2022_Equation_Update_Attempt.docx` | 98.60% containment from first to second | very close revision, likely equation/conclusion-oriented |
| `SA_9_20_2022_Equation_Update_Attempt.docx` -> `SA_9_21_2022.docx` | 99.78% containment from first to second | `SA_9_21_2022` almost fully subsumes the equation-update attempt |
| `SA_9_23_2022_CEM.docx` -> `SA_CEM_9_26_2022.docx` | 100.00% 7-gram containment both ways; line ratio 1.0000 | text-equivalent; binary DOCX packages differ |
| `SA_CEM_9_26_2022.docx` -> `SA_CEM_9_26_2022_MJ.docx` | accepted-change diff: 176 insertions / 173 deletions in Markdown extraction | MJ file is an editorial tracked-change revision, not a simple additive superset |
| `SA_CEM_9_26_2022_MJ.docx` -> `SA_CEM_9_26_2022_MJ_Issue_Adressing.docx` | track-all diff: 44 insertions / 45 deletions; DOCX tracked changes increase from 181 to 238 | issue-addressing file preserves MJ markup and adds Sajid-authored issue-addressing markup |

## Clean Base vs Latest Annotated State

Use these distinctions for future revival work:

| Need | Best source | Reason |
| --- | --- | --- |
| Cleanest pre-MJ manuscript text | `SA_CEM_9_26_2022.docx` | latest clean Sajid-authored main draft before tracked MJ edits |
| Advisor/comment provenance | `SA_CEM_9_26_2022_MJ.docx` | contains 10 Jens Meiler comments and 181 tracked-change artifacts |
| Latest issue-response evidence | `SA_CEM_9_26_2022_MJ_Issue_Adressing.docx` | contains the MJ comments plus Sajid-authored tracked insertions dated 2022-10-17 |
| Clean accepted/rejected text views | Pandoc outputs under `docx_markdown_accept/` and `docx_markdown_reject/` | avoids flattening unresolved tracked changes into one ambiguous text |
| Main branch PDF snapshots | top-level PDFs | useful for layout/export history, secondary to DOCX for editable text |
| Separate conceptual/physics note | `some_soul_wrenching_physics.docx` | long side document, not a manuscript successor |

## Revision Artifacts

DOCX comment/tracked-change counts:

| File | Comments | Tracked changes | Authors |
| --- | ---: | ---: | --- |
| `V1_CEM.docx` | 5 | 0 | comments by `Unknown Author` |
| `SA_CEM_9_26_2022_MJ.docx` | 10 | 181 | `Jens Meiler` |
| `SA_CEM_9_26_2022_MJ_Issue_Adressing.docx` | 10 | 238 | `Ahmed, Sajid`; `Jens Meiler` |
| all other top-level DOCX files | 0 | 0 | none detected |

Key MJ comments concern:

- adding affiliations/contact information;
- reporting quantitative performance metrics and improvements;
- figure shading/font/style cleanup;
- using traditional results headings and fewer subheadings;
- whether datasets are non-overlapping;
- combining low-content figures and formatting tables as tables.

Key Sajid-authored issue-addressing insertions in the latest file concern:

- adding interpretive text around Figure 4/feature-feature decorrelation;
- adding interpretive text around Figure 5/final feature-set correlations;
- inserting notes that a proposed wording change may distort meaning.

This is why `SA_CEM_9_26_2022_MJ_Issue_Adressing.docx` should be treated as
the latest annotated working state, not as a resolved final manuscript.

## PDF Relationship

PDFs appear to be export snapshots of the manuscript line:

| PDF | Relationship |
| --- | --- |
| `V1_PDF.pdf` | early export snapshot, smaller extracted text than `V1.docx` |
| `SA_9_20_2022.pdf` | export snapshot around the 2022-09-20/21 draft |
| `SA_9_20_2022_CEM.pdf` | text-identical to `SA_9_20_2022.pdf` by PDF extraction, but binary different |
| `SA_9_21_2022.pdf` | export snapshot of the 2022-09-21 line |
| `SA_9_23_2022_CEM.pdf` | export snapshot around CEM-stage edits |
| `SA_CEM_9_26_2022.pdf` | export snapshot around the 2022-09-26 clean CEM save |

For manuscript revival, use DOCX as the editable text source and PDFs as
layout/export provenance.

## Figure and Side Assets

Top-level PMPNN-DDG figure assets include:

- `System_Schematic.png`, `System_Diagram_One.png`, `System_Diagram_Two.png`
- `Vector_Extraction_Schematic.png`
- `Neighbor_Message_Norm_Ratio_Logic.png`
- `Neighbor_Embedding_Change_Norm_Logic.png`
- `S_921_Feature_Combinations.png`
- `Feature-Feature_Correlation.png`
- `Full_Feature_Set_PairWise_Correlation.png`
- `CN_NR_Encoding_Comparison.png`
- `Feature_Combinations_MultiPlot.png`

Side folders:

- `Soul_Wrenching_Physics/` contains physics/concept images dated mainly
  2022-10-08 to 2022-10-18 and relates to `some_soul_wrenching_physics.docx`.
- `ELI_CFTR/` contains `RE_Max_Normalized_Entropy.png`, dated 2022-10-29.

## Working Conclusion

For the next stage, preserve three manuscript states side by side:

1. `SA_CEM_9_26_2022.docx` as the clean pre-MJ manuscript base.
2. `SA_CEM_9_26_2022_MJ.docx` as advisor-comment provenance.
3. `SA_CEM_9_26_2022_MJ_Issue_Adressing.docx` as latest annotated
   issue-addressing provenance.

Do not collapse the MJ and issue-addressing files into a single "latest text"
without reviewing tracked changes/comments. That would erase exactly the
provenance signal this folder preserves.
