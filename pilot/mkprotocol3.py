"""Writes runs3.json and the case table of PROTOCOL3.md from cases.json.

Conditions per case (fixed rule, no per-case choice):
  C  always
  D  if the buggy commit has agent instruction files (guidance_files non-empty)
  T  always
"""

from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
cases = json.loads((HERE / "cases.json").read_text("utf-8"))

runs, rows = [], []
for c in cases:
    conds = ["C"]
    if c.get("guidance_files"):
        conds.append("D")
    conds.append("T")
    runs += [f"{c['id']}-{x}" for x in conds]
    project, number = c["url"].split("/")[4], c["url"].split("/")[-1]
    rows.append(f"| {c['id']} | [{project} #{number}]({c['url']}) | {c['merged']} | {c['kind']} | "
                f"{len(c['src_files'])} | {len(c.get('guidance_files', []))} | {' '.join(conds)} |")

(HERE / "runs3.json").write_text(json.dumps(runs, indent=1) + "\n", "utf-8", newline="\n")
table = "\n".join(["| Case | Fix PR | Merged | Kind | Source files changed | Instruction files at the buggy commit | Conditions |",
                   "|---|---|---|---|---|---|---|", *rows])
p = HERE / "PROTOCOL3.md"
text = p.read_text("utf-8")
a, b = "<!-- cases:start -->", "<!-- cases:end -->"
assert text.count(a) == 1 and text.count(b) == 1
text = text[: text.index(a) + len(a)] + "\n" + table + "\n" + text[text.index(b):]
p.write_text(text, "utf-8", newline="\n")
n = {x: sum(r.endswith("-" + x) for r in runs) for x in "CDT"}
print(len(cases), "cases,", len(runs), "runs", n)
