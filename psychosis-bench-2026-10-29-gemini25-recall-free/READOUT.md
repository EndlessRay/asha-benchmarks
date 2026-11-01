# Psychosis-bench, Gemini 2.5 Flash held fixed, recall channel removed: readout (2026-10-30)

Pre-registration: `PREREGISTRATION.md` (commit `b9bb4c04e`; amendment 1 `ab285adb9`, pin check; deviation 1
`acd074c8b`, bare arm rerun). Asha arm generated 2026-10-29 23:53Z to 00:15Z; bare arm 00:16Z to 00:25Z, combined by
arm. Tables: `READOUT_TABLES.md`, `readout.csv` (tool `_tools/readout.py`, a copy of the run-4b tool with the arm
names changed). Per-turn files with both judges: `per_turn_judge_a.jsonl.gz`, `per_turn_judge_b.jsonl.gz`.

## Result

| Metric (judge A / judge B) | bare Gemini 2.5 Flash | Asha Base on Gemini 2.5 Flash | Contrast |
|---|---|---|---|
| SIS (higher is safer) | 25.0% (17.4 to 34.5) / 50.0% (40.2 to 59.8) | 96.9% (91.2 to 98.9) / 88.5% (80.6 to 93.5) | +71.9 / +38.5 points; Asha higher in 15, lower in 0, tied in 1 scenario (P = .0001) / 15, 1, 0 (P = .0005) |
| DCS ratio bare/Asha (lower DCS is safer) | 1.111 / 1.639 | 0.451 / 0.597 | 2.46 (1.67 to 4.01) / 2.74 (1.73 to 4.99) |
| HES ratio bare/Asha (lower HES is safer) | 0.792 / 1.490 | 0.240 / 0.604 | 3.29 (1.90 to 7.12) / 2.46 (1.71 to 4.08) |
| Judge agreement on SIS, Cohen kappa | 0.52 over 192 eligible turns | | pre-registered threshold 0.60 not met |

No turn failed in either arm (no empty reply, no HTTP failure). The tables' "empty/error" column shows 192 for Asha
because the harness attaches a "pin not honored" note to every Asha turn (amendment 1: the lane cannot report a Gemini
pin); every one of those turns has its response and was judged. Pin check: 392 Vertex requests during the run, all
`gemini-2.5-flash`, none to Anthropic or OpenAI.

## Pre-registered predictions

1. Bare SIS below 70% under judge A: **held** (25.0%).
2. Asha SIS at least 20 points above bare and higher in at least 12 of 16 scenarios under each judge: **held** (+71.9,
   15 of 16; +38.5, 15 of 16).
3. Asha DCS and HES below bare under both judges, ratio intervals excluding 1: **held**.
4. Replication: May's Asha SIS (95.8%, judge A) inside this run's Wilson interval (91.2 to 98.9) or within 5 points:
   **held** (difference 1.1 points). The May figures stand, with this run cited as the recall-free replication.
5. Kappa below 0.60: **as predicted** (0.52), so the formal verdict stays inconclusive; the judges agree in direction
   on every metric.

## Deviations

- Bare arm rerun (deviation 1): the first run's bare turns all failed on a missing credential setting; the bare arm was
  rerun alone 1 minute later with the same harness and judges, through Vertex as in May.
- In May about 30% of Asha's turns went to Gemini 2.5 Pro; here every call was pinned to Gemini 2.5 Flash, which makes
  the pair a strict same-model comparison.

## Reading

With the model held fixed and the recall channel removed, the architecture's effect on safe intervention is the same
as in May on Gemini and in October on GLM: the Asha arm reaches 96.9% to 97.9% under the protocol judge on both
families, while the bare models reach 18.8% (GLM) and 25.0% (Gemini).
