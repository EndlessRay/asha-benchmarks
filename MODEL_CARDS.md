# DNAi model cards

> Rubric scores in this revision are graded with OpenAI's reference rubric rendering (each criterion shown to the grader with its point value), as the HealthBench reference implementation grades them; the re-grade of 31 Oct 2026 is in [`healthbench-reference-rendering-2026-10-31/`](healthbench-reference-rendering-2026-10-31/). Where the first grading (criterion text only) differs, it is given as "as first graded". Axis and theme breakdowns and the GPT-5.4 and Claude Opus 4.8 sensitivity grades on HealthBench Standard and Hard are as first graded.

DNAi Systems. Revision of 5 November 2026. Supersedes the launch revision of 24 September 2026 (kept in this file's history). Changes: scores on the reference rendering, matching the public register and the v2 preprint; HealthBench Professional and psychosis-bench rows filled in; the served backbone since 14 October 2026; automatic provider failover; the status of the identity check and of Apex-J's external validation.

Asha is an AI system in the HealthBench Professional paper's sense: a model plus a harness. Every tier below is the same neurosymbolic stack (retrieval, falsification, safety gating, composition) wrapped around vendor language models. No tier uses a fine-tuned model. Every gain over a bare model reported here is measured against that model on the same items, under the same grader. For Apex-J the comparator is the bare answer-writing model (the composer model); the agents inside Apex-J run other vendor models, so the paired difference is the effect of the whole system and cannot be attributed to any single component.

Numbers carry their source, set size and grader. Where a number is not on the public register at [dnai.systems/benchmarks](https://dnai.systems/benchmarks) it is marked as such. The register is canonical; if this card and the register ever disagree, the register is right and this card is stale.

## 1. What every tier shares

**Knowledge.** One curated corpus, retrieved through the Knowledge Integration Layer (KIL): PubMed and PMC full text, OpenAlex, drug labels (DailyMed, FDA, FAERS), clinical references and guidelines, medical coding, textbooks, and domain corpora for finance, law, nutrition and fitness, refreshed on schedule. Per-user memory is stored separately and is never a knowledge source. A contamination probe on 200 of the 5,000 HealthBench items found no retrievable benchmark content in the collections Asha searches (nearest-neighbour cosine below 0.92 throughout).

**Backbone models.** At the freeze of 20 September 2026, panel agents ran on Claude Sonnet 5 and Claude Opus 5, selected per query by task gravity, and every score on this card was measured on that configuration. Since 14 October 2026 production runs Claude Sonnet 5.5 in place of Sonnet 5 in the lower-gravity band; Opus 5 is unchanged. No score on this card or on the register was measured with Sonnet 5.5 inside Asha. The Apex-J composer is GPT-6 Astra with a 4,096-token budget and the concise style. Gemini serves PHI-adjacent pipelines under the Vertex AI BAA.

**Safety, all tiers.** Jailbreak detection; a contract validator on every agent output; a capitulation detector with one restraint regeneration; crisis resources surfaced whenever risk language appears (988 in the US), bypassing quotas; an evidence gate; every answer written to a ledger and every API call to an audit log. Refusals are rare by design: Asha answers with safety framing rather than declining. Across the 5,000-item HealthBench run, 525 clinician prompts, and 500 study-sample items reported below, the refusal count is zero.

**Routing.** Task gravity, a stakes score computed per query, chooses the tier on the consumer surfaces: Base for most queries, Mid for higher-stakes queries, Apex for the highest-stakes queries with a daily cap. API customer keys run Base by default; Apex is an explicit, asynchronous, per-answer product.

**Shared limitations.** Deep paths take 40 to 150 seconds. Since 25 October 2026 a provider outage fails over automatically to Gemini on Vertex AI (after three provider errors within 60 seconds), so answers during an outage come from a backbone that these scores did not measure; before that date, an outage on 22 September 2026 was handled by a manual switch. Knowledge recency depends on the refresh lanes. Rubric-graded benchmarks move several points between graders, so every headline number is reported with its grader and, where measured, two sensitivity graders.

## 2. Asha Base

| Field | Value |
|---|---|
| Pipeline id | P2 |
| Architecture | One KIL-grounded pass: retrieval across the admitted collections, evidence assembled into the prompt, one backbone call, safety gates, ledger write |
| Backbone | Claude Sonnet 5 or Claude Opus 5 by task gravity when measured; Claude Sonnet 5.5 replaced Sonnet 5 in the lower band on 14 Oct 2026 |
| Where it runs | Consumer queries in the low gravity band; the API default for customer keys; the panel members inside Apex-J |
| Intended use | Everyday health questions, medication facts, triage guidance, documentation help; high volume, low latency |
| Not for | Complex multi-morbidity consults (the cascade escalates); research syntheses that need the panel |
| Latency | about 20 to 30 s typical on the API; seconds to first token on the stream path |
| HealthBench Standard (5,000, gpt-4.1) | 44.1 (June 2026 build, as first graded; independently recomputed 44.06 by Airpixels Innovations LLP, 10 Sep 2026). Not re-graded with the reference rendering. Kept as lineage on the register |
| HealthBench Hard (1,000; 995 scored) | 29.9 (June 2026 build, reference rendering, re-graded 31 Oct 2026); as first graded 28.4, recomputed 28.35 by Airpixels |
| HealthBench Professional (524 paired, GPT-5.4 official, length-adjusted) | 53.0 vs Claude Sonnet 5 alone 54.0: -1.1, p = 0.57. On the 191 red-team items +7.4 over Sonnet 5 alone (p = 0.074). Per-item data withheld at OpenAI's request |
| MedQA (locked 1,273) | 95.5% (1,216 of 1,273, May 2026 build) against 92.3% for Gemini 3.1 Pro alone. Most of that gain is answer formatting: on the items the model alone answered in a readable format, Asha was better on 15 and worse on 25 (p = 0.15). Register row `medqa-usmle-locked` |
| Psychosis Bench | May 2026 build with Gemini 2.5 Flash: 95.8% safe intervention against 30.2% for the same model alone (higher in 14 of 16 scenarios, none lower; sign test p = 1.2e-4). Asha Base 100% in the 20 Sep 2026 re-run; deployed Asha fresh run by the independent validator 96.9% SIS (93 of 96 turns) |
| Known limitations | Single-model answer, so no cross-family check |

## 3. Asha Mid

| Field | Value |
|---|---|
| Pipeline id | P5 (deep-mode ensemble) |
| Architecture | Three KIL-grounded drafts in parallel from different model families, then a composer merges under a union-of-correct, falsify-before-include discipline |
| Where it runs | Consumer stream path, middle gravity band |
| Intended use | Higher-stakes single-question consults where a second model family adds a check without the panel's cost |
| Latency | roughly 40 to 50 s design envelope |
| HealthBench Standard (5,000, gpt-4.1) | 60.6 (June 2026 build, as first graded; recomputed 60.59). Not re-graded with the reference rendering. Kept as lineage on the register |
| HealthBench Hard (1,000; 898 scored) | 41.8 (reference rendering, re-graded 31 Oct 2026); as first graded 37.9 (recomputed 37.94), +9.7 pp over Base, paired, p about 1e-19 |
| Known limitations | The least-measured tier: not run on HealthBench Professional, MedHELM or the Psychosis Bench as a separate arm |

## 4. Asha Apex (P6): the June 2026 build, lineage

| Field | Value |
|---|---|
| Pipeline id | P6, composer Claude Opus 4.8, FENG on |
| Architecture | A panel of specialist agents, each drafting with its own retrieval; FENG falsifies extracted claims against the corpus; a domain-expert composer merges; waits for all agents |
| Status | Replaced as the served Apex tier by Apex-J on 20 September 2026. Its June numbers stay on the register as lineage comparators |
| HealthBench Hard (1,000, gpt-4.1) | 51.4 (June 2026 answers, reference rendering, re-graded 31 Oct 2026); as first graded 44.8 [43.0, 46.6], and 44.8 again when today's gpt-4.1 re-graded the identical answers on 22 Sep 2026 (grader stable) |
| HealthBench, Vishwanath 500 | 68.4 under the study's published three-judge panel (Claude Opus 4.6, Gemini 3.1 Pro Preview, GPT-5.2; graded 23 Sep 2026 in the study's own pipeline on the June answers). Earlier figures quoted for this set (72.6 under gpt-4.1 single) were a different grader from the published tools' and are retired |
| MedHELM efficient (n = 30 per scenario) | see the register appendix; small samples, never headline claims |
| Psychosis Bench | SIS 97.9% (30 June 2026) |
| Known limitations | Waited for the slowest agent; the longest answers of any tier (about 4,600 characters median on the 500) |

## 5. Asha Apex-J (frozen 20 September 2026): the served Apex tier at launch

| Field | Value |
|---|---|
| Pipeline id | P6-J. Freeze tag `freeze-2026-09-20`. Process fingerprint of the measured build `edd4f69f9a9bd6d2` |
| Architecture | The Apex panel rebuilt as jiva agents, each drafting with its own retrieval; a grounding check on the composed answer. Composer GPT-6 Astra, 4,096 tokens, concise style. FENG on, KIL on |
| Where it runs | The Apex tier of the production cascade since 20 September 2026 (web stream path, non-stream `/api/query`, A2A `message:send` at depth auto, and the OpenAI-compatible model `asha-apex`) |
| Intended use | Clinician-facing consults, documentation, research synthesis: the tier DNAi publishes |
| Not for | Real-time use: 60 to 150 s deep path |
| Latency | mean about 80 s, p90 about 110 s on the bench lane |
| **HealthBench Standard (5,000, gpt-4.1)** | **65.5** vs bare GPT-6 Astra 55.6 on the same items: +9.8 pp [9.2, 10.5], p = 9.7e-181; length-adjusted +7.4 [6.8, 8.0] (63.6 vs 56.2), p = 2.1e-111. As first graded 60.7 vs 52.7 (+8.0, wins/losses/ties 2,618 / 1,162 / 1,220). Sensitivity graders, as first graded: GPT-5.4 55.2 vs 48.1 (+7.1); Claude Opus 4.8 65.9 vs 57.8 (+8.4) |
| **HealthBench Hard (1,000, gpt-4.1)** | **48.7** vs bare GPT-6 Astra 32.4: +16.3 pp [14.6, 18.1], p = 3.8e-64; length-adjusted +13.7 [12.0, 15.4] (46.8 vs 33.1), p = 1.5e-49. As first graded 42.0 vs 29.4. Sensitivity graders, as first graded: GPT-5.4 37.3 vs 24.9; Opus 4.8 50.3 vs 35.7 |
| **HealthBench, Vishwanath 500 (study pipeline, three-judge panel)** | **63.8** vs OpenEvidence 62.6 and UpToDate Expert AI 61.3 as published by the study under the same panel; bare GPT-6 Astra 54.9 under the same panel. Every one of the 5,782 criteria received three clean votes. Under gpt-4.1 with the reference rendering on the same answers: 65.7 vs 56.5, +9.2 [7.2, 11.2], p = 1.0e-18 |
| HealthBench Professional (525, three trials per arm) | 69.6 vs bare GPT-6 Astra 65.3 under GPT-5.4 (the benchmark's official grader, length-adjusted, reference rendering): +4.3 [1.8, 6.7], p = 6.5e-4. The ladder that selected this configuration ran on 300 of these items; on the 225 holdout items never used for that choice the lead is +2.7 [-0.8, 6.2], p = 0.13, not statistically significant. Under Claude Opus 4.8, the grader of Anthropic's system card: 73.9 vs 68.6 on all 525 and 74.0 on the holdout (+4.8, p = 0.012); Anthropic reports 66.0 for Claude Mythos 5 in its own harness. Per-item data withheld at OpenAI's request |
| Psychosis Bench | 95.8% [89.8, 98.4] safe intervention, DCS 0.146, HES 0.021 (20 Sep 2026, protocol judge gpt-4o-mini); bare Claude Sonnet 4.5 100%, so on this protocol today's frontier models alone are at parity |
| Refusals | 0 on the 5,000; 0 on the 500; 0 on the 525 |
| **Pre-registered harm test** | Harm proxy = share of negative-point rubric criteria the answer triggers, vs bare GPT-6 Astra on the same items, bound +2.0 points. With the reference rendering under gpt-4.1: Standard **20.3% vs 20.8% (met)**; Hard 23.8% vs 27.9% (-4.1 [-5.5, -2.8]). Among Hard conversations where all three graders flagged a severe harm (a criterion worth -9 or -10) in only one system's answer, it was Apex-J's in 2 and the bare model's in 17 (p = 0.0007). As first graded (criterion text only), gpt-4.1 read +2.8 on Standard, a miss concentrated in length and over-detail criteria (factual-error criteria were 59 of the 1,851 extra hits), and GPT-5.4 -0.3, Opus 4.8 -0.4; on Hard +1.6, -3.2, -4.1 |
| Where it wins and loses (Standard, gpt-4.1 as first graded, vs bare Astra) | Wins every theme: global health +12.3, context seeking +11.1, hedging +9.0, health data tasks +7.4, communication +4.7, emergency referrals +4.3, complex responses +1.1. Axes: completeness +13.9, accuracy +6.6, context awareness +3.6, instruction following +1.7, communication quality -8.0. Median answer 2,725 characters vs 1,400 |
| Deployed-code identity check | The served code was re-run on the 500 on 23 Sep 2026 because other changes landed on the shared engine after the freeze: panel 63.7 vs the frozen run's 63.8, gpt-4.1 61.4 vs 61.6 (p = 0.83; as first graded). A second re-run started on 24 Sep is not reported |
| Style check | The default composer style on the same code and items scored lower than concise on every grader (panel 62.2 vs 63.7; gpt-4.1 58.3 vs 61.4, p = 0.0009) and produced shorter answers. Concise stays |
| Lineage, stated plainly | The frozen build is below the June P6 build on raw rubric scoring: 48.7 vs 51.4 on Hard with the reference rendering (42.0 vs 44.8 as first graded), 63.8 vs 68.4 on the 500 under the same panel. The June build's fuller answers (about 4,600 vs 2,700 characters) earn completeness points that the concise style gives up |
| Known limitations | Communication-quality axis below the bare answer-writing model; the Professional holdout lead is not significant; deep-path latency; the corpus recency lanes; scores measured with Sonnet 5 in the panel (see section 1) |
| External validation | The June builds were validated by Airpixels Innovations LLP (Package 1, signed 10 Sep 2026), and the validator's fresh psychosis-bench run of the deployed engine read 96.9%. The frozen Apex-J's own external validation (Package 2) has not been performed as of this revision; every per-item artifact needed for it is in this repository |

## 6. Comparison chart

| Dimension | Base | Mid | Apex (P6, June) | Apex-J (frozen, served) |
|---|---|---|---|---|
| Model families per answer | 1 | 3 + composer | agent panel + composer | agent panel + composer |
| Retrieval | KIL, 1 pass | KIL, 3 grounded drafts | KIL per agent + FENG | KIL per agent + FENG |
| Typical / p90 latency | ~25 s / ~30 s | ~45 s / ~50 s | 81 s / 124 s | ~80 s / ~110 s |
| HealthBench Standard 5,000 (gpt-4.1) | 44.1 (June, as first graded) | 60.6 (June, as first graded) | not run on 5,000 | **65.5** |
| HealthBench Hard 1,000 (gpt-4.1) | 29.9 (June) | 41.8 (June) | 51.4 (June) | **48.7** |
| Vishwanath 500, published panel | not run | not run | 68.4 | **63.8** (OpenEvidence 62.6, UpToDate 61.3) |
| Refusals on clinician prompts | rare | rare | 0 | 0 |
| Served on 1 Oct 2026 | yes (API default, cascade low band) | yes (cascade mid band) | no | yes (cascade high band, `asha-apex`) |

## 7. API model names

| API name | Tier | Notes |
|---|---|---|
| `asha-base` | Base | default for customer keys |
| `asha-mid` | Mid | cascade middle band |
| `asha-apex` | Apex-J | asynchronous; explicit per-answer product |

The other DNAi agents (Harley, Artha, Sage, Polymath, Lyra, Leo, Mira, Ren, Arohi, Ray) are reachable over the A2A protocol and documented in their own public repositories under [github.com/EndlessRay](https://github.com/EndlessRay).

## 8. Sources

Public benchmark register: [dnai.systems/benchmarks](https://dnai.systems/benchmarks) (JSON at `/benchmarks.json`, API at `/api/benchmarks`). The reference-rendering re-grade of every HealthBench arm, with a script that recomputes the paired readout from the public files: [`healthbench-reference-rendering-2026-10-31/`](healthbench-reference-rendering-2026-10-31/). Per-item artifacts for the 5,000-item run, the 500-item panel grades, the identity and style checks: [`healthbench-5000-2026-09-20/`](healthbench-5000-2026-09-20/). June 2026 artifacts: [healthbench-2026-06-26/](https://github.com/EndlessRay/asha-benchmarks/tree/main/healthbench-2026-06-26). MedQA, Psychosis Bench, answer-format normalization: [asha-benchmarks](https://github.com/EndlessRay/asha-benchmarks). Vishwanath et al., Nature Medicine 2026, and the study's public pipeline: [nyuolab/clinical-llm-benchmarks](https://github.com/nyuolab/clinical-llm-benchmarks). HealthBench: Arora et al., arXiv:2505.08775.
