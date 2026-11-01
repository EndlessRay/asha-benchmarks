# Pre-registration: reference rubric rendering for every arm in the benchmarks paper (2026-10-31)

Written and committed before any grading in this round. Principal approval: /superstonk, 2026-10-31 21:20 ET.

## Why

`tests/healthbench_grader.py` on `main` shows the grader the criterion text alone. OpenAI's reference
implementation (`openai/simple-evals`, `healthbench_eval.py`, `RubricItem.__str__`) shows
`[points] criterion`. The pre-registered S1/S2 re-grade (`Docs/benchmarking/grader_validity_2026-10/`)
moved the frozen Apex-J and bare GPT-6 Astra pair to the reference rendering; this round moves every
other rubric-graded arm the benchmarks paper reports, so each table uses one rendering.

## Arms

| Set | Grader | Arms (5090 `healthbench_results/`) | Criteria re-graded |
|---|---|---|---|
| HealthBench Hard | GPT-4.1 | June Asha Base `single_hard_1000_gpu`, June Asha Mid `deepmode_hard_1000_gpu`, June Asha Apex `hard1000_apex_final` | penalty only |
| HealthBench Professional | GPT-5.4, reasoning low (official) | `hbp_20260911/`: `full_L9_concise_t1..t3`, `bare_gpt6astra_t1..t3`, `bare_gpt56sol_t1..t2`, `bare_fable51_t1..t2`, `bare_opus5_t1`, `bare_sonnet5_t1`, `bare_opus48_t1..t2`, `bare_gpt56luna_t1`, `bare_gemini38flash_t1`, `bare_gemini31pro_t1`, `bare_glass55_t1`, `bare_sonnet46_t1`, `p6_t1..t3`, `bare_asha_base_s5_t1..t2`, `physician` | penalty only |
| HealthBench Professional | Claude Opus 4.8 | `full_L9_concise_t1..t3`, `bare_gpt6astra_t1..t3`, `physician`, `bare_glass55_t1` | penalty only |

Not re-graded:
- Frozen Apex-J and GPT-6 Astra on all 5,000 (GPT-4.1): done in S1/S2; per-criterion verdicts in
  `bench_results/grader_arena/runs/`.
- May 2026 bare GPT-5.2, Gemini 3.1 Pro and Claude Opus 4.5 (`tests/benchmarks/healthbench_hard_4arm.py`):
  graded with `[points]` when run.
- GPT-5.4 and Claude Opus 4.8 sensitivity grades on the 5,000 items: kept as run (polarity errors 2 to 5%
  of omission verdicts, against 18 to 27% for GPT-4.1 without points; a re-grade would cost over $1,000).
- MedQA and psychosis-bench: not rubric-graded.
- GLM-5.2 on Hard (June 2026): answers not archived; the row is dropped.

## Method

1. Grader code: `tests/healthbench_grader.py` at `feat/cheap-grader-arena` `58e463404` (blob `93b77b31ff8f`),
   `--rubric-render points`, production settings identical to S1/S2: system message "You are an expert
   medical AI evaluator."; GPT-4.1 temperature 0.1, max_tokens 500; GPT-5.4 reasoning effort low; Claude
   Opus 4.8 default.
2. Inputs: each arm's archived answers with its rubric list restricted to criteria with negative points
   (`scripts/audits/grader_arena/points_regrade.py build`). One grading pass per criterion.
3. Merge (`points_regrade.py merge`): positive-criterion verdicts from the as-run grade file (rendering does
   not move them: 96.1% agreement, kappa 0.906 in S1b), penalty verdicts from this round, matched by position
   with a criterion-text and points check. An item with a failed grader call is excluded, as in
   `hbp_score.py`.
4. Validation before use: the as-run grade file of each arm, scored by the same code, must reproduce the
   published as-run number within 0.1 point; otherwise the arm is reported as run and labelled.
5. Scoring: HealthBench, achieved points over positive points per item, mean clipped to [0, 1], with the
   HealthBench Professional length adjustment where the paper reports it; HealthBench Professional,
   `scripts/audits/healthbench_professional/hbp_score.py` unchanged (length-adjusted, trials pooled).
   Paired tests as in the paper (paired t, exact sign test).
6. Harm: penalty criteria met over penalty criteria present, pooled. Severe-harm agreement on Hard: items
   where GPT-4.1 (`[points]`), GPT-5.4 and Claude Opus 4.8 all mark a criterion worth -9 or -10 met in one
   arm's answer and none marks one met in the other's.

## Decision rule

Every rubric-graded table and figure in the benchmarks paper reports the reference rendering for every
arm re-graded here; as-run numbers stay in the artifacts. An arm with more than 2% failed grader calls
in this round is reported as run and labelled. No result in this round changes which arms are compared.

## Budget

Cap USD 250 across OpenAI and Anthropic; the grader stops on quota or billing errors.

## Amendment 1 (2026-10-31 21:31 ET, before any usable data)

The grader's own loop saves a row only when its score is defined; a penalty-only item has no positive points,
so the first launch (01:29 to 01:31 UTC) saved nothing and was stopped. `points_regrade_drive.py` calls the
same `HealthBenchGrader.grade_sample` (same prompt, rendering and model settings) and writes every row; it
stops a run when more than half of its first 100 criterion calls fail. No grading choice changes.
