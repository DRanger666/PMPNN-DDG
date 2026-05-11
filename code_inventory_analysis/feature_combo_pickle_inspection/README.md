# Feature-Combination Pickle Inspection

Generated at: `2026-05-11T03:33:01.669449+00:00`
Runtime: Python `3.10.15`, scikit-learn `1.1.3`, NumPy `1.26.4`.

This report inspects the large historical model pickles and nearby result-summary pickles in `Protein_MPNN_Digging`.

## Model Pickles

- `feature_combo_model_dict.pickle`: top-level `builtins.dict`, len `63`, model entries `63`, size `952599676` bytes
  - `sklearn.ensemble._forest.RandomForestRegressor`: `63` entries
  - Load warnings: `19026` total, `2` unique
- `S_669_feature_combo_model_dict.pickle`: top-level `builtins.dict`, len `63`, model entries `63`, size `237692804` bytes
  - `sklearn.ensemble._forest.RandomForestRegressor`: `63` entries
  - Load warnings: `19026` total, `2` unique

## Context Result Pickles

- `feature_combo_result_dict.pickle`: top-level `builtins.dict`, len `3`, model entries `0`, size `6490` bytes
  - Numeric result rows extracted: `189`
- `S_669_feature_combo_result_dict.pickle`: top-level `builtins.dict`, len `3`, model entries `0`, size `6491` bytes
  - Numeric result rows extracted: `189`
- `incremental_feature_result_dict.pickle`: top-level `builtins.dict`, len `18`, model entries `0`, size `3265` bytes
  - Numeric result rows extracted: `144`
- `list_incremental_feature_result_dict.pickle`: top-level `builtins.list`, len `10`, model entries `0`, size `50451` bytes
  - Numeric result rows extracted: `1920`
- `res_dict.pickle`: top-level `builtins.dict`, len `132`, model entries `0`, size `19866522` bytes

## Interpretation Guardrails

- A saved model pickle can explain historical evaluation only if a notebook or code path loads it for prediction/evaluation.
- If the manuscript numbers were produced by training models inside a notebook, these pickles may be saved byproducts rather than the direct source of the manuscript table.
- The model metadata here is therefore evidence for possible reuse, not by itself proof of manuscript-number provenance.

## Generated Files

- `feature_combo_pickle_summary.json`
- `feature_combo_model_entries.tsv`
- `feature_combo_result_entries.tsv`
- `README.md`
