# ProteinMPNN-DDG Feature Equation-to-Code Mapping: Initial Pass

Date: 2026-05-06

This note resolves the current feature-E confusion and records the first
equation-level mapping between the 2022 ProteinMPNN-DDG manuscript concept and
the code evidence. It is based on source-only notebook exports in
`code_inventory_analysis/notebook_sources/git_sajid_additions/`; old pickle
artifacts were not unpickled for this pass.

## Short Answer

The remembered concept is supported by the code: both neighbor-identity /
neighbor-state change and center-to-neighbor message change are real feature
families in the 2022 implementation.

The apparent "feature E = reverse neighbor-KPCA" issue came from mixing two
different matrix layouts:

- In the pre-augmentation 75-column matrix `S_2648_X`, columns `31..40` are
  reverse-oriented neighbor-embedding KPCA features.
- In the post-augmentation 41-column matrix `S_2648_X_aug`, columns `31..40`
  are message-change KPCA features. The final `feature_to_index_map` is applied
  to `S_2648_X_aug`, so `E -> [31,32,33,34,35]` refers to the first five
  message-change KPCA components in the final model.

So the current evidence says manuscript feature E is probably aligned with the
final ML code at the feature-family level: it is message-change RBF-KPCA, not
neighbor-embedding KPCA.

## Conceptual Model in Code

The working idea was:

1. Treat ProteinMPNN as a frozen structural prior learned from
   backbone-conditioned sequence generation.
2. For a mutation at center position `c`, compare the model state when the
   sequence has the wildtype amino acid `w` at `c` versus the mutant amino acid
   `m` at `c`, with the backbone held fixed.
3. Extract small, hand-engineered DDG features from how ProteinMPNN's
   probabilities, neighbor node embeddings, and center-to-neighbor decoder
   messages change.
4. Train lightweight regressors on DDG-labeled datasets instead of fine-tuning
   ProteinMPNN.

This is not generic "use ProteinMPNN score as DDG"; the notebooks use several
internal readouts from the frozen model.

## ProteinMPNN Internals Used

The modified notebook copy of `DecLayer.forward` computes a 128-dimensional
decoder message vector per receiver-neighbor pair:

```text
h_message = W3(act(W2(act(W1([h_receiver, edge_features])))))
dh_receiver = sum_neighbors(h_message) / scale
```

The notebook returns both the updated node embedding `h_V` and the scaled
`h_message` tensor. In the feature extraction notebooks, `h_V` is the neighbor
node embedding readout and `h_message` is the decoder message readout.

Primary source:

- `ProteinMPNNTesting_V6_V2.ipynb.py.txt:805-831`

## Neighbor Selection

For a mutation at sequence index `c`, the code looks at
`decoder_messages[0, c, :, :]`, takes the L2 norm of each of the 48 message
vectors, and selects the top 15 message-norm neighbors. Those local neighbor
slots are mapped back to residue indices through `return_neighbor_info`.

Equation-level sketch:

```text
score(c <- n) = || M_{c,n} ||_2
N_15(c) = top 15 neighbors n by score(c <- n)
```

Primary source:

- `ProteinMPNNTesting_V6_V2.ipynb.py.txt:1765-1790`

Interpretation: this first ranking uses messages contributing to the center
position's decoder update. Later message-change features use the opposite slot,
the center-to-neighbor message contributing to each neighbor's update.

## Per-Neighbor Raw Quantities

For each selected neighbor `n` in `N_15(c)`, the code extracts the following
under two sequence contexts:

- WT-center context: center residue is `w`.
- MT-center context: center residue is replaced by `m`.

It stores log-probability vectors, plus embeddings and message vectors:

```text
ell_w^n(a) = log p_w^n(a) at neighbor n with center=w
ell_m^n(a) = log p_m^n(a) at neighbor n with center=m
E_w^n    = ProteinMPNN neighbor node embedding h_V[n] with center=w
E_m^n    = ProteinMPNN neighbor node embedding h_V[n] with center=m
M_w^{c->n} = decoder message from center c to neighbor n with center=w
M_m^{c->n} = decoder message from center c to neighbor n with center=m
```

The center-to-neighbor message is read as
`decoder_messages[0, n, neighbor_neighbor_index, :]`, where
`neighbor_neighbor_index` is the slot in neighbor `n`'s 48-neighbor list that
points back to center `c`. If center `c` is absent from that neighbor list, the
code stores a zero vector.

Primary source:

- `ProteinMPNNTesting_V6_V2.ipynb.py.txt:1888-1946`

## Derived Raw Changes

For each selected neighbor, the code derives:

```text
neighbor energy change:
  (-ell_m^n(native_aa_n)) - (-ell_w^n(native_aa_n))

forward KL:
  KL(p_w^n || p_m^n)

backward KL:
  KL(p_m^n || p_w^n)

neighbor entropy change:
  H(p_m^n) - H(p_w^n)

center-to-neighbor message norm ratio:
  ||M_w^{c->n}||_2 / ||M_m^{c->n}||_2

neighbor embedding change norm:
  ||E_w^n - E_m^n||_2

raw neighbor embedding change:
  E_w^n - E_m^n

raw center-to-neighbor message change:
  M_w^{c->n} - M_m^{c->n}

message change norm:
  ||M_w^{c->n} - M_m^{c->n}||_2
```

Primary source:

- `ProteinMPNNTesting_V6_V2.ipynb.py.txt:2020-2161`

## Final A-H Feature Mapping

The final feature map in `Quick_Dirty_MPNN_ML_V2_VGRAPHS_V1.ipynb` is applied
to `S_2648_X_aug`, `S_921_X_aug`, `S_669_X_aug`, and `Ssym_X_aug`.

| Manuscript feature | Augmented column(s) | Code key / meaning |
|---|---:|---|
| A | `0` | `center_mut_wild_energy = -ell_c(m) - (-ell_c(w))` |
| B | `6` | `V2_backward_weighted_neighbor_entropy_changes` |
| C | `7` | `center_neighbor_weight_check_w_m = sum_n ||M_w^{c->n}|| / ||M_m^{c->n}||` |
| D | `8` | `neighbor_embedding_change_m_w = sum_n ||E_w^n - E_m^n||` |
| E | `31..35` | first five message-change RBF-KPCA sum features in augmented layout |
| F | `5` | `wild_pssm - alternate_pssm` |
| G | `9` | `wild_pssm` |
| H | `10` | `alternate_pssm` |

Primary source:

- Feature-map definition:
  `Quick_Dirty_MPNN_ML_V2_VGRAPHS_V1.ipynb.py.txt:929-936`
- Feature combinations train RFs using `S_*_X_aug[:, f_index_comb]`:
  `Quick_Dirty_MPNN_ML_V2_VGRAPHS_V1.ipynb.py.txt:977-988`

## Feature B Detail

Feature B is not merely an unweighted entropy-change sum in the final ML
mapping. It is the V2 "backward weighted" entropy-change feature:

```text
B = sum_{n in N_15(c)}
      sigmoid(||M_w^{c->n}||_2 / ||M_m^{c->n}||_2)
      * (H(p_m^n) - H(p_w^n))
```

Primary source:

- `ProteinMPNNTesting_V6_V2.ipynb.py.txt:2121-2123`
- `Quick_Dirty_MPNN_ML_V2_VGRAPHS_V1.ipynb.py.txt:207-209`

This is a real manuscript-code reconciliation point: if the manuscript says
"neighbor entropy-change summation" without the message-ratio weighting, the
method text should be tightened.

## Feature E Detail

The raw message-change matrix for one mutation is:

```text
Delta_M(c) =
  rows over n in N_15(c): M_w^{c->n} - M_m^{c->n}

shape: 15 x 128
```

The ML notebook concatenates all S_2648 message-change rows, fits a
`StandardScaler`, then fits:

```text
KernelPCA(n_components=10, kernel="rbf")
```

on a 10,000-row random sample from the scaled S_2648 message-change rows. For
each mutation, it transforms the 15 rows and sums over neighbors:

```text
Z_M(c) = sum_{n in N_15(c)} KPCA(scale(Delta_M(c)_n))
```

The final model uses the first five components of that 10-component vector:

```text
E = Z_M(c)[0:5]
```

Primary source:

- Raw message-change arrays added to `cur_X`:
  `Quick_Dirty_MPNN_ML_V2_VGRAPHS_V1.ipynb.py.txt:234-238`
- Message KPCA fit:
  `Quick_Dirty_MPNN_ML_V2_VGRAPHS_V1.ipynb.py.txt:291-315`
- Message KPCA transform and summation:
  `Quick_Dirty_MPNN_ML_V2_VGRAPHS_V1.ipynb.py.txt:328-343`

## Where "Reverse Neighbor-KPCA" Came From

The phrase is meaningful, but it refers to the pre-augmentation matrix, not the
final feature-map matrix.

In the pre-augmentation 75-column `S_*_X` matrix:

| Columns | Meaning |
|---:|---|
| `11..15` | forward neighbor-embedding PCA |
| `16..25` | forward neighbor-embedding KPCA |
| `26..30` | reverse-oriented neighbor-embedding PCA |
| `31..40` | reverse-oriented neighbor-embedding KPCA |
| `41..45` | forward message PCA |
| `46..55` | forward message KPCA |
| `56..60` | reverse-oriented message PCA |
| `61..70` | reverse-oriented message KPCA |
| `71` | neighbor embedding norm ratio |
| `72` | message norm ratio |
| `73` | neighbor embedding difference norm |
| `74` | message difference norm |

Primary source:

- Pre-augmentation projection layout:
  `Quick_Dirty_MPNN_ML_V2_VGRAPHS_V1.ipynb.py.txt:352-368`
- Norm/check features:
  `Quick_Dirty_MPNN_ML_V2_VGRAPHS_V1.ipynb.py.txt:370-388`

Then the notebook builds a compact augmented matrix. For direct mutation rows:

```text
aug 0..10  = raw 0..10
aug 11..15 = raw 11..15   forward neighbor PCA
aug 16..25 = raw 16..25   forward neighbor KPCA
aug 26..30 = raw 41..45   forward message PCA
aug 31..40 = raw 46..55   forward message KPCA
```

For synthetic reverse mutation rows, with DDG label multiplied by `-1`:

```text
aug 0..10  = sign/inversion/swapped scalar features
aug 11..15 = raw 26..30   reverse neighbor PCA
aug 16..25 = raw 31..40   reverse neighbor KPCA
aug 26..30 = raw 56..60   reverse message PCA
aug 31..40 = raw 61..70   reverse message KPCA
```

Primary source:

- Augmentation and column compaction:
  `Quick_Dirty_MPNN_ML_V2_VGRAPHS_V1.ipynb.py.txt:562-602`

Therefore, in the final A-H map, `31..35` are message-KPCA slots in
`S_*_X_aug`. For direct rows they are forward message KPCA; for synthetic
reverse rows they are reverse-oriented message KPCA. They are not neighbor KPCA
in the final model input.

## Remaining Cautions

1. The feature-E family now appears aligned with the manuscript, but the exact
   wording should mention that the code fits 10 KPCA components and uses the
   first five in the final A-H map.
2. Feature B needs manuscript cleanup if the manuscript numbers are confirmed
   to come from this final code path and the manuscript does not describe its
   message-ratio weighting. This is also recorded as an open provenance item in
   `MANUSCRIPT_TABLE_FIGURE_PROVENANCE_PLAN.md`.
3. The notebook comments at `Quick_Dirty_MPNN_ML_V2_VGRAPHS_V1.ipynb.py.txt`
   around column `61..70` say "neighbor_kpca_features" for reverse message
   KPCA. That looks like a stale copy-paste comment; the variables used there
   are `m_rev_cur_kpca_reduced_sum_feature`.
4. Table and figure numbers still need to be matched to exact executed
   notebook outputs or result artifacts before making final reproducibility or
   manuscript-cleanup claims.
5. "Backward", "reverse", and KL direction are overloaded terms in the code:
   - `backward_KL` means `KL(p_m || p_w)`.
   - `backward_weighted_*` means weighting neighbor features by a
     center-to-neighbor message-norm ratio instead of the initial top-neighbor
     message weights.
   - `reverse-mutant` means adding a synthetic mutation row with sign/swapped
     features and DDG label `-y`.
