"""Round 3 sandboxes. Run after cases.json and runs3.json are final.

For every run in runs3.json makes <work>/sandbox3/<case>-<cond>/ from the
buggy commit (no git history) and one <work>/pristine3/<case>/ for diffing.
  C  agent instruction files removed
  D  the repository's own instruction files kept
  T  instruction files removed, then guidance_T.md written as AGENTS.md
Compiled files that are untracked in the clone (*.pyd, *.so, _version.py)
are copied in, so packages with extensions import from the sandbox.
Checks that the package imports from the sandbox, then parks every clone on
a buggy commit so the fix is not checked out anywhere while agents run.
"""

from __future__ import annotations

import io
import json
import os
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path

import run  # same directory

HERE = Path(__file__).resolve().parent
WORK = Path(os.environ.get("PILOT_WORK", "work")).resolve()
GUIDE_NAMES = {"AGENTS.md", "CLAUDE.md", "GEMINI.md", ".cursorrules", "copilot-instructions.md"}
GUIDE_DIRS = {".claude", ".cursor"}
BUILT = (".pyd", ".so")


def export(repo: Path, commit: str, dest: Path) -> None:
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    data = subprocess.run(["git", "-C", str(repo), "archive", commit], check=True, capture_output=True).stdout
    with tarfile.open(fileobj=io.BytesIO(data)) as tar:
        for m in tar:
            if set(m.name) & set('<>:"|?*'):  # not a legal file name on Windows
                print(f"  skipped (file name not legal on this OS): {m.name}")
                continue
            if m.isfile() or m.isdir():
                tar.extract(m, dest, filter="data")
    # untracked build products the package needs at import time
    others = subprocess.run(["git", "-C", str(repo), "ls-files", "--others"], check=True,
                            capture_output=True, text=True).stdout.splitlines()
    for rel in others:
        if "__pycache__" in rel or not (rel.endswith(BUILT) or rel.endswith("/_version.py")):
            continue
        (dest / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(repo / rel, dest / rel)


def strip_guidance(d: Path) -> list[str]:
    removed = []
    for p in sorted(d.rglob("*"), reverse=True):
        if p.is_dir() and p.name in GUIDE_DIRS:
            removed.append(p.relative_to(d).as_posix() + "/")
            shutil.rmtree(p)
        elif p.is_file() and p.name in GUIDE_NAMES:
            removed.append(p.relative_to(d).as_posix())
            p.unlink()
    return sorted(removed)


def main() -> int:
    runs = json.loads((HERE / "runs3.json").read_text("utf-8"))
    only = set(sys.argv[1:])
    guide_t = (HERE / "guidance_T.md").read_text("utf-8")
    done = set()
    for r in runs:
        if only and r not in only:
            continue
        cid, cond = r.rsplit("-", 1)
        c = run.CASES[cid]
        repo = WORK / c["repo"]
        if cid not in done:
            export(repo, c["buggy"], WORK / "pristine3" / cid)
            done.add(cid)
        sb = WORK / "sandbox3" / r
        export(repo, c["buggy"], sb)
        removed = strip_guidance(sb) if cond in "CT" else []
        if cond == "T":
            (sb / "AGENTS.md").write_text(guide_t, "utf-8", newline="\n")
        pkg = c["src_files"][0].split("/")[0]
        p = subprocess.run([run.py_for(WORK, c), "-c", f"import {pkg} as m; print(m.__file__)"],
                           cwd=sb, capture_output=True, text=True)
        where = Path(p.stdout.strip().splitlines()[-1]).resolve() if p.returncode == 0 and p.stdout.strip() else None
        ok = where is not None and sb.resolve() in where.parents
        print(f"{r:24} import-from-sandbox={'ok' if ok else 'FAIL'} removed={removed}")
        if not ok:
            print(p.stdout[-300:], p.stderr[-600:])
            return 1
    for c in run.CASES.values():  # last case of each repo wins; any buggy commit will do
        run.git(WORK / c["repo"], "checkout", "-q", "--force", c["buggy"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
