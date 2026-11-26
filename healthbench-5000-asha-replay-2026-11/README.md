# HealthBench 5,000: replay of the rows where Asha's draft arrived late (Nov 2026)

In the frozen Apex-J run of 20 to 22 September 2026 (`../healthbench-5000-2026-09-20/`), the composer waited 12 s
for straggling panel drafts. Asha's draft missed that wait on 969 of the 5,000 conversations, and the composer
wrote those answers from the other drafts. The drafts of 968 of those rows were stored. This replay composes the
968 rows again from the stored drafts with the frozen code (tag `freeze-2026-09-20`), with Asha's draft
included, and grades them the way the published numbers were graded. The plan, its amendments and the decision rule
are in `PREREGISTRATION.md`, written before any replay answer was generated.

## Result

Asha's late draft moves no published September number by more than 0.1 point, and no change is distinguishable
from zero.

| Published row | Grader and metric | As run | Corrected | Change (95% CI) |
|---|---|---:|---:|---|
| All 5,000, length-adjusted | GPT-4.1, reference rendering | 63.56 | 63.63 | +0.07 (-0.12 to +0.25) |
| All 5,000, unadjusted | GPT-4.1, reference rendering | 65.46 | 65.55 | +0.09 (-0.09 to +0.28) |
| Apex-J minus GPT-6 Astra alone, all 5,000, length-adjusted | same | +7.38 | +7.45 | |
| HealthBench Hard, length-adjusted | same | 46.83 | 46.74 | -0.08 (-0.63 to +0.46) |
| HealthBench Hard, unadjusted | same | 48.72 | 48.67 | -0.05 (-0.59 to +0.49) |
| Harm criteria met, all 5,000 / Hard | same | 20.28% / 23.81% | 20.20% / 23.76% | |
| Vishwanath et al. 500 | the study's three-judge panel, pooled | 63.77 | 63.81 | +0.04 |
| Apex-J minus GPT-6 Astra alone, Vishwanath et al. 500 | same | +8.88 | +8.91 | |

Effect of the draft on the replayed rows (arm B minus September), GPT-4.1 with the reference rendering: +0.47 points
on 968 rows (bootstrap 95% CI -0.49 to +1.42; length-adjusted +0.35, -0.62 to +1.29). Under the three-judge panel on
the 74 Vishwanath et al. rows: +0.26 (-2.29 to +2.79); on these rows the mean of per-row scores moves the other way
(-0.27), and neither figure is distinguishable from zero. The first pass of grading, before the penalty criteria were
re-graded with the reference rendering, gave +1.09 (t-based 95% CI -0.12 to +2.30, from the `*_gpt41_graded` files;
`reproduce.sh` does not check it); the reference rendering is the paper's metric.

## Checks

- Reproduction: the September files in this repository, scored by `scripts/points_readout.py`, give the published
  65.46, 63.56, 48.72, 46.83, 65.73 and 63.79 exactly; `scripts/panel_readout.py` gives the published 63.77 and 54.90.
- Fidelity: on the first 200 rows the replay without Asha's draft (arm A) scored 0.17 points below September
  (-1.89 to +1.54), so the replay reproduces the September system.
- Grading lane: 100 September answers (355 penalty criteria) re-graded with this lane agreed with the published
  penalty verdicts on 94.6% of criteria (kappa 0.82; criteria met 18.0% against 18.3%).
- Failed grader calls: none in any arm; no panel criterion without three clean votes.
- One of the 969 rows has no stored drafts and stays as run.

## Contents

| Path | What it is |
|---|---|
| `PREREGISTRATION.md` | Plan with amendments A1 to A3 (A3 pushed 2026-11-25T01:09:16Z, before the extension was generated) |
| `sample_first200_ids.json`, `sample_ext_ids.json` | The 200 sampled rows and the 768 extension rows |
| `arm-a-first200/` | Arm A (September as run, replayed) on the first 200: answers, first-pass GPT-4.1 grades, merged grades with re-graded penalty criteria |
| `arm-b/` | Arm B (with Asha's draft) on all 968 rows, same three files for each part |
| `harness-check/` | The 100 September answers re-graded with this lane's penalty grader |
| `panel-74/` | The study's three-judge panel on arm B for the 74 Vishwanath et al. rows |
| `results/` | `READOUT_points.json` (GPT-4.1) and `READOUT_panel74.json` (panel) |
| `scripts/` | `points_regrade.py` (build and merge), `points_readout.py`, `panel_readout.py`; standard library only |
| `MANIFEST.json` | SHA-256 of every file here, the grader and code identifiers |
| `reproduce.sh` | Checks the manifest and recomputes both readouts from this folder, the September files and the public HealthBench data |

The panel drafts that the composer read are not published; they carry internal instructions. Answers, rubric
verdicts and scores are complete.

## Reproduce

```bash
bash reproduce.sh
```

It prints the number of files and numeric fields compared and exits non-zero on any difference.
