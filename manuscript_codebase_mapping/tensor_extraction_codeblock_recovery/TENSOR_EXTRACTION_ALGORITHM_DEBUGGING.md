# Tensor Extraction Algorithm Debugging

Scope: ProteinMPNN-DDG V3 direct tensor-field recovery. This note compares the
manuscript-described tensor-extraction algorithm with the recovered V6_V2-style
code and flags current suspicious operational choices.

## Current Status

The recovered V6_V2 scaffold is a plausible implementation of the manuscript's
tensor-extraction procedure, but it is not value-proven against the saved Ssym
V3 pickle.

Proven so far:

- Current code traverses all `342` saved Ssym V3 entries without shape or finite
  numeric failures.
- Local closest-neighbor geometry is consistent with the saved pickle:
  `top_15_closest_neighbor_indices` and `top_10_closest_neighbor_indices` match
  all `342/342` entries exactly.
- Saved V3 direct tensor fields plus local PSSM files reproduce the saved Ssym
  engineered/PSSM fields at value level.

Not proven:

- Current code does not regenerate the saved Ssym V3 direct tensor values.
- All numeric direct tensor fields except closest-neighbor indices have
  value-level mismatches against the saved V3 pickle.

Evidence table:

- `ssym_all_entries_tensor_extraction/tables/ssym_tensor_value_mismatch_summary.tsv`

## Manuscript Algorithm Checklist

The manuscript describes this tensor-extraction logic:

1. Mask the mutation position, keep other residue identities unmasked, and run
   ProteinMPNN on the wildtype backbone/sequence context.
2. For the mutation position, collect the last-decoder-layer vectors received
   from its 48 nearest spatial neighbors.
3. Rank those 48 neighbors by L2 norm of the neighbor -> center message vector.
4. Select the top `K=15` neighbors and memorize their positions.
5. Save the mutation-position probability distribution from this masked-center
   pass for feature A.
6. For each selected neighbor, mask that neighbor position while keeping the
   mutation position unmasked.
7. Run two neighbor-masked passes: one with the center as wildtype residue and
   one with the center changed to mutant residue.
8. For each selected neighbor, extract neighbor log-probabilities,
   center -> neighbor message vectors, and neighbor embeddings under both
   center states.

## What V6_V2 Operationalizes Correctly

The V6_V2 notebook code and the recovered scaffold both implement the main
control flow above:

- `DecLayer.forward` returns the scaled decoder message tensor from the last
  decoder layer.
- `ProteinMPNN.forward` returns `log_probs`, `decoder_messages`, and final node
  embeddings `h_V`.
- The center pass masks only the mutation position by fixing all other
  positions.
- Neighbor ranking uses L2 norms over
  `decoder_messages[0, seq_index, :, :]`.
- The selected local neighbor slots are converted back to residue indices using
  `local_neighbors`.
- The neighbor loop masks each selected neighbor position, then runs wildtype
  and mutant center states.
- The neighbor loop extracts `w_n_log_prob`, `m_n_log_prob`,
  `neighbor_w_message_vector_coming_from_center`,
  `neighbor_m_message_vector_coming_from_center`,
  `neighbor_w_neighbor_embedding`, and `neighbor_m_neighbor_embedding`.

This means V6_V2 is still a serious algorithmic candidate. The current failure
is value-level reproduction, not absence of the manuscript-level control flow.

## Suspicious Operational Choices

### 1. Random Decoding Order Is Not Described In The Manuscript

The manuscript describes masking and tensor extraction, but not random decoding
order. The V6_V2 code uses:

`decoding_order = torch.argsort((chain_M + 0.0001) * torch.abs(randn))`

The current all-entry script also resets the PyTorch seed per mutation entry.
That is not how the notebook code reads: the notebook appears to consume the
runtime RNG stream continuously as it loops through proteins, mutations, and
neighbors.

This can change decoder messages, attended-neighbor ordering, log-probabilities,
neighbor embeddings, and downstream engineered features.

### 2. Closest-Neighbor Geometry Matches, But Attended-Neighbor Ranking Does Not

The exact match for closest-neighbor indices strongly suggests that PDB parsing,
residue indexing, and local 48-neighbor geometry are aligned.

The attended-neighbor fields do not match:

- `top_15_neighbor_indices`: `0/342` exact matches.
- `top_10_neighbor_indices`: `14/342` exact matches.
- `top_5_neighbor_indices`: `108/342` exact matches.
- `top_15_attention_weights`, `top_10_attention_weights`, and
  `top_5_attention_weights`: `0/342` value matches at `1e-6`.

For `1amqA C191Y`, a center-pass seed sweep over seeds `0..99` found seed `98`
with the same top-15 neighbor set as the saved V3 entry, but still not the same
top-15 ordering and not the same `log_prob` tensor. That supports RNG/order
sensitivity, but it does not prove RNG alone explains the saved V3 values.

Seed-sweep output:

- `ssym_algorithm_debugging/tables/1amqA_C191Y_center_seed_sweep.tsv`

### 3. Directed Edge Reciprocity Is A Real Algorithmic Choice

The manuscript says to extract center -> neighbor messages for selected
neighbors. ProteinMPNN's neighbor graph is directed by local k-nearest-neighbor
lists. A selected neighbor from the center's neighbor list does not necessarily
have the center in its own 48-neighbor list.

The recovered code handles that by storing a zero vector when the reciprocal
edge is absent. This follows the V6_V2 notebook comments, but the manuscript
does not explicitly describe this zero-vector fallback. This should be checked
against saved V3 zero-vector patterns before treating it as scientifically
settled.

### 4. Current Feature B Code Does Not Match The Manuscript Equation Directly

The manuscript's feature B is unweighted entropy-change summation:

`sum_j H(P_j^WT) - H(P_j^MT)`

The saved V3/recovered engineered fields include several weighted entropy
variants, including `V2_backward_weighted_neighbor_entropy_changes`. The Ssym
engineered-field recovery proves the saved V3 arithmetic, but it does not prove
that the saved V3 field chosen by the RF notebooks is identical to manuscript
feature B.

This is a manuscript-to-code mapping issue, not a tensor-extraction issue, but
it directly affects whether the recovered pipeline operationalizes the written
method.

### 5. Feature E Is Downstream Of The Direct Tensor Pickle

The manuscript's feature E is an RBF-kernel PCA projection over summed
center -> neighbor message-change vectors. The direct V3 pickle stores raw
message/embedding/log-probability fields and engineered scalar/vector helpers.
The final E-1..E-5 values appear to be produced downstream in RF/ML notebooks,
not inside the direct tensor-extraction code itself.

Therefore, V3 tensor recovery is necessary for feature E, but not sufficient to
prove the final manuscript feature-E implementation.

## Debugging Direction

The next tensor-extraction debugging step should not be broad refactoring. It
should compare small candidate operational variants against saved V3 direct
tensors:

1. Re-run Ssym using continuous notebook-style RNG consumption, without
   resetting the seed per mutation.
2. Re-run with saved V3 `top_15_neighbor_indices` replayed into the neighbor
   loop, to isolate first-step attended-neighbor ranking mismatch from second-
   step neighbor extraction mismatch.
3. Compare reciprocal-edge zero-vector patterns between saved V3 and generated
   candidates.
4. Test deterministic decoding-order variants only as diagnostics, and label
   them clearly as diagnostics unless notebook evidence supports them.
5. Persist generated candidate direct tensors for each run in a separate
   artifact directory before applying engineered/PSSM feature construction.

Until one of these candidates value-matches the saved direct tensor fields, the
correct statement is:

`V6_V2 implements the manuscript-level tensor-extraction control flow, but the
exact historical tensor values in the saved Ssym V3 pickle have not yet been
reproduced.`
