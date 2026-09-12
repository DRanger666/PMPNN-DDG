# Train / test split for each table and figure

S2648 is the training set. S669, Ssym, and S921 are held-out test sets.

## Figures

| Figure | Data | Role |
| --- | --- | --- |
| 1 | all sets | Pipeline schematic (non-numeric) |
| 2 | — | Feature-extraction schematic (non-numeric) |
| 3 | S2648 only | Message vs embedding norm-ratio / change-norm |
| 4 | S2648 only | Feature–feature correlations A–E |
| 5 | S2648 only | Feature–feature correlations A–H |
| 6 | train S2648 → eval S669 and Ssym | Incremental A→H contribution (rF+R) |

## Tables

| Table | Data | Role |
| --- | --- | --- |
| 1 | S669, Ssym, S921 | Independent-test metrics |
| 2 | S669 | External-method comparison (PMPNN-DDG row = Table 1) |
| 3 | Ssym | External-method comparison (PMPNN-DDG row = Table 1) |

Figures 3–5 must not be matched against test-set numbers. Figure 6 and Tables
1–3 must not be used as evidence that a feature was *chosen* on the test sets.
