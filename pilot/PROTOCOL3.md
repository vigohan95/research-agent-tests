# Pilot 3 protocol

Written and committed before any round 3 agent run. The commit that adds this file is the
record of that; `RESULTS3.md` will list every departure from it.

## Question

Rounds 1 and 2 used 5 bugs. Round 2 found that in 2 of 9 runs the agent's fix was wrong and the
agent's own test passed on it. Round 3 asks three things, in this order:

1. Does that rate hold on more cases and more projects?
2. How much do single runs move? The 9 round 2 runs are repeated from scratch with the same
   prompts and the same model.
3. Is there any sign that what the repository tells the agent about tests changes the rate?
   With one run per condition this round can only show a direction worth testing, not an effect.

## Cases

A case is one merged upstream bug fix. All of the following must hold (`cases.json`):

- merged into the default branch on or after 2026-08-01 (`fixed` = the commit that landed the PR
  there: the squash commit, or for statsmodels the merge commit; `buggy` = its first parent);
- the bug gave a silently wrong result (a wrong number, unit, sign, alignment or selection of
  data), not a crash, warning, performance or packaging problem;
- the fix changes 1 to 3 non-test `.py` files, and the same PR adds or changes tests;
- the PR's tests pass on the fixed tree and fail on the fixed tree with only those source files
  reverted (`python run.py validate` prints `catches` for every case);
- the package installs and its tests run on the machine used (Windows 11, Python 3.12, no C
  compiler; compiled extensions come from the nearest release wheel, and a case is dropped if a
  compiled source on its code path changed between that release and the case).

The 5 cases of rounds 1 and 2 are kept. New cases were searched in statsmodels, numpyro,
ESMValTool / ESMValCore and a list of other research packages (pymc, pyvista, arviz, sympy,
astropy, scikit-image, MDAnalysis, nilearn, lmfit, and further PRs in xarray, networkx, pint and
mne-python), newest PRs first, by helper agents that only prepared cases and ran the reference
tests. They were asked for 2 to 4 cases per project and to prefer bugs whose correct value can be
checked against a reference. So the cases are chosen by hand, not sampled, as in rounds 1 and 2.
No agent attempted to fix any new case before this file was committed.

Candidates the helpers looked at and did not use:

- numpyro: #2348, #2373, #2405 and #2296 also pass the checks above; the helper kept the four whose
  symptom a user would notice most easily (#2348 is silently wrong only when rank equals
  dimension, #2373 is a fractional-threshold edge case, #2405 and #2296 are about shapes and
  sampler internals). #2414 is mainly a crash.
- ESMValCore: #3246 (the test that shows the wrong values needs the compiled regridding library),
  #3282 (the tests import a class the PR adds, so they error on the old code), #3238 (not a
  wrong result). ESMValTool: no wrong-result fix with tests since August (#4600 and #4671 are
  about a file extension and a recipe path).
- statsmodels: #10636 (a crash), #10574 (passes the checks; reference tests take 70 s per run,
  left out as a spare), #10758 (passes the checks; left out because only an unusual input shape
  triggers it).
- Other packages: astropy #20573 and networkx #8837 (more than 3 source files or a wide diff).
  xarray #11615, pint #2425 and #2408 and pymc #8452 look as if they qualify and were not set
  up. The remaining astropy, scikit-image and MDAnalysis candidates need compiled extensions and
  were skipped once four other cases were in. Nothing was taken from arviz, sympy or lmfit.

So within numpyro and statsmodels the helper's choice among qualifying PRs is a selection step
that favours bugs a user can see.

<!-- cases:start -->
| Case | Fix PR | Merged | Kind | Source files changed | Instruction files at the buggy commit | Conditions |
|---|---|---|---|---|---|---|
| networkx-8879 | [networkx #8879](https://github.com/networkx/networkx/pull/8879) | 2026-08-29 | wrong numeric result | 1 | 1 | C D T |
| networkx-8906 | [networkx #8906](https://github.com/networkx/networkx/pull/8906) | 2026-09-25 | wrong numeric result | 1 | 1 | C D T |
| pint-2464 | [pint #2464](https://github.com/hgrecco/pint/pull/2464) | 2026-10-09 | wrong physical-units result | 1 | 0 | C T |
| xarray-11817 | [xarray #11817](https://github.com/pydata/xarray/pull/11817) | 2026-10-31 | wrong data transformation | 1 | 6 | C D T |
| mne-14439 | [mne-python #14439](https://github.com/mne-tools/mne-python/pull/14439) | 2026-10-21 | misaligned data and events | 1 | 2 | C D T |
| numpyro-2431 | [numpyro #2431](https://github.com/pyro-ppl/numpyro/pull/2431) | 2026-11-15 | wrong numeric result | 1 | 1 | C D T |
| numpyro-2369 | [numpyro #2369](https://github.com/pyro-ppl/numpyro/pull/2369) | 2026-10-20 | wrong numeric result | 1 | 1 | C D T |
| numpyro-2372 | [numpyro #2372](https://github.com/pyro-ppl/numpyro/pull/2372) | 2026-10-19 | wrong numeric result | 1 | 1 | C D T |
| numpyro-2289 | [numpyro #2289](https://github.com/pyro-ppl/numpyro/pull/2289) | 2026-09-27 | wrong numeric result | 1 | 1 | C D T |
| ESMValCore-3291 | [ESMValCore #3291](https://github.com/ESMValGroup/ESMValCore/pull/3291) | 2026-11-11 | wrong selection of data | 1 | 2 | C D T |
| ESMValCore-3192 | [ESMValCore #3192](https://github.com/ESMValGroup/ESMValCore/pull/3192) | 2026-08-10 | wrong unit conversion | 1 | 0 | C T |
| statsmodels-10660 | [statsmodels #10660](https://github.com/statsmodels/statsmodels/pull/10660) | 2026-11-04 | wrong numeric result | 1 | 1 | C D T |
| statsmodels-10671 | [statsmodels #10671](https://github.com/statsmodels/statsmodels/pull/10671) | 2026-11-06 | wrong statistical test result | 1 | 1 | C D T |
| statsmodels-10684 | [statsmodels #10684](https://github.com/statsmodels/statsmodels/pull/10684) | 2026-11-05 | wrong numeric result | 1 | 1 | C D T |
| statsmodels-10744 | [statsmodels #10744](https://github.com/statsmodels/statsmodels/pull/10744) | 2026-11-16 | wrong numeric result | 2 | 1 | C D T |
| nilearn-6611 | [nilearn #6611](https://github.com/nilearn/nilearn/pull/6611) | 2026-09-29 | wrong statistic | 1 | 2 | C D T |
| nilearn-6722 | [nilearn #6722](https://github.com/nilearn/nilearn/pull/6722) | 2026-11-18 | numerical tolerance | 1 | 2 | C D T |
| mne-14497 | [mne-python #14497](https://github.com/mne-tools/mne-python/pull/14497) | 2026-11-05 | wrong scaling | 1 | 2 | C D T |
| pyvista-9340 | [pyvista #9340](https://github.com/pyvista/pyvista/pull/9340) | 2026-09-25 | wrong coordinates | 1 | 11 | C D T |
<!-- cases:end -->

"Instruction files" counts `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.cursorrules`,
`copilot-instructions.md` at any level and every file under a `.claude/` or `.cursor/` directory
(for xarray and pyvista most of the count is skill files under `.claude/skills/`). The kind labels
are descriptive only and are not used in the analysis.

The symptom given to the agent is `symptom_vague`: what a researcher would see in an analysis,
without the function's wrong value, the faulty line or the fix. These texts were written by the
helper agents from the PR and its issue and checked against this rule before this commit. They
are fixed from this commit on.

## Conditions

Every sandbox is the tree of the buggy commit without git history.

| | Instruction files in the sandbox | Extra sentence in the prompt |
|---|---|---|
| **C** | none: `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.cursorrules`, `copilot-instructions.md`, `.claude/`, `.cursor/` removed at every level | none |
| **D** | the repository's own, as they were at the buggy commit | "Before you start, read the repository's agent instruction files (AGENTS.md / CLAUDE.md, including nested ones) and follow them." |
| **T** | the repository's own removed; `guidance_T.md` placed as `AGENTS.md` in the sandbox root | same sentence as D |

`guidance_T.md` is three bullets quoted word for word from the "Testing conventions" section of
the statsmodels `AGENTS.md` (statsmodels is BSD-3-Clause; file read 2026-11-17): check against an
external or closed-form truth, run the test on both trees and alter the changed line to see a test
fail, and tolerance rules. They were chosen because the audit in `../audit/` found statsmodels to
be the only one of 20 files that asks for a mutation check, and because these three bullets do not
depend on the statsmodels code base. The other bullets of that section do (directory layout, CI
on Pyodide, its random-state fixture, its warning filters, its pytest command). The sandbox copy
carries no project name.

Which conditions a case gets is a fixed rule (`mkprotocol3.py` writes `runs3.json`):

- C: every case.
- D: every case whose buggy commit has at least one instruction file.
- T: every case. For the statsmodels cases T overlaps with D: at the buggy commits of
  statsmodels-10660, -10671 and -10684 the project's own file has the first of the three bullets
  and not the other two (they were added upstream on 2026-11-11); at statsmodels-10744 it has all
  three, so there T is D with everything else removed.

The prompt is round 2's (`mkprompts3.py`): the vague symptom, "find the cause, fix it, write a
regression test in one new file", the interpreter to use, and the rules (no network, no git, no
pip install, nothing outside the sandbox, do not look for the upstream fix).

## Notes on single cases and the environment

Things a reader should know before reading the results; none of them was decided after seeing a
run.

- **numpyro-2372**: the upstream fix PR says it was written with AI assistance. The case is kept;
  the reference tests are the maintainers' merged tests either way.
- **numpyro**: the reference tests are single test functions (`path::name` selectors), because
  the full test modules take minutes; all other cases run whole test files.
- **ESMValCore**: the package imports `esmpy`, which has no Windows wheel. The environment has a
  stub module of that name that raises on any call; neither case reaches it. One instruction file
  of the repository, under `.github/instructions/`, has a `*` in its name and cannot exist on
  Windows, so it is absent from every ESMValCore sandbox, D included (`mk3.py` prints what it
  skips).
- **statsmodels**: not installed; imported from the sandbox, with the 26 compiled modules and
  `_version.py` copied from the 0.15.0 wheel. Two Cython sources changed between that release and
  the cases (`nonparametric/linbin.pyx`, `robust/_qn.pyx`); none of the four cases uses them.
- **mne-14497** runs in a second clone of mne-python (`mne-python-r3`) with its own environment,
  so that the round 2 case mne-14439 keeps the environment it had. `pytest-qt` is removed from
  the new environment because it stops pytest from starting without a Qt binding.
- **pyvista**: the `pytest-pyvista` plugin fails under `-p no:cacheprovider`, which the runner
  uses; a local pytest plugin in the environment gives it a temporary cache directory. No
  repository file is changed.
- **nilearn-6722** was merged on 2026-11-18, one day before this file; it is the newest case.
- The four statsmodels cases, the two nilearn cases, the four numpyro cases, the two networkx
  cases, the two ESMValCore cases and the two mne-python cases share a project each, so the 19
  cases are 9 projects, not 19 independent draws.

## Agent and runs

- Claude Opus 5.5, run as a sub-agent of Claude Code with file and shell tools, the same setup as
  rounds 1 and 2. One run per case and condition. Fresh context for every run; runs do not see
  each other.
- While agents run, every clone is parked on a buggy commit, so no checked-out tree contains a
  fix. The clones' git objects still do. "No network, no git, nothing outside the sandbox" are
  instructions to the agent and are not enforced.
- A run is repeated only if the session dies before the agent replies or the sandbox import check
  in `mk3.py` fails; each such repeat is reported. A run that finishes is never repeated, whatever
  its result.

## Measures (`grade3.py`, all mechanical; no model judges anything)

Per run, as in round 2:

- `test`: the agent's test on the maintainers' trees (`catches` / `misses` / `broken`).
- `fix_ref`: the maintainers' tests from the fix PR on the buggy tree plus the agent's source
  edits (`pass` / `fail`).
- `test_own`: the agent's test on the agent's own fix.
- **`shared`** (main measure): `test_own` passes and `fix_ref` fails. The agent's test agrees with
  the agent's wrong fix.

Reported in `RESULTS3.md`:

1. `shared`, `fix_ref` fail and `test` verdict counts over all runs and per condition.
2. Paired by case: C against D on the cases that have both, C against T on the cases that have
   both, as counts of cases where the two conditions differ and in which direction. No
   significance test is planned; with one run per cell and this many cases none would mean much.
3. Replication: for the 9 runs that also exist in round 2 (same case, condition, prompt and
   model), how many give the same three verdicts in round 3.
4. Every `broken` test and every `fix_ref` fail read by hand and described, because round 2 showed
   that `broken` can mean "the agent's test found something the maintainers' fix left open", and a
   `fix_ref` fail can in principle come from an over-strict reference test.
5. Tokens, tool calls and wall time per run (`usage3.jsonl`).

All runs are reported, including any that make the picture worse for the proposal.

## Limits known in advance

- One run per condition and one agent model, so differences between conditions are within noise;
  item 3 above is there to show how large that noise is.
- Isolation is instructed, not enforced.
- The T text was chosen by hand, from one project.
- D is missing where a project has no instruction file, so the conditions do not cover the same
  cases; comparisons are paired for that reason.
- Cases come from projects that install on Windows without a compiler, and symptom texts were
  written with knowledge of the fix.
- The maintainers' tests are the reference. They can be incomplete, and a fix that passes them
  can still be wrong.
