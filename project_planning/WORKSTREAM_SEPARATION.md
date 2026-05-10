# ProteinMPNN-DDG Workstream Separation

Date: 2026-05-10

Purpose: keep the recovery effort, algorithm-design effort, and later
manuscript synthesis effort distinct while the ProteinMPNN-DDG project is being
revived.

## Core Position

The project now has at least three related but separate workstreams:

1. Historical recovery and reproduction.
2. Algorithm design and implication analysis.
3. Later synthesis of recovered evidence and improved algorithmic framing into
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
- `proteinmpnn_ddg/`
- `scripts/`

## Workstream 2: Algorithm Design And Implication Analysis

Goal: understand whether the tensor-generation and feature-engineering
algorithm is scientifically well-framed, robust, and defensible.

This workstream should study questions such as:

- What does single-mutation masking imply inside a multi-layer ProteinMPNN
  decoder?
- How does random decoder order affect extracted tensors?
- Do tensor-level variations materially affect engineered scalar/vector
  features?
- Should future ProteinMPNN-DDG use deterministic ordering, stochastic
  ordering, seed averaging, or another explicitly justified design?
- Which algorithmic choices need main-text explanation, supplementary analysis,
  or reviewer-response preparation?

Rule: this workstream can propose better algorithmic framing or future method
changes, but it should not overwrite the historical recovery target.

Primary location:

- `algorithmic_deliberations/`

Operational separation between the main recovery session and the future
algorithmic session is tracked in:

- `CODEX_SESSION_AND_GIT_WORKTREE_SEPARATION.md`

## Workstream 3: Manuscript Synthesis

Goal: decide how recovered provenance and algorithmic analysis should affect a
revived manuscript, preprint, supplementary material, and accompanying code.

This workstream comes later. It should merge evidence from Workstream 1 and
analysis from Workstream 2 into submission-facing decisions.

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
- Scientific/method deliberation -> `algorithmic_deliberations/`.
- Submission-facing integration decision -> later manuscript synthesis notes.

This separation is meant to prevent three different questions from being
collapsed:

1. What happened in 2022?
2. What is scientifically defensible now?
3. What should be written or submitted later?
