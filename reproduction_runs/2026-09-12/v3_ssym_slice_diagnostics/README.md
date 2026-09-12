# Ssym V3 Slice RNG / Neighbor-Replay Diagnostics

Entries: `6` (limit=6, seed=0, device=cpu)

## Headline Match Counts

| Mode | top_15_neighbor exact | closest15 exact | log_prob allclose@1e-6 |
| --- | --- | --- | --- |
| `baseline` | 0/6 | 6/6 | 0/6 |
| `continuous_rng` | 0/6 | 6/6 | 0/6 |
| `replay_neighbors` | 6/6 | 6/6 | 0/6 |

## Interpretation Guardrails

- `continuous_rng` tests notebook-style continuous RNG consumption.
- `replay_neighbors` forces saved attended-neighbor identities into the
  neighbor loop; it is a diagnostic, not historical proof.
- Closest-neighbor geometry matching without attended-neighbor/log_prob
  matching remains the known V3 blocker pattern.

## Files

- `tables/mode_field_comparisons.tsv`
- `tables/mode_entry_summary.tsv`
- `tables/mode_vs_baseline_key_fields.tsv`
- `json/v3_slice_diagnostic_summary.json`
