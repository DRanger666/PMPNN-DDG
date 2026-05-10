# Tensor Extraction Codeblock Recovery

Scope: Set 1 recovery for ProteinMPNN-DDG V3 pickle-level reproduction.
This report identifies codeblocks that expose ProteinMPNN intermediate tensors.
It does not cover the later engineered/PSSM feature-construction codeblocks.

## Main Finding

The strongest current evidence points to notebook-side copied ProteinMPNN
class/function definitions as the effective tensor-extraction source for the
V3 pickle generation notebooks. The checked-out old fork Python source is
useful history, but it does not by itself contain the complete V6_V2 behavior.

Primary V6_V2 notebooks with all direct V3 tensor-field assignments: True.

## Recovered Set 1 Scaffold

The V6_V2 tensor-extraction behavior is now represented in a small workspace
module:

- `proteinmpnn_ddg_recovery/recovered_v6v2.py`

This module keeps the scope narrow: it loads the recovered ProteinMPNN utility
source, applies the two V6_V2 tensor-return changes, and exposes helpers for
one-mutation tensor extraction. It does not construct engineered/PSSM features
and does not claim full V3 pickle reproduction.

The first smoke test is:

- `scripts/smoke_test_ssym_tensor_extraction.py`

Current Ssym test target:

- Protein: `1amqA`
- Mutation: `C191Y`
- PDB residue-map sequence index: `179`
- Result: all direct V3 tensor-field shapes match the saved Ssym V3 target
  entry, and all generated numeric tensors are finite.

Smoke-test outputs:

- `ssym_smoke_test/SSYM_TENSOR_EXTRACTION_SMOKE_TEST.md`
- `ssym_smoke_test/tables/ssym_tensor_field_schema_compare.tsv`
- `ssym_smoke_test/json/ssym_tensor_extraction_smoke_summary.json`

## Ssym All-Entry Tensor Experiment

A dedicated all-entry Ssym tensor-only experiment has now been run:

- Script: `scripts/test_ssym_tensor_extraction_all_entries.py`
- Target: all saved `Ssym_pmppn_info_dict_V3.pickle` mutation entries
- Mutation entries: `342`
- Direct V3 tensor fields checked per entry: `16`
- Successful entries: `342`
- Schema failures: `0`
- Runtime errors: `0`

This result means the recovered Set 1 scaffold can traverse the complete Ssym
V3 direct tensor-field surface without shape mismatches or finite-numeric
failures. It does not validate engineered/PSSM feature construction.

Important value-level boundary: this is not a direct tensor-value reproduction.
The closest-neighbor geometry fields match all `342/342` Ssym entries, but all
other numeric direct tensor fields have value-level mismatches against the saved
Ssym V3 pickle. See:

- `ssym_all_entries_tensor_extraction/tables/ssym_tensor_value_mismatch_summary.tsv`
- `TENSOR_EXTRACTION_ALGORITHM_DEBUGGING.md`

All-entry outputs:

- `ssym_all_entries_tensor_extraction/SSYM_ALL_ENTRIES_TENSOR_EXTRACTION_EXPERIMENT.md`
- `ssym_all_entries_tensor_extraction/tables/ssym_all_entries_mutation_status.tsv`
- `ssym_all_entries_tensor_extraction/tables/ssym_all_entries_field_schema_compare.tsv`
- `ssym_all_entries_tensor_extraction/json/ssym_all_entries_tensor_extraction_summary.json`

Primary candidate notebooks:

- `colab_notebooks_inventory_analysis/git_notebook_sources/ProteinMPNNTesting_V6_V2.ipynb.py.txt`: primary V3 tensor-extraction candidate; field assignments=16.
- `colab_notebooks_inventory_analysis/git_notebook_sources/S669_ProteinMPNNTesting_V6_V2.ipynb.py.txt`: primary V3 tensor-extraction candidate; field assignments=16.
- `colab_notebooks_inventory_analysis/git_notebook_sources/S921_ProteinMPNNTesting_V6_V2.ipynb.py.txt`: primary V3 tensor-extraction candidate; field assignments=16.
- `colab_notebooks_inventory_analysis/git_notebook_sources/Ssym_ProteinMPNNTesting_V6_V2.ipynb.py.txt`: primary V3 tensor-extraction candidate; field assignments=16.

## Direct Answers

Which files/cells modified or wrapped ProteinMPNN inference?

- The V6_V2 notebook source exports redefine `DecLayer.forward` and
  `ProteinMPNN.forward` in notebook code. These are copied definitions, not
  just calls into the checked-out Python source.
- Earlier V4/V5/V6 notebook variants expose decoder messages; V6_V2 adds
  final node embeddings by returning `h_V` from `ProteinMPNN.forward`.

Where were message tensors exposed?

- `DecLayer.forward` returns `h_message/self.scale`: `colab_notebooks_inventory_analysis/git_notebook_sources/ProteinMPNNTesting_V4.ipynb.py.txt:831`; `colab_notebooks_inventory_analysis/git_notebook_sources/ProteinMPNNTesting_V5.ipynb.py.txt:831`; `colab_notebooks_inventory_analysis/git_notebook_sources/ProteinMPNNTesting_V6.ipynb.py.txt:831`; `colab_notebooks_inventory_analysis/git_notebook_sources/ProteinMPNNTesting_V6_V2.ipynb.py.txt:831`; `colab_notebooks_inventory_analysis/git_notebook_sources/S669_ProteinMPNNTesting_V6.ipynb.py.txt:830`; `colab_notebooks_inventory_analysis/git_notebook_sources/S669_ProteinMPNNTesting_V6_V2.ipynb.py.txt:831`.
- `ProteinMPNN.forward` returns `decoder_messages`: `colab_notebooks_inventory_analysis/git_notebook_sources/ProteinMPNNTesting_V6_V2.ipynb.py.txt:1072`; `colab_notebooks_inventory_analysis/git_notebook_sources/S669_ProteinMPNNTesting_V6_V2.ipynb.py.txt:1072`; `colab_notebooks_inventory_analysis/git_notebook_sources/S921_ProteinMPNNTesting_V6_V2.ipynb.py.txt:1072`; `colab_notebooks_inventory_analysis/git_notebook_sources/Ssym_ProteinMPNNTesting_V6_V2.ipynb.py.txt:1072`; `colab_notebooks_inventory_analysis/notebook_sources/ProteinMPNNTesting_V6_V2.ipynb.py.txt:1072`; `colab_notebooks_inventory_analysis/notebook_sources/ProteinMPNNTesting_V6_V2_debug.ipynb.py.txt:1072`.

Where were neighbor embeddings exposed?

- V6_V2 returns `h_V`, and the neighbor loop reads `mpnn_model(...)[2][0,n_ind,:]`: `colab_notebooks_inventory_analysis/git_notebook_sources/ProteinMPNNTesting_V6_V2.ipynb.py.txt:1905`; `colab_notebooks_inventory_analysis/git_notebook_sources/ProteinMPNNTesting_V6_V2.ipynb.py.txt:1930`; `colab_notebooks_inventory_analysis/git_notebook_sources/S669_ProteinMPNNTesting_V6_V2.ipynb.py.txt:1912`; `colab_notebooks_inventory_analysis/git_notebook_sources/S669_ProteinMPNNTesting_V6_V2.ipynb.py.txt:1937`; `colab_notebooks_inventory_analysis/git_notebook_sources/S921_ProteinMPNNTesting_V6_V2.ipynb.py.txt:1905`; `colab_notebooks_inventory_analysis/git_notebook_sources/S921_ProteinMPNNTesting_V6_V2.ipynb.py.txt:1930`.

Where were neighbor indices and identities exposed?

- `return_neighbor_info(X, mask)` exposes nearest-neighbor residue indices: `colab_notebooks_inventory_analysis/git_notebook_sources/ProteinMPNNTesting_V4.ipynb.py.txt:1609`; `colab_notebooks_inventory_analysis/git_notebook_sources/ProteinMPNNTesting_V5.ipynb.py.txt:1609`; `colab_notebooks_inventory_analysis/git_notebook_sources/ProteinMPNNTesting_V6.ipynb.py.txt:1609`; `colab_notebooks_inventory_analysis/git_notebook_sources/ProteinMPNNTesting_V6_V2.ipynb.py.txt:1610`; `colab_notebooks_inventory_analysis/git_notebook_sources/S669_ProteinMPNNTesting_V6.ipynb.py.txt:1615`; `colab_notebooks_inventory_analysis/git_notebook_sources/S669_ProteinMPNNTesting_V6_V2.ipynb.py.txt:1617`.
- Neighbor amino-acid identity is stored from `seq_chain[n_ind]`; see the
  `neighbor_aa_identities` row in `tables/v3_field_to_tensor_extraction_evidence.tsv`.

Where were wild-type vs mutant log-probabilities extracted?

- The center-position log-probability tensor is stored in `mut["log_prob"]`.
- Neighbor wild-type and mutant log-probability vectors come from modified
  forward output index 0 before and after `S[0,seq_index]` is edited.
- Center mutation assignment evidence: `colab_notebooks_inventory_analysis/git_notebook_sources/ProteinMPNNTesting_V5.ipynb.py.txt:1883`; `colab_notebooks_inventory_analysis/git_notebook_sources/ProteinMPNNTesting_V6.ipynb.py.txt:1902`; `colab_notebooks_inventory_analysis/git_notebook_sources/ProteinMPNNTesting_V6_V2.ipynb.py.txt:1924`; `colab_notebooks_inventory_analysis/git_notebook_sources/S669_ProteinMPNNTesting_V6.ipynb.py.txt:1908`; `colab_notebooks_inventory_analysis/git_notebook_sources/S669_ProteinMPNNTesting_V6_V2.ipynb.py.txt:1931`; `colab_notebooks_inventory_analysis/git_notebook_sources/S921_ProteinMPNNTesting_V6_V2.ipynb.py.txt:1924`.

Which exposed tensors correspond to each V3 pickle field?

- See `tables/v3_field_to_tensor_extraction_evidence.tsv`.

Were tensors produced by edited source files, monkeypatching, copied
functions, or plain call-site extraction?

- Current evidence: copied notebook-side class/function definitions plus
  call-site extraction. The old fork Python source contains neighbor-info
  history, but the complete V6_V2 three-output `ProteinMPNN.forward` is in
  notebook source exports.

## Old Fork History Clue

- `7dd03b9` `added neighbor extraction function to ProteinFeatures`
  by Sajid Ahmed <sajid.ahmed@vanderbilt.edu> on 2022-08-09T10:29:28-05:00.
- This supports the history of neighbor extraction work, but the direct
  V3 tensor-extraction evidence is still the V6_V2 notebook source.

## Evidence Tables

- `tables/tensor_extraction_codeblock_hits.tsv`: line-level hits for tensor
  exposure, neighbor mapping, mutation editing, and V3 field storage.
- `tables/tensor_extraction_source_versions.tsv`: source-file version summary
  showing which notebooks contain message, embedding, and V3 storage code.
- `tables/v3_field_to_tensor_extraction_evidence.tsv`: field-by-field mapping
  from V3 pickle field to exposed tensor or direct code value.
- `tables/old_fork_proteinmpnn_history.tsv`: commits touching old fork
  ProteinMPNN source files.

## Current Debugging Boundary

The Ssym engineered/PSSM feature-construction segment has been value-proven
when it starts from saved V3 direct tensor fields. The remaining unresolved
part is the direct tensor-extraction segment itself: the recovered V6_V2-style
scaffold operationalizes the manuscript-level control flow, but it does not yet
regenerate the saved Ssym V3 direct tensor values.
