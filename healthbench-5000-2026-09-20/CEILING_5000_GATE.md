# Ceiling gate: 525 Professional -> 5,000 Standard single Apex run

Pre-registered 2026-09-18 20:30 ET (Polymath, bench owner), before the
525 x 2 pre-freeze readout exists. Analysis battery: `CEILING_5000_ANALYSIS_DESIGN.md`
(Lyra + Polymath). Nothing in this file changes after the readout lands; if a
rule proves wrong, the change is written as a dated amendment below it.

## 1. What is being decided

The ceiling ladder closed 2026-09-18 with incumbent **Apex-J, GPT-6 Astra
composer, concise style** (300-slice: 69.4 length-adjusted, GPT-5.4 grader;
pooled K=2 vs the 16 Sep Fable baseline +6.4, p=0.007, harm -8.8, red-team
harm -12.0). The pre-freeze run now on `dnai-api` is that incumbent on all 525
Professional items, two trials, against bare GPT-6 Astra 525 x 2 already on
record (same pin, same three graders). Its readout decides whether the build
freezes and the single 5,000-item HealthBench Standard run fires.

Comparator on record (GPT-5.4 official grader, 525, length-adjusted):
bare Astra t1 65.34, t2 64.42, pooled about 64.9 (raw about 68.8).
September board for the floor: Apex-J Fable 5.1 composer 59.66, Apex-J
default 56.41, P6 54.91.

## 2. Trigger rule (pre-registered)

Readout: `hbp_ceiling_readout.py --dataset prof_dataset_clean.jsonl
--candidate full_L9_concise --incumbent bare_gpt6astra`, paired on the 525
shared items, pooled K=2 on both sides.

| Outcome | Condition (all parts required) | Action |
|---|---|---|
| **GO-A, superiority** | official length-adjusted diff >= +3.0 (so pooled >= about 67.9) with paired p < 0.05; sensitivity grader (Opus 4.8) same sign or within 1.5; harm rate and red-team harm rate not above Astra; empty answers and refusals not above Astra; pin identical across both trials | freeze the build, fire the 5,000 run on the principal's approval |
| **GO-B, safety-dominant parity** | diff inside (-1.5, +3.0); harm rate at least 5 points below Astra overall AND on red-team items; every other gate as in GO-A | freeze and fire; the public claim is "safer at equal score", never "higher" |
| **HOLD** | diff <= -1.5, or any gate fails, or pin drift between trials | no 5,000 run; diagnose on the 300 slice, fix, re-run 525 x 2 |

Two more conditions, both required for either GO:

- Board floor: pooled incumbent >= 62.7 (September board best Apex-J 59.66
  plus 3). A ceiling that does not clear the published board by the adopt
  margin is not a ceiling.
- Holdout: the 225 never-tuned items (`prof_holdout225.jsonl`, restricted
  from the same 525 trials) read NEUTRAL or better against bare Astra on the
  same ids. A slice gain that vanishes on untouched items is tuning, not
  capability.

Expected under the slice result carrying over: pooled about 68 to 69,
diff about +3 to +4, GO-A. If the diff lands in (+1.5, +3.0) with p < 0.05
the rule says HOLD; the amendment path is a third trial per side
(`HBP_TRIALS=3`), not a lowered bar.

## 3. Harness and repository: bulletproof before the 5,000 fires

Each item is a checkbox the bench owner ticks in the ledger before
`GO_5000` is written. The 5,000 run costs roughly ten 525 trials; a schema
failure like the 18 Sep raw-file 422 at that scale burns a day.

1. **Dataset validator as a hard gate.** `run_hbp_battery.sh` and
   `run_bare_arm.sh` refuse to start unless every row has `prompt_id`,
   `prompt` (list of role/content turns with a non-empty user turn),
   `rubrics`, `example_tags`; they print the row count and the SHA-256 of
   the file into `config.json`. The raw OpenAI schema (`id`,
   `conversation.messages`, `rubric_items`) is rejected by name with the
   normalizer command in the error text.
2. **Three-item preflight, end to end.** Generate three items, grade them
   with all three graders, run the readout script on them, then start the
   real run. Any 4xx from `/api/eval/apex_j` aborts before item four.
3. **Pin recorded and asserted.** `pin_start.json` at start, `pin_end.json`
   at finish, the run is void if they differ; `git_sha.txt` of the host
   checkout and the container's image digest in `config.json`. No
   `--allow-drift` on the 5,000 run: the lane container is restarted on the
   frozen commit first, then nothing restarts it.
4. **Resumable, idempotent generation.** Existing records skipped by
   `prompt_id` (already true); the driver retries transient 5xx and
   timeouts with backoff and records permanent failures per item; the
   completeness check tolerates at most 5 hard failures in 5,000 and lists
   them by id.
5. **Grader completeness.** Empty completions are scored as zero, never
   dropped (fixed 9/13); grader call failures are stored as `grader_error`,
   never as `met=false`; a trial is graded only when graded rows equal
   generated rows.
6. **Contamination probe before the run.** Canary strings from the 5,000
   file checked against the corpus; embedding nearest-neighbour probe on a
   200-item stratified sample against every knowledge collection the incumbent
   retrieves from, with `_DYNAMIC_EXCLUDE_NAMES` (`ciu_chain`,
   `inference_cius`, `cognition_cius`, `vague_queries`, `healthbench_*`) in
   force. Hits are excluded by id and listed.
7. **Frozen artifacts, versioned.** The waiter scripts that today live only
   in `healthbench_results/hbp_20260911/` (`fullset_waiter.sh`,
   `base_lane_queue.sh`, `r1_test_waiter.sh`, `p2_evidence_waiter.sh`) are
   committed under `scripts/audits/healthbench_professional/waiters/`; the
   frozen build gets an annotated git tag `freeze-2026-09-<dd>`; the
   register row cites the tag, the pin, the dataset SHA, and the grader
   model strings.
8. **One writer, one lock.** The 5,000 run holds the battery lock; Base and
   Mid freeze arms run through the bare runner (separate lock) so they do
   not collide; no other Apex-J generation on the lane until `FULL5000_DONE`.
9. **Budget guard.** Model spend logged per item; the driver pauses at the
   configured ceiling (section 5) and alerts via `notify.sh` instead of
   running past it.
10. **Off-box copies.** Results directory rsynced to the NAS
    (`citadel-raw-data/benchmarks/`) at each 1,000-item checkpoint and at the
    end; the register sync reads only from the finished, checksummed copy.
11. **Approval file.** The run starts only when `healthbench_results/
    hbp_20260911/GO_5000` exists, containing the principal's approval text,
    the readout JSON path it is based on, and the timestamp; the ledger
    records the same line. Superstonk fires from that file, not from chat.

## 4. What one 5,000 run yields (no extra generation)

| Readout | Items | Comparator | Grader for the comparison |
|---|---|---|---|
| HealthBench Standard, number of record | 5,000 | bare GPT-6 Astra 5,000 x 1 (same pin, same graders) | GPT-5.4 official + Opus 4.8 sensitivity |
| HealthBench Hard | 1,000 (exact subset of the 5,000) | bare Astra restricted to the same ids; June 2026 Apex 44.8 for the history line | same |
| Consensus subset | if its id list is public | same | same |
| Vishwanath seed-62 sample vs OpenEvidence 62.6 / UpToDate Expert AI 61.3 | 500 (id list on the 5090 at `/home/deepan/clinical-llm-benchmarks/hb500_seed62.jsonl`; verify 500/500 against the study's pipeline `github.com/nyuolab/clinical-llm-benchmarks`) | published values, plus bare Astra on the same 500 | **three-judge panel majority, raw HealthBench scoring** (Claude Opus 4.6, Gemini 3.1 Pro Preview, GPT-5.2: the published study's configuration, see Amendment 1); gpt-4.1 single as a second row that ties the 500 to the 5,000 main grade |
| Theme and axis breakdowns | all tags | bare Astra | same |
| Lyra analysis battery (empathy, bias, LGBTQ competency, intent, hedging, emergency, multilingual, refusals) | post-hoc on outputs; small extra perturbation sets where the design says so | per axis | per axis |

Professional replication: the 525 x 2 pre-freeze trials are the replication;
a third trial per side is appended at freeze if either GO condition rests on
a p-value between 0.01 and 0.05.

## 5. Cost, runtime, schedule

- Generation: median 133 s per Apex-J item on the lane. At concurrency 4,
  5,000 items is about 46 h; at concurrency 6, about 31 h, if the lane holds
  (check `dnai-api` latency and the 5070 TEI queue at hour one).
- Model spend: the 525 trials run $600 to $1,200 each with FENG and the
  composer, so 5,000 items is $6k to $12k for generation; graders add
  roughly $1.5k to $3k each for Opus 4.8 and GPT-5.4 on 5,000 rubric sets,
  less for gpt-4.1. Bare Astra 5,000 comparator: under $1k plus grading.
  Order of magnitude for the whole package: **$15k to $25k**. Budget guard
  set at $25k; the principal raises it or the run pauses.
- Schedule if GO on Saturday 20 Sep morning: preflight and freeze tag
  Saturday; fire on approval Saturday midday; generation complete Monday
  22 Sep evening (concurrency 4); grading Tuesday; readouts and register
  rows Wednesday 24 Sep. Base and Mid freeze arms (525 x 2 each, bare
  runner) run alongside from Sunday.

## 6. Superstonk firing sequence (on the principal's approval only)

1. Readout lands; bench owner posts the GO/HOLD table in chat and the ledger.
2. Principal approves in writing; bench owner writes `GO_5000`.
3. Freeze: merge nothing to the cognition path; tag `freeze-2026-09-<dd>`;
   restart `dnai-api` on the tag (the only lane restart); record the pin.
4. Section 3 checklist ticked in the ledger, items 1 to 11.
5. Preflight three items; then the 5,000 driver in tmux `hbp_5000` with the
   budget guard; bare Astra 5,000 in parallel through the bare runner.
6. Watchers: `container-watchdog.sh` covers the lane; a 30-minute progress
   line to `phase2.log`; `notify.sh` on any abort.
7. Readouts in section 4 order; register rows via `sync_ceiling_results.py`
   and a PR from a clean worktree; the page publishes from main.

## Amendments

**A1, 2026-09-18 20:50 ET (Polymath, verified against the Nature Medicine
methods and the peer-review file).** The published Vishwanath et al. study
(Nat Med, 12 Jun 2026, doi:10.1038/s41591-026-04431-5) graded HealthBench with
panel-majority voting across three judges (Claude Opus 4.6, Gemini 3.1 Pro
Preview, GPT-5.2), raw proportion of rubric points, 0 to 100. The peer-review
response states the authors "replaced the sole GPT-4.1 grader" with that panel
between preprint and final. The gpt-4.1 single grader belongs to the arXiv
2512.01191 preprint, whose "mean consensus scores" (GPT-5 97.0, OpenEvidence
74.3) sit on a different scale and are never comparable to ours. Consequences:
(1) section 4 now names the panel as the apples-to-apples grader for the 500,
with gpt-4.1 single kept as a second row; (2) our June (72.6) and September
(66.6) Asha-vs-tools comparisons on the 500 used gpt-4.1 single against
panel-graded tool scores and are grader-mismatched until the 500 responses are
re-graded by the panel; the register row `healthbench-500-independent` says so
as of tonight; (3) the seed-62 id list is already in-house (path in section 4).
Found by Lyra during the analysis-battery design.

**A2, 2026-09-19 11:45 ET (Polymath), written after the K=2 readout and before
the K=3 readout exists.** K=2 result: +4.4 length-adjusted (p=0.0004), red-team
+5.4 (p=0.03), harm +1.2 points on the 525 (72 vs 67 negative criteria of 426,
no criterion differing by more than two hits, red-team harm -0.4); holdout +2.0
(p=0.30) with harm +2.7. Two clarifications, both tightening toward the
program's standing rule rather than loosening it:
1. GO-A's "harm rate not above Astra" is read as the ceiling ladder's harm gate
   used in every readout since 17 Sep: overall and red-team harm each within
   +2.0 points of the comparator. The K=2 525 result passes that gate; the
   holdout does not. A "not above zero" clause would have made the whole
   program's ADOPT decisions inconsistent with this one; the error was in my
   drafting, not in the ladder.
2. The third trial per side (the pre-registered path for this case) is running;
   the decision is taken on pooled K=3 for both the 525 and the holdout. The
   holdout condition stays as written: NEUTRAL or better, harm within the gate.
   If the holdout fails on harm at K=3, the outcome is HOLD and the first
   candidate fix is the guarded composer style (round 2: score inside noise,
   harm -4.2), tested on the slice under the ladder rule before any 525 re-run.
3. Freeze target: the frozen build is `main` at freeze time, not the 17 Sep lane
   pin `cfa13318`, because main now carries the folded-transcript jailbreak fix
   (#983) and the empty-answer guard (#1020). A Lane C identity arm (Base + the
   Apex-J incumbent on the 300 slice, one trial each) runs on the frozen build
   first; NEUTRAL against the runs on record is required before `GO_5000`.

**A3, 2026-09-20 12:14 ET (principal ruling, recorded by Polymath).** K=3 on the
525: concise incumbent GO-A (+4.0, p=0.001, all gates). Holdout 225: +2.2
(p=0.23), harm +2.5, gate fails (K=2: +2.7). The A2 fix path was exhausted:
guarded style on the 525 x 2 read +1.4 vs Astra (p=0.29), holdout harm +3.2,
and -2.6 vs concise (p=0.009); the harm uptick is present for both styles and
is architectural (fuller answers trip more negative-point criteria) while the
red-team subset is safer in every readout. Ruling: freeze concise; the 5,000
run (fully untuned) replaces the 225-item holdout as the decisive harm test,
pre-registered here: harm rate vs bare Astra on the 5,000 within +2.0 points,
else the number of record ships with the caveat and the freeze is reconsidered
before any launch claim. Freeze tag `freeze-2026-09-20` = `ac1189712` (main
with #983, #1020, #1027 and the #1032 `APEX_TIER_PIPELINE` switch, default
off). Identity arms on `main` `35abaec88` (Base, Apex-J concise, 300 slice)
must read NEUTRAL before `GO_5000` fires; the switch commit differs from the
measured one only by the byte-identical default-off branch (4 unit tests).
Contamination probe on 200 of the 5,000: retrievable collections clean
(`cognition_verified` max cosine 0.826, 0 hits >= 0.92); `ciu_chain` 3 hits
and the scaffolding collections are excluded from retrieval by code.
Approval text is in `healthbench_results/hbp_20260911/GO_5000`.
