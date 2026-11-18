"""Copy each agent-written candidate out of its sandbox and grade it with run.py.

Sandboxes live at <work>/sandbox/<case>-<cond>/ (a git-archive snapshot of the
buggy commit; condition A had agent instruction files removed, B kept them).
Graded tests are copied to pilot/tests/<case>-<cond>.py, verdicts appended to
pilot/results.jsonl.
"""

from __future__ import annotations

import os
import json
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
WORK = Path(os.environ.get("PILOT_WORK", "work")).resolve()
CASES = {c["id"]: c for c in json.loads((HERE / "cases.json").read_text("utf-8"))}


def main() -> int:
    out_dir = HERE / "tests"
    out_dir.mkdir(exist_ok=True)
    rows = []
    for sb in sorted((WORK / "sandbox").iterdir()):
        cid, cond = sb.name.rsplit("-", 1)
        c = CASES[cid]
        cand = sb / c["test_dir"] / "test_pilot_candidate.py"
        if not cand.exists():
            rows.append({"case": cid, "cond": cond, "verdict": "no-test"})
            continue
        dest = out_dir / f"{cid}-{cond}.py"
        shutil.copyfile(cand, dest)
        p = subprocess.run([sys.executable, str(HERE / "run.py"), "check", cid, str(cand), "--json"],
                           capture_output=True, text=True, check=True)
        r = json.loads(p.stdout)
        rows.append({"case": cid, "cond": cond, "verdict": r["verdict"],
                     "fixed": r["fixed"]["summary"], "buggy": r["buggy"]["summary"],
                     "lines": len(dest.read_text("utf-8").splitlines())})
    with open(HERE / "results.jsonl", "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
            print(f"{r['case']:14} {r['cond']} {r['verdict']:8} {r.get('fixed','')} | {r.get('buggy','')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
