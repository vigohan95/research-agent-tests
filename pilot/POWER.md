# How large a difference could the full study detect?

Output of `python pilot/power.py` (numpy only, seed fixed), run on 2026-11-20 against
`results3.jsonl`.

pilot: 19 cases, 6 with at least one shared misunderstanding, mean per-case rate 0.246

| cases | rate multiplied by | power, independent repeats | power, correlated repeats |
|---|---|---|---|
| 60 | 0.75 | 0.89 | 0.27 |
| 60 | 0.67 | 0.96 | 0.41 |
| 60 | 0.5 | 1.00 | 0.72 |
| 60 | 0.25 | 1.00 | 0.96 |
| 50 | 0.75 | 0.81 | 0.23 |
| 50 | 0.67 | 0.93 | 0.35 |
| 50 | 0.5 | 0.99 | 0.64 |
| 50 | 0.25 | 1.00 | 0.92 |
| 20 | 0.75 | 0.40 | 0.06 |
| 20 | 0.67 | 0.52 | 0.11 |
| 20 | 0.5 | 0.71 | 0.24 |
| 20 | 0.25 | 0.82 | 0.48 |

false-positive check (no effect, 60 cases): independent 0.038, correlated 0.049

## What the simulation does

- Takes each of the 19 round 3 cases' share of runs with a shared misunderstanding (the agent's
  own test passes on an agent fix that the maintainers' tests reject).
- Draws a study of N cases from those 19 with replacement, runs a baseline condition at the
  pilot's per-case rates and a guidance condition with every case's rate multiplied by the
  factor in the second column, 6 runs per case and condition (2 agents x 3 repeats).
- Tests the per-case difference with a paired t statistic, |t| > 2. Power is the share of 4,000
  simulated studies in which that test fires. With no effect it fires in about 4 to 5% of them.

## What it assumes, and why the answer is a range

- **Repeats.** "Independent" treats each of the 6 runs on a case as a fresh draw; "correlated"
  treats them as always agreeing, so 6 runs carry the information of 1. Round 3 repeated 9 runs
  of round 2 and 7 kept their verdict, so the truth is between the two columns and probably nearer
  the second.
- **Cases.** The 19 pilot cases were chosen, not sampled, and 13 of them had no shared
  misunderstanding in any run. A study with a different mix of cases has different power.
- **Effect.** One multiplier for every case. Real guidance could help on some kinds of bug and
  not on others.
- **Rates.** Per-case rates come from 2 or 3 runs each, so they are coarse (0, 1/3, 2/3 or 1).

## What follows for the study design

- With 60 cases, halving the rate is detected in about 7 of 10 studies even if repeats add
  nothing, and almost always if they are independent.
- A 25% reduction is detected reliably only if repeats are close to independent.
- The 20 held-out cases alone cannot support a test in either column; they give an interval.
- Dropping from 60 to 50 cases costs about 0.08 of power at a halving in the worst case
  (0.72 to 0.64).
