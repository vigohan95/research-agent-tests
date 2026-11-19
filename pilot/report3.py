"""Tables for RESULTS3.md from results3.jsonl, results2.jsonl and usage3.jsonl.

Prints markdown; nothing here judges a run, it only counts graded verdicts.
"""

from __future__ import annotations

import json
import statistics
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load(name: str) -> dict:
    p = HERE / name
    if not p.exists():
        return {}
    rows = [json.loads(line) for line in p.read_text("utf-8").splitlines() if line.strip()]
    return {r.get("run") or f"{r['case']}-{r['cond']}": r for r in rows}


r3, r2, use = load("results3.jsonl"), load("results2.jsonl"), load("usage3.jsonl")
planned = json.loads((HERE / "runs3.json").read_text("utf-8"))
missing = [r for r in planned if r not in r3]


def yes(b: bool) -> str:
    return "**yes**" if b else "no"


print("## All runs\n")
print("| Run | Agent's test | Agent's fix vs maintainers' tests | Agent's test on its own fix | Shared misunderstanding |")
print("|---|---|---|---|---|")
for k in planned:
    if k not in r3:
        print(f"| {k} | not graded | | | |")
        continue
    r = r3[k]
    fix = "pass" if r["fix_ref"] == "pass" else f"**fail** ({r['fix_ref_summary']})"
    print(f"| {k} | {r['test']} | {fix} | {r.get('test_own', '-')} | {yes(r['shared'])} |")

print("\n## Counts per condition\n")
print("| Condition | Runs | Test catches | Test misses | Test broken | Other | Fix fails maintainers' tests | Shared misunderstanding |")
print("|---|---|---|---|---|---|---|---|")
for cond in ["C", "D", "T", "all"]:
    rows = [r for r in r3.values() if cond in (r["cond"], "all")]
    t = [r["test"] for r in rows]
    other = len(t) - t.count("catches") - t.count("misses") - t.count("broken")
    print(f"| {cond} | {len(rows)} | {t.count('catches')} | {t.count('misses')} | {t.count('broken')} | {other} | "
          f"{sum(r['fix_ref'] == 'fail' for r in rows)} | {sum(r['shared'] for r in rows)} |")

print("\n## Paired by case\n")
print("| Pair | Cases with both | Same on all three verdicts | Fix wrong only in first | Fix wrong only in second | "
      "Shared only in first | Shared only in second |")
print("|---|---|---|---|---|---|---|")
cases = sorted({r["case"] for r in r3.values()})
for a, b in [("C", "D"), ("C", "T"), ("D", "T")]:
    both = [(r3[f"{c}-{a}"], r3[f"{c}-{b}"]) for c in cases if f"{c}-{a}" in r3 and f"{c}-{b}" in r3]
    same = sum((x["test"], x["fix_ref"], x["shared"]) == (y["test"], y["fix_ref"], y["shared"]) for x, y in both)
    f1 = sum(x["fix_ref"] == "fail" and y["fix_ref"] == "pass" for x, y in both)
    f2 = sum(x["fix_ref"] == "pass" and y["fix_ref"] == "fail" for x, y in both)
    s1 = sum(x["shared"] and not y["shared"] for x, y in both)
    s2 = sum(y["shared"] and not x["shared"] for x, y in both)
    print(f"| {a} vs {b} | {len(both)} | {same} | {f1} | {f2} | {s1} | {s2} |")

print("\n## Replication of round 2 (same case, condition, prompt and model)\n")
print("| Run | Test r2 -> r3 | Fix r2 -> r3 | Shared r2 -> r3 | Same |")
print("|---|---|---|---|---|")
n_same = 0
rep = [k for k in planned if k in r2 and k in r3]
for k in rep:
    x, y = r2[k], r3[k]
    same = (x["test"], x["fix_ref"], x["shared"]) == (y["test"], y["fix_ref"], y["shared"])
    n_same += same
    print(f"| {k} | {x['test']} -> {y['test']} | {x['fix_ref']} -> {y['fix_ref']} | "
          f"{yes(x['shared'])} -> {yes(y['shared'])} | {'yes' if same else 'no'} |")
print(f"\n{n_same} of {len(rep)} repeated runs gave the same three verdicts.")

if use:
    tok = [u["tokens"] for u in use.values()]
    sec = [u["seconds"] for u in use.values()]
    tools = [u["tool_uses"] for u in use.values()]
    print(f"\n## Cost\n\n{len(use)} runs, {sum(tok) / 1e6:.2f}M tokens (min {min(tok) / 1e3:.1f}k, mean "
          f"{statistics.mean(tok) / 1e3:.1f}k, max {max(tok) / 1e3:.1f}k), {min(tools)} to {max(tools)} tool calls, "
          f"median {statistics.median(sec):.0f} s per run.")
if missing:
    print("\nNot graded:", ", ".join(missing))
