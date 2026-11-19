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

## `pilot/`: 19 real bugs, 73 agent runs

Cases (`cases.json`): 19 wrong-result fixes merged 2026-08-10 to 2026-11-18 in 9 projects
(networkx, pint, xarray, mne-python, numpyro, ESMValCore, statsmodels, nilearn, pyvista), none by
the author of this repository. Rounds 1 and 2 used 5 of them: networkx #8879 and #8906, pint
#2464, xarray #11817 and mne-python #14439, all merged after the agent model's training cutoff.
Each case's reference tests from the fix PR fail on the buggy tree and pass on the fixed tree
(`python pilot/run.py validate`).

| Round | Task given to the agent | Result |
|---|---|---|
| 1 (`RESULTS.md`) | 5 cases. Specific symptom; write a regression test | 9 of 9 tests fail on buggy, pass on fixed. The measure hit a ceiling. |
| 2 (`RESULTS2.md`) | 5 cases. Vague symptom; write the fix **and** the test | 9 of 9 agents said "my test fails before and passes after". **2 of 9 fixes were wrong, and the agent's own test passed on the wrong fix.** |
| 3 (`PROTOCOL3.md`, `RESULTS3.md`) | 19 cases, same task, three conditions: no instruction files, the repository's own, and three testing rules taken from statsmodels. Protocol committed before the first run; the 9 runs of round 2 repeated | **In 12 of 55 runs the agent's fix fails the maintainers' tests and the agent's own test passes on it.** Read by hand: 5 leave wrong results, 3 fix less than the maintainers did, 4 are defensible choices that the reference tests rule out. 7 of the 9 repeated runs gave the same verdicts. Differences between conditions are within that noise. |

Round 2 also turned up a directed-graph case where `networkx.effective_size(G, nodes=...)` still
returns `nan` on networkx main of 2026-11-14 (details at the end of `RESULTS2.md`).

Grading is mechanical; no model judges anything:

- `run.py check CASE CANDIDATE.py`: the candidate test on the fixed tree, then on the fixed tree with
  only the source files reverted to the buggy commit (catches / misses / broken).
- `grade2.py`, `grade3.py`: rounds 2 and 3 add the maintainers' tests on the agent's fix and the
  agent's test on its own fix; "shared misunderstanding" = own test passes, maintainers' tests fail.
- Round 3 adds a step that is not mechanical and is labelled as such: every failing fix and every
  broken test was read by hand, and `RESULTS3.md` describes each one.

Agent-written tests are in `tests/` (round 1), `tests2/` and `tests3/`, the agents' source diffs in
`fixes2/` and `fixes3/`, raw verdicts in `results*.jsonl`, token and time use per run in
`usage*.jsonl`. `report3.py` prints the count tables of `RESULTS3.md` from those files.

### Reproduce

Set `PILOT_WORK` to a directory holding clones of the projects and the virtual environments named
in `cases.json` (default: `./work`; each case names its clone in `repo` and, if it does not use
`.venv`, its environment in `venv`). `PROTOCOL3.md` lists what had to be done by hand to make
each project import on Windows without a compiler.

- Round 2: `mk2.sh` builds the sandboxes, `mkprompts2.py` writes the prompts, `collect.py` /
  `grade2.py` grade whatever the agents left in the sandboxes.
- Round 3: `mkprotocol3.py` writes `runs3.json`, `mk3.py` builds the 55 sandboxes and parks the
  clones on buggy commits, `mkprompts3.py` writes the prompts, `grade3.py` grades, `report3.py`
  prints the tables.

### Limits

One run per case and condition, one agent (Claude Opus 5.5), 19 hand-picked cases from 9
projects, 18 of them with one changed source file. Isolation from the network and git history
was instructed, not enforced, and 5 round 3 runs touched something outside their sandbox (listed
in `RESULTS3.md`). Two of nine identical repeats changed a verdict, so differences between
conditions are noise until there are repeats. The hand reading in round 3 was not done by a
maintainer of any of the projects. These are pilot numbers for a larger study design, not results.

## License

MIT for the scripts and write-ups in this repository. Diffs in `pilot/fixes2/` and `pilot/fixes3/`
include context lines from the upstream projects, which remain under their own licenses (networkx,
pint, mne-python, statsmodels and nilearn: BSD-style; xarray, numpyro and ESMValCore: Apache-2.0;
pyvista: MIT). `pilot/guidance_T.md` quotes three bullets from the statsmodels `AGENTS.md`
(BSD-3-Clause).

## Citing

Each release is archived on Zenodo. To cite all versions use https://doi.org/10.5281/zenodo.24368783
(it resolves to the latest one). v0.1.0 (rounds 1 and 2) is https://doi.org/10.5281/zenodo.24368784;
the DOI of each later version is listed on that Zenodo page. See `CITATION.cff`.
