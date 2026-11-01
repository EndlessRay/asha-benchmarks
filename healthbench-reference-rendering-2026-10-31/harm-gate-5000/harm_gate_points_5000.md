# A3 harm gate under the simple-evals rubric rendering

GPT-4.1, production settings. Harm proxy = penalty criteria met / penalty criteria present (pooled). Margin: +2.0. Paired item bootstrap 95% CI over items with every penalty criterion graded for both arms.

| items | n | rubric item | apexj | astra | gap (apexj minus astra) [95% CI] | within margin |
|---|---|---|---|---|---|---|
| all items | 4681 | criterion text only (official on disk) | 29.82% | 26.98% | +2.84 [+2.21, +3.49] | no |
| all items | 4681 | [points] criterion (simple-evals) | 20.28% | 20.77% | -0.50 [-1.05, +0.07] | yes |
| HealthBench Hard items | 997 | criterion text only (official on disk) | 33.99% | 32.37% | +1.62 [+0.22, +3.03] | yes |
| HealthBench Hard items | 997 | [points] criterion (simple-evals) | 23.81% | 27.92% | -4.11 [-5.45, -2.77] | yes |

- all items: change in gap from rendering -3.33 [-4.05, -2.61]
- HealthBench Hard items: change in gap from rendering -5.73 [-7.30, -4.12]

## HealthBench score under each rendering

simple-evals scoring: per-item achieved over positive points, run score = mean clipped to [0, 1]. The rerendered score keeps the official verdicts on positive criteria (rendering does not move them: 96.1% agreement, kappa 0.906) and uses the [points] verdicts on penalty criteria. Items with an ungraded penalty criterion are dropped from both columns.

| items | n | apexj, text only | apexj, [points] | astra, text only | astra, [points] | difference, text only | difference, [points] |
|---|---|---|---|---|---|---|---|
| all items | 5000 | 60.7 | 65.5 | 52.7 | 55.6 | +8.0 | +9.8 |
| HealthBench Hard items | 1000 | 42.0 | 48.7 | 29.4 | 32.4 | +12.6 | +16.3 |
