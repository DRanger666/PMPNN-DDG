# Feature B diagnostic: manuscript-unweighted Eq. 1

Date: 2026-09-12

**Diagnostic only** — not the primary Table 1 comparison.

Replaces Feature B with unweighted `Σ_j (H(P_j^WT) − H(P_j^MT))` recomputed from
saved `w_n_log_prob` / `m_n_log_prob`, holding other features and
`notebook_table1` RF settings fixed. n_runs=3.

| Dataset | rF+R ours | paper | rmsF+R ours | paper |
| --- | ---: | ---: | ---: | ---: |
| S_669 | 0.6432 → 0.64 | 0.64 | 1.4535 → 1.45 | 1.45 |
| Ssym | 0.8099 → 0.81 | 0.81 | 1.1050 → 1.11 | 1.10 |
| S_921 | 0.7948 → 0.79 | 0.79 | 1.4936 → 1.49 | 1.49 |

Sensitivity is small vs `historical_weighted` on this short run. That supports
treating Feature B weighting as an **open fidelity / wording question**, not a
confirmed blocker for Table 1-level metrics. See
`manuscript_codebase_mapping/MANUSCRIPT_TENSOR_EXTRACTION_FIDELITY.md`.
