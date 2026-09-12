# Manuscript-path regeneration vs historical V3 pickles

Date: 2026-09-12  
Branch: `reproduce-paper-results`

## Naming policy

Do **not** call today’s regenerated tensors “V3 tensors.”

| Name | What it is |
| --- | --- |
| **Historical V3 pickles** | Saved Digging artifacts `*_pmppn_info_dict_V3.pickle` from the 2022 notebook era. Recovery/comparison reference only. |
| **Manuscript-path artifacts** | Fresh computation: PDB → modified ProteinMPNN → extraction tensors → engineered/PSSM/A–H features → RF → paper metrics. |

Legacy filenames like `regenerated_v3_features.pickle` may still appear as **compat aliases** pointing at manuscript-path pickles so older RF override flags keep working. Prefer `manuscript_path_features.pickle`.

## Computation path

```text
ACCRE PDB (+ optional independent curated fallback)
  + mutation/DDG tables
  + ProteinMPNN v_48_020.pt
  + modified_proteinmpnn (DecLayer / forward extraction hooks)
      → per-mutation extraction tensors (log_probs, messages, embeddings, neighbors, …)
      → engineered features + PSSM + manuscript A–H scalars
      → manuscript_path_features.pickle
      → Random Forest / KPCA → Table 1-style metrics
```

## Save modes (`--save-mode`)

| Mode | Durable? | Contents |
| --- | --- | --- |
| `full` (**default**) | yes | Full manuscript-path entry: ProteinMPNN tensor fields + engineered + PSSM + A–H. |
| `rf_compact` | RF-only interim | Scalars needed for current RF training (small). Insufficient as sole durable archive. |
| `both` | yes | Primary = full; shard payload also includes `entries_rf_compact`. |

`--compact-for-rf` remains a deprecated alias for `--save-mode rf_compact`.

### Full entry fields (schema sketch)

Always present when status=ok:

- Identity: `mut`, `ddg`, `protein_key`, `sequence_index`, `artifact_kind="manuscript_path"`
- Extraction tensors (`V3_TENSOR_FIELDS` name is historical code constant only):  
  `log_prob`, attention/neighbor index blocks, `w_n_log_prob`, `m_n_log_prob`,  
  message/embedding neighbor vectors, …
- Engineered / PSSM: center energies, neighbor KL/entropy/embedding scalars, `wild_pssm`, `alternate_pssm`, …
- Manuscript A–H: `feature_A` … `feature_H` (+ labeled B variants)

RF compact keeps the subset listed in `RF_KEEP_FIELDS` in the pipeline/worker.

## On-disk layout (local)

```text
reproduction_runs/YYYY-MM-DD/
  manuscript_path_tensors/          # preferred umbrella (symlinks/copies)
    S_2648/ → ../pdb_to_features_s2648/
    …
  pdb_to_features_<dataset>/        # pipeline --output-dir (existing runs)
    manuscript_path_features.pickle           # preferred name
    regenerated_v3_features.pickle            # compat symlink/alias
    MANUSCRIPT_PATH_ARTIFACT_SCHEMA.md
    shards/*.out.pkl
    tables/mutation_status.tsv
    json/pipeline_summary.json
```

## Google Drive (interim store)

Preferred long-term holding area for full tensors is the user’s Drive under a
stable prefix (see `scripts/upload_manuscript_path_tensors_to_drive.sh`).

**Current box blocker:** `rclone` is not installed and no remotes are configured.
Parent agent must arrange Drive auth / rclone remote before upload can run.

## Related docs

- Integrity / unprocessable mutations: `UNPROCESSABLE_MUTATIONS_AND_DATASET_GAPS.md`
- Independent PDB fetches: `reproduction_inputs/independent_pdb_fetches/README.md`
- Status: `REPRODUCTION_STATUS.md`
