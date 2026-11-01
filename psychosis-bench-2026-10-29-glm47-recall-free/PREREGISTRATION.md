# Psychosis-bench, GLM-4.7-Flash held fixed, recall channel removed: pre-registration (2026-10-29)

Written and pushed before any generation. Replicates run 4b of 2026-10-28
(`Docs/benchmarking/psychosis_glm47_2026-10/`) with one intended difference: the Asha lane runs current `main`
(`b9656ace4`), which removed cross-session recall for shared identities (#1513, 2026-10-28). In run 4b the
Asha arm's recall pool held the preceding scenarios' turns, so Asha could see its own earlier interventions and the
bare arm could not. This run fills placeholder P-1 of the nonmaleficence manuscript and part of PENDING-R of the
benchmarks v2 manuscript.

This is a pre-final-build replication. If the principal's final frozen build differs from `b9656ace4`, the
psychosis arms of `Docs/benchmarking/psychosis_final_build_2026-11/` are run on it as planned; this run does not
replace them.

## Arms

| Arm | What runs | Where |
|---|---|---|
| `bare_glm47flash` | GLM-4.7-Flash alone, no system prompt, conversation verbatim | Node B vLLM container `bench-glm47flash` (vLLM, BF16, `--max-model-len 131072`, `--max-num-seqs 8`, thinking off through `--default-chat-template-kwargs`, GPU power-capped at 300 W), port 8010 |
| `asha_glm` | Asha Base, every LLM call pinned to the same server (`BENCH_FORCE_MODELS=glm-4.7-flash`, Anthropic Messages API through `bench-litellm-glm`) | Node A lane `asha-curglm`, port 8034: image `citadel-frozen/asha-base:2026-10-18-genai175`, code `b9656ace4`, env files of run 4b (`asha-base-v3-2026-10-19/runtime.env`, `asha-base-v3-glm-2026-10-27/runtime-glm.env`), refdata of run 4b |

Same server, weights and decoding defaults for both arms. Code differences from run 4b's lane (`0a3b831af`) besides
#1513: the emergency vector gate, entropy caution, the dosing ruling, evidence passages reaching synthesis whole
(#1561, #1564, #1576), the reconciled active inference engine (advisory) and the new promotion gate (outside the
answer path). The run therefore tests whether the run-4b result holds on current code with recall removed; it does
not attribute any change to one of these.

## Protocol

Harness `scripts/audits/psychosis_bench_asha/run_bench_two_judges.py` from the run-4b worktree
(`/home/deepan/frozen/asha-base-v2-2026-10-18/repo-cal`), unchanged: 16 scenarios, 12 turns, all scenarios, one
trial, scenario concurrency 4. Judge A `gpt-4o-mini` (protocol judge), judge B `claude-haiku-4-5`, prompts
byte-identical to run 4b. Readout: `Docs/benchmarking/psychosis_glm47_2026-10/_tools/readout.py`, unchanged.

## Predictions

1. Bare GLM-4.7-Flash SIS below 70% under judge A.
2. Asha SIS at least 20 points above bare, and higher in at least 12 of 16 scenarios, under each judge.
3. Asha DCS and HES below bare under both judges (ratio intervals exclude 1).
4. Replication. Run 4b's Asha SIS under judge A (96.9%) lies inside this run's Wilson 95% interval for Asha SIS
   under judge A, or the two differ by at most 5 points. If this holds with (2), the P-1 markers are deleted and the
   run-4b figures stand with this run cited as the recall-free replication. If it fails, this run's figures replace
   run 4b's in both manuscripts and the May-run sentence is re-weighed, as P-1 states.
5. Judge agreement (Cohen's kappa on SIS) below 0.60, so the formal verdict under the original rule stays
   inconclusive; direction agreement across judges is reported.

## Stopping rules

Stop and record if the Node B GPU reaches 89 C, if more than 5% of turns in either arm return an error or an empty
reply, or if the lane's pin check reports any model other than `glm-4.7-flash`. Resume only on the same output
directory with the harness's idempotent resume, and log every restart in `driver.log`.

## Cost

Generation is local (no vendor cost). Judges: 2 arms x 192 turns x 2 judges, about 5 USD.
