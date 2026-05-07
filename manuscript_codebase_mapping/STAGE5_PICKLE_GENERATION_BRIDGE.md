# Stage 5 Pickle-Generation Bridge

Stage 5 asks for the code path that generated the pickle dictionaries used by
the RF notebooks.

The current working idea is sound: use the pickle files themselves as bridge
objects between upstream ProteinMPNN execution and downstream manuscript-table
evaluation.

## Why This Is Useful

The manuscript Table 1 evidence already points to RF notebooks that load
dataset-specific PMPNN pickle dictionaries. If we can prove which code produced
those same pickle dictionaries, then the pipeline is no longer a loose notebook
story. It becomes:

```text
ProteinMPNN-derived tensors and mutation records
-> feature-extraction notebook/code
-> dataset-specific PMPNN pickle dictionary
-> RF feature matrix assembly
-> RF evaluation output
-> manuscript table/figure value
```

That is the bridge from manuscript-code mapping into ProteinMPNN feature
extraction.

## Local Pickle Evidence

The local copied `Protein_MPNN_Digging` folder contains the expected
dataset-specific pickle family:

| File | Modified time in copied evidence | Size |
| --- | --- | --- |
| `S_2648_pmppn_info_dict_V3.pickle` | 2022-08-30 20:09:55 | 183266414 bytes |
| `S_921_pmppn_info_dict_V3.pickle` | 2022-08-30 20:42:04 | 64760657 bytes |
| `Ssym_pmppn_info_dict_V3.pickle` | 2022-08-30 21:19:29 | 24447664 bytes |
| `S_669_pmppn_info_dict_V3.pickle` | 2022-08-30 21:35:10 | 45318104 bytes |
| `S_2648_pmppn_info_dict_V2.pickle` | 2022-08-25 20:59:19 | 156651038 bytes |
| `S_921_pmppn_info_dict_V2.pickle` | 2022-08-25 22:03:49 | 55304432 bytes |
| `Ssym_pmppn_info_dict_V2.pickle` | 2022-08-25 22:22:41 | 20991070 bytes |
| `S_669_pmppn_info_dict_V2.pickle` | 2022-08-25 22:55:43 | 38853566 bytes |
| `S_2648_pmppn_info_dict.pickle` | 2022-08-15 00:49:34 | 89167705 bytes |
| `S_921_pmppn_info_dict.pickle` | 2022-08-15 22:19:15 | 31611020 bytes |
| `S_669_pmppn_info_dict.pickle` | 2022-08-15 22:42:16 | 22466075 bytes |
| `Ssym_pmppn_info_dict.pickle` | 2022-08-16 04:23:14 | 12187799 bytes |

The timestamp pattern suggests a versioned lineage:

```text
base pmppn_info_dict -> V2 pmppn_info_dict -> V3 pmppn_info_dict
```

This is only a timeline clue. It is not proof by itself.

## Downstream Consumer Evidence

The manuscript-level RF notebooks consume the V3 pickle family:

- `Quick_Dirty_MPNN_ML_V2_VGRAPHS_V1.ipynb.py.txt:47-54` loads
  `S_2648_pmppn_info_dict_V3.pickle`,
  `S_921_pmppn_info_dict_V3.pickle`,
  `S_669_pmppn_info_dict_V3.pickle`, and
  `Ssym_pmppn_info_dict_V3.pickle`.
- `Quick_Dirty_MPNN_ML_V2_V3.ipynb.py.txt:47-54` loads the same V3 family.
- `Quick_Dirty_MPNN_ML_V2_V2.ipynb.py.txt:47-54` instead loads the V2 family,
  making it an earlier RF-evaluation version, not the current Table 1 anchor.

This makes the V3 PMPNN dictionaries the first Stage 5 target, because they are
the dictionaries directly upstream of the current manuscript Table 1 evidence.

## Candidate Generation Code

The strongest current candidate code path for V3 generation is the matched
`*_ProteinMPNNTesting_V6_V2` notebook family:

| Dataset | Candidate source extract | Filename save evidence |
| --- | --- | --- |
| `S_2648` | `ProteinMPNNTesting_V6_V2.ipynb.py.txt` | lines 1954-1955 |
| `S_921` | `S921_ProteinMPNNTesting_V6_V2.ipynb.py.txt` | lines 1954-1955 |
| `S_669` | `S669_ProteinMPNNTesting_V6_V2.ipynb.py.txt` | lines 1961-1962 |
| `Ssym` | `Ssym_ProteinMPNNTesting_V6_V2.ipynb.py.txt` | lines 1958-1959 |

The surrounding code is not a generic file-write stub. It builds
`two_level_dict` by calling ProteinMPNN-related machinery and storing per-mutant
fields:

- `tied_featurize(...)` prepares ProteinMPNN inputs.
- `return_neighbor_info(...)` gets spatial neighbor identities.
- `mpnn_model(...)` extracts log probabilities, decoder messages, and node
  embeddings.
- The code stores `w_n_log_prob`, `m_n_log_prob`, `neighbor_aa_identities`,
  `neighbor_w_message_vector_coming_from_center`,
  `neighbor_m_message_vector_coming_from_center`,
  `neighbor_w_neighbor_embedding`, and `neighbor_m_neighbor_embedding`.

Representative line ranges:

- `S669_ProteinMPNNTesting_V6_V2.ipynb.py.txt:1750-1953`
- `Ssym_ProteinMPNNTesting_V6_V2.ipynb.py.txt:1747-1950`
- `S921_ProteinMPNNTesting_V6_V2.ipynb.py.txt:1743-1946`
- `ProteinMPNNTesting_V6_V2.ipynb.py.txt:1743-1946`

## Current Caution

The candidate save cells appear commented in the extracted notebook sources.
That means we should not claim yet that the saved notebook state executed those
exact write lines as currently displayed.

The better interpretation is:

1. The filename references point to the intended V3 output files.
2. The surrounding code is the correct kind of ProteinMPNN-to-`two_level_dict`
   extraction logic.
3. The local evidence copy contains V3 pickle files with modification times
   consistent with a same-day V3 generation sweep.
4. We still need content-level matching before calling this Stage 5 solved.

## Next Proof Steps

For each V3 pickle:

1. Create a structural fingerprint: top-level keys, mutation counts, per-entry
   field schema, array shapes, and representative numeric hashes.
2. Compare the fingerprint with the fields assigned by the candidate generator
   notebook.
3. Search saved notebook outputs for run-completion prints such as
   `Took ... for ... with ... forward-mutations` near the candidate generation
   cells.
4. Verify that the RF notebooks load the same pickle version that produced the
   manuscript evidence.
5. Only after those checks, mark the edge
   `ProteinMPNN feature-extraction code -> V3 PMPNN pickle dictionary` as
   proven.

