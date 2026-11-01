# HealthBench with OpenAI's reference rubric rendering (re-grade of 31 Oct 2026)

OpenAI's reference grader (simple-evals) shows GPT-4.1 each rubric criterion with its point value, for example
`[-8] Fails to mention X`. Our harness first showed the criterion text alone. Without the point value GPT-4.1 marks
some omission criteria as met when the answer contains the content, more often on longer answers. Every arm in the
Asha benchmarks preprint (Research Square rs-10206806, v2) was re-graded on its penalty criteria with the reference
rendering, under a pre-registered plan; positive verdicts were kept, because the rendering leaves them unchanged
(96.1% agreement, kappa 0.906). Every rubric score in v2 comes from these files.

## Contents

| Path | What it is |
|---|---|
| `PREREGISTRATION.md` | Plan, arms, settings and decision rule, committed before grading, with amendment 1 |
| `READOUT.md` | Results, failure counts and the as-run reproduction check |
| `frozen-5000/` | Frozen Apex-J and GPT-6 Astra alone on all 5,000 conversations: inputs (`eval_*.jsonl.gz`: prompt, answer, rubric, as-run verdicts) and the GPT-4.1 penalty re-grade verdicts (`verdicts/`) |
| `june-tiers-hard/` | June 2026 Asha Base, Mid and Apex on HealthBench Hard: merged per-item grades (as-run positives, re-graded penalties) |
| `harm-gate-5000/` | Harm-criteria comparison on all 5,000 conversations under the reference rendering |
| `results/` | `frozen_pair_points.json`, `june_tiers_points.json`; HealthBench Professional readouts (aggregates only) |
| `scripts/` | Re-grade driver, merge and readout code; `hbp_score.py` holds the scoring and test functions |
| `reproduce.sh` | Recomputes `results/frozen_pair_points.json` from this folder and the public HealthBench data |

HealthBench Professional per-item data are withheld: the dataset card asks users not to reveal its examples
online. Its rows here are aggregate readouts.

## Reproduce

```bash
bash reproduce.sh
```

On 1 Nov 2026 this compared 130 numeric fields with `results/frozen_pair_points.json` and found no difference.

## Headline numbers (GPT-4.1 grader, reference rendering)

| Set | GPT-6 Astra alone | Asha Apex-J | Difference |
|---|---:|---:|---:|
| HealthBench Hard, length-adjusted | 33.1 | 46.8 | +13.7 (12.0 to 15.4) |
| HealthBench Hard, unadjusted | 32.4 | 48.7 | +16.3 (14.6 to 18.1) |
| All 5,000, length-adjusted | 56.2 | 63.6 | +7.4 |
| All 5,000, unadjusted | 55.6 | 65.5 | +9.8 |
| Hard, share of penalty criteria met (harm) | 27.9% | 23.8% | -4.1 points |
| Hard, conversations where all three graders flagged a severe harm in one arm only | 17 | 2 | sign test P = 0.0007 |
