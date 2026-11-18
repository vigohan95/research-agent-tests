# Full read of the 20 agent instruction files (2026-11-17)

Source: the 20 repositories that `audit.py` found with a root-level instruction file on 2026-11-06.
All files were re-fetched on 2026-11-17 from the default branch and read in full (the long ones,
dask / firedrake / dolfinx / ESMValTool / numpyro / nilearn / awkward / lammps, were read section by
section with every testing, verification and correctness paragraph read in full). Files that only
redirect (`CLAUDE.md` -> `AGENTS.md`, pyvista's Copilot file) are folded into their repository.
Nested guides the root file points to were read where they are about tests (xarray
`xarray/tests/AGENTS.md`); pandas' `pandas-review` skill, pyvista's `pyvista-testing` skill and
lammps' `.github/instructions/*` were **not** read and are not counted.

Columns (yes only if the file itself says it, not a linked document):
- **Fail-first**: a bug-fix test must fail without the fix.
- **No weakening**: do not skip / loosen / delete / change existing tests to make a change pass.
- **External truth**: compare numbers against another package, analytic result or reference implementation.
- **Meaningful-test rule**: any other rule about what makes a test prove something.

| Repo | Fail-first | No weakening | External truth | Meaningful-test rule / other test content |
|---|---|---|---|---|
| scikit-learn | – | – | – | none; file is about disclosure and triage labels |
| pandas | – | – | – | run a separate review skill in a fresh session before review (not read) |
| xarray | – | – (only: do not touch known-flaky network tests) | – | nested tests guide: skip at collection, share one body for numpy and dask "checks that numpy and dask give the same result" |
| sympy | – | – | – | none beyond running quality checks |
| networkx | – | – | – | none; confirm an issue reproduces on `main` before filing |
| mne-python | **yes**, with an exact procedure (restore source files from `main`, run, re-apply) | **yes** (skip, xfail, loosen, delete) | – | "a regression test that passes without the fix guards nothing"; extend existing parametrized tests |
| nilearn | – | – | – | synthetic data only; mark AI-written tests `ai_generated` |
| pymc | – | – | – | about deciding whether a bug is real: reproduce through the real compiled workflow; constant-only evaluation is not evidence |
| statsmodels | **yes** | – | **yes** (R, Stata, SAS, closed form; document source of each value) | "alter the changed line and a test must fail"; internal-consistency tests are "necessary but not sufficient"; rtol by default, a reason for every atol; no asserting rounding zeros or optimizer stopping points |
| dask | – | – | – | `assert_eq` against pandas/numpy; how to run tests |
| lammps | – | – | – | how to build and run ctest; check sibling style variants for the same bug |
| firedrake | – | partly ("do not patch individual failing test cases", about code) | – | narrowest test that proves the change; parallel runs must match serial; an unmarked green run is not evidence the MPI tests passed |
| dolfinx | – | – | – | build in Developer mode; run the affected suite |
| pyvista | – | – | – | "a plotting test that ends in close() tests nothing"; a probe's tests can pass "when they assert the damage" |
| yt | – (tests required for bug fixes, via CONTRIBUTING) | – | – | start with the nearest tests, widen when shared code changes |
| ESMValTool | – | **yes** ("do not change existing tests to make new code pass") | – | "make sure the scientific results are reliable"; diagnostics verified by inspecting output figures |
| nextflow | – | – | – | run the tests of each changed module |
| ROOT | **yes** | **yes** | – | report which tests were and were not run |
| awkward | – | – | partly (kernel YAML spec holds a Python reference implementation; generated tests check against it) | one test file per issue number |
| numpyro | – | – | **yes** (SciPy or analytic results, float32 tolerances) | – |

## Counts (20 repositories)

- Say nothing about tests at all: 4 (scikit-learn, pandas root file, sympy, networkx).
- Fail-first rule: 3 (mne-python, statsmodels, ROOT).
- No-weakening rule: 3 (mne-python, ESMValTool, ROOT), plus firedrake partly.
- External numerical truth: 2 (statsmodels, numpyro), plus awkward partly.
- A check that each changed line is guarded by a test (a hand-run mutation check): 1 (statsmodels).
- Only one file (statsmodels) combines fail-first, external truth and tolerance rules.

## What changes for the proposal

1. The 2026-11-06 keyword pass said "few said what makes a test meaningful". The full read confirms it
   with numbers: 3 of 20 require fail-first, 1 of 20 asks for a mutation-style check.
2. statsmodels' file is already close to the guidance we would test. The study should use it as one of
   the guidance conditions (a strong real-world file) rather than writing our own from scratch.
3. Two files name failure modes the pilot saw: pyvista ("assert the damage") and statsmodels
   ("internal-consistency-only ... not sufficient"). Both are evidence that maintainers already see
   agent tests that pass on wrong behaviour.
4. Limitation to state: the audit only looks at root-level files; several projects keep test guidance
   in nested files or skills (xarray, pandas, pyvista, lammps). Counts are a lower bound for those four.
