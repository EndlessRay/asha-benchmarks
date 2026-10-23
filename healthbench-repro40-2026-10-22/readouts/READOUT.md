# Reproducibility run readout: 40 seeded random HealthBench items (seed-62 500 subsample), every arm on freeze asha-base-v3-2026-10-19

Grader of record gpt-4.1; Claude Opus 4.8 sensitivity. n is small by design: SE about 4 to 5 points per arm, so only large gaps resolve. The replication rows are the point: the same frozen build on the same items should land inside noise of its October record.

| Arm | n | gpt-4.1 [95% CI] | harm % | Opus 4.8 | median chars | median s | $/answer | empty |
|---|---|---|---|---|---|---|---|---|
| apex_a | 40 | 67.1 [60.8, 73.6] | 23.8 | 74.2 | 2816.0 | 111.5 | n/a | 0 |
| apex_b | 40 | 68.9 [60.9, 76.6] | 26.5 | 77.3 | 5416.0 | 67.2 | n/a | 0 |
| bare_low | 40 | 59.5 [52.1, 66.9] | 29.9 | 68.7 | 2120.5 | 7.2 | n/a | 0 |
| bare_max | 40 | 62.2 [55.0, 70.1] | 31.3 | 70.2 | 2163.5 | 26.3 | n/a | 0 |
| base | 40 | 59.7 [53.3, 66.2] | 32.7 | 63.8 | 4544.0 | 38.4 | 0.067 | 0 |
| mid | 40 | 58.2 [49.6, 66.5] | 24.5 | 59.9 | 3799.0 | 80.3 | 0.056 | 4 |

## References on the same items (gpt-4.1, per-item grades from the record)

| Reference | n | mean |
|---|---|---|
| oct_base | 40 | 63.1 |
| oct_bare_low | 40 | 62.2 |
| oct_bare_max | 40 | 63.6 |
| sept_apexj | 40 | 62.2 |
| sept_bare_astra | 40 | 56.3 |

## Replication: same build, same items, fresh generation vs the October record (gpt-4.1)

| Pair | n | diff [95% CI] | W/L/T |
|---|---|---|---|
| base (replicate) minus oct_base | 40 | -3.4 [-7.2, +0.1] | 7/19/14 |
| bare_low (replicate) minus oct_bare_low | 40 | -2.6 [-7.9, +2.2] | 10/18/12 |
| bare_max (replicate) minus oct_bare_max | 40 | -1.4 [-6.0, +3.3] | 10/15/15 |

## Pairwise arm comparisons (A minus B, raw points)

| Pair | n | diff [95% CI] | W/L/T |
|---|---|---|---|
| apex_a minus apex_b [gpt_4_1] | 40 | -1.8 [-8.4, +4.6] | 14/16/10 |
| apex_a minus apex_b [claude_opus_4_8] | 40 | -3.0 [-9.3, +3.3] | 12/17/11 |
| apex_a minus base [gpt_4_1] | 40 | +7.4 [+2.3, +12.8] | 22/11/7 |
| apex_a minus base [claude_opus_4_8] | 40 | +10.5 [+3.4, +18.0] | 25/8/7 |
| apex_b minus base [gpt_4_1] | 40 | +9.2 [+1.9, +16.7] | 27/9/4 |
| apex_b minus base [claude_opus_4_8] | 40 | +13.5 [+7.6, +19.9] | 26/2/12 |
| mid minus base [gpt_4_1] | 40 | -1.5 [-9.9, +6.7] | 18/13/9 |
| mid minus base [claude_opus_4_8] | 40 | -3.9 [-14.4, +6.2] | 20/13/7 |
| apex_a minus bare_max [gpt_4_1] | 40 | +4.9 [-3.0, +12.4] | 20/11/9 |
| apex_a minus bare_max [claude_opus_4_8] | 40 | +4.0 [-1.8, +9.3] | 22/9/9 |
| apex_b minus bare_max [gpt_4_1] | 40 | +6.7 [-0.1, +13.7] | 21/9/10 |
| apex_b minus bare_max [claude_opus_4_8] | 40 | +7.1 [+1.0, +13.1] | 20/8/12 |
| mid minus bare_max [gpt_4_1] | 40 | -4.0 [-15.2, +5.8] | 17/12/11 |
| mid minus bare_max [claude_opus_4_8] | 40 | -10.3 [-21.9, -0.1] | 15/19/6 |
| base minus bare_low [gpt_4_1] | 40 | +0.2 [-6.6, +7.0] | 14/15/11 |
| base minus bare_low [claude_opus_4_8] | 40 | -5.0 [-11.7, +2.1] | 12/18/10 |
| bare_max minus bare_low [gpt_4_1] | 40 | +2.6 [-2.0, +8.1] | 14/14/12 |
| bare_max minus bare_low [claude_opus_4_8] | 40 | +1.5 [-3.2, +6.4] | 14/12/14 |
| apex_a minus sept_apexj [gpt_4_1] | 40 | +4.9 [-1.5, +11.3] | 16/13/11 |
| apex_a minus sept_bare_astra [gpt_4_1] | 40 | +10.8 [+4.4, +17.8] | 18/10/12 |
| apex_b minus sept_apexj [gpt_4_1] | 40 | +6.7 [+1.0, +12.4] | 19/13/8 |
| apex_b minus sept_bare_astra [gpt_4_1] | 40 | +12.6 [+4.7, +20.7] | 23/10/7 |
| mid minus sept_apexj [gpt_4_1] | 40 | -4.0 [-14.0, +5.0] | 16/16/8 |
| mid minus sept_bare_astra [gpt_4_1] | 40 | +1.9 [-7.7, +11.4] | 18/17/5 |
| base minus sept_apexj [gpt_4_1] | 40 | -2.5 [-8.5, +3.0] | 13/18/9 |
| base minus sept_bare_astra [gpt_4_1] | 40 | +3.4 [-2.7, +9.3] | 21/14/5 |
