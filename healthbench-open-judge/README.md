# healthbench-open-judge

Grade [HealthBench](https://arxiv.org/abs/2505.08775) with an open-weight or low-cost judge, and know how far to trust the grade.

**Status: v0.1.0, released 2026-10-29.** `flashlite-v1` passed the gate in [VALIDATION.md](VALIDATION.md) on 2026-10-28. `oss120b-v1` did not pass alone; with `flashlite-v1` it forms a two-judge panel that cancels vendor leanings. A judge profile is recommended only after it passes delta replication against the official grader on real model pairs, the self-preference and missing-grade checks, the polarity audit, physician agreement with confidence intervals, and a holdout set it was never tuned on.

## Why

HealthBench's official grader is GPT-4.1, called once per rubric criterion: a full 5,000-conversation run is 57,237 calls (about 1,400 prompt tokens each). A cheap judge only helps if it makes the same decisions about which model is better. This harness keeps everything else fixed (the official grader prompt, verbatim; the official scoring) and swaps only the judge, so the judge is the single thing being validated.

## What is fixed

| Element | Value |
|---|---|
| Grader prompt | `GRADER_TEMPLATE` from `openai/simple-evals` (MIT), byte-identical; sha256 recorded in every run |
| Rubric item | rendered as `[points] criterion`, as simple-evals does, so the judge sees which items are penalties |
| Example score | achieved points over positive points, unclipped |
| Run score | mean of example scores clipped to [0, 1], 1,000-sample bootstrap std |
| Tags | theme / category tags score the whole example; axis tags score only their criteria |
| Judge settings | one frozen profile per judge (model, endpoint, system message, temperature, reasoning effort, token budget); a change is a new profile name |

## What it adds

- **Missing grades are reported, never invented.** An unparsable reply is re-asked up to 5 times; if it still has no boolean verdict, the grade is missing, the example is excluded, and the summary gives the score as it would be with missing grades counted as "not met". Some pipelines turn any reply containing the word "true" into a verdict; this one does not.
- **Polarity audit.** Every run counts penalty criteria phrased as omissions ("Fails to mention X") that the judge marked met while its own explanation says X is present.
- **Paired comparison.** `hbjudge compare` gives the difference between two graded runs on their common complete examples, with a bootstrap CI.
- **Physician check.** `hbjudge validate` scores any judge against the physician labels in OpenAI's public meta-eval with OpenAI's metric (pooled pairwise balanced F1), next to the typical-physician baseline, with CIs. On our setup this reproduces OpenAI's published GPT-4.1 (0.709) and GPT-4.1-mini (0.661) values within the confidence interval.

## Use

```bash
pip install -e .
curl -LO https://openaipublic.blob.core.windows.net/simple-evals/healthbench/2025-05-07-06-14-12_oss_eval.jsonl

# completions: one JSON per line, {"prompt_id": ..., "completion": "..."}
export GEMINI_API_KEY=...          # low-cost hosted judge
hbjudge grade --data 2025-05-07-06-14-12_oss_eval.jsonl --completions my_model.jsonl \
  --profile flashlite-v1 --out runs/my_model

# free, local: serve openai/gpt-oss-120b (vLLM, SGLang, Ollama, llama.cpp) on an OpenAI-compatible endpoint
hbjudge grade --data 2025-05-07-06-14-12_oss_eval.jsonl --completions my_model.jsonl \
  --profile oss120b-v1 --base-url http://localhost:8000/v1 --out runs/my_model_oss

hbjudge compare runs/model_a/graded.jsonl runs/model_b/graded.jsonl
hbjudge panel runs/my_model/graded.jsonl runs/my_model_oss/graded.jsonl --out runs/my_model_panel
hbjudge validate --meta-eval 2025-05-07-06-14-12_oss_meta_eval.jsonl --profile flashlite-v1 --n 3000 --out runs/validate
```

Other sets: `hard_2025-05-08-21-00-10.jsonl`, `consensus_2025-05-09-20-00-46.jsonl` (same base URL; see `hbjudge/cli.py`).

## How to use the result

A validated cheap judge is a screening and sensitivity grader. It is suited to iterating on a system, ranking candidate configurations, and confirming that a result does not depend on one vendor's grader. Report headline numbers under the official grader, or state the judge next to every number, because a judge's absolute level can differ from GPT-4.1's even when its rankings and paired differences agree. Scores from different judges are not interchangeable. When the systems you compare come from different vendors, grade with both `flashlite-v1` and `oss120b-v1` and compare panel runs: each judge leans slightly toward its own vendor's answers, in opposite directions.

## Layout

| Path | Contents |
|---|---|
| `hbjudge/template.py` | official grader prompt and rubric-item rendering |
| `hbjudge/judges.py` | frozen judge profiles and their validation status |
| `hbjudge/client.py` | OpenAI-compatible client, retry policy, strict verdict parsing |
| `hbjudge/grading.py` | grading, simple-evals aggregation, missing-grade and polarity accounting, paired deltas |
| `hbjudge/cli.py` | `grade`, `compare`, `panel`, `validate` |
| `VALIDATION.md` | the evidence for each profile |
| `tests/` | offline tests (template hash, scoring, parsing, polarity) |

License: Apache-2.0 for this code; the grader prompt and the datasets are OpenAI's (MIT), see `../NOTICE.md`.
