#!/usr/bin/env bash
# Recompute the frozen-pair HealthBench readout (Apex-J vs GPT-6 Astra alone, 5,000 conversations) from the
# files in this folder and the public HealthBench data, then compare with results/frozen_pair_points.json.
# Needs python3 and curl. Usage: bash reproduce.sh
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

BLOB=https://openaipublic.blob.core.windows.net/simple-evals/healthbench
curl -sSL -o "$WORK/hard.jsonl" "$BLOB/hard_2025-05-08-21-00-10.jsonl"
curl -sSL -o "$WORK/oss_eval.jsonl" "$BLOB/2025-05-07-06-14-12_oss_eval.jsonl"

mkdir -p "$WORK/arena"
gunzip -c "$HERE/frozen-5000/eval_a3_4500.jsonl.gz" > "$WORK/arena/eval_a3_4500.jsonl"
gunzip -c "$HERE/frozen-5000/eval_delta500.jsonl.gz" > "$WORK/arena/eval_delta500.jsonl"
for f in "$HERE"/frozen-5000/verdicts/*.verdicts.jsonl.gz; do
  b="$(basename "$f" .verdicts.jsonl.gz)"
  mkdir -p "$WORK/arena/runs/${b%%__*}/${b#*__}"
  gunzip -c "$f" > "$WORK/arena/runs/${b%%__*}/${b#*__}/verdicts.jsonl"
done

python3 "$HERE/scripts/frozen_pair_points.py" --arena "$WORK/arena" --hard "$WORK/hard.jsonl" \
  --oss "$WORK/oss_eval.jsonl" --hbp-score "$HERE/scripts/hbp_score.py" --out "$WORK/frozen_pair_points.json"

python3 - "$WORK/frozen_pair_points.json" "$HERE/results/frozen_pair_points.json" <<'PY'
import json, sys
def flat(x, p=""):
    if isinstance(x, dict):
        for k, v in x.items():
            yield from flat(v, f"{p}.{k}")
    elif isinstance(x, (int, float)) and not isinstance(x, bool):
        yield p, x
new, ref = (dict(flat(json.load(open(f)))) for f in sys.argv[1:3])
keys = [k for k in ref if k in new and "utc" not in k.lower()]
bad = [k for k in keys if abs(new[k] - ref[k]) > 1e-9]
print(f"{len(keys)} numeric fields compared, {len(bad)} differ")
sys.exit(1 if bad else 0)
PY
