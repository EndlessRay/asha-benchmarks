# Validation

| Profile | Status (2026-10-28) |
|---|---|
| `flashlite-v1` | **Passed** every check below. Suited to screening and to sensitivity analysis next to the official grader. |
| `oss120b-v1` | **Not passed alone.** Professional holdout kappa 0.803 sits below both frontier graders (0.810, 0.812); polarity flips on 2 to 8% of omission penalties marked met (reference 3 to 4%). Use it as a panel member. |
| Panel `flashlite-v1` + `oss120b-v1` (`hbjudge panel`) | **Recommended when the systems compared come from different vendors.** Passes delta replication and self-preference on both references, with every own-vendor contrast within ±0.5 points. Holdout kappa: consumer 0.783 (GPT-5.4 0.715, Opus 0.786); professional 0.8096, 0.0006 below Opus (0.8102), so it misses that bar by the smallest margin we can report. |
| `oss20b-v1` | Not validated. |
| `gpt41-reference` | The official grader, for calibration runs. |

A profile is recommended only when every check passes on the profile exactly as frozen in `hbjudge/judges.py`.

## The gate

| Check | Question | Pass condition |
|---|---|---|
| Physician agreement | Does the judge agree with physicians as often as the official grader does? | Pooled pairwise balanced F1 on OpenAI's meta-eval at or above the typical physician, CI reported against GPT-4.1 |
| Reproduction | Does our harness reproduce OpenAI's published grader numbers? | GPT-4.1 and GPT-4.1-mini within CI of 0.709 and 0.661 |
| Criterion agreement, holdout | Does agreement with GPT-4.1 hold on items never used for tuning? | Cohen's kappa on the holdout at or above a frontier grader |
| Delta replication | Does the judge make the same call about which of two systems is better? | Across all pairs of 7 systems: no pair significant in opposite directions; sign agreement on every pair the reference separates by 2.5 points or more; mean absolute error on the frontier grader's pairs at or below the frontier grader's own |
| Self-preference | Does the judge favour answers from its own vendor? | Own-vendor contrast (own-vendor answers minus other answers, judge minus reference) has a CI that includes 0 |
| Missing grades | How often is there no grade? | Under 0.5% of criteria after retries |
| Polarity | Does the judge mark "Fails to mention X" met while saying X is present? | Flip share at or below the reference grader rendered as in simple-evals (3 to 4%) |

## References

The delta set is 7 answer sets on the same 500 HealthBench conversations: two bare OpenAI and Anthropic models, two bare Google models, and three versions of one multi-agent pipeline (two on Google or Anthropic backbones).

| Reference | What it is | Used for |
|---|---|---|
| **R2 (primary, pre-registered)** | GPT-4.1 with `[points] criterion`, every criterion of 200 conversations x 7 systems (16,478 criteria) | delta replication, self-preference |
| R1 | GPT-4.1 grades from the answer owner's production pipeline, criterion text only, 500 conversations x 7 systems | delta replication, self-preference, polarity |
| Holdout reference | R1 verdicts on positive criteria plus GPT-4.1 `[points]` verdicts on penalty criteria (1,845) | holdout agreement |

The holdout reference is valid because the rendering does not move positive verdicts: on 11,620 positive criteria, GPT-4.1 with and without point values agreed 96.1% (kappa 0.906), the level of GPT-4.1 against itself (kappa 0.908), with met rates of 70.8% and 70.9%.

## Reproduction: pass

Uniform sample of 3,000 meta-eval pairs, pooled metric, 500 item-bootstrap resamples.

| Grader | MF1 [95% CI] | Published |
|---|---|---|
| GPT-4.1 (simple-evals settings) | 0.714 [0.698, 0.729] | 0.709 |
| GPT-4.1-mini (simple-evals settings) | 0.665 [0.648, 0.683] | 0.661 |
| Typical physician | 0.667 [0.641, 0.676] | |

## `flashlite-v1`: Gemini 3.1 Flash-Lite, temperature 0, `[points] criterion`

| Check | Result | Status |
|---|---|---|
| Physician agreement | MF1 0.682 [0.666, 0.698]; minus typical physician +0.015 [+0.005, +0.040]; minus GPT-4.1 −0.032 [−0.044, −0.021]. The meta-eval has no penalty items, so the rendering does not apply | pass |
| Holdout kappa | consumer 0.799 (Claude Opus 4.8: 0.786, GPT-5.4: 0.715); professional 0.816 (0.810, 0.812). Penalty criteria alone: 0.663 (Opus 0.609), met 23% vs reference 24% | pass |
| Delta replication, R2 | 21 pairs: no opposite significant calls; sign agrees on all 17 pairs with a reference gap of 2.5 points or more (19/21 overall); correlation of paired differences 0.978; mean abs error on Opus's 15 pairs 1.68 (Opus: 2.47) | pass |
| Delta replication, R1 | sign 19/21, both disagreements at reference gaps under 1 point; correlation 0.986; mean abs error 1.23 overall, 1.34 on Opus's pairs (Opus: 0.94) | sign and significance pass; error above the frontier on this reference |
| Self-preference | Google answers: +1.9 [−0.2, +3.9] (R2), +0.4 [−1.2, +1.8] (R1). It leans against the OpenAI answer set: −2.3 [−4.4, −0.2] (R2), −1.6 [−3.3, +0.1] (R1); the reference is itself an OpenAI model | pass on own vendor |
| Missing grades | 0.00% of 40,474 criteria, first pass and final | pass |
| Polarity | flips on 0 to 3% of omission penalties marked met | pass |

Cost: about $0.53 per 1,000 criteria (GPT-4.1 about $4.06). A full 5,000-conversation run is about $28 (batch about $14) against about $202.

Without the point values the same model fails: its Google-answer bias is +2.7 [+1.2, +4.3] (R1) and +3.2 [+0.8, +5.4] (R2), and it reverses a 4.0-point reference gap.

## `oss120b-v1`: gpt-oss-120b, reasoning effort low, `[points] criterion` (local)

| Check | Result | Status |
|---|---|---|
| Physician agreement | MF1 0.678 [0.662, 0.695]; minus typical physician +0.011 [+0.001, +0.038]; minus GPT-4.1 −0.036 [−0.048, −0.024] | pass |
| Holdout kappa | consumer 0.767 (Opus 0.786, GPT-5.4 0.715); professional 0.803 (Opus 0.810, GPT-5.4 0.812); penalty criteria met 28% vs reference 24% | consumer pass; **professional fail** |
| Delta replication, R2 | no opposite significant calls; sign agrees on all 17 pairs with a gap of 2.5 points or more (18/21 overall); correlation 0.976; mean abs error on Opus's pairs 1.66 (Opus 2.47) | pass |
| Delta replication, R1 | sign 20/21; correlation 0.975; mean abs error 1.09 overall, 1.24 on Opus's pairs (Opus 0.94) | sign and significance pass; error above the frontier on this reference |
| Self-preference | OpenAI answers: +1.4 [−1.1, +3.8] (R2), +1.8 [+0.1, +3.5] (R1); Google answers −1.4 [−3.9, +1.1] (R2) | pass on R2; leans toward OpenAI answers on R1 |
| Missing grades | 0.00% of 40,474 criteria | pass |
| Polarity | flips on 2 to 8% of omission penalties marked met, highest on the multi-agent pipeline's answers | **fail** |

## Two-judge panel: `flashlite-v1` + `oss120b-v1`

`hbjudge panel` averages the two judges' per-criterion verdicts on the same answers (a split verdict counts half), then scores as usual. Their vendor leanings point in opposite directions and cancel.

| Check | Result | Status |
|---|---|---|
| Delta replication, R2 | sign agrees on all 17 large-gap pairs (19/21 overall); no opposite significant calls; correlation 0.990; mean abs error on Opus's pairs 1.26 (Opus 2.47) | pass |
| Delta replication, R1 | sign 20/21, significance 20/21; correlation 0.989; mean abs error on Opus's pairs 0.93 (Opus 0.94) | pass |
| Self-preference | Google +0.3, OpenAI −0.4, Anthropic +0.1 (R2); −0.4, +0.1, +0.5 (R1); every CI includes 0 | pass |
| Holdout kappa (fractional verdicts scored as a coin flip on a split) | consumer 0.783 (Opus 0.786, GPT-5.4 0.715); professional 0.8096 (Opus 0.8102, GPT-5.4 0.8123) | consumer pass; professional 0.0006 short |
| Missing grades | 0.00% | pass |

Cost: Flash-Lite's API cost (about $28 per 5,000-conversation run) plus local GPU time for gpt-oss-120b (about 2 criteria per second on one 96 GB card at 300 W).

## A finding about the reference grader

The rubric-item rendering changes GPT-4.1's verdicts on penalty criteria and leaves positive criteria alone. On 4,858 penalty criteria (200 conversations x 7 systems), same model, same day, same settings:

| GPT-4.1 rubric item | omission penalties flipped (pipeline / bare models) | penalty criteria marked met |
|---|---|---|
| criterion text only (as in several third-party pipelines) | 26% / 16% | 30.4% / 27.9% |
| `[points] criterion` (as in simple-evals) | 3% / 4% | 21.6% / 21.8% |

Shown only "Fails to mention X", GPT-4.1 often marks the item met because the answer does mention X. Shown "[-8] Fails to mention X", it reads the item as a penalty. Agreement between the two renderings on penalties is 80.0%, against 91.2% test-retest. Overall scores barely move, because positive criteria dominate them: on 200 conversations the paired differences between the 7 systems changed by 0.78 points on average. Harm measures built from penalty criteria move a great deal. This harness always renders the point values.

## How to reproduce

The delta set and the arena that produced these numbers are internal; the meta-eval check runs from public data:

```bash
hbjudge validate --meta-eval 2025-05-07-06-14-12_oss_meta_eval.jsonl --profile flashlite-v1 --n 3000 --out runs/validate
hbjudge validate --meta-eval 2025-05-07-06-14-12_oss_meta_eval.jsonl --profile gpt41-reference --n 3000 --out runs/validate
```

To check a judge on your own systems, grade two or more answer sets with both the judge and `gpt41-reference`, then compare `hbjudge compare` output pair by pair.
