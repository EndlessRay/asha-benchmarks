#!/usr/bin/env bash
# Recompute readout.csv from the per-turn files with the unchanged October readout tool.
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
tool="$here/../psychosis-bench-2026-10-28-glm47/_tools/readout.py"
tmp="$(mktemp -d)"
trap 'rm -r "$tmp"' EXIT
gunzip -c "$here/per_turn_judge_a.jsonl.gz" | sed 's/"arm": "asha_glm_flagoff"/"arm": "asha_glm"/' > "$tmp/per_turn.jsonl"
gunzip -c "$here/per_turn_judge_b.jsonl.gz" | sed 's/"arm": "asha_glm_flagoff"/"arm": "asha_glm"/' > "$tmp/per_turn_judge_b.jsonl"
mkdir -p "$tmp/out/_tools"
cp "$tool" "$tmp/out/_tools/readout.py"
(cd "$tmp/out/_tools" && python3 readout.py --run "$tmp" --out "$tmp/out" > /dev/null)
if diff -q "$tmp/out/readout.csv" "$here/readout.csv" > /dev/null; then
  echo "readout.csv: identical"
else
  echo "readout.csv: DIFFERS"; diff "$tmp/out/readout.csv" "$here/readout.csv"; exit 1
fi
