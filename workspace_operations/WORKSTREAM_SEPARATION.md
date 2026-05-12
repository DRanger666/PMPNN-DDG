# ProteinMPNN-DDG Workstream Separation

Date: 2026-05-12

Purpose: keep historical recovery, durable method science, focused V3
direct-tensor reconciliation, ThermoMPNN method enquiries, and later manuscript
synthesis distinct while the ProteinMPNN-DDG project is being revived.

## Core Position

The project now has five related but separate workstreams:

1. Historical recovery and reproduction.
2. Durable method science and algorithmic interpretation.
3. Focused V3 direct-tensor extraction reconciliation.
4. ThermoMPNN method-landscape and dataset enquiries.
5. Later synthesis of recovered evidence and improved algorithmic framing into
   manuscript/submission material.

These should not be merged prematurely.

## Workstream 1: Historical Recovery And Reproduction

Goal: recover what actually produced the 2022 artifacts and manuscript results.

This workstream should answer:

- Which code generated the V3/full-feature pickles?
- Which input PDB, PSSM, and mutation/DDG tables were used?
- Which notebooks or cells produced manuscript tables and figures?
- Can saved artifacts be regenerated at value level?
- Where historical artifacts cannot be regenerated exactly, what evidence
  explains the gap?

Rule: do not change the historical algorithm to make it cleaner or more
defensible while doing this workstream. The target is provenance and
reproducibility of the 2022 pipeline.

Primary locations:

- `manuscript_codebase_mapping/`
- `pickle_analysis/`
- `proteinmpnn_ddg_recovery/`
- `scripts/`

The package-level workflow role of `proteinmpnn_ddg_recovery/` is tracked in:

- `RECOVERY_PACKAGE_ROLE.md`

## Workstream 2: Durable Method Science

Goal: preserve scientific reasoning about the ProteinMPNN-DDG method that
should remain useful after historical recovery is complete.

This workstream should study questions such as:

- What does each engineered feature mean scientifically?
- Which feature definitions need pseudocode, diagrams, or clearer mathematical
  framing?
- Which algorithmic choices need main-text explanation, supplementary analysis,
  or reviewer-response preparation?
- Which current interpretations should carry forward into a cleaned
  ProteinMPNN-DDG method?

Rule: this workstream can propose better algorithmic framing or future method
changes, but it should not overwrite the historical recovery target.

Primary location:

- `method_science/`

## Workstream 3: Focused V3 Direct-Tensor Extraction Reconciliation

Goal: reconcile the unresolved upstream segment:

```text
PDB
+ mutation table
+ ProteinMPNN weights/code
+ RNG/order behavior
-> saved V3 direct tensor fields
```

This workstream should study questions such as:

- What does single-mutation masking imply inside a multi-layer ProteinMPNN
  decoder?
- How does random decoder order affect extracted tensors?
- How does directed neighbor-graph asymmetry affect center-to-neighbor tensor
  extraction?
- Which tensor-extraction choices can explain current value-level mismatch
  against saved V3 direct tensor fields?
- Which diagnostic variants are candidate-historical, and which are future
  method-design alternatives?

Rule: this workstream may run diagnostic variants, but it must label them
clearly and must not present cleaner alternatives as historical facts.

Primary location:

- `v3_tensor_extraction_reconciliation/`

Operational separation between the main recovery session and the future
dedicated reconciliation session is tracked in:

- `CODEX_SESSION_AND_GIT_WORKTREE_SEPARATION.md`

## Workstream 4: ThermoMPNN Method Enquiries

Goal: study ThermoMPNN as a post-2022 method and dataset reference that may
affect ProteinMPNN-DDG revision, extension, benchmarking, or manuscript
framing.

This workstream should study questions such as:

- Which ThermoMPNN datasets, weak-supervision choices, and benchmarks are
  relevant to ProteinMPNN-DDG?
- How does ThermoMPNN use ProteinMPNN code, weights, embeddings, or learned
  representations differently from ProteinMPNN-DDG?
- Which 2022 manuscript claims become outdated in a post-ThermoMPNN method
  landscape?
- Which ThermoMPNN ideas should be incorporated only after the current
  ProteinMPNN-DDG reproduction baseline is recovered and stable?

Rule: this workstream is comparative and forward-looking. It should not replace
the historical recovery target, and it should not be treated as evidence that
the 2022 ProteinMPNN-DDG pipeline behaved differently.

Primary branch/worktree:

- Git branch: `thermompnn-method-enquiries`
- Git worktree: `/home/mpr/proteinmpnn_ddg_thermompnn_method_enquiries`
- Primary branch-local directory: `thermompnn_enquiries/`

## Workstream 5: Manuscript Synthesis

Goal: decide how recovered provenance, method-science notes, and V3
reconciliation results, plus later ThermoMPNN enquiry findings, should affect a
revived manuscript, preprint, supplementary material, and accompanying code.

This workstream comes later. It should merge evidence from Workstream 1,
analysis from Workstreams 2 and 3, and carefully selected comparative context
from Workstream 4 into submission-facing decisions.

Possible outcomes:

- Preserve the 2022 method and add clearer explanation.
- Add robustness experiments or supplementary analyses.
- Revise the method text to match recovered code evidence.
- Extend the method before submission while clearly separating historical
  recovery from new work.
- Build a cleaned, usable accompanying tool after the historical pipeline is
  understood.

Rule: manuscript synthesis should not claim more certainty than Workstream 1
supports, and should not present Workstream 2 design alternatives as historical
facts.

## Practical Rule

When a new finding appears, classify it before writing it down:

- Artifact/provenance evidence -> `manuscript_codebase_mapping/` or
  `pickle_analysis/`.
- Durable scientific/method reasoning -> `method_science/`.
- Focused V3 direct-tensor mismatch/reconciliation work ->
  `v3_tensor_extraction_reconciliation/`.
- ThermoMPNN comparative/dataset/method-landscape enquiry ->
  `thermompnn_enquiries/` on the `thermompnn-method-enquiries` branch.
- Submission-facing integration decision -> later manuscript synthesis notes.

This separation is meant to prevent three different questions from being
collapsed:

1. What happened in 2022?
2. What is scientifically defensible now?
3. Why do current direct-tensor extraction attempts mismatch saved V3 tensors?
4. What did later methods such as ThermoMPNN change about the comparison
   landscape?
5. What should be written or submitted later?
