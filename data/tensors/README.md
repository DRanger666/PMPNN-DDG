# Extraction tensors

Published ProteinMPNN intermediates plus engineered features A–H. **This is
the source of truth for Table 1 and Figure 3.**

| File | Dataset | n |
| --- | --- | ---: |
| `S2648_extraction_tensors.pickle` | S2648 (train) | 2647 |
| `S669_extraction_tensors.pickle` | S669 (test) | 638 |
| `S921_extraction_tensors.pickle` | S921 (test) | 921 |
| `Ssym_extraction_tensors.pickle` | Ssym (test) | 342 |

Canonical keys (`center_masked_log_probs`, `message_norm_top15_weights`, …)
are documented in [SCHEMA.md](SCHEMA.md). Stored as Git LFS.

Compact RF-only tables: [`../features/`](../features/).
