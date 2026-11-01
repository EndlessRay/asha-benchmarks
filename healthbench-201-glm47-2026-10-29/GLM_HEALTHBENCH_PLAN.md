# Asha Base on GLM-4.7-Flash vs GLM-4.7-Flash alone, 603 HealthBench items: analysis plan (2026-10-29)

Committed before generation. Free generation (open weights on Node B); grading by the open judge. Purpose: the
architecture's lift on a weak backbone, on the same 603 items as the current-build comparison (Claude Sonnet 5.5
backbone), so lift can be read against backbone strength. Exploratory; no claim is made from it without a
gpt-4.1 regrade.

## Arms

| Arm | What runs |
|---|---|
| `bare_glm` | GLM-4.7-Flash alone through `run_bare_model.py --provider hosted` against the Node B vLLM server of the psychosis rerun (same container and flags), no system prompt |
| `asha_glm` | Asha Base, lane `asha-curglm` (code `b9656ace4`, `BENCH_FORCE_MODELS=glm-4.7-flash`), `run_bare_model.py --provider asha-query` |

Items: `healthbench_data/emergency_gate_ab_2026-10-27.jsonl` (603; sha256 prefix `cd66beffed60920f`). One
generation per item. Concurrency 6 bare, 4 Asha. Runs after the psychosis rerun on the same server, never beside it.

## Amendment 1 (2026-10-29 18:37Z, before any HealthBench generation)

Measured decode throughput during the psychosis rerun: about 135 tokens per second across 8 concurrent requests
(GPU power-capped at 300 W; Asha contexts reach 57K tokens). At that rate the Asha arm on 603 items would take about
3.5 hours. Both arms run on a fixed subset instead: every third item of the 603 in file order (items 1, 4, 7, ...;
201 items), written to `healthbench_data/emergency_gate_ab_2026-10-27_every3.jsonl` before generation. The Sonnet 5.5
comparison is read on the same 201 items.

## Grading and outcomes

Open judge `flashlite-v1` on both arms. Primary: paired difference in mean item score, Asha minus bare, with the
hbjudge paired bootstrap CI, and the same difference length-adjusted (2.94e-5 per character above 2,000).
Secondary: harm proxy, refusals and empty replies, and the lift beside the Sonnet 5.5 comparison on the same
items (current build under the same judge). A gpt-4.1 regrade of both arms follows only if the result is to be
reported.

## Expectations stated in advance

Asha's raw lift on GLM exceeds its lift on Claude Sonnet 5.5, because the architecture's measured lift has been
largest where the backbone is weakest (psychosis-bench; HealthBench Hard). No numeric prediction is made for
the length-adjusted lift, since Asha's answers run about twice as long as bare answers.
