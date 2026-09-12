# Current Recovery Boundary

Date: 2026-05-12

Purpose: short coordination anchor for what has been reproduced and what still
needs recovery, V3 tensor reconciliation, or method-science study.

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

At the final RF plotting layer, manuscript Figure 6 has also been numerically
recovered for the S_669/Ssym incremental-feature total-PCC plot:

```text
list_incremental_feature_result_dict.pickle
-> S_669/Ssym total-PCC means
-> exact notebook output image
-> manuscript Figure 6 standalone image
```

Evidence:

- `manuscript_codebase_mapping/FIGURE6_NUMERICAL_BASIS_VERIFICATION.md`

The final DOCX embeds Figure 6 as `media/image6.png`. That embedded PNG is not
byte-identical to the standalone manuscript PNG, but this is not a recovery
blocker or scientific-content discrepancy. The relevant recovery claim is that
the plotted S_669/Ssym incremental total-PCC series and visible figure content
match.

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

The workspace now tracks three small classes of indispensable recovery inputs via
Git LFS:

- the four dataset-specific V3 PMPNN info pickles under
  `drive_evidence_copy/sajidahmedprotres_drive/Protein_MPNN_Digging/`, used as
  saved reference artifacts for recovery/reproduction analysis;
- the final ten-run incremental-feature RF result pickle
  `drive_evidence_copy/sajidahmedprotres_drive/Protein_MPNN_Digging/list_incremental_feature_result_dict.pickle`,
  used as the recovered numerical source for the Table 1 and Figure 6 final
  RF-result evidence layer;
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
- `v3_tensor_extraction_reconciliation/RANDOM_DECODER_ORDER_SINGLE_MUTATION_MASKING.md`

## Work Ownership

Main recovery session:

- preserve historical recovery and manuscript/pickle provenance claims;
- avoid changing the historical algorithm merely to make it cleaner;
- keep value-level reproduction evidence under `manuscript_codebase_mapping/`,
  `pickle_analysis/`, `scripts/`, and `proteinmpnn_ddg_recovery/`.

V3 tensor-reconciliation Git worktree and Codex session:

- study the unresolved upstream V3 direct-tensor extraction mismatch, including
  tensor-generation implications, robustness, and scientifically defensible
  stabilization choices;
- test diagnostic variants without presenting them as historical facts;
- record focused reconciliation notes under
  `v3_tensor_extraction_reconciliation/`;
- promote durable method-science conclusions to `method_science/` when they
  should outlive the focused reconciliation task;
- communicate back through durable notes and commits before anything is merged
  into the main recovery track.

As of this note, the dedicated Git worktree/Codex session is the intended next
split point for V3 tensor-extraction reconciliation. Once it is created, update
this note only if the recovery boundary or work ownership changes.


## Regenerated compact-feature RF (2026-09-12)

Four-dataset compact features on LFS under `reproduction_inputs/pmpnn_ddg_features_2026-09-12/`
(including S921). RF outputs:
`reproduction_runs/2026-09-12/rf_from_promoted_compact_features/`.

Formal match write-up (Tables 1–3 PMPNN-DDG rows + Figure 6):
`manuscript_codebase_mapping/MANUSCRIPT_RESULTS_MATCH.md` (linked from top-level README).

Full extraction tensors: Ssym promoted; S2648 large-protein prebatch + resume in progress; S669/S921 full queued after.
