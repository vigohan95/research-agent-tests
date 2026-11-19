"""Round 3 grader: the agent wrote both a fix and a test from a vague symptom.

Sandboxes: <work>/sandbox3/<case>-<cond>/ (C = agent instruction files removed,
D = kept, T = removed and guidance_T.md given as AGENTS.md). Pristine copies of
the buggy commit: <work>/pristine3/<case>/. Each case uses its own interpreter
(run.py_for).

For each run, all mechanical, no model judges anything:
  test       the agent's test on the upstream trees (run.py verdict:
             catches / misses / broken / buggy-error)
  fix_ref    upstream reference tests on (buggy tree + agent's source edits):
             pass = the agent's fix satisfies the maintainers' tests
  test_own   the agent's test on (buggy tree + agent's source edits)
  shared     test_own passes but fix_ref fails: the agent's test agrees with
             the agent's own wrong fix (the shared-misunderstanding case)

Writes pilot/results3.jsonl, copies tests to pilot/tests3/ and the agents'
source diffs to pilot/fixes3/. Pass run names to grade only those; rows of
other runs already in results3.jsonl are kept.
"""

from __future__ import annotations

import difflib
import json
import os
import shutil
import sys
from pathlib import Path

import run  # same directory

HERE = Path(__file__).resolve().parent
WORK = Path(os.environ.get("PILOT_WORK", "work")).resolve()
SKIP_PARTS = {"__pycache__", ".pytest_cache", ".hypothesis", ".mypy_cache"}
SKIP_NAMES = {"PILOT_TASK.md", run.CANDIDATE_NAME}
TEST_PARTS = {"tests", "test", "testsuite"}


def changed_sources(sb: Path, pristine: Path) -> list[str]:
    """Relative paths of .py files the agent added or edited, tests excluded."""
    out = []
    for f in sb.rglob("*.py"):
        rel = f.relative_to(sb)
        if SKIP_PARTS & set(rel.parts) or f.name in SKIP_NAMES:
            continue
        if TEST_PARTS & set(rel.parts) or f.name.startswith("test_") or f.name == "conftest.py":
            continue
        p = pristine / rel
        if not p.exists() or p.read_bytes() != f.read_bytes():
            out.append(rel.as_posix())
    return sorted(out)


def grade(sb: Path) -> dict:
    cid, cond = sb.name.rsplit("-", 1)
    c = run.CASES[cid]
    python = run.py_for(WORK, c)
    repo = WORK / c["repo"]
    pristine = WORK / "pristine3" / cid
    cand = sb / c["test_dir"] / run.CANDIDATE_NAME
    srcs = changed_sources(sb, pristine)
    row = {"case": cid, "cond": cond, "changed": srcs}

    # Save the agent's source diff for reading.
    diff = []
    for rel in srcs:
        a = (pristine / rel).read_text("utf-8").splitlines(True) if (pristine / rel).exists() else []
        b = (sb / rel).read_text("utf-8").splitlines(True)
        diff += difflib.unified_diff(a, b, f"a/{rel}", f"b/{rel}")
    (HERE / "fixes3" / f"{sb.name}.diff").write_text("".join(diff), "utf-8", newline="\n")
    row["diff_lines"] = sum(1 for l in diff if l[:1] in "+-" and l[:3] not in ("+++", "---"))

    dest = repo / c["test_dir"] / run.CANDIDATE_NAME
    if not cand.exists():
        row["test"] = "no-test"
    else:
        shutil.copyfile(cand, HERE / "tests3" / f"{sb.name}.py")
        try:
            run.set_tree(repo, c, "fixed")
            shutil.copyfile(cand, dest)
            r = run.run_both(python, repo, c, [str(dest.relative_to(repo))])
        finally:
            dest.unlink(missing_ok=True)
        row["test"] = r["verdict"]
        row["test_fixed"], row["test_buggy"] = r["fixed"]["summary"], r["buggy"]["summary"]

    # Buggy tree + the agent's source edits.
    try:
        run.set_tree(repo, c, "buggy")
        for rel in srcs:
            (repo / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(sb / rel, repo / rel)
        ref = run.pytest(python, repo, c["ref_tests"])
        row["fix_ref"] = "pass" if ref["exit"] == 0 else "fail"
        row["fix_ref_summary"] = ref["summary"]
        if cand.exists():
            shutil.copyfile(cand, dest)
            own = run.pytest(python, repo, [str(dest.relative_to(repo))])
            row["test_own"] = "pass" if own["exit"] == 0 else "fail"
            row["test_own_summary"] = own["summary"]
    finally:
        dest.unlink(missing_ok=True)
        for rel in srcs:  # drop files the agent added
            if not (pristine / rel).exists():
                (repo / rel).unlink(missing_ok=True)
        run.set_tree(repo, c, "fixed")
    row["shared"] = row.get("test_own") == "pass" and row["fix_ref"] == "fail"
    return row


def main() -> int:
    (HERE / "tests3").mkdir(exist_ok=True)
    (HERE / "fixes3").mkdir(exist_ok=True)
    out = HERE / "results3.jsonl"
    rows = {}
    if out.exists():
        for line in out.read_text("utf-8").splitlines():
            r = json.loads(line)
            rows[f"{r['case']}-{r['cond']}"] = r
    only = set(sys.argv[1:])
    for sb in sorted((WORK / "sandbox3").iterdir()):
        if only and sb.name not in only:
            continue
        row = grade(sb)
        rows[sb.name] = row
        print(f"{sb.name:24} test={row['test']:8} fix_ref={row['fix_ref']:4} own={row.get('test_own', '-'):4} "
              f"shared={row['shared']} changed={row['changed']} | ref: {row['fix_ref_summary']}")
        with open(out, "w", encoding="utf-8", newline="\n") as f:
            for k in sorted(rows):
                f.write(json.dumps(rows[k]) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
