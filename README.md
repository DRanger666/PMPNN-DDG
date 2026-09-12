# ProteinMPNN-DDG — `reproduce-paper-results`

This branch is the **manuscript-corresponding code path** for the bioRxiv preprint
**PMPNN-DDG** (DOI [10.64898/2026.08.23.746499](https://doi.org/10.64898/2026.08.23.746499);
co-first author Sajid Ahmed).

Goal: a clean, reviewable pipeline

```text
PDB → extraction tensors → ProteinMPNN features A–E + PSSM features F–H
    → figures / Random Forest / tables
```

whose reported numbers match the manuscript’s **full results layer** (Tables 1–3,
Figures 3–6 — not only Table 1).

## Public reproducibility bar (non-negotiable)

```text
extraction tensors  →  features (A–H)  →  RF / figures / tables / audits
```

Every number in that chain must be **publicly available in this GitHub repo**
(Git LFS for large pickles). A reviewer should be able to recompute published
claims from the published tensors upward. Convenience feature tables are fine;
they do not replace publishing the extraction tensors.

**Status (2026-09-12):** All four datasets have extraction tensors and A–H
feature tables on LFS. Figs 3–5 and Tables 1–3 / Fig 6 have been regenerated
from that path. Formal tallies:
[`manuscript_codebase_mapping/MANUSCRIPT_RESULTS_MATCH.md`](manuscript_codebase_mapping/MANUSCRIPT_RESULTS_MATCH.md).

## Manuscript results correspondence

| Artifact | Role | Regenerated status (this branch) |
| --- | --- | --- |
| **Table 1** | S669 / Ssym / S921 independent-test metrics | **6 match / 15 near / 0 mismatch** of 21 (2dp, `notebook_table1`) |
| **Table 2** | S669 vs external methods | PMPNN-DDG row **near** (same as Table 1); externals = literature |
| **Table 3** | Ssym vs external methods | PMPNN-DDG row **near** (same as Table 1); externals = literature |
| **Figure 6** | Incremental feature contribution (S669/Ssym) | **7/8** combos within 0.02 of historical series |
| **Figure 3** | NR vs CN encodings for messages (C) and neighbor embeddings (D) | From S2648 extraction tensors; message NR **match**; others near / one Δ≈0.02 |
| **Figures 4–5** | S2648 feature–feature / feature–label correlations | **5 match / 6 near / 2 mismatch** of 13 at `kpca_seed=0`; residuals = KernelPCA subsample stochasticity ([experiment](manuscript_codebase_mapping/FIGURE45_KPCA_SUBSAMPLE_SENSITIVITY.md)) |
| Figures 1–2 | Schematics | Not numeric |

Dataset roles:
[`manuscript_codebase_mapping/TRAIN_TEST_FIGURE_TABLE_ANCHOR.md`](manuscript_codebase_mapping/TRAIN_TEST_FIGURE_TABLE_ANCHOR.md).

Historical pickle/notebook provenance notes under `manuscript_codebase_mapping/`
are not a substitute for this end-to-end regenerated match.

## Pipeline (this branch)

```text
PDB + mutation tables + PSSM
  → modified_proteinmpnn/                 (extraction hooks)
  → extraction tensors                    (§3.1 intermediates + A–H fields)
  → proteinmpnn_ddg_recovery/features/    (Feature A–H functions)
  → Figs 3–5 (S2648 train-set analyses; no RF)
  → RF train on S2648 (+ forward/reverse augmentation)
  → eval on S669 / Ssym / S921  →  Tables 1–3, Figure 6
  → MANUSCRIPT_RESULTS_MATCH.md
```

Entry points:

- `scripts/run_pdb_to_features_pipeline.py` — PDB → tensors/features (`--save-mode full|both|rf_compact`)
- `scripts/regenerate_s2648_figure3_from_full_tensors.py` — Figure 3 from S2648 extraction tensors
- `scripts/regenerate_s2648_train_feature_figures.py` — Figures 4–5 correlations
- `scripts/train_eval_rf_from_v3_features.py` — RF train/eval (use extraction-tensor overrides for the public path)
- `scripts/verify_table1_results_layer.py` / `scripts/verify_figure6_image_basis.py` — historical result-layer checks

Default **`--save-mode full`** (or `both`). Extraction tensors are the scientific
source of truth. Compact-only is for throwaway smoke tests — not the published
end state.

## Published artifacts (2026-09-12)

| Kind | Location | Coverage |
| --- | --- | --- |
| Extraction tensors | `reproduction_inputs/pmpnn_ddg_extraction_tensors_2026-09-12/` | Ssym 342; S2648 **2647/2648**; S669 **638/669**; S921 921 |
| ProteinMPNN + PSSM feature tables (A–H) | `reproduction_inputs/pmpnn_ddg_features_2026-09-12/` | Same coverage; `*_proteinmpnn_and_pssm_features.pickle` symlinks |
| Fig 3–5 outputs | `reproduction_runs/2026-09-12/s2648_train_feature_figures/` | PNGs, claim TSVs, KPCA seed-probe log |
| RF from extraction tensors | `reproduction_runs/2026-09-12/rf_from_extraction_tensors/` | Tables 1–3 / Fig 6 metrics |
| Naming map (BioRxiv → variables) | `manuscript_codebase_mapping/MANUSCRIPT_TO_VARIABLE_NAMING.md` | |
| Extraction / feature schema | `proteinmpnn_ddg_recovery/SCHEMA.md` | |
| RF packing (71→41; Feature E columns) | `proteinmpnn_ddg_recovery/features/rf_feature_matrix_packing.py` | |

Large pickles are tracked with **Git LFS**.

## Integrity (unprocessable mutations)

Dataset-specific gaps are **not** silent drops. Every unprocessable mutation is
audited with class, justification, and impact counts:

→ [`manuscript_codebase_mapping/UNPROCESSABLE_MUTATIONS_AND_DATASET_GAPS.md`](manuscript_codebase_mapping/UNPROCESSABLE_MUTATIONS_AND_DATASET_GAPS.md)

Machine-readable tables: `manuscript_codebase_mapping/tables/unprocessable_mutations.{tsv,json}`.

Known coverage limits on this regen: S2648 `2a01A` (missing PSSM); S669 gaps
including `3dv0I` (missing PSSM) — see the audit. Independent PDB re-fetches:
`reproduction_inputs/independent_pdb_fetches/`.

## Mapping & recovery notes

Broader provenance and historical recovery:
[`manuscript_codebase_mapping/README.md`](manuscript_codebase_mapping/README.md).

Fig 4–5 KernelPCA subsample experiment (repo burden; suggested manuscript caveat):
[`manuscript_codebase_mapping/FIGURE45_KPCA_SUBSAMPLE_SENSITIVITY.md`](manuscript_codebase_mapping/FIGURE45_KPCA_SUBSAMPLE_SENSITIVITY.md).

Older coordination note (may lag this README on regen status):
[`workspace_operations/CURRENT_RECOVERY_BOUNDARY.md`](workspace_operations/CURRENT_RECOVERY_BOUNDARY.md).

## Open items

Done on this branch (do not treat as open):

- [x] Extraction tensors for Ssym / S2648 / S669 / S921 on LFS
- [x] ProteinMPNN A–E + PSSM F–H feature tables on LFS
- [x] Figures 3–5 from the published tensor/feature path
- [x] RF train/eval → Tables 1–3 + Figure 6 match write-up
- [x] Document Fig 4–5 residual |Δ|≈0.02 as KernelPCA subsample stochasticity

Still open / author decisions:

- [ ] **Feature B** weighting vs manuscript Eq. 1 — classify deliberately (fidelity notes); RF currently uses historical weighted B
- [ ] Optional **manuscript** one-liner that Feature E / Figs 4–5 PCCs can vary slightly with the KernelPCA training subsample (suggested text in `FIGURE45_KPCA_SUBSAMPLE_SENSITIVITY.md`) — not the 2026 re-fit chronology
- [ ] Public `github.com/dRanger666/PMPNN-DDG` cited in the paper still does not exist (out of scope until confirmed)
- [ ] Do not merge PR until ownership/review agreed
