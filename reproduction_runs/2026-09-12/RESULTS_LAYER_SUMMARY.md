# Results-Layer Reproduction (2026-09-12)

Commands:

```bash
./scripts/run_results_layer_reproduction.sh
```

## Outcomes on this machine

- **Table 1:** 21/21 numeric cells matched
  (`table1_results_layer/table1_verification_summary.json`).
- **Figure 6 numerics:** S_669/Ssym total-PCC series regenerated from the
  ten-run pickle (`figure6_image_verification/figure6_plotted_total_pcc_series.tsv`).
- **Figure 6 PNG:** byte-identical match to git notebook cell 40
  (`exact_matches=1` in `logs/verify_figure6_image_basis.log`).
- **Ssym engineered/PSSM (saved tensors):** 342/342 OK under
  `ssym_engineered_pssm_reconstruction/`.
- **V3 tensor slice diagnostics:** see `v3_ssym_slice_diagnostics/` and root
  `REPRODUCTION_STATUS.md`.

## Outputs

- `table1_results_layer/`
- `figure6_image_verification/`
- `incremental_feature_pickle_inspection/`
- `ssym_engineered_pssm_reconstruction/`
- `v3_ssym_slice_diagnostics/`
- `logs/`

Scope limit: final RF result / plotting evidence plus saved-tensor→feature and
V3 diagnostics. Does not regenerate V3 tensors from PDB+ProteinMPNN at
value-level match.
