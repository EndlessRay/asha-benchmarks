# HealthBench seed-62 500, October 2026: the frozen Asha Base beside its bare models

Run 2026-10-19 19:33Z to 2026-10-20 02:15Z under a signed GO (two Asha Base arms, each beside its bare model, one pre-signed backbone rule). Build: `asha-base-v3-2026-10-19`, commit `0a3b831af3cf14e7f6ad3bfd973fc5472d5e184f`, an immutable container with a read-only worktree; provenance hashes in `readouts/study.json`. This is the first Asha measurement on a build that can be re-run.

## Items

`hb500_seed62_standard_items.jsonl`: 500 HealthBench conversations, the same seed-62 sample used for the September Apex-J readout (`../healthbench-5000-2026-09-20/readouts/official_readout_hb5000_seed62.json`) and for the Vishwanath et al. comparison. SHA-256 `3819220cc6c920150b21f31503f84acd9f34c8040367003b4f36b8912ae3e72b`.

## Arms

| Directory | Arm | What ran |
|---|---|---|
| `asha-base-v3-claude-sonnet-5-5-low/` | **Asha Base** (P2) | pinned to Claude Sonnet 5.5, effort low at every gravity, web search off, retrieval on, safety gates on |
| `asha-base-v3-gemini-4-argon/` | Asha Base on Gemini 4 Argon | pinned, gravity-mapped thinking level; rejected by the signed rule |
| `bare-claude-sonnet-5-5-effort-max/` | bare Claude Sonnet 5.5 | adaptive thinking, effort max, no retrieval, no system prompt; 6 items truncated at 64K output tokens were regenerated at 128K (originals in `truncated_at_64k_originals.jsonl.gz`) |
| `bare-claude-sonnet-5-5-effort-low/` | bare Claude Sonnet 5.5, effort low | diagnostic added 2026-10-20 after the readout, to separate the Asha layer from the effort difference |
| `bare-gemini-4-argon-level-high/` | bare Gemini 4 Argon | Vertex global endpoint, thinking level high |

Each arm directory holds `completions.jsonl.gz` (prompt, rubrics, answer, a metadata block with model, effort, tokens, elapsed seconds, refusal and empty-answer flags), `graded_gpt_4_1.jsonl.gz` (the official HealthBench grader) and `graded_claude_opus_4_8.jsonl.gz` (sensitivity grader). Internal trace and routing fields were removed before publication; the per-item answers and grades are complete.

## Results (gpt-4.1, HealthBench's official metric; 0 to 100)

| Arm | Score [95% CI] | Length-adjusted | Harm proxy | Median chars | Cost per answer | Median time |
|---|---|---|---|---|---|---|
| Asha Base, Sonnet 5.5 low | 60.9 [57.9, 63.8] | 53.5 | 31.5% | 4,384 | $0.070 | 18 s |
| Asha Base, Argon | 59.5 [56.0, 63.1] | 44.2 | 34.9% | 7,200 | $0.128 | 33 s |
| bare Sonnet 5.5, effort max | 63.8 [61.1, 66.6] | 60.7 | 29.7% | 2,356 | $0.089 | 31 s |
| bare Sonnet 5.5, effort low | 60.8 [57.9, 63.7] | 59.3 | 31.8% | 2,262 | $0.010 | 8 s |
| bare Argon, level high | 57.7 [54.8, 60.6] | 51.0 | 33.1% | 4,072 | $0.022 | 32 s |

Paired differences on the same items:

| Comparison | gpt-4.1 raw | gpt-4.1 length-adjusted | Opus 4.8 raw |
|---|---|---|---|
| Asha Base minus bare Sonnet 5.5 at the same effort (low) | **+0.0** [-2.2, +2.2], p = 0.999 | -5.8 [-8.0, -3.7] | -3.1 [-5.7, -0.4], p = 0.024 |
| bare Sonnet 5.5 low minus max (effort alone) | -3.0 [-4.8, -1.2], p = 0.001 | -1.4 [-3.2, +0.4] | -1.7 [-3.7, +0.3] |
| Asha Base minus bare Sonnet 5.5 max (the signed comparison) | -3.0 [-5.4, -0.7], p = 0.012 | -7.3 [-9.5, -5.0] | -4.5 [-6.9, -2.1] |
| Asha-Argon minus bare Argon | +1.8 [-1.4, +5.0], p = 0.27 | -6.9 [-10.1, -3.7] | -0.1 [-2.4, +2.3] |
| Asha-Argon minus Asha-Claude-low | -1.3 [-3.9, +1.2], p = 0.31 | -9.3 [-11.9, -6.8] | -1.8 [-4.0, +0.3] |

Harm proxy = share of negative-point rubric criteria the answer triggers. Pre-signed gate: Asha within +2.0 points of its bare model. Both Asha arms pass at +1.8.

**Read.** On standard HealthBench the single-pass Asha layer adds no score over the same model at the same effort, and no harm reduction; it writes answers about twice as long at seven times the cost. The signed backbone rule chose Claude Sonnet 5.5 at low effort over Gemini 4 Argon (Argon -9.3 length-adjusted, harm not lower). Note that bare Sonnet 5.5 at effort max (63.8) is above the frozen September Apex-J (61.6) on these same items under this grader.

## psychosis-bench (same build), `psychosis/`

16 scenarios, 96 intervention-eligible turns per arm; judge A gpt-4o-mini (the benchmark's protocol judge), judge B claude-haiku-4-5. `per_turn.jsonl.gz` and `per_turn_judge_b.jsonl.gz` hold every turn with both judges' scores and rationales.

| Arm | SIS judge A [95% CI] | SIS judge B [95% CI] | DCS A / B | HES A / B |
|---|---|---|---|---|
| Asha Base, Sonnet 5.5 low | **100** [96.2, 100] | **100** [96.2, 100] | 0.139 / 0.118 | 0.042 / 0.146 |
| Asha Base, Argon | **100** [96.2, 100] | **100** [96.2, 100] | 0 / 0.014 | 0 / 0 |
| bare Sonnet 5.5 | 87.5 [79.4, 92.7] | 89.6 [81.9, 94.2] | 0.132 / 0.229 | 0.083 / 0.188 |
| bare Argon | 90.6 [83.1, 95.0] | 94.8 [88.4, 97.8] | 0.09 / 0.174 | 0.115 / 0.177 |

The bare arms returned 13 empty answers between them; the Asha arms none. Crisis safety is where the single-pass layer measurably adds value on this build.

## Re-grading

A plain mean of the per-item `score` field in each `graded_gpt_4_1.jsonl.gz` reproduces the table within 0.1 (the readout uses the HealthBench scoring code with clipping and bootstrap intervals; `readouts/readout.json` has the exact values). Re-grade `completions.jsonl.gz` with the official grader from [openai/simple-evals](https://github.com/openai/simple-evals) and compare. `MANIFEST.json` carries SHA-256 for every file.

## Not in this bundle

The red-team decision study that chose the effort setting (50 HealthBench Professional red-team items) is not published: those items are withheld at OpenAI's request, and the study was a configuration choice, never a headline. Its aggregates are quoted in `BENCHMARK_TIMELINE.md`.
