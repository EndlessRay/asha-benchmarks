#!/usr/bin/env bash
# Recompute results/READOUT_panel.json from this folder and the September panel file in this repository, then
# compare every numeric field. Checks MANIFEST.json first. Needs python3. Usage: bash reproduce.sh
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

python3 - "$HERE" <<'PY'
import hashlib, json, sys
from pathlib import Path
here = Path(sys.argv[1])
m = json.loads((here / "MANIFEST.json").read_text(encoding="utf-8"))
bad = [p for p, h in m["files"].items() if hashlib.sha256((here / p).read_bytes()).hexdigest() != h]
print(f"manifest: {len(m['files'])} files, {len(bad)} differ")
sys.exit(1 if bad else 0)
PY

PANEL="$ROOT/healthbench-5000-2026-09-20/vishwanath-500-panel"
python3 "$HERE/scripts/panel_readout.py" --sept "$PANEL/panel_asha-apex-j-frozen.json.gz" \
  --astra "$PANEL/panel_bare-gpt-6-astra.json.gz" --new "$HERE/panel/panel.json.gz" \
  --noasha "$HERE/noasha74_ids.json" --out "$WORK/READOUT_panel.json" > /dev/null

python3 - "$WORK/READOUT_panel.json" "$HERE/results/READOUT_panel.json" <<'PY'
import json, sys
def flat(x, p=""):
    if isinstance(x, dict):
        for k, v in x.items():
            yield from flat(v, f"{p}.{k}")
    elif isinstance(x, list):
        for i, v in enumerate(x):
            yield from flat(v, f"{p}[{i}]")
    elif isinstance(x, (int, float)) and not isinstance(x, bool):
        yield p, x
new, ref = (dict(flat(json.load(open(f)))) for f in sys.argv[1:3])
bad = [k for k in ref if k not in new or abs(new[k] - ref[k]) > 1e-9]
print(f"READOUT_panel.json: {len(ref)} numeric fields compared, {len(bad)} differ")
sys.exit(1 if bad else 0)
PY
