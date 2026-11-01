# Asha Base on GLM-4.7-Flash vs GLM-4.7-Flash alone, 201 HealthBench items: readout (2026-10-29)

Plan: `GLM_HEALTHBENCH_PLAN.md` (amendment 1: every third item of the 603, 201 items, for throughput). Generated
22:24Z to 23:41Z on the Node B vLLM server of the psychosis reruns (same weights and flags); Asha arm on lane
`asha-curglm` (code `b9656ace4`, every call pinned to `glm-4.7-flash`). Zero errors or empty answers in either arm;
the 150-minute cap on the Asha arm was not reached. Per-item files on the 5090 in
`healthbench_results/glm_healthbench_20261029/`.

| Grader | bare GLM-4.7-Flash | Asha on GLM-4.7-Flash | Asha minus bare (95% CI) | n |
|---|---:|---:|---|---:|
| gpt-4.1 (v3 grader) | 49.43 | 49.97 | +0.54 (-4.06 to +5.22) | 201 |
| Open judge | 47.0 | 46.5 | -0.52 (-5.82 to +4.79) | 200 (one bare item lost to a judge error) |
| Open judge, length-adjusted | | | -7.84 | 200 |

Median answer length: Asha 3,974 characters, bare 2,622.

For reference on the same 201 items under the open judge, Asha on Claude Sonnet 5.5 (`current`, 29 Oct) scores 25.0
points above Asha on GLM (20.2 to 29.8): the backbone accounts for most of the HealthBench score.

## Against the expectation stated in the plan

The plan expected Asha's raw lift on GLM to exceed its lift on Claude Sonnet 5.5, because the measured lift had been
largest where the backbone is weakest. The raw lift on GLM is nil under both graders, so the expectation fails on
HealthBench (the lift on Sonnet 5.5 itself was not measured here, since this round ran no bare Sonnet 5.5 arm). On the
same backbone and server, the psychosis-bench lift is +79.1 points. The architecture moves safety behavior on a weak
open model; it does not move rubric completeness on HealthBench for that model.

## Limits

One generation per item; 201 items resolve about 5 points; the open judge and gpt-4.1 agree in reading (both null).
GLM-4.7-Flash ran with thinking disabled in both arms, as in the psychosis runs.
