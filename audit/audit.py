"""Keyword-level audit of agent instruction files in research-software repos.

Records which instruction files exist and whether they mention tests at all,
and whether they mention any verification beyond "run the tests".
It says nothing about quality; a human still has to read the hits.
"""
import base64, json, re, subprocess, sys

REPOS = """numpy/numpy scipy/scipy astropy/astropy scikit-learn/scikit-learn scikit-image/scikit-image
matplotlib/matplotlib pandas-dev/pandas pydata/xarray sympy/sympy networkx/networkx biopython/biopython
mne-tools/mne-python nipy/nibabel nilearn/nilearn pymc-devs/pymc statsmodels/statsmodels dask/dask
SciML/DifferentialEquations.jl openmm/openmm MDAnalysis/mdanalysis rdkit/rdkit lammps/lammps
firedrakeproject/firedrake FEniCS/dolfinx pyvista/pyvista sunpy/sunpy yt-project/yt Unidata/MetPy
ESMValGroup/ESMValTool scverse/scanpy scverse/anndata nextflow-io/nextflow snakemake/snakemake
galaxyproject/galaxy root-project/root scikit-hep/awkward pyro-ppl/numpyro jax-ml/jax""".split()
FILES = ["AGENTS.md", "CLAUDE.md", "GEMINI.md", ".cursorrules", ".github/copilot-instructions.md"]
TEST = re.compile(r"\b(tests?|pytest|ctest|unit test)\b", re.I)
BEYOND = re.compile(r"integration test|regression|reference (data|result|solution|value)|golden|"
                    r"tolerance|analytic|benchmark|numerical(ly)? (accura|correct|stab)|"
                    r"validat(e|ion) against|end-to-end|property-based|hypothesis", re.I)
TRIVIAL = re.compile(r"(do not|don't|never|avoid)[^.\n]{0,60}(weaken|delete|remove|skip|modify|change)[^.\n]{0,40}test|"
                     r"(trivial|tautolog|meaningless)[^.\n]{0,40}test|test[^.\n]{0,40}(trivial|tautolog)", re.I)


def get(repo, path):
    r = subprocess.run(["gh", "api", f"repos/{repo}/contents/{path}"], capture_output=True, text=True)
    if r.returncode:
        return None
    d = json.loads(r.stdout)
    return base64.b64decode(d["content"]).decode("utf8", "ignore") if isinstance(d, dict) and d.get("content") else None


rows = []
for repo in REPOS:
    found = {}
    for f in FILES:
        t = get(repo, f)
        if t:
            found[f] = {"bytes": len(t), "test": bool(TEST.search(t)), "beyond": sorted({m.group(0).lower() for m in BEYOND.finditer(t)}),
                        "guards_tests": bool(TRIVIAL.search(t))}
    rows.append({"repo": repo, "files": found})
    print(repo, {k: (v["bytes"], v["test"], v["beyond"][:4], v["guards_tests"]) for k, v in found.items()}, flush=True)

json.dump(rows, open(sys.argv[1], "w"), indent=1)
have = [r for r in rows if r["files"]]
t = [r for r in have if any(v["test"] for v in r["files"].values())]
b = [r for r in have if any(v["beyond"] for v in r["files"].values())]
g = [r for r in have if any(v["guards_tests"] for v in r["files"].values())]
print(f"repos {len(rows)} | with file {len(have)} | mention tests {len(t)} | beyond {len(b)} | guards {len(g)}")
