# Pilot 2 (2026-11-15): vague symptom, agent writes the fix and the test

## What changed from pilot 1
- **Vaguer symptoms** (`symptom_vague` in `cases.json`): the downstream effect a user would see in an analysis, without the wrong value or the triggering keyword. Example: networkx-8906 no longer mentions `nodes=`; mne-14439 no longer names `reset_first_samp`.
- **Harder task:** the agent finds the cause, edits the library, and writes the regression test. This is the case the proposal is about: one author for fix and test.
- **Tighter isolation:** while agents ran, the shared clones behind the editable installs were parked on the buggy commits, so the fix was not on disk anywhere the agent could read. Rules about network, git and outside files were still instructions, not enforced.
- Same 5 cases, same agent (Claude Opus 5.5 subagent), one run per condition. C = agent instruction files removed, D = kept and the agent told to follow them. pint has no such file, so it has only C.

## Grading (`grade2.py`, all mechanical)
- `test`: the agent's test on the maintainers' trees (catches = fails on buggy, passes on fixed; broken = fails on the fixed tree).
- `fix_ref`: the maintainers' tests from the fix PR, run on the buggy tree plus the agent's source edits.
- `test_own`: the agent's test on its own fix.
- `shared`: the agent's test passes on its own fix, but the maintainers' tests fail on that fix. The test agrees with a wrong fix.

## Result
| Run | Agent's test | Agent's fix vs maintainers' tests | Shared misunderstanding |
|---|---|---|---|
| networkx-8879-C | catches | pass | no |
| networkx-8879-D | broken (asserts a directed-graph fix beyond the PR) | pass | no |
| networkx-8906-C | broken (asserts a second fix beyond the PR) | pass | no |
| networkx-8906-D | catches | pass | no |
| pint-2464-C | broken | **fail (4 of 63)** | **yes** |
| xarray-11817-C | catches | pass | no |
| xarray-11817-D | catches | pass | no |
| mne-14439-C | catches | pass | no |
| mne-14439-D | catches | **fail (8 of 80)** | **yes** |

- All 9 agents found the right function from the vague symptom, and all 9 reported "my test fails before and passes after".
- **2 of 9 fixes were wrong, and in both the agent's own test passed on the wrong fix.** Pilot 1's measure (does the test catch the bug) would have scored both of these as success: mne-14439-D's test even "catches" against the maintainers' trees.
  - pint-2464-C moved `mod`/`remainder`/`fmod` to a different unit-handling list. It fixed the reported case but broke the existing dimensionless and energy cases (`test_mod`, `test_fmod`, `test_remainder`) and missed `floor_divide`. The agent ran two other test files (779 passed), not `test_umath.py`, where the regressions are.
  - mne-14439-D shifted the annotation onsets but did not reset `first_samp`, so 8 of the maintainers' new parametrised cases fail. mne-14439-C, on the same case without guidance, got a full fix. One run each, so this says nothing yet about guidance.
- 3 tests are "broken" (they fail on the maintainers' fixed tree). pint-2464-C's follows from its own wrong fix, above. The other 2 are not wrong tests; they assert behaviour the maintainers' PR did not cover (corrected 2026-11-20: this line used to count 2 and leave out pint-2464-C):
  - networkx-8879-D asserts correct group betweenness on directed graphs. That passes on networkx main of 2026-11-14 (`ada19dd8`), so it was fixed upstream later.
  - networkx-8906-C asserts that a directed-graph node with only incoming edges gets the same effective size from the per-node path as from the whole-graph path. **On networkx main of 2026-11-14 the per-node path still returns `nan` for it (whole-graph: 1.85).** Pilot 1 found the same thing independently. Candidate upstream issue, not yet filed.
- Cost: 9 runs, 738.5k tokens (71.9k to 101.4k, mean 82.1k), 6 to 38 tool calls, median 122 s. About 5% more tokens per run than pilot 1, with much more done per run.

## What this means for the proposal
1. **Measure the fix against the maintainers' tests, not only the test against the fix.** "Test fails before, passes after" was true for 9 of 9 runs and hid 2 wrong fixes. The headline measure becomes the shared-misunderstanding rate: how often an agent's test passes on an agent's wrong fix. Pilot value: 2 of 9.
2. **"Broken" needs a hand review step.** A test that fails on the maintainers' fix can be wrong, or can be finding a bug the maintainers left. Here 2 of the 3 were the second kind and 1 followed from the agent's own wrong fix. The benchmark must not count these as failures automatically.
3. **The work-package-1 design is now concrete:** vague symptom, fix plus test, the three mechanical checks above, plus a reviewer label for "broken".
4. **Budget:** about 82k tokens per run. 60 cases x 4 conditions x 2 agents x 3 repeats = 1,440 runs, about 118M tokens. At Claude Opus 5.5 list prices ($4 per million input tokens, $20 per million output; Anthropic's price table as of 2026-10-06) that is $473 if every token were billed as input and $2,363 if every token were output. The real split is mostly input; measure it with API usage logs in the first month before fixing the budget line. Recheck prices on the day of submission. Added 2026-11-20: the per-run totals are what the harness reported, one number per run. A metered API bills the growing context again on every model call, so billed input tokens can be several times this total; the dollar figures here are a lower bound until cost is metered.

## Limits
One run per condition, one agent, 5 chosen cases, all with a single changed source file. The C/D difference rests on one case and is noise until there are repeats. The agents' own claims ("ran other tests, all pass") were not used for grading.

## Follow-up 2026-11-15: the networkx `nan` case
- Reproduced on networkx main `ada19dd8` (2026-11-14): in a DiGraph, a node with only incoming edges gets `nan` from `effective_size(G, nodes=...)` (and from any call without scipy), weighted or not, while the whole-graph path gives a number (example: 1.583 weighted, 1.0 unweighted).
- Cause: the per-node branch treats a node as isolated with `all(u == v for u in G[v])`, which for a DiGraph sees successors only. Using `nx.all_neighbors(G, v)` there makes both paths agree; the 40 existing tests and the module doctest still pass.
- No existing issue or PR found (searched "effective_size nan", "effective_size directed").
- networkx's contributing guide asks people not to post AI-generated issue or PR text and to disclose AI use. So this is not filed by the agent; if reported, the applicant writes it personally. Not filed as of 2026-11-20.
