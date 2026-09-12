# ProteinMPNN-DDG — `reproduce-paper-results`

This branch is the **manuscript-corresponding code path** for the bioRxiv preprint
**PMPNN-DDG** (DOI [10.64898/2026.08.23.746499](https://doi.org/10.64898/2026.08.23.746499);
co-first author Sajid Ahmed).

Goal: a clean, reviewable pipeline from PDB → ProteinMPNN extraction tensors →
features A–H → Random Forest train/eval / figures / tables whose **reported
numbers match the manuscript’s full results layer** (not only Table 1).

## Public reproducibility bar (non-negotiable)

```text
full extraction tensors  →  features  →  RF / figures / tables / audits
```

Every number in that chain — tensors, features, and everything derived — must be
**publicly available through this GitHub repo** (Git LFS for large pickles).
Compact RF-only pickles are a convenience subset, not a substitute for
publishing the full tensors they come from. Interim compact-based figure/RF
checks are fine while full runs finish; the branch is not done until the
published artifacts let a reviewer recompute those numbers from tensors upward.

## Manuscript results correspondence

Formal status (tables, figures, match/mismatch, how to re-run verification):

→ **[`manuscript_codebase_mapping/MANUSCRIPT_RESULTS_MATCH.md`](manuscript_codebase_mapping/MANUSCRIPT_RESULTS_MATCH.md)**

**Full extraction tensors (2026-09-12 20:04 UTC):** S669 present on LFS (S669_extraction_tensors.pickle)

**Regen RF status (2026-09-12 17:57 UTC):** Table1 7 match / 14 near / 0 mismatch of 21 (rounded-to-2dp vs BioRxiv); T2 S669=near; T3 Ssym=near; Fig6=8/8 combos within 0.02 abs of historical series (not bit-exact; trend retained). Details: [`MANUSCRIPT_RESULTS_MATCH.md`](manuscript_codebase_mapping/MANUSCRIPT_RESULTS_MATCH.md).

**Full extraction / public bar (2026-09-12 20:27 UTC):** Ssym+S2648+S669 full tensors+features-from-full on LFS (S669 638 after 2jieA recover); S921 full in progress; Fig3 from S2648 full tensors.

**Figs 3–5 status (2026-09-12 19:23 UTC):** Fig3 from full S2648 tensors (msg NR match; emb CN/msg CN near; emb NR Δ≈0.02); Figs4–5 still interim compact — re-run from full-tensor features next.

That document is the branch’s source of truth for correspondence. Historical
recovery notes (pickle/notebook provenance) remain under
`manuscript_codebase_mapping/` and are linked from there; they are not a
substitute for end-to-end regenerated-pipeline match.

| Artifact | Role | Verification target |
| --- | --- | --- |
| Table 1 | Independent-test metrics (S669, Ssym, S921) | Regenerated RF eval |
| Table 2 | S669 vs external methods | PMPNN-DDG row from RF; externals = literature |
| Table 3 | Ssym vs external methods | PMPNN-DDG row from RF; externals = literature |
| Figure 6 | Incremental feature contribution (S669/Ssym) | Regenerated incremental RF series |
| Figures 3–5 | S2648 training-set feature analyses | Regenerated from train features |
| Figures 1–2 | Schematics | Not numeric |

Dataset roles: [`manuscript_codebase_mapping/TRAIN_TEST_FIGURE_TABLE_ANCHOR.md`](manuscript_codebase_mapping/TRAIN_TEST_FIGURE_TABLE_ANCHOR.md).

## Pipeline (this branch)

```text
PDB + mutation tables + PSSM
  → modified_proteinmpnn/   (extraction hooks)
  → extraction tensors      (log-probs, attended neighbors, messages, embeddings, …)
  → proteinmpnn_ddg_recovery/features/   (dedicated Feature A–H functions)
  → RF train on S2648 (+ reverse augmentation as in manuscript)
  → eval on S669 / Ssym / S921
  → MANUSCRIPT_RESULTS_MATCH.md
```

Entry points:

- `scripts/run_pdb_to_features_pipeline.py` — PDB→tensors/features (`--save-mode full|both|rf_compact`)
- `scripts/train_eval_rf_from_v3_features.py` — RF train/eval from feature pickles
- `scripts/verify_table1_results_layer.py` / `scripts/verify_figure6_image_basis.py` — historical result-layer checks

Default **`--save-mode full`** (or `both`). Full extraction tensors are the
scientific source of truth and must land on LFS. Compact-only is for explicit
throwaway smoke tests — never the published end state.

## Regenerated artifacts (2026-09-12)

| Kind | Location |
| --- | --- |
| Compact RF features | `reproduction_inputs/pmpnn_ddg_features_2026-09-12/` |
| Full extraction tensors | `reproduction_inputs/pmpnn_ddg_extraction_tensors_2026-09-12/` |
| Naming map (BioRxiv → variables) | `manuscript_codebase_mapping/MANUSCRIPT_TO_VARIABLE_NAMING.md` |
| Extraction / feature schema | `proteinmpnn_ddg_recovery/SCHEMA.md` |

Large pickles are tracked with **Git LFS**.

## Integrity (unprocessable mutations)

Dataset-specific gaps are **not** silent drops. Every unprocessable mutation is
audited with class, justification, and impact counts:

→ [`manuscript_codebase_mapping/UNPROCESSABLE_MUTATIONS_AND_DATASET_GAPS.md`](manuscript_codebase_mapping/UNPROCESSABLE_MUTATIONS_AND_DATASET_GAPS.md)

Machine-readable tables: `manuscript_codebase_mapping/tables/unprocessable_mutations.{tsv,json}`.

Independent re-fetches of problem PDBs: `reproduction_inputs/independent_pdb_fetches/`.

## Mapping & recovery notes

Broader provenance and historical recovery live under
[`manuscript_codebase_mapping/README.md`](manuscript_codebase_mapping/README.md).
Operational boundary (what is recovered vs still open):
[`workspace_operations/CURRENT_RECOVERY_BOUNDARY.md`](workspace_operations/CURRENT_RECOVERY_BOUNDARY.md).

## Open items (branch work)

- Finish full extraction tensors for S2648 / S669 / S921 (Ssym done).
- Promote remaining feature/tensor pickles via LFS as they complete.
- RF retrain/eval on regenerated features; fill **MANUSCRIPT_RESULTS_MATCH.md**.
- Feature B weighting vs manuscript equation — treat as an open fidelity question
  until deliberately classified (see mapping notes).
