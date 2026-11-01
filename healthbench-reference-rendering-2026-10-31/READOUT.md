# Readout: reference rubric rendering for every arm in the benchmarks paper (2026-10-31)

Pre-registration: `PREREGISTRATION.md` (commit `1b3bf35dc`, 21:28 ET), amendment 1 (`54cc0c8cd`, 21:31 ET).
Grading 01:32 to 01:52 UTC, 1 Nov 2026, on the 5090 (`/home/deepan/audits/points_regrade_1031/`).

## Runs

| Lane | Grader | Criteria graded | Failed calls |
|---|---|---:|---:|
| HealthBench June tiers | GPT-4.1 | 11,968 | 0 |
| HealthBench Professional board, 25 runs | GPT-5.4, reasoning low | 5,324 | 0 |
| HealthBench Professional, 8 runs | Claude Opus 4.8 | 1,703 | 20 (worst run 3 of 213, 1.4%) |

No run exceeded the 2% failure rule. Failed calls are excluded item by item, as in `hbp_score.py`.

## Validation (as-run reproduction)

Every arm's as-run grade file, scored by the same code, reproduces the published figure: frozen Apex-J and
GPT-6 Astra on HealthBench (all 5,000 60.7 vs 52.7; Hard 42.0 vs 29.4; length-adjusted 58.8 vs 53.2 and 40.1 vs
30.1; 500-item sample 61.6 vs 53.2; better/worse counts and axis deltas); June tiers (Base 28.3, Mid 37.9, Apex
44.8; Mid vs Base +9.7; Apex vs Mid +6.6, 449/309/140); HealthBench Professional (all 525 68.8 vs 64.8, P 0.0014;
Opus 4.8 72.7 vs 67.3; holdout 67.9 vs 65.7, P 0.23; Opus holdout +4.6, P 0.03; slice +5.3, P 0.002).
P values for HealthBench rows differ from the earlier readouts in the second significant figure; every P value in
the paper now comes from `frozen_pair_points.py`.

## Results (reference rendering)

| Comparison | Model alone | Asha | Difference (95% CI) | P |
|---|---:|---:|---|---|
| HealthBench Hard, length-adjusted | 33.1 | 46.8 | +13.7 (12.0 to 15.4) | 1.5e-49 |
| HealthBench Hard, unadjusted | 32.4 | 48.7 | +16.3 (14.6 to 18.1) | 3.8e-64 |
| HealthBench all 5,000, length-adjusted | 56.2 | 63.6 | +7.4 (6.8 to 8.0) | 2.1e-111 |
| HealthBench all 5,000, unadjusted | 55.6 | 65.5 | +9.8 (9.2 to 10.5) | 9.7e-181 |
| Vishwanath et al. 500, length-adjusted | 56.6 | 63.8 | +7.2 (5.3 to 9.1) | 3.2e-13 |
| Vishwanath et al. 500, unadjusted | 56.5 | 65.7 | +9.2 (7.2 to 11.2) | 1.0e-18 |
| Professional all 525, GPT-5.4 | 65.3 | 69.6 | +4.3 (1.8 to 6.7) | 6.5e-4 |
| Professional all 525, Opus 4.8 | 68.6 | 73.9 | +5.3 (2.9 to 7.8) | 2e-5 |
| Professional holdout 225, GPT-5.4 | 65.9 | 68.6 | +2.7 (-0.8 to 6.2) | 0.13 |
| Professional holdout 225, Opus 4.8 | 69.2 | 74.0 | +4.8 (1.1 to 8.5) | 0.012 |
| Professional slice 300, GPT-5.4 | 64.9 | 70.4 | +5.5 (2.1 to 8.9) | 0.0017 |
| Professional all 524, Asha Base vs Claude Sonnet 5, GPT-5.4 | 54.0 | 53.0 | -1.1 (-4.9 to 2.7) | 0.57 |

June tiers on Hard (GPT-4.1, unadjusted): Base 29.9, Mid 41.8, Apex 51.4; Mid vs Base +12.2 (P 2.6e-29); Apex vs
Mid +9.1 (472 better, 269 worse, 157 tied; P 8.2e-14).

Harm (penalty criteria met, pooled): all 5,000 Asha 20.3% vs 20.8%; Hard 23.8% vs 27.9%. Severe agreement on Hard
(GPT-4.1 with points, GPT-5.4 and Opus 4.8 as run): Asha-only 2, model-alone-only 17 (sign P 0.0007).

HealthBench Professional holdout board (GPT-5.4): Asha Apex-J 68.6; GPT-6 Astra 65.9; GPT-5.6 Sol 59.4; Claude
Opus 5 55.2; Claude Sonnet 5 54.6; Claude Fable 5.1 53.1; GPT-5.6 Luna 52.9; Asha P6 52.7; Asha Base 52.1; Gemini
3.8 Flash 50.1; Claude Opus 4.8 49.7; Glass Health 5.5 43.8; Gemini 3.1 Pro 40.1; Claude Sonnet 4.6 39.4
(`results/fig_head_to_head_professional_holdout.jsonl`). Opus 4.8 on all 525: physician-written answers 50.1,
Glass Health 5.5 46.2.

## Deviations

1. Asha Base vs Claude Sonnet 5 on Professional: the paper's earlier value (+0.3, P 0.88, "one grader") does not
   reproduce from the archived files, which give -0.4 (P 0.83) as run under GPT-5.4. The paper reports the
   reference-rendering readout (-1.1, P 0.57) like every other row; red-team difference +7.4 (P 0.07).
2. GLM-5.2 on Hard (June 2026): answers not archived (the `glm_local_202610` file is GLM-4.7-Flash); dropped from
   Table 2 and Fig. 4, as pre-registered.

## Files

- `results/frozen_pair_points.json`, `results/june_tiers_points.json`, `results/hbp_readouts/*.json`
- Merged per-item grade files stay on the 5090 (`merged/`, `hbp_root/`); HealthBench Professional per-item data are
  not published, per its dataset card.
