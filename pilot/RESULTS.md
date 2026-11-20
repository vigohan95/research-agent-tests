# Pilot 1 (2026-11-14): 5 real bugs, agent writes the test from the symptom

## Setup
- 5 merged wrong-result fixes, all merged 2026-08-29 to 2026-10-31 (after the agent model's training cutoff, June 2026), none by the applicant: networkx #8879 (group betweenness), networkx #8906 (effective_size), pint #2464 (np.mod with mixed units), xarray #11817 (str.zfill sign), mne-python #14439 (Raw.crop annotations). Details in `cases.json`.
- Reference tests from each fix: all 5 fail on the buggy tree and pass on the fixed tree (`python run.py validate`).
- Agent: Claude Opus 5.5 as a general-purpose subagent, one run per condition. It got a `git archive` snapshot of the buggy commit (no history), the symptom text only, and was told not to use the network, git or files outside the snapshot. These rules were stated, not enforced.
- Condition A: agent instruction files (AGENTS.md, CLAUDE.md, .claude/, nested ones) removed. Condition B: kept, and the agent was told to follow them. pint has no such file, so it has only A.
- Grading is mechanical (`run.py check`): the candidate file is dropped into the fixed tree, then into the fixed tree with only the source files reverted to the buggy commit.

## Result
| Case | A | B |
|---|---|---|
| networkx-8879 | catches (13 tests) | catches (3) |
| networkx-8906 | catches (5) | catches (7) |
| pint-2464 | catches (6) | n/a |
| xarray-11817 | catches (6) | catches (6, +6 dask skipped) |
| mne-14439 | catches (4) | catches (7) |

9 of 9 candidate tests fail on the buggy code and pass on the fixed code. Cost per run: 69.6k to 97.8k tokens (mean 78.5k, total 706k for 9 runs), 4 to 14 tool calls, median 77 s.

## What this means for the proposal
- **The main measure hit a ceiling.** With a symptom this specific (it names the function and often the wrong value), the agent reproduces the bug every time, with or without repository guidance. On these cases "fails on buggy, passes on fixed" cannot show whether guidance helps. This has to be said in the proposal, and work package 1 has to change:
  1. Vaguer symptoms: the downstream effect only (a wrong number in an analysis), not the function and value.
  2. A second measure: injected faults in the changed code (mutation score), and how well the test survives plausible but wrong fixes.
  3. A harder task variant: the agent writes the fix and the test together, and the test is then run against the buggy code. This is the case the proposal is actually about (shared author, shared misunderstanding).
- **The cost estimate can be grounded.** About 80k tokens per agent run at this difficulty. 60 cases x 4 conditions x 2 agents x 3 repeats is about 1,440 runs, about 115M tokens. Dollar figures, and why they are a lower bound, are in `RESULTS2.md`.
- **Side finding:** networkx-8906-A noticed that `effective_size(G, nodes=..., weight=...)` returns `nan` for a sink node in a directed graph. Not checked yet; if it holds on current networkx main it is a separate upstream issue.
- Guidance files changed style, not outcome: B tests followed repo conventions (type hints and the dask fixture in xarray, numpydoc and the license header in mne).

## Limits
One run per condition, one agent, 5 cases chosen by hand. Isolation rules were instructions only; the editable install in the shared venv points at clones checked out at the fixed commit, so an agent that ignored the rules could have read the fix.
