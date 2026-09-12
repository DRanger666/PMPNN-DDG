# Manuscript ↔ Code Fidelity Checklist (skeptical framing)

Date: 2026-09-12  
Branch: `reproduce-paper-results`

## How to read this note

For each flagged item we ask, **before** any “fix”:

1. Is this actually a **conflict** with the manuscript?
2. Or manuscript **shorthand / incomplete prose**, while the code is the
   intended method?
3. Or an **alternate computed field** that the final RF never used?
4. Or **unresolved / needs more evidence**?

Only after that classification do we decide: change code, change wording, or
leave alone. Prefer open questions + evidence over assuming bugs.


**Branch bar (2026-09-12):** reproduce manuscript numbers and probe mismatches;
do **not** treat bit/byte-identical historical V3 extraction as unresolved work.
See `REPRODUCTION_BAR_NOT_BYTE_IDENTICAL_V3.md`.

Related detail notes (may use older “deviation” wording; this checklist
supersedes tone):

- `FEATURE_EQUATION_CODE_MAPPING_INITIAL.md`
- `method_science/V3_DIRECTED_NEIGHBOR_ASYMMETRY_SEMANTICS.md`

---

## Item A — Random decoder order among fixed residues

**What code does.** `recovered_v6v2` / ProteinMPNN: decoding order via
`argsort((chain_M+ε)·|randn|)` unless an explicit order is supplied.

**What manuscript says.** Describes WT/MT ProteinMPNN passes; does not spell
out random order among fixed residues or seeding.

| Q | Working answer |
| --- | --- |
| 1. Conflict? | **Not established.** Absence from prose ≠ contradiction. |
| 2. Shorthand / incomplete? | **Plausible.** ProteinMPNN’s standard forward uses random order; authors may have treated it as library behavior. |
| 3. Unused alternate? | N/A (this is extraction machinery, not an unused engineered scalar). |
| 4. Unresolved? | **No as a milestone.** Bit-exact match to historical V3 `log_prob` is **not expected** (stochastic decoder order). Open only as scientific description of RNG, not as a regeneration failure. Manuscript / RF correspondence is the bar. |

**Action.** Leave extraction code as-is. Document RNG/order as expected
stochasticity (not a failed V3 reconciliation). Do not “fix toward manuscript”
by inventing a non-random order the paper never required. Judge success by
manuscript Tables/Figures from the public tensor→feature→RF path.

---

## Item B — Feature B: manuscript unweighted sum vs weighted V2 field

**What manuscript Eq. 1 shows (OCR).** Unweighted neighbor entropy-change sum,
schematically `Σ_j (H(P_j^WT) − H(P_j^MT))`.

**What Table 1 / Fig 6 RF used.** Column map points Feature B →
`V2_backward_weighted_neighbor_entropy_changes` (message-norm-ratio weighted;
per-neighbor term `H_MT − H_WT` before weighting). Evidence:
`Quick_Dirty_MPNN_ML_V2_VGRAPHS_V1` feature map + engineered-feature cell.

| Q | Working answer |
| --- | --- |
| 1. Conflict? | **Possible wording gap**, not proven scientific error. Equation text omits weighting that the final RF column uses. |
| 2. Shorthand / incomplete? | **Leading hypothesis.** Manuscript may describe the entropy-change *idea* while the shipped method (and numbers) use the weighted V2 field—common in drafts. |
| 3. Unused alternate? | **Partially yes.** Unweighted / other weighted entropy variants exist in V3 pickles (`weighted_neighbor_entropy_changes`, `backward_weighted_*`, etc.). Final A–H map uses the **V2 backward-weighted** field only. |
| 4. Unresolved? | **Yes** until someone shows either (a) a manuscript revision that names weighting, or (b) a retrain with unweighted B that still hits Table 1. |

**Action.**

- **Do not** treat weighted B as a bug by default.
- Primary RF comparison to Table 1: use **`historical_weighted`** (what produced
  the published numbers), clearly labeled.
- Optional diagnostic: `--feature-b-mode manuscript_unweighted` recomputes
  unweighted `Σ(H_WT−H_MT)` from saved `w_n_log_prob`/`m_n_log_prob` to test
  sensitivity—not asserted as “the correct fix.”
- Manuscript wording cleanup is a separate editorial question.

---

## Item C — Zero-vector when center ∉ neighbor’s local `E_idx`

**What code does.** If directed edge center→neighbor is absent in ProteinMPNN’s
top-k graph, insert zero message vectors (see asymmetry note).

**What manuscript says.** Silent on non-reciprocal neighborhoods.

| Q | Working answer |
| --- | --- |
| 1. Conflict? | **No.** Silence ≠ conflict. |
| 2. Shorthand / incomplete? | **Likely.** Implementation necessity once you read directed `E_idx`; may never have been considered prose-worthy. |
| 3. Unused alternate? | N/A. |
| 4. Unresolved? | Frequency / impact on C/E still worth measuring as optional diagnostics; not a blocker for manuscript reproduction. |

**Action.** Leave alone. Optional count of zero-vector rate on regenerated
tensors (or reference dumps); do not change primary path without evidence it
was unintended. Do not frame this as V3 byte-reconciliation work.

---

## Item D — Feature E KPCA details (sample size, 10 components, use first 5)

**What manuscript says.** Message-change vectors encoded via a reduced
representation (PCA/KPCA family); fine hyperparameters are thin in the PDF.

**What code / notebooks that match Table 1 do.** RBF `KernelPCA(n_components=10)`
on ~10k random S_2648 message-change rows; sum over 15 neighbors; Feature E =
first **5** of those 10 in the augmented matrix.

| Q | Working answer |
| --- | --- |
| 1. Conflict? | **No** at family level (message-change KPCA). |
| 2. Shorthand / incomplete? | **Yes**—component count / subsample are notebook details. |
| 3. Unused alternate? | Embedding KPCA is also fit; **not** selected as Feature E in final A–H map. |
| 4. Unresolved? | Bit-exact E vs 2022 Colab (unseeded subsample) is **not** a goal; protocol-level re-fit with explicit seed + manuscript PCC probing is enough (see `FIGURE45_KPCA_SUBSAMPLE_SENSITIVITY.md`). |

**Action.** Keep message-KPCA E as in notebooks. Label re-fit seed. Do not
swap in embedding-KPCA as “Feature E” without new evidence.

---

## Item E — RF hyperparameters: manuscript “defaults” vs notebook `max_features="sqrt"`

**Manuscript.** `n_estimators=500`, `max_samples=0.5`, other hyperparams
default.

**Notebook that saved `list_incremental_feature_result_dict.pickle`.** Also sets
`max_features="sqrt"` (and `min_samples_split=2`, which is already the usual
default).

| Q | Working answer |
| --- | --- |
| 1. Conflict? | **Mild prose vs practice gap** on `max_features` only. |
| 2. Shorthand / incomplete? | **Plausible** that “defaults” meant “defaults except the two we tuned,” and sqrt was left in the training cell. |
| 3. Unused alternate? | Early cells used 300 / 0.2 / min_samples_split=5; those are earlier experiments, not the ten-run pickle source. |
| 4. Unresolved? | Which wording to prefer in a revision is editorial; for reproduction we measure **both**. |

**Action.** Report `manuscript_literal` and `notebook_table1` side by side.
Neither is discarded as “wrong” a priori; closeness to Table 1 is empirical.

---

## Item F — S_669 ΔΔG sign flip in ML notebook

**What code does.** `S_669_y *= -1` before metrics so correlations align with
other sets.

**What manuscript says.** Does not narrate a dataset-specific flip.

| Q | Working answer |
| --- | --- |
| 1. Conflict? | **No**—dataset convention handling. |
| 2. Shorthand / incomplete? | **Yes** (S669 often uses opposite ΔΔG sign in public tables). |
| 3. Unused alternate? | N/A. |
| 4. Unresolved? | Only if someone claims Table 1 used raw unflipped labels (evidence says flipped). |

**Action.** Keep flip for Table 1 comparison; label it in reports.

---

## Item G — Features A, C, D, F, G, H (brief)

| Feature | Manuscript idea | Code / RF column | Classification |
| --- | --- | --- | --- |
| A | Center WT↔MT energy / log-prob change | `center_mut_wild_energy` | **Match** (no open conflict). |
| C | Message-norm **ratio** sum (NR) | `center_neighbor_weight_check_w_m` | **Match** with Fig. 3 NR choice. |
| D | Embedding change-norm sum (CN) | `neighbor_embedding_change_m_w` | **Match** at family level. |
| F/G/H | PSSM delta / WT / MT | saved PSSM fields | **Match**. |

---

## RF path labeling (this branch)

When reporting metrics, always state:

1. Feature source: **regenerated extraction tensors** (public LFS path) or, for
   diagnostics only, historical V3 engineered fields (+ KPCA E seed noted).
2. Feature B mode: `historical_weighted` (primary vs Table 1) or
   `manuscript_unweighted` (diagnostic only).
3. RF config: `manuscript_literal` and/or `notebook_table1`.
4. S_669 sign flip: applied.
5. **Not claimed / not a failure mode:** PDB→historical-V3 bit-exact regeneration;
   bit-exact Feature E vs 2022 Colab. Stochastic drift vs V3 dumps is expected.

**Decision summary for primary RF vs paper:** regenerate from the public
tensor→feature path; compare to manuscript Tables/Figures; probe residuals
rationally. Treat Feature B wording, decoder RNG description, and zero-vector
policy as **open fidelity / wording questions**, not as “failed V3 reconciliation.”


---

## Empirical note (2026-09-12 RF diagnostic)

A short 3-run RF retrain with `--feature-b-mode manuscript_unweighted` and
`notebook_table1` settings still rounded to paper rF+R / RMSE on S_669, Ssym,
and S_921 (`reproduction_runs/2026-09-12/rf_from_v3_features_manuscript_B/`).

That does **not** prove the manuscript equation and the weighted V2 field are
the same object; it only shows Table 1-level metrics are not highly sensitive
to this swap under the current protocol. Primary comparison remains
`historical_weighted`. Classification of Item B stays: open wording / incomplete
prose vs intended weighted method — **not** a confirmed bug.
