# Psychosis-bench, Gemini 2.5 Flash held fixed, recall channel removed: pre-registration (2026-10-29)

Written and pushed before any generation. Fills placeholder P-2 of the nonmaleficence manuscript ("Re-run B:
psychosis-bench, Asha on Gemini 2.5 Flash, served code") and the May half of PENDING-R in the benchmarks v2
manuscript. Replicates the 11 May 2026 run (`asha-benchmarks/psychosis-bench-2026-05-11`) with two intended
differences: the Asha arm runs current `main` (`b9656ace4`, cross-session recall removed for shared identities by
#1513), and every Gemini call in the Asha arm is pinned to `gemini-2.5-flash` (in May the deployed routing sent about
30% of turns to `gemini-2.5-pro`). Both models still answer on Vertex (checked on 29 October, before this file was written).

## Arms

| Arm (harness label) | What runs | Where |
|---|---|---|
| `gemini_flash` | `gemini-2.5-flash` alone through Vertex AI (harness `GeminiFlashArm`), no system prompt | Vertex, project `asha-484621` |
| `asha` | Asha Base, current code, `LLM_PROVIDER=google_vertex`, `GEMINI_MODEL_PRO`, `GEMINI_MODEL_FLASH`, `GEMINI_MODEL_PRO_GA`, `GEMINI_MODEL_FLASH_GA` and `GEMINI_MODEL_FLASH_LITE` all `gemini-2.5-flash`, `LLM_FALLBACK_PROVIDER` empty (no failover to another vendor), bench pin `gemini-2.5-flash` with web search off | Node A lane `asha-curg25` (port 8035): image `citadel-frozen/asha-base:2026-10-18-genai175`, `runtime.env` of the v3 freeze, refdata of the frozen lanes |

The pin is verified from the lane's `LLM_ACCOUNTING` lines after a 3-turn smoke and again after the run; any model
other than `gemini-2.5-flash` stops the run.

## Protocol

Harness `scripts/audits/psychosis_bench_asha/run_bench_two_judges.py` from the run-4b worktree
(`/home/deepan/frozen/asha-base-v2-2026-10-18/repo-cal`), unchanged: 16 scenarios, 12 turns, all scenarios, one
trial, scenario concurrency 4. Judge A `gpt-4o-mini` (protocol judge), judge B `claude-haiku-4-5`. Runs after the GLM
HealthBench comparison frees the GPU, never beside another Claude or GLM lane.

## Predictions

1. Bare Gemini 2.5 Flash SIS below 70% under judge A (May: 30.2%).
2. Asha SIS at least 20 points above bare, and higher in at least 12 of 16 scenarios, under each judge.
3. Asha DCS and HES below bare under both judges.
4. Replication. May's Asha SIS under judge A (95.8%) lies inside this run's Wilson 95% interval for Asha, or the two
   differ by at most 5 points. If this holds with (2), the May figures stand in both manuscripts with this run cited as
   the recall-free replication; if not, this run's figures replace them.
5. Judge agreement (kappa on SIS) below 0.60; direction agreement reported.

Failed turns (timeouts, empty replies) are reported, and SIS is given as run, with failed turns excluded, and with
failed turns counted as no intervention. The stopping rule of the GLM rerun (more than 5% failed turns in either arm)
applies and is checked by the driver after the run; the operator also checks the count every 30 minutes.

## Cost

Gemini 2.5 Flash for both arms (about 7 USD), judges about 5 USD.

## Amendment 1 (2026-10-29, after the 3-item smoke, before any psychosis-bench generation)

The lane's `LLM_ACCOUNTING` lines record Anthropic and OpenAI calls only, so they list no models for a Gemini lane,
and the lane reports `pin_ok=False` on every request. The smoke itself answered normally: all 7 Vertex requests went
to `publishers/google/models/gemini-2.5-flash:generateContent`, with no request to Anthropic or OpenAI. Pin
verification therefore uses the lane's Vertex request URLs and the absence of other vendor hosts, before and after the
run. The harness attaches a "pin not honored" note to every Asha turn because it reads `pin_ok`; those turns keep their
responses and are judged as usual. A failed turn is one with an empty response or an HTTP failure.

## Deviation 1 (2026-10-30 00:16Z, before any bare-arm turn was generated or judged)

The first run (23:53Z to 00:15Z) produced all 192 Asha turns with no failure (392 Vertex requests, all
`gemini-2.5-flash`, none to another vendor), and no bare turn: every `gemini_flash` turn failed with "missing key:
GOOGLE_API_KEY" because the driver set neither that key nor `GEMINI_VIA_VERTEX`. The bare arm is rerun alone with the
same harness, scenarios and judges, through Vertex (`GEMINI_VIA_VERTEX=true`, the May routing), and its turns are
combined with the Asha turns of the first run. Each arm's conversations and judgments are independent of the other
arm's, so the combination changes nothing the protocol compares.
