# ProteinMPNN-DDG — `reproduce-paper-results`

Manuscript-corresponding reproduction of bioRxiv **PMPNN-DDG**
(DOI [10.64898/2026.08.23.746499](https://doi.org/10.64898/2026.08.23.746499);
co-first author Sajid Ahmed).

**Git history on this repository starts 2026-05-06**, three and a half months
before the preprint (bioRxiv 2026-08-23 / posted 2026-08-27). See
[the first commit](https://github.com/dRanger666/PMPNN-DDG/commit/ddd89dfd9b9a8b79c44c0acec4660fb3f7367d23)
and the [full commit list](https://github.com/dRanger666/PMPNN-DDG/commits/main)
(143 commits; 67 dated before the preprint). This is a reconstruction of
the 2022 analysis, versioned in git from May 2026. GitHub's "Created" date on
*this URL* is 2026-09-12 (when the public mirror was opened); it is not the
start of the work.

```text
PDB → extraction tensors → ProteinMPNN features A–E + PSSM features F–H
    → Figures 3–5 / Random Forest → Tables 1–3 + Figure 6
```

Formal cell-by-cell tallies:
[`manuscript_codebase_mapping/MANUSCRIPT_RESULTS_MATCH.md`](manuscript_codebase_mapping/MANUSCRIPT_RESULTS_MATCH.md).

---

## Reproduced tables and figures

All numbers below come from the **public extraction-tensor path** on this branch
(2026-09-12), with reverse Feature C = manuscript Eq. (2) `Σ 1/r_j`
(`exact_sum_inv`). Not Digging pickle replay; not notebook `1/Σ` reverse C.

| Manuscript artifact | What it is | Regenerated verdict | Where to look |
| --- | --- | --- | --- |
| **Table 1** | S669 / Ssym / S921 independent-test metrics | **5 match / 15 near / 1 mismatch** of 21 (2 d.p., `notebook_table1`; exact reverse C) | [`ours_vs_paper_table1.tsv`](reproduction_runs/2026-09-12/rf_exact_reverse_feature_c/ours_vs_paper_table1.tsv) |
| **Table 2** | S669 vs external methods (PMPNN-DDG row) | **near** (same RF as Table 1 S669) | same RF run; externals = literature |
| **Table 3** | Ssym vs external methods (PMPNN-DDG row) | **near** (same RF as Table 1 Ssym) | same RF run; externals = literature |
| **Figure 6** | Incremental A→H total-PCC (S669 / Ssym) | **5 / 8** combos within 0.02 both sets (13/16 cells); exact reverse C | [`rf_per_run_metrics.json`](reproduction_runs/2026-09-12/rf_exact_reverse_feature_c/rf_per_run_metrics.json) |
| **Figure 3** | NR vs CN for messages (C) and neighbor embeddings (D) on S2648 | message NR **match**; others **near**; neighbor-embedding NR Δ≈0.02 | [PNG](reproduction_runs/2026-09-12/s2648_train_feature_figures/figure3_norm_ratio_vs_change_norm.png) · [claims](reproduction_runs/2026-09-12/s2648_train_feature_figures/figure3_claim_comparison.tsv) |
| **Figure 4** | S2648 feature–feature correlations (A–E) | **5 match / 6 near / 2 mismatch** of 13 at `kpca_seed=0` | [PNG](reproduction_runs/2026-09-12/s2648_train_feature_figures/figure4_feature_feature_correlation.png) · [claims](reproduction_runs/2026-09-12/s2648_train_feature_figures/figure45_claim_comparison.tsv) |
| **Figure 5** | S2648 feature–feature / feature–label (A–H) | same tallies as Fig 4 family | [PNG](reproduction_runs/2026-09-12/s2648_train_feature_figures/figure5_feature_feature_correlation.png) · [claims](reproduction_runs/2026-09-12/s2648_train_feature_figures/figure45_claim_comparison.tsv) |
| Figures 1–2 | Method schematics | non-numeric | — |

Dataset roles (train vs test per figure/table):
[`TRAIN_TEST_FIGURE_TABLE_ANCHOR.md`](manuscript_codebase_mapping/TRAIN_TEST_FIGURE_TABLE_ANCHOR.md).

### Table 1 — headline metrics (`notebook_table1`, 2 d.p.)

| Dataset | Manuscript rF+R | Regenerated rF+R | Manuscript rmsF+R | Regenerated rmsF+R |
| --- | ---: | ---: | ---: | ---: |
| S669 | 0.64 | **0.64** | 1.45 | 1.46 (near) |
| Ssym | 0.81 | **0.82** (near) | 1.10 | 1.09 (near) |
| S921 | 0.79 | **0.80** (near) | 1.49 | 1.48 (near) |

Full 21-cell grid (rF, rR, rF+R, rF-R, rms*): see
[`MANUSCRIPT_RESULTS_MATCH.md`](manuscript_codebase_mapping/MANUSCRIPT_RESULTS_MATCH.md#table-1--independent-test-performance-pmpnn-ddg)
and [`ours_vs_paper_table1.tsv`](reproduction_runs/2026-09-12/rf_exact_reverse_feature_c/ours_vs_paper_table1.tsv).

RF protocol: train on S2648 (+ forward/reverse augmentation); Feature B
`historical_weighted`; reverse Feature C **`exact_sum_inv`** (Eq. 2; not notebook
`1/Σ`); KPCA seed 0; S669 ΔΔG sign flip. Run directory:
[`reproduction_runs/2026-09-12/rf_exact_reverse_feature_c/`](reproduction_runs/2026-09-12/rf_exact_reverse_feature_c/).

### Figure 6 — incremental feature contribution

10-run mean rF+R for combos A … A–H on S669 and Ssym under **exact reverse C**.
**5/8** combos within 0.02 on both datasets (13/16 cells); S669 mid-combos that
include C sit just past 0.02 vs Digging. Detail table:
[`MANUSCRIPT_RESULTS_MATCH.md`](manuscript_codebase_mapping/MANUSCRIPT_RESULTS_MATCH.md#figure-6--incremental-feature-contribution).

### Figures 3–5 — S2648 training analyses (no RF)

| Figure | Regenerated file | Verdict (short) |
| --- | --- | --- |
| **3** | [`figure3_norm_ratio_vs_change_norm.png`](reproduction_runs/2026-09-12/s2648_train_feature_figures/figure3_norm_ratio_vs_change_norm.png) | Message NR \|r\|≈0.15 **match**; message CN / neighbor-embedding CN **near**; neighbor-embedding NR 0.28 vs notebook 0.26 |
| **4** | [`figure4_feature_feature_correlation.png`](reproduction_runs/2026-09-12/s2648_train_feature_figures/figure4_feature_feature_correlation.png) | 5 / 6 / 2 of 13 at `kpca_seed=0` |
| **5** | [`figure5_feature_feature_correlation.png`](reproduction_runs/2026-09-12/s2648_train_feature_figures/figure5_feature_feature_correlation.png) | same claim set |

Fig 4–5 residual \|Δ\|≈0.02 cells (e.g. E3↔ΔΔG, E2↔E4) track **KernelPCA
subsample stochasticity**, not a Feature A–H bug — seed sweep in
[`FIGURE45_KPCA_SUBSAMPLE_SENSITIVITY.md`](manuscript_codebase_mapping/FIGURE45_KPCA_SUBSAMPLE_SENSITIVITY.md)
([`kpca_seed_probe.log`](reproduction_runs/2026-09-12/s2648_train_feature_figures/kpca_seed_probe.log)).

---

## Public reproducibility bar

```text
extraction tensors → features (A–H) → RF / figures / tables / audits
```

Every number in that chain is on this GitHub branch (Git LFS for large pickles).
Reviewers recompute from published tensors upward. Compact feature tables are a
convenience; they do not replace extraction tensors.

**Coverage:** Ssym 342/342; S2648 **2647/2648**; S669 **638/669**; S921 921/921.
Gaps are audited (not silent drops) — see [Integrity](#integrity-unprocessable-mutations).

**Not the bar:** byte-identical historical Digging V3 pickles (stochastic decoder
order / KernelPCA). Stance:
[`REPRODUCTION_BAR_NOT_BYTE_IDENTICAL_V3.md`](manuscript_codebase_mapping/REPRODUCTION_BAR_NOT_BYTE_IDENTICAL_V3.md).

---

## Pipeline and how to regenerate

```text
PDB + mutation tables + PSSM
  → modified_proteinmpnn/              (extraction hooks)
  → extraction tensors                 (§3.1 intermediates + A–H fields)
  → proteinmpnn_ddg_recovery/features/ (Feature A–H)
  → Figs 3–5 (S2648; no RF)
  → RF train S2648 → eval S669 / Ssym / S921
  → Tables 1–3, Figure 6
```

| Step | Script |
| --- | --- |
| PDB → tensors / features | `scripts/run_pdb_to_features_pipeline.py` (`--save-mode full` or `both`) |
| Figure 3 | `scripts/regenerate_s2648_figure3_from_full_tensors.py` |
| Figures 4–5 | `scripts/regenerate_s2648_train_feature_figures.py` |
| RF → Tables 1–3 / Fig 6 | `scripts/train_eval_rf_from_v3_features.py` with extraction-tensor overrides; default `--feature-c-reverse-mode exact_sum_inv` |

Default save mode is **`full`** (or `both`). Extraction tensors are the source of
truth.

---

## Published inputs and outputs

| Kind | Location |
| --- | --- |
| ACCRE PDB + PSSM dirs | [`reproduction_inputs/accre_dataset_pdb_pssm/`](reproduction_inputs/accre_dataset_pdb_pssm/) |
| Mutation / ΔΔG tables | `reproduction_inputs/mutation_ddg_tables/` |
| ProteinMPNN checkpoint | `reproduction_inputs/proteinmpnn_checkpoints/` |
| Extraction tensors (LFS) | [`reproduction_inputs/pmpnn_ddg_extraction_tensors_2026-09-12/`](reproduction_inputs/pmpnn_ddg_extraction_tensors_2026-09-12/) |
| Feature tables A–H (LFS) | [`reproduction_inputs/pmpnn_ddg_features_2026-09-12/`](reproduction_inputs/pmpnn_ddg_features_2026-09-12/) |
| Fig 3–5 PNGs + claim TSVs | [`reproduction_runs/2026-09-12/s2648_train_feature_figures/`](reproduction_runs/2026-09-12/s2648_train_feature_figures/) |
| RF / Table 1 / Fig 6 metrics (exact reverse C) | [`reproduction_runs/2026-09-12/rf_exact_reverse_feature_c/`](reproduction_runs/2026-09-12/rf_exact_reverse_feature_c/) |
| RF baseline (historical `1/Σ` reverse C) | [`reproduction_runs/2026-09-12/rf_from_extraction_tensors/`](reproduction_runs/2026-09-12/rf_from_extraction_tensors/) |
| Historical Digging pickles (reference only) | [`reproduction_inputs/historical_reference_pickles/`](reproduction_inputs/historical_reference_pickles/) |
| BioRxiv → variable names | [`MANUSCRIPT_TO_VARIABLE_NAMING.md`](manuscript_codebase_mapping/MANUSCRIPT_TO_VARIABLE_NAMING.md) |
| RF packing (71→41; Feature E cols) | [`rf_feature_matrix_packing.py`](proteinmpnn_ddg_recovery/features/rf_feature_matrix_packing.py) |

`drive_evidence_copy/` is **not** on this branch (Drive/Colab/manuscript mirrors
stay on [`main`](https://github.com/DRanger666/ProteinMPNN-DDG/tree/main)).

---

## Integrity (unprocessable mutations)

→ [`UNPROCESSABLE_MUTATIONS_AND_DATASET_GAPS.md`](manuscript_codebase_mapping/UNPROCESSABLE_MUTATIONS_AND_DATASET_GAPS.md)
· tables: `manuscript_codebase_mapping/tables/unprocessable_mutations.{tsv,json}`

Known regen gaps include S2648 `2a01A` and S669 `3dv0I` (missing PSSM). Independent
PDB fetches: `reproduction_inputs/independent_pdb_fetches/`.

---

## Branch roles

| Branch | Role |
| --- | --- |
| **`reproduce-paper-results`** (this) | Living manuscript pipeline + regenerated Tables 1–3 / Figures 3–6 |
| **[`main`](https://github.com/DRanger666/ProteinMPNN-DDG/tree/main)** | Historical recovery archive (inventories, Drive evidence, Digging dumps) |

Evidence / match docs for *this* pipeline live under
[`manuscript_codebase_mapping/`](manuscript_codebase_mapping/README.md)
(`MANUSCRIPT_RESULTS_MATCH`, integrity, KPCA probe, fidelity, naming). Inventory
archaeology was pruned here on purpose.

---

## Still open

- **Feature B** weighting vs manuscript Eq. 1 — still needs a deliberate call; RF uses historical weighted B for now ([fidelity notes](manuscript_codebase_mapping/MANUSCRIPT_TENSOR_EXTRACTION_FIDELITY.md))
- Optional **manuscript** one-liner on KernelPCA subsample sensitivity for Figs 4–5 (suggested text in [`FIGURE45_KPCA_SUBSAMPLE_SENSITIVITY.md`](manuscript_codebase_mapping/FIGURE45_KPCA_SUBSAMPLE_SENSITIVITY.md))
- Public repo is [github.com/dRanger666/PMPNN-DDG](https://github.com/dRanger666/PMPNN-DDG)
- Do not merge this PR until ownership/review is agreed
