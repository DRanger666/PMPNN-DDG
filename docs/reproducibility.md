# Reproducibility

The public bar is **manuscript numbers**, regenerated from the published
extraction tensors:

```text
data/tensors/*.pickle  →  features A–H  →  RF / Figures 3–6  →  Tables 1–3
```

## What to expect

- `scripts/train_eval_rf.py` and the figure scripts are deterministic given the
  tensors, `--kpca-seed 0`, and `--n-runs 10`. Headline Table 1 values are in
  the top-level README; cell-by-cell comparison is [results-match.md](results-match.md).
- `scripts/extract.py` re-runs ProteinMPNN. Decoder order among fixed residues
  is stochastic, and Feature E uses a KernelPCA subsample, so a fresh extraction
  will **not** byte-match `data/tensors/`. That is expected. Do not treat pickle
  identity as a success criterion.

## Reference pickles

`data/historical/` holds original analysis dumps (column maps, historical
incremental RF series). They are not required to reproduce Table 1 from the
published tensors.
