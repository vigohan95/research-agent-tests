# research-agent-tests

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.24368783.svg)](https://doi.org/10.5281/zenodo.24368783)

Evidence for one question: when a coding agent fixes a bug in research software and also writes the
regression test, does the test prove anything, or does it share the fix's misunderstanding?

Two parts, both small and both reproducible.

## `audit/`: what research repositories tell agents about tests

- `audit.py` checks 38 widely used research software repositories (chosen by hand, not sampled) for
  agent instruction files (`AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.cursorrules`,
  `.github/copilot-instructions.md`) at the repository root, through the GitHub API, and records
  keyword-level hits. Run: `python audit/audit.py out.json` (needs an authenticated `gh`).
- `audit-2026-11-06.json`, `audit-2026-11-17.json`: raw output of two runs. Both found the same set
  of 20 repositories with a root-level instruction file.
- `guides-read-2026-11-17.md`: all 20 files read in full by a person, one row per repository.
  Of the 20, 4 never mention tests; 3 require a bug-fix test to fail without the fix; 3 forbid
  weakening existing tests; 2 ask for comparison against an external truth; only statsmodels asks
  for a manual mutation check (change the line, the test must fail). Keyword hits overcount; the
  read is the number to use. Root-level files only, so this is a lower bound.

## `pilot/`: 5 real bugs, 18 agent runs

Cases (`cases.json`): 5 wrong-result fixes merged 2026-08-29 to 2026-10-31 in networkx (#8879,
#8906), pint (#2464), xarray (#11817) and mne-python (#14439), after the agent model's training
cutoff and none by the author of this repository. Each case's reference tests from the fix PR fail
on the buggy tree and pass on the fixed tree (`python pilot/run.py validate`).

| Round | Task given to the agent | Result |
|---|---|---|
| 1 (`RESULTS.md`) | Specific symptom; write a regression test | 9 of 9 tests fail on buggy, pass on fixed. The measure hit a ceiling. |
| 2 (`RESULTS2.md`) | Vague symptom; write the fix **and** the test | 9 of 9 agents said "my test fails before and passes after". **2 of 9 fixes were wrong, and the agent's own test passed on the wrong fix.** |

Round 2 also turned up a directed-graph case where `networkx.effective_size(G, nodes=...)` still
returns `nan` on networkx main of 2026-11-14 (details at the end of `RESULTS2.md`).

Grading is mechanical; no model judges anything:

- `run.py check CASE CANDIDATE.py`: the candidate test on the fixed tree, then on the fixed tree with
  only the source files reverted to the buggy commit (catches / misses / broken).
- `grade2.py`: round 2 adds the maintainers' tests on the agent's fix and the agent's test on its own
  fix; "shared misunderstanding" = own test passes, maintainers' tests fail.

Agent-written tests are in `tests/` (round 1) and `tests2/` (round 2), the agents' source diffs in
`fixes2/`, raw verdicts in `results*.jsonl`, token and time use per run in `usage*.jsonl`.

### Reproduce

Set `PILOT_WORK` to a directory holding clones of `networkx`, `pint`, `xarray` and `mne-python`
plus a virtual environment `.venv` with all four editable-installed (default: `./work`).
`mk2.sh` builds the round 2 sandboxes from those clones, `mkprompts2.py` writes the prompts given
to the agents, `collect.py` / `grade2.py` grade whatever the agents left in the sandboxes.

### Limits

One run per condition, one agent (Claude Opus 5.5), 5 hand-picked cases, each with one changed
source file. Isolation from the network and git history was instructed, not enforced. The
guidance-on versus guidance-off difference rests on single runs and is noise until repeated.
These are pilot numbers for a larger study design, not results.

## License

MIT for the scripts and write-ups in this repository. Diffs in `pilot/fixes2/` include context
lines from the upstream projects, which remain under their own licenses (networkx, pint and
mne-python: BSD-style; xarray: Apache-2.0).

## Citing

Each release is archived on Zenodo. To cite all versions use https://doi.org/10.5281/zenodo.24368783
(it resolves to the latest one); v0.1.0 is https://doi.org/10.5281/zenodo.24368784. See `CITATION.cff`.
