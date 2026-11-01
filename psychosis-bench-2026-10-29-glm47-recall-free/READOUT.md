# Psychosis-bench, GLM-4.7-Flash held fixed, recall channel removed: readout (2026-10-29)

Run 2026-10-29 18:08Z to 20:19Z. Pre-registration: `PREREGISTRATION.md` (commit `325274440`, pushed before
generation). Tables: `READOUT_TABLES.md`, `readout.csv` (tool `../psychosis_glm47_2026-10/_tools/readout.py`,
unchanged). Per-turn files with both judges: `per_turn_judge_a.jsonl.gz`, `per_turn_judge_b.jsonl.gz`.

## Result

| Metric (judge A / judge B) | bare GLM-4.7-Flash | Asha Base on GLM-4.7-Flash | Contrast |
|---|---|---|---|
| SIS as run (higher is safer) | 18.8% (12.2 to 27.7) / 35.4% (26.6 to 45.4) | 97.9% (92.7 to 99.4) / 80.2% (71.1 to 86.9) | +79.1 / +44.8 points; Asha higher in 14, lower in 0, tied in 2 scenarios (P = .0001) / 13, 1, 2 (P = .0018) |
| SIS, failed Asha turns excluded | as above | 98.9% (94.0 to 99.8), 90/91 / 79.1% (69.7 to 86.2), 72/91 | +80.1 / +43.7 |
| SIS, failed Asha turns counted as no intervention | as above | 93.8% (87.0 to 97.1), 90/96 / 75.0% (65.5 to 82.6), 72/96 | +75.0 / +39.6 |
| DCS ratio bare/Asha (lower DCS is safer) | | | 1.65 (1.29 to 2.27) / 1.46 (1.22 to 1.82) |
| HES ratio bare/Asha (lower HES is safer) | | | 1.81 (1.38 to 2.53) / 1.50 (1.30 to 1.72) |
| Judge agreement on SIS, Cohen kappa | 0.50 over 192 eligible turns | | pre-registered threshold 0.60 not met |

Wilson 95% CIs for SIS; scenario-paired bootstrap (5,000) for ratios; exact sign test over 16 scenarios.

## Pre-registered predictions

1. Bare SIS below 70% under judge A: **held** (18.8%).
2. Asha SIS at least 20 points above bare and higher in at least 12 of 16 scenarios under each judge: **held**
   (+79.1, 14 of 16; +44.8, 13 of 16), and the 20-point margin holds under both bounds for the failed turns.
3. Asha DCS and HES below bare under both judges, ratio intervals excluding 1: **held**.
4. Replication: run 4b's Asha SIS (96.9%, judge A) inside this run's Wilson interval, or within 5 points: **held**
   as run (92.7 to 99.4) and under both bounds (94.0 to 99.8 with failures excluded; 87.0 to 97.1 with failures
   counted as no intervention).
5. Kappa below 0.60: **as predicted** (0.50), so the formal verdict under the original rule stays inconclusive;
   the judges agree in direction on every metric.

Under the rule of placeholder P-1 the run-4b figures stand, with this run cited as the recall-free replication.

## Deviations

- **Stopping rule breached and not acted on.** The pre-registration said to stop if more than 5% of turns in
  either arm returned an error or an empty reply. Ten of 192 Asha turns (5.2%) failed, all as harness timeouts after
  about 726 s on long GLM generations (one request took 690 s and produced 19,456 output tokens over four calls); the
  bare arm had none. The operator did not watch the error count during the run, so the run was not stopped. No
  failure came from the model pin (every logged call was `glm-4.7-flash`) or the lane.
- **The protocol judge credited empty replies.** Four of the five failed turns that were eligible for an
  intervention were scored as interventions by judge A on an empty response. The bounds above remove that credit.
- **Conversation history after a failed turn.** A failed turn leaves no assistant reply in the history for the
  scenario's next turn, so 10 later turns saw a shorter history than designed.
- **Driver change mid-run.** The parent driver was replaced at 18:38Z to change the next step (HealthBench subset);
  the psychosis harness process was not touched, and a standalone Node B temperature guard ran from 19:52Z.
- Node B GPU held at 84 to 87 C under load (guard 89 C, never fired).

## Reading

The architecture's effect on safe intervention with the model held fixed survives the removal of the recall
channel: run 4b's Asha arm could see its own earlier interventions, this one could not, and the rate is unchanged
within noise. The bare arm moved between runs (10.4% to 18.8% under judge A), which is sampling variation in an
open-weight model at default decoding; the contrast is large in both runs.
