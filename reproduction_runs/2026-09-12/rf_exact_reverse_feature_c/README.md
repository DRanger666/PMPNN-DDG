# RF from extraction tensors — exact reverse Feature C (canonical)

Date: 2026-09-12  
Protocol: `--feature-c-reverse-mode exact_sum_inv` (default)

Reverse-row Feature C uses Eq. (2) after WT↔MT swap:
`Σ_j ‖M_j^MT‖/‖M_j^WT‖` (= `center_neighbor_weight_check_m_w`),
**not** the Digging/notebook shortcut `1/Σ_j r_j`.

That shortcut inflates a naive F+R stacked Feature-C↔label PCC via a scale cliff
(forward C ~15 vs reverse C ~0.07); it is **not** stronger ΔΔG information.
Manuscript Eq. (2) is the sum-of-ratios form; exact reverse is the consistent
choice. Historical `reciprocal_of_sum` remains available as a diagnostic CLI flag.

Baseline comparison (same tensors, historical reverse C):
`../rf_from_extraction_tensors/` (pre-fix).
