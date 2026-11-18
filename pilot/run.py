"""Pilot runner: does a test fail on the buggy code and pass on the fixed code?

Each case in cases.json is a merged, squash-committed bug fix. "fixed" is the
merge commit and "buggy" its parent. To get the buggy tree we check out the
fixed commit and restore only the non-test source files from the parent, so
the test files under evaluation are identical in both runs.

Usage (repos are cloned under --work, editable-installed in the venv):
  python run.py validate [--case ID]          # reference tests from the fix
  python run.py check CASE_ID CANDIDATE.py    # a candidate test file

A verdict is mechanical, no model judges it:
  catches  passes on fixed, fails on buggy
  misses   passes on both
  broken   fails (or errors / collects nothing) on fixed
"""

from __future__ import annotations

import os
import argparse
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
CASES = {c["id"]: c for c in json.loads((HERE / "cases.json").read_text("utf-8"))}
CANDIDATE_NAME = "test_pilot_candidate.py"


def git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args], check=True, capture_output=True, text=True
    ).stdout


def pytest(python: str, repo: Path, targets: list[str]) -> dict:
    t0 = time.time()
    p = subprocess.run(
        [python, "-m", "pytest", "-q", "-p", "no:cacheprovider", "-rN",
         "--no-header", "-o", "addopts=", *targets],
        cwd=repo, capture_output=True, text=True,
    )
    tail = (p.stdout + p.stderr).strip().splitlines()[-1:] or [""]
    # exit 0 = all passed, 1 = some failed, 2+ = error / nothing collected
    return {"exit": p.returncode, "summary": tail[0], "seconds": round(time.time() - t0, 1)}


def set_tree(repo: Path, case: dict, state: str) -> None:
    git(repo, "checkout", "-q", "--force", case["fixed"])
    if state == "buggy":
        git(repo, "checkout", "-q", case["buggy"], "--", *case["src_files"])


def run_both(python: str, repo: Path, case: dict, targets: list[str]) -> dict:
    out = {}
    for state in ("fixed", "buggy"):
        set_tree(repo, case, state)
        out[state] = pytest(python, repo, targets)
    set_tree(repo, case, "fixed")
    f, b = out["fixed"]["exit"], out["buggy"]["exit"]
    out["verdict"] = "broken" if f != 0 else ("catches" if b == 1 else "misses" if b == 0 else "buggy-error")
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["validate", "check"])
    ap.add_argument("case", nargs="?")
    ap.add_argument("candidate", nargs="?")
    ap.add_argument("--work", default=str(Path(os.environ.get("PILOT_WORK", "work")).resolve()))
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    work = Path(a.work)
    python = str(work / ".venv" / "Scripts" / "python.exe")
    if not Path(python).exists():
        python = str(work / ".venv" / "bin" / "python")

    results = []
    if a.cmd == "validate":
        ids = [a.case] if a.case else list(CASES)
        for cid in ids:
            c = CASES[cid]
            r = run_both(python, work / c["repo"], c, c["ref_tests"])
            results.append({"case": cid, "test": "reference", **r})
    else:
        c = CASES[a.case]
        repo = work / c["repo"]
        dest = repo / c["test_dir"] / CANDIDATE_NAME
        try:
            set_tree(repo, c, "fixed")
            shutil.copyfile(a.candidate, dest)
            r = run_both(python, repo, c, [str(dest.relative_to(repo))])
        finally:
            dest.unlink(missing_ok=True)
        results.append({"case": a.case, "test": str(a.candidate), **r})

    for r in results:
        if a.json:
            print(json.dumps(r))
        else:
            print(f"{r['case']:14} {r['verdict']:8} fixed: {r['fixed']['summary']} | buggy: {r['buggy']['summary']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
