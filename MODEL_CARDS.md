# DNAi model cards: final revision, 22 October 2026

DNAi Systems. One card per anchored build. Supersedes the 24 September launch revision and the 21 October interim revision (both in git history). The register at [dnai.systems/benchmarks](https://dnai.systems/benchmarks) is canonical for any number; if a card and the register disagree, the register is right. Every run behind these cards is listed in date order in [`BENCHMARK_TIMELINE.md`](BENCHMARK_TIMELINE.md).

Asha is an AI system in the HealthBench Professional paper's sense: a model plus a harness. Every tier is the same neurosymbolic stack (retrieval, falsification, safety gating, composition) wrapped around vendor language models. No tier uses a fine-tuned model. Gains are measured against the bare model on the same items under the same grader.

## 0. Portfolio and naming

Three public tiers, one code freeze, one name per tier. Builds are identified by freeze date. "Apex-J", "P2", "P5", "P6", "P6-J" are internal pipeline ids, never product names.

| Public name | API id | Pipeline | Current build | State on 22 October 2026 |
|---|---|---|---|---|
| **Asha Base** | `asha-base` | P2 | freeze `asha-base-v3-2026-10-19` (commit `0a3b831af`), Claude Sonnet 5.5 at effort low | Measured on 500 + psychosis (card F); replicated on the 40-item reproducibility set |
| **Asha Mid** | `asha-mid` | P5 | same freeze; three-family deep-mode ensemble | First measured on the current build on the 40-item set (card G); 500-item run pending |
| **Asha Apex** | `asha-apex` | P6-J | same freeze; agent panel + FENG + one composer | Two composer recipes measured on the 40-item set (card H); 500-item composer decision pending |

## 1. What "reproducible" means here, and which builds are

A build is **reproducible** when the following are all pinned and preserved: the code (git commit and container image digest), the agent manifests, the runtime environment (hash), the knowledge corpus (collection manifest with point counts and an off-box copy), the vendor model ids and effort settings, and the item set (SHA-256). Vendor models are external services; a reproducible build re-runs the same request to the same model id, and vendor-side drift shows up as a replication delta that we measure rather than assume away.

| Build | Code pin | Corpus | Models | Re-generate today | Re-grade today |
|---|---|---|---|---|---|
| Asha Base, May 2026 (P1) | commit only | gone | Gemini 2.5 Flash / Pro (retired) | no | yes (answers published) |
| Asha Base / Mid / Apex, June 2026 (P2 / P5 / P6) | commit only | gone | Claude Sonnet 4.6 / Opus 4.8, Gemini 3.1 Pro, GPT-5 (snapshots moved) | no | yes (per-item HealthBench answers and grades published; Professional aggregates only) |
| Asha Apex-J, 20 Sept 2026 (P6-J) | tag `freeze-2026-09-20`, fingerprint `edd4f69f9a9bd6d2`, code in a private record repo | gone (7-day NAS snapshots rolled) | Claude Sonnet 5 / Opus 5, GPT-6 Astra | no | yes (all 5,000 + 1,000 + 500 answers and three graders published) |
| **Asha, freeze 19 Oct 2026** (Base / Mid / Apex, P2 / P5 / P6-J) | commit `0a3b831af`, image `citadel-frozen/asha-base:2026-10-18-genai175`, env hash in `study.json`, read-only worktree, 15 agent manifests | manifest 345 knowledge collections / 144,397,558 points; NAS copy `citadel-qdrant/frozen/asha-base-2026-10-18/` | Claude Sonnet 5.5 / Opus 5, GPT-6 Astra (ids pinned per request) | **yes** (immutable containers on the 5090) | yes |

**Replication check (22 October 2026).** The reproducibility run re-generated every current arm on 40 seeded random items from the seed-62 500 (sample sha `42771977…`, seed 20261022) and compared the fresh answers with the per-item grades on record for the same items. Results are in card F, G and H and in [`healthbench-repro40-2026-10-22/`](healthbench-repro40-2026-10-22/). A replication delta inside the sample's noise means the frozen build reproduces its record; the bare-model rows show how much of any delta is vendor-side variance.

## 2. What every tier shares

**Knowledge.** One curated corpus retrieved through the Knowledge Integration Layer (KIL): PubMed and PMC full text, OpenAlex, drug labels (DailyMed, FDA, FAERS), clinical references and guidelines, medical coding, textbooks, and domain corpora. Per-user memory is stored separately and is never a knowledge source. Contamination probes (200 of the 5,000 HealthBench items in September; 500 items against 336 of 345 collections in October) found no retrievable benchmark content.

**Safety, all tiers.** Jailbreak detection; a contract validator on every agent output; a capitulation detector with one restraint regeneration; crisis resources surfaced whenever risk language appears, bypassing quotas; an evidence gate; every answer written to a ledger and every API call to an audit log. Refusals are rare by design: Asha answers with safety framing rather than declining. Across every HealthBench run on the register the refusal count is zero.

**Routing.** Task gravity, a stakes score computed per query, chooses the tier on the consumer surfaces: Base for most queries, Mid for higher-stakes queries, Apex for the highest-stakes queries with a daily cap. API customer keys run Base by default; Apex is an explicit, asynchronous, per-answer product.

**Shared limitations.** Deep paths take 40 to 230 seconds. Provider failover is manual. Rubric-graded benchmarks move several points between graders, so every headline number carries its grader and, where measured, sensitivity graders. Vendor model ids are external and can change behaviour without notice; the replication check above is how we detect it.

## 3. Cards

### Card A. Asha Base, May 2026 (P1): the first anchored build

| Field | Value |
|---|---|
| Pipeline | P1: one KIL-grounded pass, Gemini 2.5 Flash routed to 2.5 Pro by task gravity (Vertex, BAA) |
| Reproducible | No (model snapshots retired). Per-item answers published |
| MedQA USMLE 4-option test, 1,273 (2026-05-04) | **95.52%** [94.2, 96.5] vs Gemini 3.1 Pro 92.30%; paired +3.2, McNemar p = 2.0e-5. The "wrong answers independent of Gemini" claim was retracted 2026-05-11: 51 of 66 paired wins came from answer-format normalisation |
| psychosis-bench, 96 turns (2026-05-11) | SIS **95.8%** vs bare Gemini 2.5 Flash 30.2%; DCS 3.4x lower, HES 7.9x lower; judge kappa 0.25 below the 0.60 gate (formally inconclusive, direction agreed) |
| Attribution (2026-05-12) | bare 2.5 Pro no safer than 2.5 Flash: the routed Pro share does not explain the gap |
| Artifacts | [`medqa-2026-05-04/`](medqa-2026-05-04/), [`psychosis-bench-2026-05-11/`](psychosis-bench-2026-05-11/), [`psychosis-attribution-2026-05-12/`](psychosis-attribution-2026-05-12/) |

### Card B. Asha Base, June 2026 (P2)

| Field | Value |
|---|---|
| Pipeline | P2: one KIL-grounded pass, Claude Sonnet 4.6 / Opus 4.8 routed by gravity (direct Anthropic API) |
| Reproducible | No. Per-item HealthBench answers and grades published |
| HealthBench Standard 5,000 (gpt-4.1) | **44.1** (Airpixels recomputed 44.06, 2026-09-10) |
| HealthBench Hard 1,000 (gpt-4.1) | **28.4** (recomputed 28.35) |
| KaBLE belief-reasoning subset, 220 (2026-06) | 97.7% |
| Locked pediatric AOM chart, 36 identity variants (2026-08-26, production P2) | plan, dose and duration invariant 36 of 36 |
| Enclomiphene-bench (2026-09-18, production P2 on Sonnet 5) | patient arm SIS 100%; clinician red-team arm 0 of 29 harm criteria vs 5 / 6 / 3 prompts for bare Gemini 3.5 Flash, GPT-5, Claude Sonnet 4.5; small n, DNAi-authored |
| HealthBench Professional, 524 (2026-09, Base on Sonnet 5 vs bare Sonnet 5, length-adjusted) | +0.3, p = 0.88 (tie); 191 red-team items +10.1 |
| Artifacts | [`healthbench-2026-06-26/`](healthbench-2026-06-26/), [`aom-chart-2026-08/`](aom-chart-2026-08/), [`enclomiphene-bench-2026-09-18/`](enclomiphene-bench-2026-09-18/) |

### Card C. Asha Mid, June 2026 (P5)

| Field | Value |
|---|---|
| Pipeline | P5: three KIL-grounded drafts (Claude Opus 4.8, Gemini 3.1 Pro, GPT-5) from the same evidence, merged by a domain-expert composer |
| Reproducible | No. Per-item answers and grades published |
| HealthBench Standard 5,000 (gpt-4.1) | **60.6** (recomputed 60.59) |
| HealthBench Hard, 898 scored (gpt-4.1) | **37.9** (recomputed 37.94); +9.7 over Base paired, p ~ 1e-19 |
| Limits | The least-measured tier: never run on Professional, MedHELM, psychosis-bench or the Vishwanath 500 as its own arm |
| Artifacts | [`healthbench-2026-06-26/`](healthbench-2026-06-26/) |

### Card D. Asha Apex, June 2026 (P6)

| Field | Value |
|---|---|
| Pipeline | P6: a panel of domain-specialist agents, each with its own retrieval; FENG falsifies extracted claims against the corpus; Claude Opus 4.8 composer, full-length; waits for all agents |
| Reproducible | No. Per-item Hard answers and grades published; Professional aggregates only; Vishwanath 500 panel grades published |
| HealthBench Hard 1,000 (gpt-4.1) | **44.8** [43.0, 46.6]; re-graded 2026-09-22 with the current gpt-4.1 on the identical answers: 44.8 (grader stable). The highest Hard number DNAi holds |
| HealthBench Professional, 525 | 70.5 raw / 65.5 length-adjusted (Claude Opus 4.8 grader); 67.4 (gpt-4.1); 56.4 (GPT-5.2) |
| Vishwanath 500, study three-judge panel (graded 2026-09-23 on the June answers) | **68.4** |
| psychosis-bench (2026-06-30) | SIS 97.9% |
| MedHELM efficient, 13 scenarios, n = 30 each | first on mtsamples, aci_bench, medcalc (0.400 vs Base 0.133), medhallu 0.933; weak on medbullets 0.467; appendix only |
| Limits | Longest answers of any build (about 4,600 characters median on the 500); p90 latency 124 s; harm proxy never measured against its bare composer |
| Artifacts | [`healthbench-2026-06-26/hard/`](healthbench-2026-06-26/hard/), [`healthbench-5000-2026-09-20/vishwanath-500-panel/`](healthbench-5000-2026-09-20/vishwanath-500-panel/), [`healthbench-5000-2026-09-20/readouts/`](healthbench-5000-2026-09-20/readouts/) |

### Card E. Asha Apex-J, frozen 20 September 2026 (P6-J): the launch build

| Field | Value |
|---|---|
| Pipeline | P6-J: the Apex panel rebuilt as jiva agents on Claude Sonnet 5 / Opus 5, FENG on, grounding check, composer GPT-6 Astra, concise style, 4,096 tokens |
| Pin | tag `freeze-2026-09-20`, process fingerprint `edd4f69f9a9bd6d2`; code, configuration and ledger in the private record repo `asha-apex-j-private-2026-09` |
| Reproducible | No: the corpus snapshot at that fingerprint rolled off the 7-day NAS retention. Every answer and every per-criterion grade under three graders is published, so every number re-grades |
| Selected by | the September ladder on HealthBench Professional (300-item slice, 225 holdout), GPT-5.4 grader length-adjusted, Opus 4.8 sensitivity, plus a harm bound. Holdout: +2.2 vs bare Astra, p = 0.23 (not significant); Opus 4.8 +4.6, p = 0.03 |
| **HealthBench Standard 5,000 (gpt-4.1)** | **60.7** [59.8, 61.5] vs bare GPT-6 Astra 52.7: +8.0 [7.3, 8.7], length-adjusted +5.6. GPT-5.4: 55.2 vs 48.1. Opus 4.8: 65.9 vs 57.8 |
| **HealthBench Hard 1,000 (gpt-4.1)** | **42.0** [40.1, 43.7] vs 29.4: +12.6 [10.7, 14.4]. GPT-5.4 37.3 vs 24.9; Opus 4.8 50.3 vs 35.7 |
| **Vishwanath 500, study panel** | **63.8** vs OpenEvidence 62.6 and UpToDate Expert AI 61.3 (as published); bare Astra 54.9. gpt-4.1 on the same 500: 61.6 vs 53.2 |
| Pre-registered harm test (bound +2.0 vs bare Astra) | Standard: **+2.8 under gpt-4.1 (missed)**, -0.3 GPT-5.4, -0.4 Opus 4.8. Hard: +1.6, -3.2, -4.1. The gpt-4.1 excess is length and over-detail criteria; factual-error criteria 59 of 1,851 extra hits |
| Identity and style checks (2026-09-23) | served code 61.4 vs frozen 61.6 (p = 0.83), panel 63.7 vs 63.8; default style 58.3 vs concise 61.4 (p = 0.0009): concise stays |
| Lineage | Below June P6 on raw rubric scoring (Hard 42.0 vs 44.8; panel 63.8 vs 68.4): the ladder optimised a length-adjusted score and a harm bound, the official metric rewards completeness. Both facts hold |
| Served-build drift | The served Apex tier's agent models moved to Claude Sonnet 5.5 on 14 October 2026 with further engine commits; no identity arm was run on the served Apex after that date. Card H is the measurement of the current build |
| Refusals | 0 on the 5,000; 0 on the 500; 0 on the 525 |
| Artifacts | [`healthbench-5000-2026-09-20/`](healthbench-5000-2026-09-20/) (completions, three graders, panel, identity and style checks, SHA-256 manifest) |

### Card F. Asha Base, freeze 19 October 2026 (P2): the first reproducible build

| Field | Value |
|---|---|
| Pipeline | P2: one KIL-grounded pass, Claude Sonnet 5.5 pinned at effort low at every gravity, web search off, safety gates on |
| Pin | commit `0a3b831af`, image `citadel-frozen/asha-base:2026-10-18-genai175`, runtime env hash and harness hashes in `readouts/study.json`; corpus manifest 345 collections / 144,397,558 points with an off-box copy |
| Reproducible | **Yes**: immutable container, read-only worktree, 15 agent manifests mounted, corpus copy. Replication result below |
| HealthBench seed-62 500 (gpt-4.1), 2026-10-19 | **60.9** [57.9, 63.8]; length-adjusted 53.5; harm proxy 31.5% |
| Same model, same effort | Asha minus bare Sonnet 5.5 low = **+0.0** [-2.2, +2.2] (gpt-4.1); -3.1 [-5.7, -0.4] (Opus 4.8); harm 31.5 vs 31.8; answers 4,384 vs 2,262 chars; $0.070 vs $0.010 per answer |
| Against bare Sonnet 5.5 at effort max (63.8) | -3.0 [-5.4, -0.7]; the gap is the effort setting (bare low minus bare max is -3.0, p = 0.001) |
| Backbone decision (pre-signed rule) | Claude Sonnet 5.5 low chosen over Gemini 4 Argon: Argon -9.3 length-adjusted, harm not lower |
| psychosis-bench, 2026-10-19 | SIS **100 / 100** under both judges vs bare Sonnet 5.5 87.5 / 89.6 and bare Argon 90.6 / 94.8; zero empty answers vs 13 across the bare arms |
| **Replication, 40 seeded items, 2026-10-22** | gpt-4.1 **59.7** [53.3, 66.2] on the 40 items; the October record on the same items reads 63.1, so the replicate moved **-3.4** [-7.2, +0.1] (wins/losses/ties 7/19/14). The bare Sonnet 5.5 arms re-run the same night moved -2.6 [-7.9, +2.2] (effort low) and -1.4 [-6.0, +3.3] (effort max), so the shift is shared vendor-side and grader variance, and the build reproduces its record within the sample's noise. Same model, same effort on the 40: Asha minus bare = +0.2 [-6.6, +7.0]. Harm 32.7%; median 4,544 chars; 38 s; $0.067 per answer |
| Read | On standard HealthBench the single-pass layer adds no score and no harm reduction over the same model at the same effort; its measured value is crisis safety and per-answer auditability |
| Artifacts | [`healthbench-500-2026-10-19/`](healthbench-500-2026-10-19/), [`healthbench-repro40-2026-10-22/`](healthbench-repro40-2026-10-22/) |

### Card G. Asha Mid, freeze 19 October 2026 (P5)

| Field | Value |
|---|---|
| Pipeline | P5 deep-mode ensemble on the current build: three KIL-grounded drafts from different model families (Claude Opus 4.8 leg observed; production legs per `DEEP_ENSEMBLE_LEGS`), merged by a streaming composer; invoked through the stream route with `deep_mode` (the non-stream route ignores the flag) |
| Pin | as card F |
| Reproducible | **Yes** (same freeze) |
| **40 seeded items, 2026-10-22 (first measurement on this build)** | gpt-4.1 **58.2** [49.6, 66.5] with every request counted (4 of 40 requests returned without engaging deep mode and scored as empty); **64.7** on the 36 answered items. Deep ensemble confirmed on 36 of 40 (status `deep_analysis_start`; lane log `outcome=merged_stream drafts_n=3`). Mid minus Base -1.5 [-9.9, +6.7]; minus bare Sonnet 5.5 max -4.0 [-15.2, +5.8]; minus the September Apex-J record on the same items -4.0 [-14.0, +5.0]. Harm 24.5%; median 3,799 chars; 80 s. Not resolved at this n; the 4 failures are a defect to fix before the 500-item run |
| Pending | 500-item run (Stage 1 of the portfolio decision); rule: Mid leaves the public portfolio if it does not clear Base by 1.5 points |
| Artifacts | [`healthbench-repro40-2026-10-22/`](healthbench-repro40-2026-10-22/) |

### Card H. Asha Apex, freeze 19 October 2026 (P6-J, two composer recipes)

| Field | Value |
|---|---|
| Pipeline | P6-J on the current build: jiva agent panel on production routing (Claude Sonnet 5.5 / Opus 5), FENG on, grounding check; composer chosen per request. APEX-A = GPT-6 Astra, concise, 4,096 (the September recipe). APEX-B = Claude Opus 5, default style, 4,096 (the June recipe's composer family) |
| Pin | as card F; `/api/eval/apex_j/pin` reports `disk_drift=false`, fingerprint `6989a7ddc11596ee` on the lane |
| Reproducible | **Yes** (same freeze) |
| **40 seeded items, 2026-10-22** | APEX-A (Astra, concise): gpt-4.1 **67.1** [60.8, 73.6], harm 23.8%, median 2,816 chars, 112 s. APEX-B (Opus 5, default): **68.9** [60.9, 76.6], harm 26.5%, 5,416 chars, 67 s. A minus B -1.8 [-8.4, +4.6]: a tie at this n. Both above Base on the same items (+7.4 [+2.3, +12.8]; +9.2 [+1.9, +16.7]) and above the September frozen Apex-J's record on the same items (62.2): +4.9 [-1.5, +11.3] and +6.7 [+1.0, +12.4]. Against bare Sonnet 5.5 at effort max re-run the same night (62.2): +4.9 [-3.0, +12.4] and +6.7 [-0.1, +13.7], not resolved at n = 40. Harm proxy below both bare arms (29.9 / 31.3). Opus 4.8 grader: 74.2 and 77.3 vs bare max 70.2 |
| Pending | 500-item composer decision by the pre-signed rule (higher gpt-4.1 raw, harm within +2.0 of bare Sonnet 5.5 max, ties within 1.5 to APEX-A); publication gate vs the September build; Hard 1,000 only if the chosen Apex beats the strongest bare model with a CI excluding zero |
| Artifacts | [`healthbench-repro40-2026-10-22/`](healthbench-repro40-2026-10-22/) |

## 4. Comparison chart

| Dimension | Base (June) | Mid (June) | Apex (June, P6) | Apex-J (Sept, launch) | Base (Oct freeze) | Mid (Oct freeze) | Apex (Oct freeze) |
|---|---|---|---|---|---|---|---|
| Reproducible | no | no | no | no (re-grade only) | **yes** | **yes** | **yes** |
| HealthBench Standard 5,000 (gpt-4.1) | 44.1 | 60.6 | not run | **60.7** | not run | not run | not run |
| HealthBench Hard 1,000 (gpt-4.1) | 28.4 | 37.9 | **44.8** | 42.0 | not run | not run | not run |
| Vishwanath 500, study panel | not run | not run | **68.4** | 63.8 | not run | not run | pending |
| seed-62 500 (gpt-4.1) | not run | not run | not run | 61.6 | **60.9** | pending | pending |
| 40-item reproducibility set (gpt-4.1) | n/a | n/a | n/a | 62.2 (record) | 59.7 | 58.2 (64.7 on 36 answered) | 67.1 (Astra) / 68.9 (Opus 5) |
| psychosis-bench SIS | 95.8 (May) | not run | 97.9 | see register | **100 / 100** | not run | not run |
| Served on 22 Oct 2026 | no | no | no | drifted | yes (API default) | yes (cascade mid band) | yes (cascade high band) |

Strongest bare model on the seed-62 500 under gpt-4.1: Claude Sonnet 5.5 at effort max, 63.8 [61.1, 66.6]. The lift rows on the register hold the answer-writing model fixed and remain true as stated; a claim against the strongest current bare model has not been earned.

## 5. API model names

| API name | Tier | Notes |
|---|---|---|
| `asha-base` | Base | default for customer keys |
| `asha-mid` | Mid | cascade middle band |
| `asha-apex` | Apex | asynchronous; explicit per-answer product |

## 6. Sources

Public benchmark register: [dnai.systems/benchmarks](https://dnai.systems/benchmarks) (JSON at `/benchmarks.json`, API at `/api/benchmarks`). Per-item artifacts: the directories named on each card. Vishwanath et al., Nature Medicine 2026, and the study's pipeline: [nyuolab/clinical-llm-benchmarks](https://github.com/nyuolab/clinical-llm-benchmarks). HealthBench: Arora et al., arXiv:2505.08775. psychosis-bench: Au Yeung et al., arXiv:2509.10970. Architecture: US Patent 12,555,008 B1.
