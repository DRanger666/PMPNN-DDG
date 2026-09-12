# Reproduction Status (`reproduce-paper-results`)

Date: 2026-09-12  
Machine run directory: `reproduction_runs/2026-09-12/`  
Runtime: `.venv_proteinmpnn_ddg_reproduction/` (Python 3.12, CPU torch 2.6.0+cpu)

## Honest scope

Enough material exists to regenerate/verify the **results layer** (manuscript
Table 1 + Figure 6) from the saved RF pickle and notebook/image evidence, and to
diagnose the still-failing **V3 direct-tensor** segment on a small Ssym slice.

Not enough (yet) for guaranteed end-to-end:

```text
PDB + ProteinMPNN → V3 direct tensors → engineered features → RF → Table 1/Fig 6
```

without solving V3 tensor value-level regeneration.

## What matched on this machine

### Table 1 (results layer) — SUCCESS

Command:

```bash
./scripts/run_results_layer_reproduction.sh
# or:
.venv_proteinmpnn_ddg_reproduction/bin/python scripts/verify_table1_results_layer.py \
  --output-dir reproduction_runs/2026-09-12/table1_results_layer
```

Result:

| Evidence | Cells |
| --- | --- |
| Pickle ten-run means (`rF,rR,rF+R,rmsF,rmsR,rmsF+R`) | **18/18** match manuscript rounding |
| Notebook-output `rF-R` | **3/3** match manuscript rounding |
| **Total Table 1 numeric cells** | **21/21** |

Artifact: `reproduction_runs/2026-09-12/table1_results_layer/`

### Figure 6 (results layer) — SUCCESS

Same one-command runner regenerates:

- plotted S_669/Ssym incremental total-PCC series from
  `list_incremental_feature_result_dict.pickle` (exact means match prior
  milestone note);
- byte-identical PNG match of manuscript
  `Feature_Combinations_MultiPlot.png` to
  `source_repos/SajidAhmeduiu_ProteinMPNN/.../Quick_Dirty_MPNN_ML_V2_VGRAPHS_V1.ipynb`
  cell 40 / execution_count 58
  (SHA256 `9cec9fcf1d3f466b8bf0f1766bc98c20152b2c617c5d872d3e3588f79143da95`);
- DOCX maps Figure 6 → `media/image6.png` (embedded PNG not byte-identical;
  content equivalence already established historically).

Prerequisite for PNG byte-match: local clone of
`https://github.com/SajidAhmeduiu/ProteinMPNN` under
`source_repos/SajidAhmeduiu_ProteinMPNN/` (gitignored nested evidence clone).

Artifact: `reproduction_runs/2026-09-12/figure6_image_verification/`

### Ssym engineered/PSSM segment (saved tensors → features) — SUCCESS

```bash
.venv_proteinmpnn_ddg_reproduction/bin/python \
  scripts/test_ssym_engineered_feature_reconstruction.py \
  --output-dir reproduction_runs/2026-09-12/ssym_engineered_pssm_reconstruction
```

Result: **342/342** entries OK; **8208/8208** field comparisons allclose at
`atol=rtol=1e-6`; mismatches `0`; runtime errors `0`.

This proves saved-V3-tensor → engineered/PSSM only, not PDB→tensor.

## V3 direct-tensor diagnostics (still the hard blocker)

Command:

```bash
.venv_proteinmpnn_ddg_reproduction/bin/python \
  scripts/diagnose_ssym_v3_slice_rng_neighbor_replay.py \
  --limit 6 \
  --output-dir reproduction_runs/2026-09-12/v3_ssym_slice_diagnostics
```

Slice: first 6 Ssym V3 entries (`1amqA`×4 + `1bniA`×2), CPU, seed base `0`.

| Mode | top_15_neighbor exact | closest15 exact | log_prob allclose@1e-6 |
| --- | --- | --- | --- |
| `baseline` (per-mutation seed reset) | **0/6** | **6/6** | **0/6** |
| `continuous_rng` (seed once, no per-mut reset) | **0/6** | **6/6** | **0/6** |
| `replay_neighbors` (force saved top_15 indices) | **6/6** | **6/6** | **0/6** |

Additional observations on this slice:

- Closest-neighbor geometry remains solid in all modes (`top_15/10_closest` exact).
- Continuous RNG did **not** recover attended-neighbor ranking or `log_prob`.
- Neighbor-index replay recovers neighbor identity fields (`top_15/10/5`,
  `neighbor_aa_identities`) by construction, but **does not** recover
  `log_prob`, attention weights, neighbor log-probs, message vectors, or
  embeddings (all still 0/6 allclose).
- Baseline already had `top_5_neighbor_indices` exact on this tiny slice (6/6);
  that does not generalize to the historical full-Ssym `top_15` failure pattern.

Artifact: `reproduction_runs/2026-09-12/v3_ssym_slice_diagnostics/`

### Interpretation

The blocker remains upstream of engineered features:

```text
PDB + mutation table + ProteinMPNN weights/code + RNG/order behavior
  ↛  saved V3 direct tensor fields (value-level)
```

Especially: random decoder order among fixed residues, attended-neighbor ranking
by message norms, and possibly other unreconciled V6_V2 vs historical details.
Continuous RNG alone is insufficient on this slice; replaying saved neighbors
isolates that neighbor **identity** is not enough without matching center/neighbor
pass tensors.

## One-command results-layer path

```bash
# After creating .venv_proteinmpnn_ddg_reproduction (see RUNTIME_ENVIRONMENT.md)
# and cloning SajidAhmeduiu/ProteinMPNN into source_repos/ for Fig6 PNG match:
export REPRO_STAMP=2026-09-12   # optional; default is UTC date
./scripts/run_results_layer_reproduction.sh
```

Outputs land in `reproduction_runs/<stamp>/` with `reproduction_runs/latest` symlink.

## Exact remaining gaps vs full paper reproduction

1. **V3 direct tensors from PDB+ProteinMPNN** still fail value-level match
   (attended neighbors, log_probs, neighbor tensors). Geometry/closest-neighbors
   and schema traversal work.
2. **No end-to-end RF retrain** from regenerated features to Table 1 on this
   branch (results layer uses the saved ten-run RF pickle).
3. **S_669 / S_921 / S_2648** engineered-feature reconstruction and tensor
   extraction not re-proven here (Ssym feature segment only this run).
4. **Runtime rebuild spec** still incomplete (no root lockfile); venv recreated
   ad hoc on this machine with CPU torch + biopython/numpy/sklearn/matplotlib.
5. **ProteinMPNN utils** used from local
   `drive_evidence_copy/.../ProteinMPNN/vanilla_proteinmpnn/protein_mpnn_utils.py`
   (present on disk; nested `Protein_MPNN_Digging/ProteinMPNN/` tree is not the
   narrowly promoted LFS set). `source_repos/dauparas_ProteinMPNN` is a fallback
   clone path.
6. Nested evidence clones under `source_repos/` remain gitignored; Fig6 PNG
   byte-match needs the SajidAhmeduiu notebook clone locally.

## Next experiment

1. Expand continuous-RNG diagnostics to a longer sequential prefix that mirrors
   historical notebook protein/mutation order (not just first-N pickle order),
   recording RNG draw counts between center and neighbor passes.
2. Center-pass-only seed search / decoding-order capture for several mutations
   where a seed yields matching `top_15` **set** (historical `1amqA C191Y` seed
   98 hint), then freeze that order for neighbor passes.
3. Compare decoder message norms / local-48 slot mapping against saved
   `top_15_attention_weights` when neighbors are forced, to see whether the
   remaining gap is purely RNG or a codepath divergence (masking, featurize,
   checkpoint, utils version).

## Files added/updated on this branch for reproduction automation

- `scripts/run_results_layer_reproduction.sh`
- `scripts/verify_table1_results_layer.py`
- `scripts/diagnose_ssym_v3_slice_rng_neighbor_replay.py`
- `scripts/verify_figure6_image_basis.py` (skip missing notebooks)
- `scripts/analyze_incremental_feature_results.py` (skip missing one-run pickle)
- `proteinmpnn_ddg_recovery/recovered_v6v2.py` (`neighbor_indices_override` diagnostic hook)
- `reproduction_runs/2026-09-12/**`
- `REPRODUCTION_STATUS.md` (this file)
