# When the 20 instruction files first appeared (checked 2026-11-20)

Output of `python audit/first_commit.py audit/audit-2026-11-17.json`. For each of the 20
repositories that `audit.py` found with a root-level agent instruction file, the earliest
commit on the default branch that touches any of its instruction-file paths.

| Repository | Earliest instruction file | First commit (UTC) | Commits on that path |
|---|---|---|---|
| pydata/xarray | `CLAUDE.md` | 2025-09-03 | 8 |
| lammps/lammps | `.github/copilot-instructions.md` | 2025-10-18 | 33 |
| scikit-learn/scikit-learn | `AGENTS.md` | 2025-10-30 | 3 |
| pandas-dev/pandas | `AGENTS.md` | 2025-11-13 | 5 |
| nilearn/nilearn | `AGENTS.md` | 2026-05-13 | 5 |
| dask/dask | `AGENTS.md` | 2026-05-29 | 4 |
| scikit-hep/awkward | `AGENTS.md` | 2026-06-10 | 4 |
| mne-tools/mne-python | `CLAUDE.md` | 2026-07-02 | 2 |
| sympy/sympy | `CLAUDE.md` | 2026-07-08 | 3 |
| firedrakeproject/firedrake | `AGENTS.md` | 2026-07-09 | 5 |
| FEniCS/dolfinx | `AGENTS.md` | 2026-07-18 | 20 |
| statsmodels/statsmodels | `AGENTS.md` | 2026-08-11 | 8 |
| networkx/networkx | `AGENTS.md` | 2026-08-13 | 2 |
| pyvista/pyvista | `AGENTS.md` | 2026-08-16 | 10 |
| pyro-ppl/numpyro | `AGENTS.md` | 2026-09-20 | 1 |
| root-project/root | `AGENTS.md` | 2026-09-29 | 1 |
| yt-project/yt | `AGENTS.md` | 2026-09-29 | 2 |
| pymc-devs/pymc | `AGENTS.md` | 2026-10-25 | 2 |
| ESMValGroup/ESMValTool | `AGENTS.md` | 2026-10-28 | 1 |
| nextflow-io/nextflow | `AGENTS.md` | 2026-10-30 | 2 |

Of the 20: 4 first appeared in 2025, 16 in 2026, and 13 of those on or after 1 July 2026.

Caveats:

- The commit list for a path does not follow renames. A file moved to its current name from
  somewhere else looks younger than it is, so a file can be older than the date shown.
- Root-level files only (`AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.cursorrules`,
  `.github/copilot-instructions.md`), as in `audit.py`. Guidance kept elsewhere is not seen.
- The 38 repositories checked were chosen, not sampled. This says how recent these 20 files
  are, not how common such files are in research software.
- Raw output: `first-commit-2026-11-20.json`.
