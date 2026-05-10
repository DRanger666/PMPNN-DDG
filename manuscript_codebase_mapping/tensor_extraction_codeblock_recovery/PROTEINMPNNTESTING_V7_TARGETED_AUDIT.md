# ProteinMPNNTesting_V7 Targeted Audit

Scope: targeted audit of `ProteinMPNNTesting_V7.ipynb` after the current
Ssym direct-tensor value mismatch raised the question of whether V7 had been
missed during tensor-generation recovery.

This note is part of manuscript-codebase mapping, not manuscript inventory.
It uses the tracked source/output exports and inventory tables for the local
Drive evidence copy. The raw notebook remains an ignored local evidence file.
No FUSE mount content was read or modified for this audit.

## Main Conclusion

`ProteinMPNNTesting_V7.ipynb` is not a direct V3 tensor-generation notebook
under the current evidence.

Best current classification: S_2648 scalar feature-analysis and PSSM
augmentation notebook that consumes an already-existing early
`S_2648_pmppn_info_dict.pickle` object.

It should not be treated as a candidate explanation for the Ssym V3 direct
tensor-value mismatch, because it does not contain the ProteinMPNN inference
modifications or call-site tensor extraction needed to create the V3 direct
tensor fields.

## Files Checked

- Raw local notebook:
  `drive_evidence_copy/sajidahmedprotres_drive/Colab Notebooks/ProteinMPNNTesting_V7.ipynb`
- Source export:
  `colab_notebooks_inventory_analysis/notebook_sources/ProteinMPNNTesting_V7.ipynb.py.txt`
- Output export:
  `colab_notebooks_inventory_analysis/notebook_outputs/ProteinMPNNTesting_V7.ipynb.outputs.txt`
- Inventory and provenance tables:
  `colab_notebooks_inventory_analysis/colab_notebook_inventory.tsv`
  `colab_notebooks_inventory_analysis/colab_vs_git_notebooks_by_filename.tsv`
  `colab_notebooks_inventory_analysis/colab_artifact_mentions_by_cell.tsv`
  `colab_notebooks_inventory_analysis/colab_notebook_feature_result_cells.tsv`
  `colab_notebooks_inventory_analysis/colab_vs_git_notebook_similarity.tsv`
  `colab_notebooks_inventory_analysis/colab_notebook_internal_similarity.tsv`
  `manuscript_codebase_mapping/tensor_extraction_codeblock_recovery/tables/tensor_extraction_source_versions.tsv`

## Raw Notebook Status

- The raw notebook exists in the local evidence copy.
- It is ignored by the repo-level rule
  `.gitignore:6` `drive_evidence_copy/sajidahmedprotres_drive/*`.
- It is not tracked as a raw `.ipynb`.
- Its tracked derivatives are:
  `colab_notebooks_inventory_analysis/notebook_sources/ProteinMPNNTesting_V7.ipynb.py.txt`
  and
  `colab_notebooks_inventory_analysis/notebook_outputs/ProteinMPNNTesting_V7.ipynb.outputs.txt`.
- Local raw file fingerprint:
  `sha256=66cad8a8848a70304cc8247d38d9d2bb9b4b33f37994b476456e0c8e0d7d6bda`
- Local raw file size and mtime:
  `121399` bytes, `2022-08-18 00:27:05.388000000 +0600`.

## Why V7 Is Not The Direct V3 Tensor Generator

The source export does not define or call the core tensor-extraction machinery
that appears in the V6/V6_V2 generation candidates:

- no `DecLayer.forward` redefinition;
- no `ProteinMPNN.forward` redefinition;
- no `return_neighbor_info` function definition;
- no `mpnn_model(...)` call;
- no `decoding_order` or random-order construction;
- no direct storage of message-vector fields;
- no direct storage of neighbor-embedding fields.

The tensor-source version table records the same boundary:

- `ProteinMPNNTesting_V7.ipynb.py.txt`
- `has_modified_declayer_message_return=False`
- `has_forward_return_log_probs_decoder_messages_h_v=False`
- `has_return_neighbor_info_def=False`
- `has_decoder_message_topk=False`
- `has_neighbor_log_prob_fields=True`
- `has_neighbor_message_vector_fields=False`
- `has_neighbor_embedding_fields=False`
- `v3_tensor_field_assignment_count=6`
- `has_all_v3_tensor_field_assignments=False`
- `probable_role=NA`

That means V7 refers to some ProteinMPNN-derived fields, but does not show the
code path that creates the full V3 direct tensor surface.

## What V7 Does Contain

V7 mounts Google Drive, adds the old `vanilla_proteinmpnn` path to `sys.path`,
and changes into `/content/drive/MyDrive/Protein_MPNN_Digging`.

It then builds an S_2648 PDB residue-index mapping from:

`/content/drive/MyDrive/ACCRE_PyRun_Setup/S_2648_PDB_Files`

The saved outputs show ICODE-related skip evidence for:

- `1lveA:S27`
- `2immA:N31`

V7 has only commented references to the early pickle:

- `S_2648_pmppn_info_dict.pickle` as a commented save target.
- `S_2648_pmppn_info_dict.pickle` as a commented load source.

It has no V2/V3 pickle filename reference.

The main executed analysis loops over an existing `two_level_dict` and uses
already-present fields such as:

- `log_prob`
- `w_n_log_prob`
- `m_n_log_prob`
- `neighbor_aa_identities`
- `top_15_neighbor_indices`
- `top_15_attention_weights`

It computes scalar predictors/correlations from those existing fields, then
adds PSSM-derived values from:

`/content/drive/MyDrive/ACCRE_PyRun_Setup/S_2648_pssm_dir`

The output export preserves correlation blocks from cells 11 and 16, plus
plot outputs from cells 22 and 23.

## Feature-History Clues

V7 is still important, but for feature-history and S_2648 provenance rather
than direct V3 tensor generation.

It records an intermediate moment where `log_prob` and neighbor log-probability
fields existed in `two_level_dict`, while the notebook comments explicitly
questioned why top-5 neighbor fields were absent.

It also uses `softmax(top_15_attention_weights)` for weighted neighbor entropy,
energy-change, and KL predictors. Later recovered V3 engineered-feature code
uses different weighting logic for some fields, so V7 is useful evidence for
feature evolution and possible manuscript-method tightening.

Similarity tables support this role. V7 is a much smaller notebook than the
V6/V6_V2 generation candidates and is highly contained within the older
S_2648 feature-analysis tails:

- V7 vs Git `ProteinMPNNTesting_V6.ipynb`: containment of smaller source
  `0.9835`.
- V7 vs Git `ProteinMPNNTesting_V6_V2.ipynb`: containment of smaller source
  `0.8848`.
- Internal local V6 vs V7: containment of smaller source `0.9890`.
- Internal local V6_V2 vs V7: containment of smaller source `0.9104`.

That pattern is consistent with V7 being a reduced/sliced feature-analysis
notebook, not a later complete tensor-generation notebook.

## Relevance To Current Tensor Mismatch

For the current Ssym V3 direct-tensor value mismatch, V7 does not change the
main debugging path.

The direct tensor-value mismatch still has to be investigated against the
V6/V6_V2-style tensor-generation candidates and the algorithmic choices already
tracked in:

- `TENSOR_EXTRACTION_ALGORITHM_DEBUGGING.md`

V7 should be kept in mind for separate questions:

- early S_2648 `S_2648_pmppn_info_dict.pickle` provenance;
- S_2648 ICODE skip behavior for `1lveA` and `2immA`;
- evolution from early attention/softmax-weighted scalar features to later V3
  engineered fields;
- possible mismatch between manuscript method wording and the exact scalar
  feature variants used in notebooks.

## Audit Verdict

V7 was correctly excluded as a primary V3 tensor-extraction source in the
current recovery notes. The earlier classification was not enough by itself,
but this targeted audit supports it.

Operational consequence: do not use V7 as the next tensor-value debugging
candidate. Use it later when reconstructing early S_2648 feature history and
when explaining how scalar feature definitions evolved across notebooks.
