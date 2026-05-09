# S_921 Table 1 Notebook Cell Evidence

This note records the current local evidence linking the S_921 row in manuscript Table 1 to saved notebook cells.

Manuscript Table 1 row:

```text
S_921 | rF 0.77 | rR 0.77 | rF+R 0.79 | rF-R -1.00 | rmsF 1.49 | rmsR 1.49 | rmsF+R 1.49
```

## Primary Rounded Table Output

Notebook:

```text
source_repos/SajidAhmeduiu_ProteinMPNN/Sajid_Additions/Quick_Dirty_MPNN_ML_V2_VGRAPHS_V1.ipynb
```

Extracted source/output:

```text
colab_notebooks_inventory_analysis/git_notebook_sources/Quick_Dirty_MPNN_ML_V2_VGRAPHS_V1.ipynb.py.txt
colab_notebooks_inventory_analysis/git_notebook_outputs/Quick_Dirty_MPNN_ML_V2_VGRAPHS_V1.ipynb.outputs.txt
```

Relevant cells:

- Cell 5 loads `S_921_pmppn_info_dict_V3.pickle` (`git_notebook_sources`, lines 45-54).
- Cell 28 runs the RF feature-combination loop, including full `A+B+C+D+E+F+G+H` (`git_notebook_sources`, lines 977-1004).
- Cell 35 is explicitly annotated as quick averaging/printing for the manuscript table (`git_notebook_sources`, lines 1116-1147).

Cell 35 source prints S_921 metrics in this order:

```text
direct_PCC, reverse_PCC, total_PCC, direct_RMSE, reverse_RMSE, total_RMSE
```

The corresponding saved output for the S_921 block is:

```text
0.77
0.77
0.79
1.49
1.49
1.49
```

This output is in `git_notebook_outputs`, lines 5111-5135; the S_921 block is lines 5129-5134.

This accounts for every manuscript S_921 Table 1 value except `rF-R`.

## Forward-Vs-Reverse PCC Evidence

The `rF-R` value is computed in the full-feature branch of the same RF-loop logic:

```text
results_tracking_dict["S_921_forward_reverse_PCC"] = pearsonr(S_921_aug_preds[0::2], S_921_aug_preds[1::2])[0]
```

That computation appears in `git_notebook_sources`, lines 1025-1029, and in the
parallel `.ipynb.py.txt` V3 code-cell text file, lines 983-987.

Saved notebook output in `Quick_Dirty_MPNN_ML_V2_V3.ipynb` and the Drive-side `Quick_Dirty_MPNN_ML_V2_VGRAPHS_V1.ipynb` records:

```text
-0.9960837257021014
-0.9939184352208846
-0.9946606797887094
```

The visible source for that cell has the corresponding print lines commented, but the saved output order is aligned with those source comments:

```text
S_921_forward_reverse_PCC
S_669_forward_reverse_PCC
Ssym_forward_reverse_PCC
```

The V3 output is in `git_notebook_outputs`, lines 565-570. The Drive-side VGRAPHS output is in `notebook_outputs`, lines 5090-5095.

Therefore the S_921 forward-vs-reverse PCC is `-0.9960837257021014`, which rounds to `-1.00` in the manuscript table.

## Caution

I did not find a saved notebook output cell that prints the full seven-value S_921 manuscript row literally in one line. The six non-`rF-R` rounded values are emitted cleanly by the table-printing cell. The `rF-R` value is present as an unrounded saved output from the forward-vs-reverse PCC cell and rounds to the manuscript value.
