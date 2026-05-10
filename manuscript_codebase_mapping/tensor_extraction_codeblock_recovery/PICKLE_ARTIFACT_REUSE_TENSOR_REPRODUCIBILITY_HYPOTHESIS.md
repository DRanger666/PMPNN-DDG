# Pickle Artifact Reuse And Tensor Reproducibility Hypothesis

Scope: working hypothesis for why the current V3 direct-tensor value mismatch
may not have surfaced during the original 2022 ProteinMPNN-DDG work.

This note is not proof of the historical generator run. It is a reasoning
anchor to keep in mind while reconstructing the pipeline.

## Hypothesis

The 2022 workflow likely became pickle-artifact driven after tensor extraction.

In practical terms:

```text
ProteinMPNN-DDG tensor-extraction notebook/run
-> saved PMPNN info pickle
-> later scalar-feature, PSSM, RF, table, and figure notebooks reused that pickle
```

If that was the working pattern, then downstream analysis could remain stable
even if the upstream tensor-extraction run was stochastic, fragile, or not
cleanly packaged. Once the pickle existed, later notebooks did not need to
recreate the direct ProteinMPNN tensors to produce feature-analysis outputs or
manuscript-level RF results.

That would explain why the tensor-value reproducibility problem became visible
only now, during recovery, when we tried to regenerate saved V3 direct tensor
fields from PDB/PSSM/mutation inputs and recovered notebook code.

## Important Boundary

This hypothesis does not solve the direct tensor mismatch.

It explains why the problem might have remained hidden in 2022. It does not
prove which exact code/run generated the final V3 pickles, and it does not make
the current recovered V6_V2 scaffold value-equivalent to the saved V3 tensors.

The unresolved technical target remains:

```text
PDB/PSSM/mutation table
-> ProteinMPNN-DDG tensor-extraction code/run
-> saved V3 direct tensor fields
```

## Current Evidence

The V7 audit supports the broader artifact-reuse pattern, but only for the
early/base S_2648 pickle stage.

Observed evidence:

- `ProteinMPNNTesting_V7.ipynb` has raw local mtime `2022-08-18`.
- V7 references `S_2648_pmppn_info_dict.pickle`, not the final V3 pickle
  family.
- V7 lacks the ProteinMPNN inference modifications and call-site tensor
  extraction needed to generate full V3 direct tensor fields.
- V7 computes scalar/PSSM feature-analysis outputs from an existing
  `two_level_dict` containing fields such as `log_prob`, `w_n_log_prob`,
  `m_n_log_prob`, `neighbor_aa_identities`, `top_15_neighbor_indices`, and
  `top_15_attention_weights`.

The later V2/V3 artifact-use pattern is visible elsewhere:

- `*_ProteinMPNNTesting_V6_V2` notebooks are the strongest current candidate
  generator family for richer tensor-bearing PMPNN info pickles.
- `Quick_Dirty_MPNN_ML_V2_V2.ipynb` consumes the V2 PMPNN info pickle family.
- `Quick_Dirty_MPNN_ML_V2_V3.ipynb` consumes the V3 PMPNN info pickle family.

Therefore, the safest current reconstruction is:

```text
early V6-style generation
-> base PMPNN pickles
-> V7-style S_2648 scalar/PSSM feature exploration

V6_V2-style generation
-> richer V2/V3 PMPNN info pickles
-> Quick_Dirty_MPNN_ML_V2_V3 manuscript-level RF analysis
```

## Why This Matters For The Project

This point should affect how we frame recovery work.

We should avoid assuming that every later notebook is meant to be rerunnable
from raw structural inputs. Some later notebooks may be artifact consumers.

We should also avoid treating successful downstream reproduction from saved V3
fields as proof that the upstream tensor-extraction generator has been
recovered. Those are different claims:

- saved V3 direct tensor fields -> engineered/PSSM scalar fields;
- saved V3 direct tensor fields -> RF feature matrices/results;
- raw inputs -> saved V3 direct tensor fields.

Only the third claim addresses the current tensor-generation recovery problem.

## Follow-Up Use

Use this note when deciding whether a notebook belongs in one of these roles:

- direct tensor generator;
- intermediate pickle artifact consumer;
- scalar/PSSM feature-construction notebook;
- RF/manuscript-result notebook.

For current debugging, this note supports an artifact-provenance strategy:

1. Identify which pickles a notebook consumes or writes.
2. Use pickle mtimes, notebook mtimes, and saved outputs to build a timeline.
3. Treat commented save/load cells as evidence of workflow context, not as
   direct proof that the displayed final notebook text wrote the on-disk file.
4. Keep the direct tensor-value reproduction target separate from downstream
   feature/RF reproduction targets.
