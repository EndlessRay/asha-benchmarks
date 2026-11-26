# Psychosis-bench, GLM-4.7-Flash held fixed, evaluation flag off (26 Nov 2026)

In the earlier psychosis-bench runs of Asha's single-pass tier, each Asha request carried an evaluation flag that
adds a short directive to the prompt (the request is a benchmark prompt whose audience may be a grader). The model
alone received no such text. This pre-registered run repeats the 29 October GLM-4.7-Flash pair
(`../psychosis-bench-2026-10-29-glm47-recall-free/`) with the flag off and nothing else changed: same weights,
server, Asha code, harness and judges. The plan and predictions are in `PREREGISTRATION.md`, pushed before
generation.

## Result

| Safe-intervention rate (SIS), judge A / judge B | GLM-4.7-Flash alone | Asha on GLM-4.7-Flash, flag off |
|---|---|---|
| As run | 17.7% / 36.5% | 96.9% / 81.2% |
| Failed Asha turns counted as no intervention | | 92.7% / 78.1% |

Asha was higher in 14 of 16 scenarios under each judge (sign test P = .0001 and .0010). With the flag on
(29 October) Asha scored 97.9% under judge A. All five pre-registered predictions held; the flag does not explain
the held-model lift. Judge A is `gpt-4o-mini` (the protocol judge), judge B `claude-haiku-4-5`; their agreement on
SIS was κ = 0.37, below the 0.60 the original protocol requires, so the formal verdict under that rule stays
inconclusive, as in every earlier run. Full tables: `READOUT_TABLES.md`, `readout.csv`.

## Reproduce

```bash
bash reproduce.sh
```

It recomputes `readout.csv` from the two per-turn files with the unchanged October readout tool
(`../psychosis-bench-2026-10-28-glm47/_tools/readout.py`) and exits non-zero on any difference.

## Contents

| Path | What it is |
|---|---|
| `PREREGISTRATION.md` | Plan, predictions and stopping rules, pushed before generation |
| `per_turn_judge_a.jsonl.gz`, `per_turn_judge_b.jsonl.gz` | Every turn of both arms with both judges' scores and rationales |
| `READOUT_TABLES.md`, `readout.csv` | Per-arm and per-judge tables |
| `run_flagoff.py` | The wrapper that sets the flag off and runs the unchanged harness |
| `reproduce.sh` | Recomputes the readout |

## Notes

- The flag was verified off: the Asha server logs a line whenever it adds the directive; a flag-on smoke turn
  logged it, and the run logged it 0 times.
- 6 of 192 Asha turns failed (5 eligible); no bare turn failed.
- Seven responses of the Asha arm repeated parts of the system's own instructions and are withheld in full in both
  per-turn files (lines 185, 200, 215, 233, 268, 298 and 372; each row is marked). The scores were computed on the
  full responses and are unchanged. Four of the seven are eligible turns judge A credited as interventions; scoring
  those and the failed turns as no intervention gives 85 of 96 (88.5%).
- The readout tool reads the Asha arm under the label `asha_glm`; `reproduce.sh` renames `asha_glm_flagoff` in a
  temporary copy and changes nothing else.
