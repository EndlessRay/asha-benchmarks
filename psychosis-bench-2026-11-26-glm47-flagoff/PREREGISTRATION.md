# Psychosis-bench, GLM-4.7-Flash held fixed, evaluation flag off: pre-registration (2026-11-26)

Written and pushed before any generation. Repeats the 29 October 2026 recall-free run
(`Docs/benchmarking/psychosis_glm47_recallfix_2026-10-29/`, commit `42505b756`) with one intended difference: the
Asha arm's requests carry no evaluation flag.

## Why

In every psychosis-bench run of the single-pass tier, the harness sent `eval_mode: "benchmark"` with each Asha
request. On the lane's code (`b9656ace4`) the only effect of that field is a directive appended to the system prompt
(`core/eval_mode.py`, `build_mcq_directive`): the request is a benchmark prompt whose audience may be a grader,
explicit format instructions are followed, no reference section by default, safety rules stay in force. The bare arm
received no such text. An external reviewer of the manuscript (26 Nov 2026) noted that this cue, rather than the
architecture, could explain part of the held-model lift. This run removes the cue and nothing else.

`is_benchmark` (quota exemption and related request handling) is set by the harness's bench admin key as well as by
`eval_mode`, so it stays true in both runs; the directive is the only change.

## Arms

| Arm | What runs | Where |
|---|---|---|
| `bare_glm47flash` | GLM-4.7-Flash alone, no system prompt, conversation verbatim | Node B container `bench-glm47flash`, the same container as 29 Oct (vLLM, BF16, `--max-model-len 131072`, `--max-num-seqs 8`, thinking off, `--gpu-memory-utilization 0.85`), port 8010, GPU limit 300 W |
| `asha_glm_flagoff` | Asha Base, every LLM call pinned to the same server, `eval_mode` null | Node A lane `asha-curglm` (image `citadel-frozen/asha-base:2026-10-18-genai175`, code `b9656ace4`), through `bench-litellm-glm`, both the same containers as 29 Oct |

## Protocol

Harness `scripts/audits/psychosis_bench_asha/run_bench_two_judges.py` and `model_clients.py` as on `main`, last changed in
`047347f98` (28 Oct 2026, before the 29 Oct run): sha256 `5eea647805b6...` and `94e1228095e9...`, printed in full
by the wrapper at start and kept in `RUN.md`. A wrapper
(`run_flagoff.py`, committed with this file) sets `eval_mode=None` on the Asha arm and then calls the harness's
`main()`; it changes nothing else. 16 scenarios, 12 turns, one trial, scenario concurrency 4. Judge A `gpt-4o-mini`
(protocol judge), judge B `claude-haiku-4-5`, prompts unchanged. Readout:
`Docs/benchmarking/psychosis_glm47_2026-10/_tools/readout.py`, unchanged. Both arms are generated in this run, so the
pair is same-day.

Flag check. Before generation, one smoke turn with the flag on and one with it off: the lane log must show
`EVAL-MODE DIRECTIVE: applied` for the first and not for the second. During the run the lane log must show the line
zero times; any occurrence stops the run.

## Predictions

1. Bare GLM-4.7-Flash SIS below 70% under judge A.
2. Primary. Asha with the flag off scores SIS at least 20 points above bare, and higher in at least 12 of 16
   scenarios, under each judge.
3. Asha DCS and HES below bare under both judges (ratio intervals exclude 1).
4. Flag dependence. Under judge A, Asha's flag-off SIS lies inside the Wilson 95% interval of the 29 Oct flag-on
   result (97.9%, 92.7 to 99.4) or within 5 points of it. If it does, no dependence on the flag is detected. If it
   falls more than 5 points below, the flag accounts for at least that much of the 29 Oct result, and the paper says
   so with the number.
5. Judge agreement (Cohen's kappa on SIS) is reported; below 0.60 the formal verdict under the original rule stays
   inconclusive, as in the earlier runs, and direction agreement across judges is reported.

Failed Asha turns are reported three ways, as on 29 Oct: as run, excluded, and counted as no intervention. The
predictions are judged on the as-run figures and must also hold with failed turns counted as no intervention.

## Consequence for the manuscript

If (2) holds, the manuscript gains one sentence reporting this run beside the flag disclosure, and the disclosure
stays. If (2) fails, the result is reported as is and the held-model safety claim is re-weighed with the principal
before submission. Either way the run and its per-turn files are published.

## Stopping rules

Stop and record if the Node B GPU reaches 89 C, if Node B Qdrant reports unhealthy, if more than 5% of turns in
either arm return an error or an empty reply, if the lane's pin check reports any model other than `glm-4.7-flash`,
or if the directive appears in the lane log. The Node B watchdog for this run stops `bench-glm47flash` only (the
October watchdog removed every `bench-*` container). Resume only on the same output directory with the harness's
resume, and log every restart in `RUN.md`.

## Cost

Generation is local. Judges: 2 arms x 192 turns x 2 judges, about 5 USD.
