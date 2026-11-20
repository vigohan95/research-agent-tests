"""How large a difference could the full study detect? A simulation from the round-3 pilot rates.

Reads results3.jsonl, takes each case's share of runs with a shared misunderstanding
(the agent's test passes on an agent fix that the maintainers' tests reject), and simulates
a study of N cases under two conditions: a baseline with the pilot's per-case rates and a
guidance condition that multiplies every case's rate by RR.

Cases are resampled from the 19 pilot cases, which were chosen, not sampled, so this is a
rough guide and not a guarantee. Two extremes are shown for the repeats on one case:
  independent  every run on a case is a fresh draw (best case: 6 runs carry 6 runs of information)
  correlated   runs on a case always agree (worst case: 6 runs carry 1 run of information)
Round 3 repeated 9 round-2 runs and 7 kept their verdict, so reality is between the two and
closer to "correlated".

Test: paired t statistic on the per-case difference in rates, |t| > 2.
Usage: python power.py            (numpy only; seed fixed)
"""
import json
import pathlib
from collections import defaultdict

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
SIMS = 4000
RUNS_PER_CASE = 6  # 2 agents x 3 repeats per condition


def pilot_rates():
    n, k = defaultdict(int), defaultdict(int)
    for line in (HERE / "results3.jsonl").read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        o = json.loads(line)
        n[o["case"]] += 1
        k[o["case"]] += bool(o["shared"])
    return np.array([k[c] / n[c] for c in sorted(n)])


def power(rates, n_cases, rr, runs, rng):
    hits = 0
    for _ in range(SIMS):
        p = rng.choice(rates, size=n_cases, replace=True)
        base = rng.binomial(runs, p) / runs
        guided = rng.binomial(runs, p * rr) / runs
        d = base - guided
        sd = d.std(ddof=1)
        if sd > 0 and abs(d.mean() / (sd / np.sqrt(n_cases))) > 2:
            hits += 1
    return hits / SIMS


def main():
    rates = pilot_rates()
    rng = np.random.default_rng(20261120)
    print(f"pilot: {len(rates)} cases, {int((rates > 0).sum())} with at least one shared misunderstanding, "
          f"mean per-case rate {rates.mean():.3f}")
    print("| cases | rate multiplied by | power, independent repeats | power, correlated repeats |")
    print("|---|---|---|---|")
    for n_cases in (60, 50, 20):
        for rr in (0.75, 0.67, 0.5, 0.25):
            a = power(rates, n_cases, rr, RUNS_PER_CASE, rng)
            b = power(rates, n_cases, rr, 1, rng)
            print(f"| {n_cases} | {rr} | {a:.2f} | {b:.2f} |")
    print("false-positive check (no effect, 60 cases): "
          f"independent {power(rates, 60, 1.0, RUNS_PER_CASE, rng):.3f}, correlated {power(rates, 60, 1.0, 1, rng):.3f}")


if __name__ == "__main__":
    main()
