# Pilot 3 (2026-11-19): 19 bugs, 9 projects, 55 runs

The protocol is `PROTOCOL3.md`. It was committed and pushed as `fee562c` on 2026-11-19 12:51 UTC,
before any agent run of this round. This file reports every run, and the last two sections list
every departure from the protocol and every limit.

## What changed from pilot 2

- **19 cases instead of 5**, from 9 projects: networkx, pint, xarray, mne-python (the 5 cases of
  rounds 1 and 2), plus numpyro, ESMValCore, statsmodels, nilearn, pyvista and a second mne-python
  case. All 19 fixes were merged between 2026-08-10 and 2026-11-18. The selection rules are in the
  protocol.
- **A third condition, T**: the repository's own instruction files removed and three testing rules
  quoted from the statsmodels `AGENTS.md` put in their place (`guidance_T.md`). C (no instruction
  files) and D (the repository's own files) are as in round 2. D exists for 17 of the 19 cases;
  pint-2464 and ESMValCore-3192 had no instruction file at the buggy commit.
- **The 9 runs of round 2 were repeated** from scratch, same prompt, same model, to see how much a
  single run moves.
- Task, prompt, agent (Claude Opus 5.5 as a sub-agent of Claude Code) and grading are those of
  round 2: the agent gets the buggy tree and a vague symptom, and writes a fix and a regression
  test. `grade3.py` then runs the agent's test on the maintainers' trees (`test`), the maintainers'
  tests on the agent's fix (`fix_ref`), and the agent's test on the agent's fix (`test_own`).
  `shared` means `test_own` passes and `fix_ref` fails.

## Short answers to the three questions of the protocol

1. **Does the rate hold?** Mechanically, yes: 12 of 55 runs (22%) are `shared`; round 2 had 2 of 9
   (22%). Read by hand, the 12 are not all the same thing: in 5 the fix leaves or creates wrong
   results, in 3 it fixes the reported case but not a sibling case the maintainers also fixed, and
   in 4 the agent made a defensible choice that the maintainers' tests happen to rule out. So the
   mechanical number overstates "wrong fix that its own test did not see"; that is 8 of 55 (15%)
   at most, 5 of 55 (9%) at the strictest.
2. **How much do single runs move?** 7 of the 9 repeated runs gave the same three verdicts. One
   of the two that moved is the run round 2 used as its example of a C/D difference.
3. **Any sign that instructions change the rate?** A weak one, in the expected direction, resting
   on two cases. Not an effect. Details under "Conditions" below.

## All runs

Tokens, tool calls and seconds are from `usage3.jsonl`. The agent's test passed on the agent's own
fix in all 55 runs, so that column is left out.

| Run | Agent's test | Agent's fix vs maintainers' tests | Shared | Tokens | Tool calls | Seconds |
|---|---|---|---|---|---|---|
| networkx-8879-C | catches | pass | no | 76.2k | 10 | 107 |
| networkx-8879-D | broken | pass | no | 88.8k | 26 | 206 |
| networkx-8879-T | catches | pass | no | 82.7k | 15 | 151 |
| networkx-8906-C | catches | pass | no | 74.0k | 7 | 72 |
| networkx-8906-D | catches | pass | no | 75.5k | 9 | 68 |
| networkx-8906-T | catches | pass | no | 76.0k | 7 | 73 |
| pint-2464-C | broken | **fail** (4 of 63) | **yes** | 68.4k | 4 | 64 |
| pint-2464-T | catches | **fail** (1 of 63) | **yes** | 80.6k | 11 | 81 |
| xarray-11817-C | catches | pass | no | 72.4k | 8 | 82 |
| xarray-11817-D | catches | pass | no | 72.4k | 6 | 66 |
| xarray-11817-T | catches | pass | no | 70.8k | 8 | 80 |
| mne-14439-C | catches | **fail** (8 of 80) | **yes** | 79.0k | 11 | 108 |
| mne-14439-D | catches | **fail** (8 of 80) | **yes** | 85.9k | 12 | 120 |
| mne-14439-T | catches | **fail** (8 of 80) | **yes** | 75.8k | 12 | 155 |
| numpyro-2431-C | catches | pass | no | 74.1k | 9 | 140 |
| numpyro-2431-D | catches | pass | no | 79.5k | 10 | 125 |
| numpyro-2431-T | catches | pass | no | 79.4k | 16 | 255 |
| numpyro-2369-C | catches | pass | no | 74.8k | 9 | 681 |
| numpyro-2369-D | catches | pass | no | 82.8k | 13 | 1088 |
| numpyro-2369-T | catches | pass | no | 70.4k | 5 | 124 |
| numpyro-2372-C | catches | pass | no | 73.9k | 10 | 271 |
| numpyro-2372-D | catches | pass | no | 73.1k | 4 | 107 |
| numpyro-2372-T | catches | pass | no | 69.5k | 5 | 276 |
| numpyro-2289-C | catches | pass | no | 69.7k | 6 | 121 |
| numpyro-2289-D | catches | pass | no | 75.8k | 7 | 178 |
| numpyro-2289-T | catches | pass | no | 76.5k | 15 | 270 |
| ESMValCore-3291-C | catches | pass | no | 71.1k | 6 | 133 |
| ESMValCore-3291-D | catches | pass | no | 77.6k | 8 | 127 |
| ESMValCore-3291-T | catches | pass | no | 81.6k | 14 | 140 |
| ESMValCore-3192-C | broken | **fail** (1 of 53) | **yes** | 78.8k | 15 | 365 |
| ESMValCore-3192-T | catches | **fail** (1 of 53) | **yes** | 77.6k | 8 | 233 |
| statsmodels-10660-C | catches | **fail** (3 of 1342) | **yes** | 71.1k | 5 | 99 |
| statsmodels-10660-D | catches | pass | no | 90.2k | 14 | 150 |
| statsmodels-10660-T | catches | pass | no | 75.4k | 7 | 141 |
| statsmodels-10671-C | broken | **fail** (1 of 155) | **yes** | 68.0k | 5 | 70 |
| statsmodels-10671-D | broken | pass | no | 96.5k | 31 | 483 |
| statsmodels-10671-T | broken | **fail** (1 of 155) | **yes** | 71.4k | 7 | 132 |
| statsmodels-10684-C | catches | pass | no | 68.3k | 6 | 107 |
| statsmodels-10684-D | catches | pass | no | 77.0k | 10 | 146 |
| statsmodels-10684-T | catches | pass | no | 70.0k | 4 | 126 |
| statsmodels-10744-C | catches | **fail** (3 of 13) | **yes** | 69.8k | 10 | 125 |
| statsmodels-10744-D | catches | **fail** (3 of 13) | **yes** | 83.5k | 14 | 171 |
| statsmodels-10744-T | catches | pass | no | 88.7k | 27 | 394 |
| nilearn-6611-C | catches | pass | no | 74.8k | 6 | 140 |
| nilearn-6611-D | catches | pass | no | 92.8k | 21 | 288 |
| nilearn-6611-T | catches | pass | no | 71.4k | 6 | 126 |
| nilearn-6722-C | catches | pass | no | 77.1k | 11 | 299 |
| nilearn-6722-D | catches | pass | no | 102.6k | 28 | 565 |
| nilearn-6722-T | catches | pass | no | 91.4k | 21 | 644 |
| mne-14497-C | catches | pass | no | 70.2k | 8 | 131 |
| mne-14497-D | catches | pass | no | 78.9k | 8 | 108 |
| mne-14497-T | catches | pass | no | 71.4k | 7 | 195 |
| pyvista-9340-C | catches | pass | no | 69.2k | 5 | 124 |
| pyvista-9340-D | catches | pass | no | 88.8k | 19 | 323 |
| pyvista-9340-T | catches | pass | no | 83.5k | 13 | 206 |

In all 55 runs the agent edited a source file that the maintainers' fix also changed, and no other
source file. The agents' diffs (`fixes3/`) change between 2 and 70 lines, median 7.

## Counts per condition

| Condition | Runs | Test catches | Test misses | Test broken | Fix fails maintainers' tests | Shared |
|---|---|---|---|---|---|---|
| C | 19 | 16 | 0 | 3 | 6 | 6 |
| D | 17 | 15 | 0 | 2 | 2 | 2 |
| T | 19 | 18 | 0 | 1 | 4 | 4 |
| all | 55 | 49 | 0 | 6 | 12 | 12 |

D does not cover pint-2464 and ESMValCore-3192, and both are cases where C and T fail. On the 17
cases that have all three conditions the `shared` counts are C 4, D 2, T 2.

## Every `fix_ref` fail, read by hand (12 runs, 6 cases)

"By hand" here and below means not by a script: the author read these with an AI agent. No
second reader labelled them (note added 2026-11-20).

All 12 are also `shared`: no agent's own test failed on its own fix.

**The fix leaves or creates wrong results (5 runs).**

- **pint-2464-C.** Moved `mod`, `remainder` and `fmod` into the list of functions that require
  matching units. That fixes the reported case and breaks behaviour that worked: 4 of the
  maintainers' tests fail (`test_mod`, `test_remainder` and related cases with a dimensionless or
  other-unit operand). The agent's test expects an exception that the maintainers' fix does not
  raise, so it is also `broken`. Round 2's run of this case did the same thing.
- **mne-14439-C, -D and -T.** All three subtract the crop offset from the annotation onsets and
  still let the offset shift the first and last sample. That is right for one crop of data held in
  memory. It is wrong for a recording read from file and for a second crop: 8 of the maintainers'
  parametrised cases fail (the first sample is 200 after cropping, or events land at samples 100
  and 300 instead of 300 and 500). Each agent's test covers the in-memory single crop only.
- **statsmodels-10660-C.** The confidence interval formula had two errors. The agent fixed the
  exposure scaling and left the second (`0.25 * crit` where it should be `0.25 * crit**2`). The
  maintainers' closed-form test fails in all 3 parametrisations at `rtol=1e-12`; the intervals are
  off by 0.3% to 0.8%. The agent's tests check that the interval scales with exposure and that it
  agrees with another method to 10%, and both hold with the second error in place. The D and T
  runs of this case fixed both errors, and both wrote a closed-form test.

**The fix is right for the reported case and narrower than the maintainers' fix (3 runs).**

- **pint-2464-T.** Handles `mod`, `remainder` and `fmod` correctly, which is what the symptom
  names. The maintainers' PR also fixed `floor_divide`; their test for it fails (1 of 63).
- **statsmodels-10744-C and -D.** Both use the corrected degrees of freedom in the regression
  prediction code. The same error exists in the prediction code for GLM and discrete models, which
  the maintainers fixed in the same PR and the T run also fixed; 3 of the maintainers' tests (GLM,
  Poisson, logit) fail. The symptom text speaks of "a regression". C's test covers OLS; D's covers
  OLS and WLS over several covariance types.

**A defensible choice that the maintainers' tests rule out (4 runs).**

- **ESMValCore-3192-C and -T.** The fix needs the molar mass of carbon. The agents used 12.0107
  g/mol, the maintainers 12.011. The maintainers' test compares with the default tolerance of
  `numpy.testing.assert_allclose` (`rtol=1e-7`), and the two constants differ by 0.0025%. C's test
  asserts 12.0107 at `rtol=1e-6`, so it also fails on the maintainers' tree (`broken`). T's test
  asserts 12.011 at `rtol=1e-4` and `catches`; its comment says the tolerance is there to allow
  for the last digits of the atomic weight (12.0107 or 12.011) and not for the factor between
  carbon and CO2. The third bullet of `guidance_T.md` is about tolerances; one run does not show
  that the bullet caused this.
- **statsmodels-10671-C and -T.** For a table with no discordant pairs the agents return
  statistic 0 and p-value 1. The maintainers' fix leaves that input as 0/0 and returns `nan`, and
  one of their test cases asserts `nan`. The symptom text says the exact test "reports no evidence
  of a difference" for such a table, so 0 and 1 is a fair reading. Both agents' tests assert 0, so
  both are `broken` on the maintainers' tree.

By condition:

| Condition | Runs | Wrong results | Narrower than the maintainers' fix | Choice ruled out by the reference tests | All `shared` |
|---|---|---|---|---|---|
| C | 19 | 3 | 1 | 2 | 6 |
| D | 17 | 1 | 1 | 0 | 2 |
| T | 19 | 1 | 1 | 2 | 4 |
| all | 55 | 5 | 3 | 4 | 12 |

## Every `broken` test, read by hand (6 runs)

None of the 6 is simply a wrong test.

- **pint-2464-C**: follows from its wrong fix (above).
- **ESMValCore-3192-C**, **statsmodels-10671-C**, **statsmodels-10671-T**: follow from the choices
  described above.
- **statsmodels-10671-D**: the fix passes the maintainers' tests. The agent's test turns warnings
  into errors and requires `nan` without a warning for the table with no discordant pairs. The
  maintainers' fix returns `nan` and numpy emits `RuntimeWarning: invalid value encountered in
  scalar divide`. The test is stricter than the maintainers' fix.
- **networkx-8879-D**: the fix passes the maintainers' tests. The agent's test also asserts group
  betweenness on directed graphs, which the PR did not fix: 2 of its 4 tests fail on the fixed
  commit and all 4 pass on networkx main of 2026-11-14 (`ada19dd8`). Round 2's run of this case
  did the same thing.

Two of the three kinds of `broken` are information a maintainer may want (a case fixed only
later, a warning on a degenerate input). A benchmark that counts `broken` as failure would count
them against the agent.

## Conditions (paired by case)

| Pair | Cases with both | Same on all three verdicts | Fix fails only in first | Fix fails only in second | Shared only in first | Shared only in second |
|---|---|---|---|---|---|---|
| C vs D | 17 | 14 | 2 | 0 | 2 | 0 |
| C vs T | 19 | 15 | 2 | 0 | 2 | 0 |
| D vs T | 17 | 14 | 1 | 1 | 1 | 1 |

- C vs D differs on statsmodels-10660 and statsmodels-10671; C vs T on statsmodels-10660 and
  statsmodels-10744. After the hand reading only two of these are about results: 10660 (C left
  the second error, D and T did not) and 10744 (T covered the GLM path, C and D did not).
- In statsmodels-10660 the two runs whose instruction text asks for a check against a closed form
  (D: the project's own file has that bullet at this commit; T: `guidance_T.md`) both wrote a
  closed-form test and both found the second error. The run without that text wrote a scaling
  test and missed it. This is the mechanism the proposal is about, seen once.
- Against it: at statsmodels-10744 the project's own file already has all three T bullets, so D
  and T had the same testing text, and D still missed the GLM path. And mne-14439 failed the same
  way in all three conditions.
- No condition was better on every case. With one run per cell, and with the replication below
  showing that a single run can flip, none of this is an effect. It is a direction to test with
  repeats.

## Replication of round 2 (same case, condition, prompt and model)

| Run | Test r2 -> r3 | Fix r2 -> r3 | Shared r2 -> r3 | Same |
|---|---|---|---|---|
| networkx-8879-C | catches -> catches | pass -> pass | no -> no | yes |
| networkx-8879-D | broken -> broken | pass -> pass | no -> no | yes |
| networkx-8906-C | broken -> catches | pass -> pass | no -> no | no |
| networkx-8906-D | catches -> catches | pass -> pass | no -> no | yes |
| pint-2464-C | broken -> broken | fail -> fail | **yes** -> **yes** | yes |
| xarray-11817-C | catches -> catches | pass -> pass | no -> no | yes |
| xarray-11817-D | catches -> catches | pass -> pass | no -> no | yes |
| mne-14439-C | catches -> catches | pass -> fail | no -> **yes** | no |
| mne-14439-D | catches -> catches | fail -> fail | **yes** -> **yes** | yes |

7 of 9 repeated runs gave the same three verdicts.

- **mne-14439-C** passed the maintainers' tests in round 2 and fails them now, with the same
  partial fix that D had in round 2. `RESULTS2.md` noted "mne-14439-C, on the same case without
  guidance, got a full fix. One run each, so this says nothing yet about guidance". The repeat
  confirms the caution: that difference was run-to-run variation.
- **networkx-8906-C** in round 2 asserted a second, unfixed directed-graph case (the `nan` result
  described in `RESULTS2.md`) and was `broken`; this time the agent did not look at that case and
  the test `catches`.
- Both `shared` runs of round 2 are `shared` again, with the same wrong fixes.

## Cost

55 runs, 4.27M tokens (68.0k to 102.6k, mean 77.6k), 4 to 31 tool calls, 64 to 1,088 s per run,
median 140 s, 3.2 hours of agent time in total.

| Condition | Runs | Mean tokens | Mean tool calls | Median seconds |
|---|---|---|---|---|
| C | 19 | 72.7k | 7.9 | 124 |
| D | 17 | 83.6k | 14.1 | 150 |
| T | 19 | 77.1k | 10.9 | 151 |

Runs with instruction files use more tool calls and about 6% (T) to 15% (D) more tokens than runs
without. Token counts are the totals the harness reports for each sub-agent; there is no split
into input and output.

## What this means for the proposal

1. **The mechanical rate is stable and needs the hand reading.** 22% in both rounds. But a third
   of the round 3 `shared` runs (4 of 12) are disagreements with the reference tests, not wrong
   fixes. The full study has to report both numbers, and the reviewer step in the proposal has to
   cover `fix_ref` fails as well as `broken` tests. Round 2 only saw the need for the second.
2. **Reference tests can be over-strict.** A default tolerance of 1e-7 on a physical constant and
   an assertion of `nan` on a degenerate input both turned a reasonable fix into a "fail". Case
   selection should record the tolerance the maintainers' tests use and flag cases where the
   symptom text allows more than one correct answer.
3. **"Narrower than the maintainers' fix" is its own category.** In 3 runs the agent fixed what
   was reported and not a sibling function or model class with the same error. For a maintainer
   that is a real review cost, and neither "catches" nor the agent's own test shows it.
4. **Repeats are not optional.** 2 of 9 repeated runs changed a verdict, and one of them reverses
   the only C/D difference of round 2. The three repeats per cell in the proposal are the minimum
   that makes a comparison between conditions readable.
5. **The same wrong fix comes back.** pint-2464-C and mne-14439 gave the same wrong fix in every
   run of both rounds (2 and 4 runs). Some cases seem to pull agents to one particular partial
   fix, whatever the instructions say. Those cases are where a research-specific check would have
   to do its work, and they are easy to find again.
6. **Budget.** 77.6k tokens per run here, 82.1k in round 2. 1,440 runs at 78k to 82k tokens is
   112M to 118M tokens, the range the proposal already uses.

## Departures from the protocol, and things observed that the grading does not use

No finished run was repeated and no session died, so there are 55 runs for 55 planned. The 55
prompts sent were compared with the planned prompts afterwards and are identical.

- **Grading in several processes.** `grade3.py` grades runs one after another and rewrites
  `results3.jsonl` each time. To save time the same `grade()` function was called from a wrapper,
  one process per project, and the rows were merged; the run names were checked against
  `runs3.json`. The wrapper is not in the repository; `python grade3.py` gives the same rows.
- **Cache files in three diffs.** In nilearn-6611-D, nilearn-6722-C and nilearn-6722-T the agent
  ran existing nilearn tests inside the sandbox, and nilearn's joblib cache wrote copies of nilearn
  functions as `.py` files there. `grade3.py` counts every changed non-test `.py` file as an agent
  edit, so `results3.jsonl` lists these files under `changed` and counts their lines in
  `diff_lines` (710, 559 and 736). They were copied onto the buggy tree during grading and have no
  effect on any import. They are removed from the three files in `fixes3/`, which now hold only
  the real edits (7, 16 and 29 changed lines).
- **Isolation slips, as reported by the agents themselves (5 runs).** networkx-8879-C and
  nilearn-6722-D first ran a script that imported the package from the shared clone outside the
  sandbox, then repeated it against the sandbox. mne-14439-C, statsmodels-10684-C and
  nilearn-6611-D made a temporary copy of a source file outside the sandbox. The clones were on
  buggy commits throughout, so no fix was in any checked-out tree.
- **The operator's instruction file.** Five runs (numpyro-2431-C, numpyro-2372-T, numpyro-2369-D,
  mne-14497-T, statsmodels-10744-T) wrote their final report in the operator's working language
  instead of English. The likely cause is that the sub-agent harness also loads the operator's
  own project instruction file, which sets that language. That file says nothing about tests or
  about these projects, and it was there in all three conditions and in rounds 1 and 2. It still
  means that C was "no instruction file from the repository", not "no instruction file at all".
- **Encoding damage in two diffs.** networkx-8906-D added a byte-order mark and damaged one
  non-ASCII character in a docstring; statsmodels-10660-T damaged curly quotes in several
  docstrings (most of its 70 changed lines). Both look like a round trip through a Windows legacy
  code page. No test notices either. A maintainer would.
- **Checks the agents skipped or got by luck, by their own reports.** numpyro-2289-C and
  statsmodels-10671-C did not run their new test on the unchanged code. One test function each in
  pyvista-9340-C and nilearn-6722-T passes on the unchanged code and is described by the agent as
  a guard. pyvista-9340-D's first version of its test passed on the unchanged code by coincidence
  and was changed.
- **D runs did more than code.** Several D runs added release notes, changelog entries,
  `versionchanged` notes or an AI-generated marker on the test because the repository's
  instructions ask for them. The grader looks at `.py` files only.
- **Usage records.** Two runs (numpyro-2369-D, statsmodels-10671-D) sent an interim message before
  the final one; their usage is taken from the final notice.

## Limits

- One run per cell and one agent model. The replication shows what that is worth: 2 of 9
  identical runs changed a verdict.
- 19 cases from 9 projects. The 12 failing runs come from 6 cases in 4 projects, and three
  statsmodels cases account for 5 of them. The rate depends heavily on which cases are in the
  set.
- The hand reading was done by the operator with the agent that also ran the study, not by a
  maintainer of any of the projects. The three-way split above is a reading, and the files to
  check it are in `fixes3/` and `tests3/`.
- Isolation was instructed, not enforced, and was not kept in 5 runs.
- T uses text from one project, chosen by hand, and overlaps with D on the four statsmodels cases.
- D is missing for two cases, both of which fail in C and T.
- Symptom texts were written with knowledge of the fix. Two of the four "choice" results trace
  back to a symptom text that allowed more than one answer.
- The maintainers' tests are the reference. This round shows both sides of that: they rejected
  reasonable fixes in 4 runs, and a fix that passes them can still be incomplete.
- Cases are limited to packages that run on Windows without a compiler.

## Files

`cases.json` (19 cases), `runs3.json` (55 planned runs), `guidance_T.md`, `mk3.py` and
`mkprompts3.py` (sandboxes and prompts), `grade3.py`, `report3.py` (the count tables above),
`results3.jsonl`, `usage3.jsonl`, `tests3/` (55 agent tests), `fixes3/` (55 agent diffs).
