"""Round 2 grader: the agent wrote both a fix and a test from a vague symptom.

Sandboxes: <work>/sandbox2/<case>-<cond>/ (C = agent instruction files removed,
D = kept). Pristine copies of the buggy commit: <work>/pristine/<case>/.

For each run, all mechanical, no model judges anything:
  test       the agent's test on the upstream trees (run.py verdict:
             catches / misses / broken / buggy-error)
  fix_ref    upstream reference tests on (buggy tree + agent's source edits):
             pass = the agent's fix satisfies the maintainers' tests
  test_own   the agent's test on (buggy tree + agent's source edits)
  shared     test_own passes but fix_ref fails: the agent's test agrees with
             the agent's own wrong fix (the shared-misunderstanding case)

Writes pilot/results2.jsonl, copies tests to pilot/tests2/ and the agents'
source diffs to pilot/fixes2/.
"""

from __future__ import annotations

import os
import difflib
import json
import shutil
import sys
from pathlib import Path

import run  # same directory

HERE = Path(__file__).resolve().parent
WORK = Path(os.environ.get("PILOT_WORK", "work")).resolve()
SKIP_PARTS = {"__pycache__", ".pytest_cache", ".hypothesis", ".mypy_cache"}
SKIP_NAMES = {"PILOT_TASK.md", run.CANDIDATE_NAME}


def changed_sources(sb: Path, pristine: Path) -> list[str]:
    """Relative paths of .py files the agent added or edited, tests excluded."""
    out = []
    for f in sb.rglob("*.py"):
        rel = f.relative_to(sb)
        if SKIP_PARTS & set(rel.parts) or f.name in SKIP_NAMES:
            continue
        if "tests" in rel.parts or "testsuite" in rel.parts or f.name.startswith("test_"):
            continue
        p = pristine / rel
        if not p.exists() or p.read_bytes() != f.read_bytes():
            out.append(rel.as_posix())
    return sorted(out)


def main() -> int:
    python = str(WORK / ".venv" / "Scripts" / "python.exe")
    if not Path(python).exists():
        python = str(WORK / ".venv" / "bin" / "python")
    (HERE / "tests2").mkdir(exist_ok=True)
    (HERE / "fixes2").mkdir(exist_ok=True)
    rows = []
    for sb in sorted((WORK / "sandbox2").iterdir()):
        cid, cond = sb.name.rsplit("-", 1)
        c = run.CASES[cid]
        repo = WORK / c["repo"]
        pristine = WORK / "pristine" / cid
        cand = sb / c["test_dir"] / run.CANDIDATE_NAME
        srcs = changed_sources(sb, pristine)
        row = {"case": cid, "cond": cond, "changed": srcs}

        # Save the agent's source diff for reading.
        diff = []
        for rel in srcs:
            a = (pristine / rel).read_text("utf-8").splitlines(True) if (pristine / rel).exists() else []
            b = (sb / rel).read_text("utf-8").splitlines(True)
            diff += difflib.unified_diff(a, b, f"a/{rel}", f"b/{rel}")
        (HERE / "fixes2" / f"{sb.name}.diff").write_text("".join(diff), "utf-8")
        row["diff_lines"] = sum(1 for l in diff if l[:1] in "+-" and l[:3] not in ("+++", "---"))

        if not cand.exists():
            row["test"] = "no-test"
        else:
            shutil.copyfile(cand, HERE / "tests2" / f"{sb.name}.py")
            dest = repo / c["test_dir"] / run.CANDIDATE_NAME
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
                shutil.copyfile(sb / rel, repo / rel)
            ref = run.pytest(python, repo, c["ref_tests"])
            row["fix_ref"] = "pass" if ref["exit"] == 0 else "fail"
            row["fix_ref_summary"] = ref["summary"]
            if cand.exists():
                dest = repo / c["test_dir"] / run.CANDIDATE_NAME
                shutil.copyfile(cand, dest)
                own = run.pytest(python, repo, [str(dest.relative_to(repo))])
                dest.unlink(missing_ok=True)
                row["test_own"] = "pass" if own["exit"] == 0 else "fail"
        finally:
            for rel in srcs:  # drop files the agent added
                if not (pristine / rel).exists():
                    (repo / rel).unlink(missing_ok=True)
            run.set_tree(repo, c, "fixed")
        row["shared"] = row.get("test_own") == "pass" and row["fix_ref"] == "fail"
        rows.append(row)
        print(f"{sb.name:16} test={row['test']:8} fix_ref={row['fix_ref']:4} own={row.get('test_own','-'):4} "
              f"shared={row['shared']} changed={srcs} | ref: {row['fix_ref_summary']}")

    with open(HERE / "results2.jsonl", "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
