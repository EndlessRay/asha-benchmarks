#!/usr/bin/env bash
# Build a mirror root with merged [points] grade files and rerun hbp_ceiling_readout.py unchanged.
set -eu
W=/home/deepan/audits/points_regrade_1031; H=/home/deepan/Citadel/healthbench_results/hbp_20260911
C=/home/deepan/Citadel; PY=/home/deepan/Citadel/.venv/bin/python; RO=$C/scripts/audits/healthbench_professional/hbp_ceiling_readout.py
FULL=$C/healthbench_data/professional/healthbench_professional_eval.jsonl
cd $W; mkdir -p hbp_root readouts
for d in full_L9_concise_t1 full_L9_concise_t2 full_L9_concise_t3 bare_gpt6astra_t1 bare_gpt6astra_t2 bare_gpt6astra_t3 bare_gpt56sol_t1 bare_gpt56sol_t2 bare_fable51_t1 bare_fable51_t2 bare_opus5_t1 bare_sonnet5_t1 bare_opus48_t1 bare_opus48_t2 bare_gpt56luna_t1 bare_gemini38flash_t1 bare_gemini31pro_t1 bare_glass55_t1 bare_sonnet46_t1 p6_t1 p6_t2 p6_t3 bare_asha_base_s5_t1 bare_asha_base_s5_t2 physician; do
  t=$d; [ "$d" = physician ] && t=physician_t1
  mkdir -p hbp_root/$t
  for f in $H/$d/*; do b=$(basename "$f"); case "$b" in raw_*_graded.jsonl) ;; *) ln -sf "$f" hbp_root/$t/$b ;; esac; done
  for g in gpt_5_4 claude_opus_4_8; do
    if [ -s out/hbp_${d}__${g}.jsonl ]; then
      python3 points_regrade.py merge --graded $H/$d/raw_${g}_graded.jsonl --regraded out/hbp_${d}__${g}.jsonl --out hbp_root/$t/raw_${g}_graded.jsonl
    else
      ln -sf $H/$d/raw_${g}_graded.jsonl hbp_root/$t/raw_${g}_graded.jsonl
    fi
  done
done > logs/hbp_merge.log
ro() { # name root dataset incumbent candidate official sensitivity
  $PY $RO --root $2 --dataset $3 --incumbent $4 --candidate $5 --official $6 --sensitivity $7 --json readouts/$1.json > readouts/$1.txt 2>&1 || echo "readout $1 failed" >> logs/hbp_readouts.err
}
for root in asrun points; do
  R=$H; [ $root = points ] && R=$W/hbp_root
  ro ${root}__full_L9_vs_astra $R $FULL bare_gpt6astra full_L9_concise gpt_5_4 claude_opus_4_8
  ro ${root}__hold_L9_vs_astra $R $H/prof_holdout225.jsonl bare_gpt6astra full_L9_concise gpt_5_4 claude_opus_4_8
  ro ${root}__slice_L9_vs_astra $R $H/prof_slice300.jsonl bare_gpt6astra full_L9_concise gpt_5_4 claude_opus_4_8
  ro ${root}__full_base_vs_sonnet5 $R $FULL bare_sonnet5 bare_asha_base_s5 gpt_5_4 claude_opus_4_8
done
for x in bare_gpt56sol bare_fable51 bare_opus5 bare_sonnet5 bare_opus48 bare_gpt56luna bare_gemini38flash bare_gemini31pro bare_glass55 bare_sonnet46 p6 bare_asha_base_s5; do
  ro points__hold_L9_vs_$x $W/hbp_root $H/prof_holdout225.jsonl $x full_L9_concise gpt_5_4 claude_opus_4_8
done
for x in physician bare_glass55; do
  ro points__full_L9_vs_${x}__opus $W/hbp_root $FULL $x full_L9_concise claude_opus_4_8 gpt_5_4
done
echo HBP_POINTS_DONE >> logs/hbp_merge.log
