# Random Decoder Order Under Single-Mutation Masking

Date: 2026-05-10

Status: active scientific/method note. This is not a final manuscript claim.

## Question

If the ProteinMPNN-DDG pipeline masks exactly one residue at a time, should
random decoder order affect the extracted tensors?

The intuitive argument is strong:

- Only one residue is designable.
- All other residues have fixed sequence identities.
- Therefore the single designable residue should be decoded last.
- If it is decoded last, it can attend to every other residue.
- Therefore random decoder order may seem irrelevant.

## Current Answer

Random decoder order can still affect the extracted tensors.

The reason is that fixed sequence identity is not the same as fixed decoder
hidden state. ProteinMPNN still updates hidden states for fixed residues inside
the decoder. The random order among the fixed residues can change those
fixed-residue hidden states. In later decoder layers, the single designable
residue receives messages from those order-conditioned fixed-residue states.

So the corrected statement is:

> Single-mutation masking guarantees that the mutated residue is decoded last;
> it does not freeze the decoder representations of the non-mutated residues.

This means there is not one valid decoding order. There is one hard constraint:

`all fixed residues before the designable residue`

There are still many valid orders among the fixed residues themselves, and those
orders can affect ProteinMPNN decoder states.

## Code Path

The recovered V6_V2-style forward path uses:

`decoding_order = torch.argsort((chain_M + 0.0001) * torch.abs(randn))`

Relevant code:

- `proteinmpnn_ddg/recovered_v6v2.py`: patched `ProteinMPNN.forward`
- `proteinmpnn_ddg/recovered_v6v2.py`: `fixed_positions_dict_for_one_designable_position`
- `proteinmpnn_ddg/recovered_v6v2.py`: `featurize_for_one_designable_position`

With one designable position, `chain_M * chain_M_pos * mask` has exactly one
nonzero entry. That pushes the designable residue to the end of the order, while
the fixed residues are randomly ordered before it.

## Local Diagnostic

A spot check was run on Ssym mutation `1amqA C191Y` using the recovered V6_V2
scaffold and the copied ACCRE input PDB.

Observed mask/order facts:

```text
effective_mask_sum 1.0
effective_mask_nonzero_indices [179]
target_seq_index 179
seed 0:  target index 179 was rank 395 of 395
seed 1:  target index 179 was rank 395 of 395
seed 2:  target index 179 was rank 395 of 395
seed 98: target index 179 was rank 395 of 395
```

More explicitly, for seeds `0`, `1`, `2`, and `98`, the target residue was last
in the decoding order every time.

Observed tensor sensitivity:

```text
seed 0:  center log-prob maxdiff 0.0000, center message maxdiff 0.0000
seed 1:  center log-prob maxdiff 0.1679, center message maxdiff 0.1689
seed 2:  center log-prob maxdiff 0.2966, center message maxdiff 0.1326
seed 98: center log-prob maxdiff 0.1860, center message maxdiff 0.1610
```

Interpretation: the target residue remained last, but its extracted center
log-probability row and center decoder-message tensor still changed across
random seeds.

This proves that single-designable-position masking is not sufficient to make
the recovered ProteinMPNN-DDG tensor-extraction segment invariant to random
decoder order.

## Mechanistic Explanation

The key distinction is between sequence identity and decoder hidden state.

At each decoder layer, the model builds neighbor messages using the current
node hidden states. Fixed residues keep their sequence identities, but their
hidden states are still updated by decoder layers.

Layer-level sketch:

1. The designable residue is last and can attend to fixed residues.
2. The fixed residues are ordered randomly among themselves.
3. During decoder layer 1, fixed residues are updated according to that random
   fixed-residue order.
4. During later decoder layers, the designable residue receives messages from
   fixed residues whose hidden states now carry order-dependent information.

Therefore, random order can enter the designable residue indirectly through the
hidden states of fixed residues.

## Scientific Implications

This issue matters even if downstream random-forest performance is not strongly
affected.

It can affect:

- direct tensor-level reproducibility of V3 pickles;
- attended-neighbor ranking by decoder-message norms;
- center log-probability fields;
- neighbor message-change fields;
- engineered features derived from those tensors;
- reviewer-facing questions about determinism and robustness.

This does not prove that random decoder order explains the saved V3 mismatch.
It only proves that random decoder order is a real algorithmic variable in the
recovered tensor-extraction path.

## Open Checks

1. Repeat the seed-sensitivity diagnostic across all Ssym entries, or a
   clearly defined representative subset, without changing the historical
   recovery target.
2. Measure whether tensor-level variation propagates strongly or weakly into
   engineered scalar/vector features.
3. Determine whether the saved 2022 V3 pickles can be matched by recovering the
   historical random-number stream, an explicit decoding order, or a different
   tensor-extraction code path.
4. For future cleaned ProteinMPNN-DDG work, decide whether the method should use
   deterministic fixed-residue ordering, seed-averaged extraction, or the
   original stochastic order with explicit reporting.
5. If the manuscript is revived, decide whether this belongs in Methods,
   Limitations, supplementary robustness analysis, or reviewer-response
   material.

## Working Rule

For historical recovery, do not change the algorithm merely to make it cleaner.
First recover what generated the 2022 artifacts.

For future method development, treat decoder-order handling as an explicit
method-design choice, not an incidental implementation detail.
