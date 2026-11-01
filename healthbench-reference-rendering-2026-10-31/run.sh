#!/usr/bin/env bash
set -u
cd /home/deepan/audits/points_regrade_1031
PY=/home/deepan/Citadel/.venv/bin/python
export OPENAI_API_KEY="$(grep '^OPENAI_API_KEY=' /home/deepan/Citadel/.env | head -1 | cut -d= -f2- | tr -d '\r"')"
export ANTHROPIC_API_KEY="$(grep '^ANTHROPIC_API_KEY=' /home/deepan/Citadel/.env | head -1 | cut -d= -f2- | tr -d '\r"')"
lane="$1"
run() {
  local n="$1" m="$2"; shift 2
  echo "$(date -u +%FT%TZ) start $n $m" >> logs/lane_$lane.log
  $PY drive.py --grader grader.py --input in/$n.jsonl --output out/$n.jsonl --model "$m" "$@" >> logs/$n.log 2>&1
  local rc=$?
  echo "$(date -u +%FT%TZ) done $n rc=$rc $(tail -n 1 logs/$n.log)" >> logs/lane_$lane.log
  [ $rc -eq 2 ] && { echo "$(date -u +%FT%TZ) STOP failures" >> logs/lane_$lane.log; exit 2; }
}
case "$lane" in
  gpt41) for n in hb_june_base hb_june_mid hb_june_apex; do run $n gpt-4.1 --sample-concurrency 12; done ;;
  gpt54) for f in in/hbp_*__gpt_5_4.jsonl; do n=$(basename "$f" .jsonl); run "$n" gpt-5.4 --reasoning-effort low --sample-concurrency 10; done ;;
  opus)  for d in full_L9_concise_t1 full_L9_concise_t2 full_L9_concise_t3 bare_gpt6astra_t1 bare_gpt6astra_t2 bare_gpt6astra_t3 physician bare_glass55_t1; do run hbp_${d}__claude_opus_4_8 claude-opus-4-8 --sample-concurrency 6; done ;;
esac
echo "$(date -u +%FT%TZ) LANE_DONE" >> logs/lane_$lane.log
