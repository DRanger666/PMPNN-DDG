# Results vs. the preprint

Cell-by-cell comparison of numbers regenerated from `data/tensors/` against
Sajid Ahmed and Md Rafsan Jani, bioRxiv [10.64898/2026.08.23.746499](https://doi.org/10.64898/2026.08.23.746499).

**Protocol.** `scripts/train_eval_rf.py --n-runs 10 --configs notebook_table1`
(Feature C reverse = Eq. 2; KPCA seed 0). Artifacts:
[`results/table1/`](../results/table1/), [`results/figures/`](../results/figures/).

**Verdicts.** *match* = equal at the paper’s rounding; *near* = off by 0.01;
*mismatch* = off by ≥ 0.02.

| Claim | Status | Notes |
| --- | --- | --- |
| Table 1 (21 cells) | 5 match / 15 near / 1 mismatch | mismatch = S921 rmsR 1.47 vs 1.49 |
| Table 2 (S669 row) | near | same RF as Table 1 S669 |
| Table 3 (Ssym row) | near | same RF as Table 1 Ssym |
| Figure 6 (A→H rF+R) | 5/8 combos within 0.02 on both sets | 13/16 cells |
| Figures 3–5 | Figure 3 message NR match; Figs 4–5 5/6/2 of 13 | KPCA subsample, [kpca-sensitivity.md](kpca-sensitivity.md) |

Coverage: S2648 2647/2648; S669 638/669; Ssym 342/342; S921 921/921
([dataset-gaps.md](dataset-gaps.md)).

## Table 1

| Dataset | Metric | Paper | This repo | Verdict |
| --- | --- | ---: | ---: | --- |
| S669 | rF | 0.48 | 0.47 | near |
| S669 | rR | 0.48 | 0.47 | near |
| S669 | rF+R | 0.64 | 0.64 | **match** |
| S669 | rF−R | −0.99 | −0.99 | **match** |
| S669 | rmsF | 1.45 | 1.46 | near |
| S669 | rmsR | 1.45 | 1.46 | near |
| S669 | rmsF+R | 1.45 | 1.46 | near |
| Ssym | rF | 0.72 | 0.73 | near |
| Ssym | rR | 0.72 | 0.72 | **match** |
| Ssym | rF+R | 0.81 | 0.82 | near |
| Ssym | rF−R | −0.99 | −0.99 | **match** |
| Ssym | rmsF | 1.10 | 1.09 | near |
| Ssym | rmsR | 1.10 | 1.09 | near |
| Ssym | rmsF+R | 1.10 | 1.09 | near |
| S921 | rF | 0.77 | 0.76 | near |
| S921 | rR | 0.77 | 0.76 | near |
| S921 | rF+R | 0.79 | 0.80 | near |
| S921 | rF−R | −1.00 | −1.00 | **match** |
| S921 | rmsF | 1.49 | 1.48 | near |
| S921 | rmsR | 1.49 | 1.47 | mismatch |
| S921 | rmsF+R | 1.49 | 1.48 | near |

Headlines (rF+R): S669 **0.64**; Ssym **0.82**; S921 **0.80**.

## Table 2 / Table 3 (PMPNN-DDG row)

Same RF as Table 1. Other methods in those tables are literature values and
are not re-run here.

| Table | Set | Paper | This repo |
| --- | --- | --- | --- |
| 2 | S669 | 0.48 / 0.48 / 0.64 / −0.99 / 1.45 | 0.47 / 0.47 / 0.64 / −0.99 / 1.46 |
| 3 | Ssym | 0.72 / 0.72 / 0.81 / −0.99 / 1.10 | 0.73 / 0.73 / 0.82 / −1.00 / 1.08–1.09 |

## Figure 6 — incremental A→H (rF+R)

| Combo | S669 this repo | S669 original | Δ | Ssym this repo | Ssym original | Δ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| A | 0.4865 | 0.4716 | +0.015 | 0.6607 | 0.6411 | +0.020 |
| A–B | 0.5222 | 0.5260 | −0.004 | 0.7155 | 0.7007 | +0.015 |
| A–C | 0.5562 | 0.5772 | −0.021 | 0.7360 | 0.7164 | +0.020 |
| A–D | 0.5801 | 0.6011 | −0.021 | 0.7498 | 0.7426 | +0.007 |
| A–E | 0.6154 | 0.6374 | −0.022 | 0.7864 | 0.7869 | −0.001 |
| A–F | 0.6359 | 0.6438 | −0.008 | 0.8081 | 0.8027 | +0.005 |
| A–G | 0.6362 | 0.6435 | −0.007 | 0.8129 | 0.8087 | +0.004 |
| A–H | 0.6367 | 0.6440 | −0.007 | 0.8170 | 0.8122 | +0.005 |

## Figures 3–5 (S2648)

Figure 3 from `data/tensors/S2648_extraction_tensors.pickle`. Figures 4–5 from
`data/features/S2648_features.pickle`, KPCA seed 0.

| Encoding (Fig. 3) | \|PCC\| vs ΔΔG | Paper | Verdict |
| --- | ---: | ---: | --- |
| neighbor-embedding NR | 0.28 | 0.26 | mismatch |
| neighbor-embedding CN | 0.32 | 0.31 | near |
| message NR (Feature C) | 0.15 | 0.15 | **match** |
| message CN | 0.04 | 0.03 | near |

| Claim (Figs 4–5) | Paper | This repo | Verdict |
| --- | ---: | ---: | --- |
| C vs ΔΔG | −0.15 | −0.15 | **match** |
| A vs B | 0.52 | 0.52 | **match** |
| E1 vs D | 0.49 | 0.49 | **match** |
| E2 vs D | 0.17 | 0.18 | near |
| E4 vs ΔΔG | 0.21 | 0.22 | near |
| E3 vs A | 0.55 | 0.54 | near |
| E3 vs B | 0.40 | 0.39 | near |
| E3 vs C | 0.55 | 0.54 | near |
| E3 vs ΔΔG | 0.26 | 0.24 | mismatch |
| E2 vs E4 | 0.20 | 0.18 | mismatch |
| F vs A | 0.32 | 0.32 | **match** |
| G vs A | 0.15 | 0.15 | **match** |
| H vs E1 | 0.39 | 0.38 | near |

Figure 4–5 residuals of 0.02 are KernelPCA subsample noise
([kpca-sensitivity.md](kpca-sensitivity.md)).
