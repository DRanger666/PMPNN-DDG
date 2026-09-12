# PMPNN-DDG

Random Forest predictor of the change in folding free energy (ΔΔG) caused by a
single-point mutation. Features come from
[ProteinMPNN](https://github.com/dauparas/ProteinMPNN) (A–E) and from PSSM
evolutionary scores (F–H).

**Paper:** Sajid Ahmed and Md Rafsan Jani,
[*PMPNN-DDG: an accurate machine learning-based ΔΔG prediction pipeline trained
on a novel interpretable feature set extracted from ProteinMPNN*](https://doi.org/10.64898/2026.08.23.746499),
bioRxiv (2026). DOI [10.64898/2026.08.23.746499](https://doi.org/10.64898/2026.08.23.746499).

On S669, PMPNN-DDG reports **r<sub>F+R</sub> = 0.64** and RMSE = 1.45. On Ssym,
**r<sub>F+R</sub> = 0.81**, r<sub>F−R</sub> = −0.99, RMSE = 1.10.

```text
PDB + PSSM  →  ProteinMPNN tensors  →  features A–H  →  Random Forest
                                                    ↘  Figures 3–5 (train set, no RF)
                 train: S2648     test: S669, Ssym, S921
```

## Features

| | Source | What it measures |
| --- | --- | --- |
| **A** | ProteinMPNN | Mutation-site log-probability ratio (WT vs MT) |
| **B** | ProteinMPNN | Neighbor entropy change |
| **C** | ProteinMPNN | Sum of neighbor→center message-norm ratios, Eq. (2) |
| **D** | ProteinMPNN | Sum of neighbor embedding-change norms |
| **E** | ProteinMPNN | KernelPCA of center→neighbor message-change vectors |
| **F, G, H** | PSSM | Evolutionary log-odds at the mutated site |

Training uses forward and reverse (F+R) augmentation of each mutation.

## Installation

Clone with [Git LFS](https://git-lfs.com) so the published tensors download:

```bash
git lfs install
git clone https://github.com/dRanger666/PMPNN-DDG.git
cd PMPNN-DDG
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Python 3.10+, NumPy, SciPy, scikit-learn, pandas, matplotlib. **No GPU and no
PyTorch** are required to regenerate Table 1 and Figures 3–5 from the published
tensors.

From-PDB extraction additionally needs PyTorch and Biopython
(`pip install -r requirements-extract.txt`) and the ProteinMPNN weights already
in [`data/checkpoints/`](data/checkpoints/).

## Reproduce Table 1

```bash
PYTHONPATH=. python scripts/train_eval_rf.py --n-runs 10 --configs notebook_table1
```

Defaults load `data/tensors/{S2648,S669,S921,Ssym}_extraction_tensors.pickle`
and write [`results/table1/`](results/table1/). Headline metric is r<sub>F+R</sub>.

| Test set | Paper r<sub>F+R</sub> | This repo | Paper RMSE | This repo |
| ---: | ---: | ---: | ---: | ---: |
| S669 | 0.64 | **0.64** | 1.45 | 1.46 |
| Ssym | 0.81 | 0.82 | 1.10 | 1.09 |
| S921 | 0.79 | 0.80 | 1.49 | 1.48 |

Cell-by-cell Table 1, Tables 2–3, and Figure 6: [`docs/results-match.md`](docs/results-match.md).

Coverage: Ssym 342/342, S921 921/921, S2648 2647/2648, S669 638/669
(missing PSSM; [`docs/dataset-gaps.md`](docs/dataset-gaps.md)).

### Figures 3–5 (S2648, no RF)

```bash
PYTHONPATH=. python scripts/figure3.py
PYTHONPATH=. python scripts/figures4_5.py
```

Outputs land in [`results/figures/`](results/figures/).

### Extract tensors from PDB (optional)

```bash
PYTHONPATH=. python scripts/extract.py --dataset Ssym --save-mode full
```

Uses [`modified_proteinmpnn/`](modified_proteinmpnn/) and
`data/checkpoints/vanilla_model_weights/v_48_020.pt`. ProteinMPNN’s decoder
order among fixed residues is stochastic, so a fresh extraction will not
byte-match the published pickles. The reproduction bar is manuscript metrics,
not pickle identity ([`docs/reproducibility.md`](docs/reproducibility.md)).

## Layout

```text
pmpnn_ddg/                 feature A–H code and ProteinMPNN extraction
modified_proteinmpnn/      ProteinMPNN fork (decoder-message hooks)
scripts/
  train_eval_rf.py         RF → Table 1 / Figure 6
  figure3.py, figures4_5.py
  extract.py               PDB → tensors / features
data/
  tensors/                 published extraction tensors (Git LFS)  ← Table 1
  features/                compact A–H tables (LFS)
  pdbs_pssm/               PDB coordinates + PSSMs
  mutations/               S2648 / S669 / Ssym / S921 mutation tables
  checkpoints/             ProteinMPNN v_48_020.pt (LFS)
  historical/              original analysis pickles (reference only)
results/                   regenerated tables and figures
docs/                      methods notes, fidelity, dataset gaps
```

## Citation

Please cite:

```
Sajid Ahmed, Md Rafsan Jani. PMPNN-DDG: an accurate machine learning-based
ΔΔG prediction pipeline trained on a novel interpretable feature set
extracted from ProteinMPNN. bioRxiv 2026.08.23.746499 (2026).
doi: 10.64898/2026.08.23.746499
```

ProteinMPNN: Dauparas et al., *Science* (2022). The `modified_proteinmpnn`
fork and weights follow that project’s license.

## Provenance

Git history on this repository starts
[2026-05-06](https://github.com/dRanger666/PMPNN-DDG/commit/ddd89dfd9b9a8b79c44c0acec4660fb3f7367d23),
before the preprint (posted 2026-08-27). GitHub’s “Created” date on the URL is
2026-09-12, when the repository was opened publicly; it is not the start of
the work. See [commits](https://github.com/dRanger666/PMPNN-DDG/commits/main).
