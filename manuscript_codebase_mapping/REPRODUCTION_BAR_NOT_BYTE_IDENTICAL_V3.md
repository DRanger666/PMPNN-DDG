# Reproduction bar: manuscript numbers, not byte-identical V3

Date: 2026-09-12  
Branch: `reproduce-paper-results`

## Retired goal

**`v3_tensor_extraction_reconciliation` is not a valid success criterion on this
branch.**

An earlier recovery track treated closeness (or bit/byte identity) to historical
Digging **V3** extraction pickles (`*_pmppn_info_dict_V3.pickle`) as the
upstream target. That framing is **retired**.

It is **not logical** to expect regenerated extraction tensors to be
byte-identical to those 2022-era V3 dumps. Stochastic pieces in the pipeline
(decoder order / RNG among fixed residues, KernelPCA subsample for Feature E,
and related operational choices) mean value-level drift at the tensor layer is
expected even when the scientific method is the same.

The reconciliation tree was removed from this branch (git history only). Do not
reopen it as an open milestone.

## Current bar (authoritative)

```text
PDB → extraction tensors → ProteinMPNN A–E + PSSM F–H features
    → Figures 3–5 / RF → Tables 1–3 + Figure 6
```

Success is judged by:

1. **Manuscript correspondence** — regenerated metrics and figure claims vs the
   bioRxiv numbers (see `MANUSCRIPT_RESULTS_MATCH.md`).
2. **Rational mismatch probing** — when a cell is near or off, explain it with
   a deliberate experiment (e.g. KernelPCA subsample seed sweep in
   `FIGURE45_KPCA_SUBSAMPLE_SENSITIVITY.md`), not by chasing V3 pickle bytes.
3. **Public chain** — every number from tensors upward on GitHub LFS.

Historical V3 pickles remain **reference artifacts** for naming, column maps,
and recovery archaeology. They are **not** the regeneration oracle.

## What to say / not say

| Prefer | Avoid |
| --- | --- |
| “Matches / near manuscript Table 1 at 2dp; residual explained by …” | “Failed to reconcile to V3 tensors” |
| “Open fidelity question (Feature B wording)” | “Must bit-match `log_prob` to historical V3” |
| “KernelPCA subsample stochasticity” | “V3 extraction still unresolved” |

Related: `REGENERATED_FEATURES_VS_HISTORICAL_V3.md` (naming),
`MANUSCRIPT_TENSOR_EXTRACTION_FIDELITY.md` (open scientific questions),
branch `README.md`.
