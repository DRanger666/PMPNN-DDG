# Current Recovery Boundary

Date: 2026-05-11

Purpose: short coordination anchor for what has been reproduced and what still
needs recovery, reconciliation, or algorithmic study.

This is not a detailed evidence report. It should point to detailed evidence,
not duplicate it.

## Reproduced So Far

At the final RF-result level, manuscript Table 1 has been numerically recovered
for the three independent test-set rows:

```text
list_incremental_feature_result_dict.pickle
+ saved notebook-output evidence for rF-R
-> manuscript Table 1 PMPNN-DDG rows for S_669, Ssym, and S_921
```

Current result:

- `18/21` Table 1 numeric cells match by pickle-only evidence.
- The remaining `3/21` `rF-R` cells match through saved notebook-output
  evidence.
- Including saved notebook-output evidence, all Table 1 numeric cells for
  `S_669`, `Ssym`, and `S_921` are currently matched.

Evidence:

- `manuscript_codebase_mapping/TABLE1_NUMERICAL_RECOVERY_MILESTONE.md`

For Ssym, the feature-construction segment has been reproduced at value level:

```text
saved Ssym V3 direct tensor fields
+ local Ssym PDB residue mapping
+ local Ssym PSSM files
-> saved Ssym V3 engineered/PSSM fields
```

Evidence:

- `manuscript_codebase_mapping/engineered_feature_recovery/ssym_engineered_pssm_feature_reconstruction/SSYM_ENGINEERED_PSSM_FEATURE_RECONSTRUCTION.md`

Current result:

- `342/342` Ssym mutation entries passed.
- `8208/8208` field comparisons matched with `atol=1e-6, rtol=1e-6`.
- Mismatch entries: `0`.
- Runtime errors: `0`.

Important scope limit: this proves the saved-tensor-to-feature segment only. It
does not prove end-to-end V3 pickle regeneration.

## Portable Core Artifacts

The workspace now tracks two small classes of indispensable recovery inputs via
Git LFS:

- the four dataset-specific V3 PMPNN info pickles under
  `drive_evidence_copy/sajidahmedprotres_drive/Protein_MPNN_Digging/`, used as
  saved reference artifacts for recovery/reproduction analysis;
- the curated ProteinMPNN checkpoint
  `reproduction_inputs/proteinmpnn_checkpoints/vanilla_model_weights/v_48_020.pt`,
  used as the current tensor-extraction model input.

## Still Unresolved

The upstream direct-tensor segment has not yet been reproduced at value level:

```text
PDB
+ mutation table
+ ProteinMPNN weights/code
+ RNG/order behavior
-> saved V3 direct tensor fields
```

Known issues requiring recovery or reconciliation include:

- random decoder order among fixed residues;
- attended-neighbor ranking by message norms;
- directed local-neighbor graph asymmetry;
- zero-vector fallback when the center is absent from a selected neighbor's
  local neighborhood;
- continuous notebook-style RNG consumption versus per-entry seed resetting;
- whether V6_V2 is the exact historical tensor-extraction path or only a strong
  candidate.

Evidence and current debugging notes:

- `manuscript_codebase_mapping/tensor_extraction_codeblock_recovery/TENSOR_EXTRACTION_ALGORITHM_DEBUGGING.md`
- `algorithmic_deliberations/RANDOM_DECODER_ORDER_SINGLE_MUTATION_MASKING.md`

## Work Ownership

Main recovery session:

- preserve historical recovery and manuscript/pickle provenance claims;
- avoid changing the historical algorithm merely to make it cleaner;
- keep value-level reproduction evidence under `manuscript_codebase_mapping/`,
  `pickle_analysis/`, `scripts/`, and `proteinmpnn_ddg_recovery/`.

Algorithmic Git worktree and Codex session:

- study tensor-generation implications, robustness, and scientifically
  defensible alternatives;
- test diagnostic variants without presenting them as historical facts;
- record method-level reasoning under `algorithmic_deliberations/`;
- communicate back through durable notes and commits before anything is merged
  into the main recovery track.

As of this note, the algorithmic Git worktree/Codex session is the intended next
split point. Once it is created, update this note only if the recovery boundary
or work ownership changes.
