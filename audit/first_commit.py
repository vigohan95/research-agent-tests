"""When did each repository first get a root-level agent instruction file?

Reads an audit JSON written by audit.py and, for every repository that has at least one
instruction file, asks the GitHub API for the commits touching each of those paths on the
default branch. Prints the earliest committer date across the files.

Caveats: the commit list for a path does not follow renames, so a file that was moved to
its current name from somewhere else looks younger than it is; a file that was deleted and
later re-added under the same path is dated from its first appearance.

Usage: python audit/first_commit.py audit/audit-2026-11-17.json [out.json]
(needs an authenticated `gh`)
"""
import json
import subprocess
import sys


def first_commit(repo, path):
    r = subprocess.run(
        ["gh", "api", "--paginate", f"repos/{repo}/commits?path={path}&per_page=100",
         "--jq", ".[].commit.committer.date"],
        capture_output=True, text=True)
    if r.returncode:
        return None, 0
    dates = sorted(d for d in r.stdout.split() if d)
    return (dates[0] if dates else None), len(dates)


def main():
    rows = json.load(open(sys.argv[1], encoding="utf-8"))
    out = []
    for row in rows:
        best = None
        for path in row["files"]:
            date, n = first_commit(row["repo"], path)
            if date and (best is None or date < best[0]):
                best = (date, path, n)
        if best:
            out.append({"repo": row["repo"], "first_commit": best[0], "file": best[1], "commits_on_path": best[2]})
    out.sort(key=lambda o: o["first_commit"])
    print("| Repository | Earliest instruction file | First commit (UTC) | Commits on that path |")
    print("|---|---|---|---|")
    for o in out:
        print(f"| {o['repo']} | `{o['file']}` | {o['first_commit'][:10]} | {o['commits_on_path']} |")
    y2026 = [o for o in out if o["first_commit"] >= "2026-01-01"]
    july = [o for o in out if o["first_commit"] >= "2026-07-01"]
    print(f"\n{len(out)} repositories with a file; first commit in 2026: {len(y2026)}; on or after 2026-07-01: {len(july)}")
    if len(sys.argv) > 2:
        json.dump(out, open(sys.argv[2], "w", encoding="utf-8"), indent=1)


if __name__ == "__main__":
    main()
