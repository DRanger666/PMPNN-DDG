# Manuscript Number Provenance Viewpoint

Manuscript numbers should be treated as endpoints in a provenance graph, not as isolated table values.

For each reported number, we need evidence for every edge in this chain:

```text
manuscript number
<- notebook cell/output that emitted the number
<- RF training/evaluation variables used by that cell
<- feature matrix assembled from pickle dictionaries
<- pickle dictionary file loaded into the notebook
<- code that created the pickle dictionary
<- ProteinMPNN outputs, mutation rows, structures, and dataset files used by that code
```

The goal is to recover not only the value, but why that value exists.

For each manuscript table or figure number, record:

1. The exact notebook and cell that emitted it.
2. The exact output text, image, or saved object containing it.
3. The variables/features used by that cell.
4. The pickle file or files that populated those variables.
5. The code path that generated those pickle files.
6. The upstream ProteinMPNN outputs, mutation lists, and structure files.
7. Any randomness, rerun dependency, copied-notebook divergence, or ambiguity.

The S_921 Table 1 row is the current template: six rounded table values are emitted by one table-printing cell, while `rF-R = -1.00` is supported by a separate forward-vs-reverse PCC output that rounds from `-0.9960837257021014`.

Next targets:

- S_669
- Ssym
- S_2648
