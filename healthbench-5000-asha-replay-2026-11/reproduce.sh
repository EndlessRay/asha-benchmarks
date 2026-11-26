#!/usr/bin/env bash
# Recompute the replay readouts from this folder, the September files already in this repository and the public
# HealthBench data, then compare every numeric field with results/. Checks MANIFEST.json first.
# Needs python3 and curl. Usage: bash reproduce.sh
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

BLOB=https://openaipublic.blob.core.windows.net/simple-evals/healthbench
curl -sSL -o "$WORK/hard.jsonl" "$BLOB/hard_2025-05-08-21-00-10.jsonl"

FROZEN="$ROOT/healthbench-reference-rendering-2026-10-31/frozen-5000"
mkdir -p "$WORK/arena" "$WORK/replay"
gunzip -c "$FROZEN/eval_a3_4500.jsonl.gz" > "$WORK/arena/eval_a3_4500.jsonl"
gunzip -c "$FROZEN/eval_delta500.jsonl.gz" > "$WORK/arena/eval_delta500.jsonl"
for f in "$FROZEN"/verdicts/*.verdicts.jsonl.gz; do
  b="$(basename "$f" .verdicts.jsonl.gz)"
  mkdir -p "$WORK/arena/runs/${b%%__*}/${b#*__}"
  gunzip -c "$f" > "$WORK/arena/runs/${b%%__*}/${b#*__}/verdicts.jsonl"
done
for f in "$HERE"/arm-a-first200/*.jsonl.gz "$HERE"/arm-b/*.jsonl.gz; do
  gunzip -c "$f" > "$WORK/replay/$(basename "$f" .gz)"
done
gunzip -c "$HERE/harness-check/sept_check100_points.jsonl.gz" > "$WORK/check.jsonl"

python3 "$HERE/scripts/points_readout.py" --arena "$WORK/arena" --hard "$WORK/hard.jsonl" --replay "$WORK/replay" \
  --check "$WORK/check.jsonl" --out "$WORK/READOUT_points.json" > /dev/null

PANEL="$ROOT/healthbench-5000-2026-09-20/vishwanath-500-panel"
python3 "$HERE/scripts/panel_readout.py" --sept "$PANEL/panel_asha-apex-j-frozen.json.gz" \
  --astra "$PANEL/panel_bare-gpt-6-astra.json.gz" --new "$HERE/panel-74/panel.json.gz" --swap \
  --out "$WORK/READOUT_panel74.json" > /dev/null

python3 - "$WORK" "$HERE/results" <<'PY'
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
rc = 0
for name in ("READOUT_points.json", "READOUT_panel74.json"):
    new = dict(flat(json.load(open(f"{sys.argv[1]}/{name}"))))
    ref = dict(flat(json.load(open(f"{sys.argv[2]}/{name}"))))
    keys = [k for k in ref if k in new]
    bad = [k for k in keys if abs(new[k] - ref[k]) > 1e-9] + [k for k in ref if k not in new]
    print(f"{name}: {len(keys)} numeric fields compared, {len(bad)} differ")
    rc |= bool(bad)
sys.exit(rc)
PY
