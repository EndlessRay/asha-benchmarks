# HealthBench 5,000: replay with Asha's late draft (Nov 2026)

In the frozen Apex-J run of 20 to 22 September 2026 (`../healthbench-5000-2026-09-20/`), Asha's draft arrived after
the composer's 12 s wait on 969 of the 5,000 conversations. This pre-registered replay composes 968 of those answers
again with the frozen code (tag `freeze-2026-09-20`), with Asha's draft included, and grades them the way the
published numbers were graded. The plan and decision rule are in `PREREGISTRATION.md`, written before any replay
answer was generated.

## Result

Including Asha's draft changes no published number by more than 0.1 point.

| Published row | Grader and metric | As run | With Asha's draft | Change (95% CI) |
|---|---|---:|---:|---|
| All 5,000, length-adjusted | GPT-4.1, reference rendering | 63.56 | 63.63 | +0.07 (-0.12 to +0.25) |
| All 5,000, unadjusted | GPT-4.1, reference rendering | 65.46 | 65.55 | +0.09 (-0.09 to +0.28) |
| Apex-J minus GPT-6 Astra alone, all 5,000, length-adjusted | same | +7.38 | +7.45 | |
| HealthBench Hard, length-adjusted | same | 46.83 | 46.74 | -0.08 (-0.63 to +0.46) |
| HealthBench Hard, unadjusted | same | 48.72 | 48.67 | -0.05 (-0.59 to +0.49) |
| Harm criteria met, all 5,000 / Hard | same | 20.28% / 23.81% | 20.20% / 23.76% | |
| Vishwanath et al. 500 | the study's three-judge panel, pooled | 63.77 | 63.81 | +0.04 |
| Apex-J minus GPT-6 Astra alone, Vishwanath et al. 500 | same | +8.88 | +8.91 | |

## Reproduce

```bash
bash reproduce.sh
```

It checks every file against `MANIFEST.json`, recomputes both readouts from this folder, the September files and the
public HealthBench data, and exits non-zero on any difference. It also reproduces the published September numbers
(65.46, 63.56, 48.72, 46.83, 65.73, 63.79; panel 63.77 and 54.90) exactly.

## Checks

- Fidelity: replayed without Asha's draft, the first 200 rows scored 0.17 points below September (-1.89 to +1.54).
- Grading lane: re-grading 100 September answers agreed with the published penalty verdicts on 94.6% of criteria
  (kappa 0.82).
- No failed grader calls; every panel criterion has three clean votes.

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
| `reproduce.sh` | Checks the manifest and recomputes both readouts |

## Notes

- One of the 969 rows has no stored drafts and stays as run.
- Effect on the 968 replayed rows (arm B minus September, GPT-4.1, reference rendering): +0.47 (bootstrap -0.49 to
  +1.42); length-adjusted +0.35 (-0.62 to +1.29). On the 74 Vishwanath et al. rows under the panel: +0.26 pooled
  (-2.29 to +2.79), -0.27 as a mean of per-row scores.
- The first-pass grades (`*_gpt41_graded`, criterion text only) gave +1.09 (t-based -0.12 to +2.30); the published
  metric re-grades penalty criteria with the reference rendering.
- The panel drafts that the composer read are not published; they carry internal instructions. Answers, rubric
  verdicts and scores are complete.
