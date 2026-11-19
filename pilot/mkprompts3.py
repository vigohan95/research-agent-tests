"""Round 3 prompts, one per run in runs3.json. Writes <work>/prompts3.json.

The wording is round 2's. D and T get one extra sentence telling the agent to
read and follow the instruction files; C does not.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import run  # same directory

HERE = Path(__file__).resolve().parent
WORK = Path(os.environ.get("PILOT_WORK", "work")).resolve()
GUIDE = ("Before you start, read the repository's agent instruction files (AGENTS.md / CLAUDE.md, "
         "including nested ones) and follow them.\n")

out = {}
for r in json.loads((HERE / "runs3.json").read_text("utf-8")):
    cid, cond = r.rsplit("-", 1)
    c = run.CASES[cid]
    sb = WORK / "sandbox3" / r
    py = run.py_for(WORK, c)
    test_file = sb / Path(c["test_dir"]) / run.CANDIDATE_NAME
    pkg = c["src_files"][0].split("/")[0]
    project = c["url"].split("/")[4]
    guide = GUIDE if cond in "DT" else ""
    out[r] = f"""You are working on a snapshot of the open-source project {project} in the directory {sb} (no git history). A user reported this problem:

"{c['symptom_vague']}"

Task: find the cause in the library source code, fix it, and write a regression test.
{guide}- Edit library source files inside the snapshot to fix the bug.
- Put your regression test(s) in ONE new file: {test_file} . The test must fail on the original code and pass after your fix. Do not edit other test files.
- Python: {py} . Run it with the snapshot root as the working directory (e.g. `cd {sb} && {py} -m pytest -q -p no:cacheprovider -o addopts= {c['test_dir']}/{run.CANDIDATE_NAME}`) so the snapshot's package is imported; check once with `{py} -c "import {pkg} as m; print(m.__file__)"` from the snapshot root.
- Rules: no network, no git commands, no pip install, do not read or list files outside {sb}. Do not look for the upstream fix.
- When done, reply with: the files you changed, a one-sentence root cause, and the final pytest summary line for your test file."""
(WORK / "prompts3.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), "utf-8")
print(len(out), "prompts")
