# Round 2 sandboxes: C = guidance removed, D = guidance kept. Also a pristine copy per case for diffing.

cd "$(dirname "$0")"
mk() { # id repo buggy cond
  d=sandbox2/$1-$4; rm -rf "$d"; mkdir -p "$d"; git -C $2 archive $3 | tar -x -C "$d" 2>/dev/null || true
  if [ "$4" = C ]; then find "$d" \( -name AGENTS.md -o -name CLAUDE.md -o -name GEMINI.md -o -name .cursorrules -o -name copilot-instructions.md \) -delete; rm -rf "$d/.claude" "$d/.cursor"; fi
}
pr() { d=pristine/$1; rm -rf "$d"; mkdir -p "$d"; git -C $2 archive $3 | tar -x -C "$d" 2>/dev/null || true; }
pr networkx-8879 networkx a7d049b4992a1f7e9bd376ce7378d3825d0cfa0e; mk networkx-8879 networkx a7d049b4992a1f7e9bd376ce7378d3825d0cfa0e C; mk networkx-8879 networkx a7d049b4992a1f7e9bd376ce7378d3825d0cfa0e D
pr networkx-8906 networkx 4a72b69adcf22da900710cd39cf6212b9420db12; mk networkx-8906 networkx 4a72b69adcf22da900710cd39cf6212b9420db12 C; mk networkx-8906 networkx 4a72b69adcf22da900710cd39cf6212b9420db12 D
pr pint-2464 pint 8c9448cb95a230f196d9c1e7e90fb61a84acb74e; mk pint-2464 pint 8c9448cb95a230f196d9c1e7e90fb61a84acb74e C
pr xarray-11817 xarray ddbd474109883ca97d70257e0df1a5ac060b137f; mk xarray-11817 xarray ddbd474109883ca97d70257e0df1a5ac060b137f C; mk xarray-11817 xarray ddbd474109883ca97d70257e0df1a5ac060b137f D
pr mne-14439 mne-python b46a31b407a35c4cd2c56a92988f7cf59405bedc; mk mne-14439 mne-python b46a31b407a35c4cd2c56a92988f7cf59405bedc C; mk mne-14439 mne-python b46a31b407a35c4cd2c56a92988f7cf59405bedc D
# While agents run, park the shared clones on buggy commits so the editable installs cannot leak the fix.
git -C networkx checkout -q --force a7d049b4992a1f7e9bd376ce7378d3825d0cfa0e
git -C pint checkout -q --force 8c9448cb95a230f196d9c1e7e90fb61a84acb74e
git -C xarray checkout -q --force ddbd474109883ca97d70257e0df1a5ac060b137f
git -C mne-python checkout -q --force b46a31b407a35c4cd2c56a92988f7cf59405bedc
ls sandbox2 pristine
