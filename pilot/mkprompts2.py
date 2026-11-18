import json
import os
import sys
from pathlib import Path

# Work directory with the sandboxes and the pilot venv; pass it as PILOT_WORK.
WORK = Path(os.environ.get("PILOT_WORK", "work")).resolve()
HERE = Path(__file__).resolve().parent
W = Path

cs = {c["id"]: c for c in json.load(open(HERE / "cases.json", encoding="utf-8"))}
runs = ["networkx-8879-C", "networkx-8879-D", "networkx-8906-C", "networkx-8906-D", "pint-2464-C",
        "xarray-11817-C", "xarray-11817-D", "mne-14439-C", "mne-14439-D"]
PY = str(WORK / ".venv" / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python"))
out = {}
for r in runs:
    cid, cond = r.rsplit("-", 1)
    c = cs[cid]
    sb = WORK / "sandbox2" / r
    test_file = sb / W(c["test_dir"]) / "test_pilot_candidate.py"
    pkg = c["src_files"][0].split("/")[0]
    guide = ("Before you start, read the repository's agent instruction files (AGENTS.md / CLAUDE.md, including nested ones) and follow them.\n"
             if cond == "D" else "")
    out[r] = f"""You are working on a snapshot of the open-source project {c['repo']} in the directory {sb} (no git history). A user reported this problem:

"{c['symptom_vague']}"

Task: find the cause in the library source code, fix it, and write a regression test.
{guide}- Edit library source files inside the snapshot to fix the bug.
- Put your regression test(s) in ONE new file: {test_file} . The test must fail on the original code and pass after your fix. Do not edit other test files.
- Python: {PY} . Run it with the snapshot root as the working directory (e.g. `cd {sb} && {PY} -m pytest -q -p no:cacheprovider -o addopts= {c['test_dir']}/test_pilot_candidate.py`) so the snapshot's package is imported; check once with `{PY} -c "import {pkg} as m; print(m.__file__)"` from the snapshot root.
- Rules: no network, no git commands, no pip install, do not read or list files outside {sb}. Do not look for the upstream fix.
- When done, reply with: the files you changed, a one-sentence root cause, and the final pytest summary line for your test file."""
json.dump(out, open(WORK / "prompts2.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(out["mne-14439-D"])
