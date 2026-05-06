# SajidAhmeduiu ProteinMPNN Provenance Audit

Target repository: `https://github.com/SajidAhmeduiu/ProteinMPNN.git`

Local audit clone: `source_repos/SajidAhmeduiu_ProteinMPNN`

## Repository Shape

- GitHub repo: `SajidAhmeduiu/ProteinMPNN`
- Visibility: public
- Default branch: `main`
- Fork: yes
- Parent repo: `dauparas/ProteinMPNN`
- Created: `2022-07-27T21:16:38Z`
- Last pushed: `2022-10-25T19:21:34Z`
- Current `main` / `HEAD`: `121bef560acbf47ea98a47ba6fc08d35401cc17a`
- Current head subject: `Local Run Updated Copy`

## History Summary

- Total commits in old fork clone: 105
- Canonical `dauparas/ProteinMPNN` commits fetched for comparison: 93
- Merge base with current canonical main: `c602ced6ad4b6997d89afa9432607ac9d0572539`
- Merge base subject: `updating af_backprop version`
- Divergence from current canonical main:
  - 44 commits unique to `SajidAhmeduiu/ProteinMPNN`
  - 32 commits unique to current `dauparas/ProteinMPNN`

## Sajid-Authored Unique Commits

Unique fork-side commits after the merge base are all authored by Sajid identities:

- 34 commits: `Sajid <sahmed133002@bscse.uiu.ac.bd>`
- 10 commits: `Sajid Ahmed <sajid.ahmed@vanderbilt.edu>`

Committer emails for those 44 unique commits:

- 34 commits: `sahmed133002@bscse.uiu.ac.bd`
- 10 commits: `noreply@github.com`

Important attribution implication:

- The two author emails that matter for GitHub commit attribution are `sahmed133002@bscse.uiu.ac.bd` and `sajid.ahmed@vanderbilt.edu`.
- These are normal email addresses in the commit author field, not GitHub `users.noreply.github.com` author addresses.
- If the goal is to reattribute the old Sajid-authored commits to the current GitHub identity, these exact author emails are the first emails to investigate for transfer/addition to the current account.

## Unique Commit Window

The unique fork-side work runs from:

- First unique commit: `d845dab` on `2022-07-28`, subject `Added some comments describing how embeddings or attention weights from different layers can be extracted`
- Last unique commit: `121bef5` on `2022-10-25`, subject `Local Run Updated Copy`

There are two merge commits in the unique history:

- `0dee66c` on `2022-07-31`, `Merge branch 'main' of https://github.com/SajidAhmeduiu/ProteinMPNN into main`
- `f459158` on `2022-08-08`, `Merge branch 'main' of https://github.com/SajidAhmeduiu/ProteinMPNN into main`

## Working Tree Shape

Top-level project additions/organization in the old fork include:

- `Sajid_Additions/`
- `ca_proteinmpnn/`
- `vanilla_proteinmpnn/`
- modified `README.md`

Approximate local sizes:

- worktree plus `.git`: 130M
- `.git`: 124M
- `vanilla_proteinmpnn`: 30M
- `ca_proteinmpnn`: 23M
- `Sajid_Additions`: 7.3M
- `colab_notebooks`: 816K

## Initial Assessment

This repo is a strong candidate for preserving history rather than copying files only. The old fork has a compact, meaningful 44-commit continuation history that is separate from later canonical upstream changes.

For account-attribution planning, do not rewrite commits yet. First verify account/email control and GitHub behavior:

1. Determine whether `sahmed133002@bscse.uiu.ac.bd` is still accessible and currently attached to the old account.
2. Determine whether `sajid.ahmed@vanderbilt.edu` is still accessible and currently attached to the old account.
3. Keep the old GitHub account operational by assigning it a different verified primary and backup email before detaching any historical commit email.
4. Only then test adding the historical author email(s) to the current GitHub account.

For code/history integration, the likely next analysis is to decide whether to:

- transfer/fork-preserve the old repository,
- import this old fork as a historical branch into a new repo,
- merge the 44 unique commits into a modern ProteinMPNN-derived repo,
- or extract only `Sajid_Additions`, `ca_proteinmpnn`, and `vanilla_proteinmpnn` with preserved history.
