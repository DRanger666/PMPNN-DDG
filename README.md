# PMPNN-DDG

Random Forest ΔΔG predictor trained on interpretable features extracted from
[ProteinMPNN](https://github.com/dauparas/ProteinMPNN) (A–E) plus PSSM
evolutionary features (F–H).

Paper: Ahmed et al., *PMPNN-DDG*, bioRxiv
[10.64898/2026.08.23.746499](https://doi.org/10.64898/2026.08.23.746499)
(2026-08-23; posted 2026-08-27).

This repository is the public code and data for that paper.
**Git history starts 2026-05-06**
([first commit](https://github.com/dRanger666/PMPNN-DDG/commit/ddd89dfd9b9a8b79c44c0acec4660fb3f7367d23)) —
before the preprint. GitHub’s “Created” date on this URL is 2026-09-12 (when
the public mirror was opened), not the start of the work.
See [commits](https://github.com/dRanger666/PMPNN-DDG/commits/main).

```text
PDB + PSSM  →  ProteinMPNN tensors  →  features A–H  →  RF  →  Tables 1–3, Figure 6
                                                    ↘  Figures 3–5 (S2648, no RF)
```

## Results (regenerated from published tensors)

Train on S2648 with forward/reverse augmentation; evaluate S669, Ssym, S921.
Reverse Feature C is manuscript Eq. (2) `Σ_j 1/r_j`. Ten RF runs, `kpca_seed=0`.

| Set | Paper rF+R | This repo | Paper RMSE | This repo |
| ---: | ---: | ---: | ---: | ---: |
| S669 | 0.64 | **0.64** | 1.45 | 1.46 |
| Ssym | 0.81 | 0.82 | 1.10 | 1.09 |
| S921 | 0.79 | 0.80 | 1.49 | 1.48 |

Full 21-cell Table 1 grid, Figure 6 combos, and figure claim tables:
[`docs/results-match.md`](docs/results-match.md),
[`results/table1/`](results/table1/),
[`results/figures/`](results/figures/).

Coverage: Ssym 342/342, S921 921/921, S2648 2647/2648, S669 638/669
(missing PSSM; audited in [`docs/dataset-gaps.md`](docs/dataset-gaps.md)).

## Layout

| Path | Contents |
| --- | --- |
| [`pmpnn_ddg/`](pmpnn_ddg/) | Feature A–H code and ProteinMPNN extraction |
| [`modified_proteinmpnn/`](modified_proteinmpnn/) | ProteinMPNN fork with decoder-message hooks |
| [`scripts/extract.py`](scripts/extract.py) | PDB → tensors / features |
| [`scripts/train_eval_rf.py`](scripts/train_eval_rf.py) | RF → Table 1 / Figure 6 |
| [`scripts/figure3.py`](scripts/figure3.py) / [`figures4_5.py`](scripts/figures4_5.py) | S2648 figures |
| [`data/tensors/`](data/tensors/) | Published extraction tensors (LFS) |
| [`data/pdbs_pssm/`](data/pdbs_pssm/), [`data/mutations/`](data/mutations/), [`data/checkpoints/`](data/checkpoints/) | Inputs for from-PDB extraction |
| [`results/`](results/) | Regenerated tables and figures |
| [`docs/`](docs/) | Methods notes, fidelity, dataset gaps |

## Install

Needs [Git LFS](https://git-lfs.com) (`git lfs install` then clone).

**Table 1 / figures from published tensors** (no GPU, no PyTorch):

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

From-PDB extraction also needs PyTorch, Biopython, and the ProteinMPNN weights
already in `data/checkpoints/` (LFS). See `requirements-extract.txt`.

## Reproduce Table 1

```bash
PYTHONPATH=. python scripts/train_eval_rf.py \
  --n-runs 10 --configs notebook_table1 \
  --feature-c-reverse-mode exact_sum_inv \
  --feature-b-mode historical_weighted \
  --kpca-seed 0 --output-dir results/table1
```

Defaults load `data/tensors/{S2648,S669,S921,Ssym}_extraction_tensors.pickle`.
Headline metric is rF+R. The `1/Σ` reverse-C diagnostic lives in
[`results/table1_reciprocal_sum_C/`](results/table1_reciprocal_sum_C/).

Figures 3–5:

```bash
PYTHONPATH=. python scripts/figure3.py
PYTHONPATH=. python scripts/figures4_5.py
```

## Extract from PDB (optional)

```bash
PYTHONPATH=. python scripts/extract.py --dataset Ssym --save-mode full
```

Uses `modified_proteinmpnn` + `data/checkpoints/vanilla_model_weights/v_48_020.pt`.
Decoder order is stochastic; byte-identical historical pickles are not the bar
([`docs/reproducibility.md`](docs/reproducibility.md)).

## Citation

Please cite the preprint (full author list there):

```
Ahmed et al. PMPNN-DDG: an accurate machine learning-based ΔΔG prediction
pipeline trained on a novel interpretable feature set extracted from
ProteinMPNN. bioRxiv 10.64898/2026.08.23.746499 (2026).
```

ProteinMPNN: Dauparas et al., *Science* (2022). Weights and the `modified_proteinmpnn`
fork follow that project’s license.
