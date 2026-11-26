<!-- Public copy of Docs/benchmarking/apexj_asha_replay_2026-11/PREREGISTRATION.md in the private repository at commit ae49dc973 (amendment A3, pushed 2026-11-25T01:09:16Z), verbatim except three marked redactions of internal names. -->
# Apex-J September 5,000: Asha-draft replay (pre-registration)

Written 2026-11-22, before any replay answer is generated. Principal GO: 200 rows, $150 cap.

## Question

In the September 5,000 run (`hb5000_apexj_t1`, process pin `edd4f69f9a9bd6d2`), Asha's draft missed the
12 s straggler grace on 969 rows, and the composer wrote those answers from the other drafts. Her draft
still finished in the background and is stored in [redacted: internal database and table name], together with every other panel
draft. How much would those answers have scored if the composer had waited for her draft?

Estimand: the paired effect of adding Asha's stored draft to the composer input, holding every other input
fixed, on the GPT-4.1 HealthBench score of the affected rows. This describes the September system with the
composer waiting for Asha. It says nothing about the lane with agent manifests and graph expansion.

## Data

- Rows: `healthbench_apex_j_20260920_192247.jsonl` (5,000), Asha absent from `contributing_agents` on 969.
- Drafts: [redacted: internal table name] panel-task rows, created 2026-09-20 19:22:21Z to 2026-09-26.
  A draft belongs to a row when `query_text` equals the charter `roe_text`, two newlines, and the row's
  folded query (frozen runner `split_prompt` + `build_query`). Tasks for one row are clustered by
  `created_at` within 10 s.
- Eligible set E: rows with exactly one cluster that holds a non-empty Asha draft and a non-empty draft for
  every agent in the row's `contributing_agents`. Rows with zero or several such clusters are excluded and
  counted.
- Sample: `random.Random(20261122).sample(sorted(E), 200)`.

## Arms (frozen code, `freeze-2026-09-20`, run unmodified from the record repo)

Both arms call the frozen `core.apex_j.apex_j_answer` with the September request settings (composer
`gpt-6-astra`, 4,096 tokens, style `concise`, the row's directive, domain `None`, effort `None`, live search
and apostille off). Panel calls are replaced by an `ask_agent` stub that returns the stored drafts.

- A (September as run): the contributing agents' stored drafts; Asha's call returns no draft.
- B (composer waits for Asha): the same drafts plus Asha's stored draft.

Shared between the arms of a row:
- FENG block: computed once by the frozen `run_feng_stage` on the row's contributing drafts in their
  September arrival order (`completed_at`), against today's corpus, and injected into both arms.
- Ledger: a stub returning the row's stored `culture.reputations`; Asha's reputation comes from the nearest
  preceding row in file order where she contributed. No culture event is written anywhere.
- NLI cross-check: the frozen scorer (`cross-encoder/nli-deberta-v3-xsmall`), on CPU.

## Grading and endpoint

- Grader: frozen `tests/healthbench_grader.py --model gpt-4.1` (the official grader behind 60.70). Up to
  three passes for failed grades. A row whose grade still fails in either arm leaves both arms.
- Primary endpoint: mean over rows of (score_B minus score_A), per-example scores as computed by the frozen
  grader, reported in points (x100). 95% CI by paired bootstrap, 10,000 resamples, seed 20261122,
  percentile method. Paired t-test reported alongside.
- Decision rule:
  - CI excludes 0: the effect is established for these rows.
  - CI includes 0 and its half-width is above 2.0 points: recommend extending to all of E (separate
    principal GO, about $650).
  - Otherwise: report a null with the CI as the bound.
- Projection to the 5,000 topline: effect x 969 / 5,000, CI scaled the same way.

## Secondary (descriptive, not gating)

1. Fidelity of the replay:
   - charter hash equals the September `culture_charter_hash`;
   - share of rows where arm A's recomputed weights for the September contributors match the stored weights
     within 0.02;
   - share of rows where arm A's guardianship flag matches the stored flag;
   - arm A score minus the stored September GPT-4.1 score on the same rows (paired mean, bootstrap CI): the
     drift from composer sampling, today's composer snapshot and today's FENG corpus.
2. In arm B: Asha's weight rank, and the number of rows where her draft turned guardianship on.
3. Effect by HealthBench theme (counts too small for inference; listed only).

## Deviations from the September run, stated in advance

- Composition runs today: the `gpt-6-astra` snapshot may differ from September's.
- FENG uses today's corpus (the September snapshot rolled off NAS retention).
- Asha's absence is a failed call in arm A instead of a late one. This changes metadata only.
- The ledger is a stub fed from stored values.
- NLI runs on CPU (same model).

## Budget

Cap $150. A 5-row pilot measures tokens first, and the run stops if the projection exceeds the cap.

## Amendment A1 (2026-11-22, before any replay answer was generated)

The first selection pass (sample sha256 `6574709537cc...`) found 708 eligible rows: 188 had no qualifying
cluster and 73 had several. A diagnostic showed that 187 of the 188 had every needed draft, split across
two clusters. The 10 s window was too tight because the September fan-out held 8 request slots for 11
agents, so the last calls started when a slot freed. Repeat fan-outs of one prompt sit at least 4 h apart.
The clustering window is now 300 s, and the sample is redrawn with the same seed. The rule for several
qualifying clusters is unchanged: those rows stay excluded and are counted.

## Operational note A2 (2026-11-22 23:20 UTC, after 12 rows, before any grading)

The CPU run reached 13 rows per hour. The frozen grounding pass timed out on every row and its threads kept
the cores busy. Its result never reaches the answer (grounding regen was off in September and the restraint
gate does not read it), so from row 13 the replay returns the pass's timeout result directly, which is what
rows 1 to 12 recorded. Torch is capped at 4 intra-op threads per call. Composer inputs are unchanged.

## Amendment A3 (2026-11-25, principal GO; written before any extension answer was generated)

Purpose: correct the published September numbers for Asha's absence. Two published rows are corrected:
the 5,000 (gpt-4.1, OpenAI's reference rendering, 65.5) and the Vishwanath seed-62 500 (the study's
three-judge panel, 63.8). Each is corrected with the grader that produced it; no other grader is run.

1. Selection. The 74 rows excluded as "ambiguous" are exactly the 74 seed-62 rows without Asha: those
   prompts were re-run in later hb500 arms (Sept 23-25). When several clusters qualify, the one that
   started inside the September run window (2026-09-20T19:22:21Z to 2026-09-23T00:00Z) is used. A probe
   resolved all 74 to one cluster. The 894 rows matched before keep their match. Extension sample: every
   eligible row not in the first 200 (`ext/sample.jsonl`).
2. Arms. Arm B only for the extension. Arm A on the first 200 matched September within -0.62
   [-2.73, +1.50] points, so September's stored answers serve as the without-Asha side for every row.
   The first 200 keep their arm A as the fidelity check.
3. Grading, 5,000 row: gpt-4.1 as first graded (frozen grader), then penalty criteria re-graded with the
   reference rendering and merged (`Docs/benchmarking/points_regrade_2026-10-31/` method, steps 1-4),
   for arm B on all 968 rows and arm A on the first 200. September's side uses the published per-item
   reference-rendering grades (`frozen_pair_points.py` inputs).
4. Grading, seed-62 row: arm B on the 74 seed-62 rows through the study's pipeline and three-judge panel,
   majority per criterion, as the published row. Priced before it runs.
5. Primary readouts. (a) Corrected 5,000 score: September per-item scores with the 968 replayed rows
   swapped for arm B; paired difference over the 968 with 95% bootstrap CI. (b) Corrected seed-62 panel
   score: the 426 September rows plus 74 arm B rows. The one row without stored drafts stays as run and
   is counted. Reported beside, never in place of, the as-run numbers.
6. Budget: generation guard $175 (expected about $146 at $0.19 per answer); grading about $50; panel priced
   separately.

## Artifacts

Code: `scripts/bench/apexj_asha_replay/`. Outputs on the company host: [redacted: internal path].
