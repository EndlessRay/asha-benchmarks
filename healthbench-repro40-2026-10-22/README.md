# Reproducibility run, 22 October 2026: every current arm on 40 seeded random HealthBench items

Purpose: show that the frozen build reproduces its own record, and put every arm of the portfolio on the same items, the same night, under the same graders. Run 2026-10-23 00:54Z to 02:43Z on freeze `asha-base-v3-2026-10-19` (commit `0a3b831af3cf14e7f6ad3bfd973fc5472d5e184f`, image `citadel-frozen/asha-base:2026-10-18-genai175`), one GPU lane at a time. Driver and readout: `readouts/driver.log`, `readouts/readout.json`, `readouts/READOUT.md`.

## Items

`repro40_items.jsonl`: 40 items drawn from the seed-62 500 (`../healthbench-500-2026-10-19/hb500_seed62_standard_items.jsonl`) with `random.Random(20261022).sample(sorted_by_prompt_id, 40)`. Every item has per-item grades on record from the October Base run and from the September 5,000-item run, so the same items anchor the replication and the lineage comparison.

## Arms

| Directory | Arm | Route |
|---|---|---|
| `asha-base-v3-claude-sonnet-5-5-low/` | **Asha Base**, pinned Claude Sonnet 5.5 effort low | `/api/query`, bench pin |
| `asha-mid-v3-deep-mode/` | **Asha Mid**, P5 deep-mode ensemble, unpinned production routing | `/api/query/stream` with `deep_mode` (the non-stream route ignores the flag) |
| `asha-apex-v3-composer-gpt-6-astra-concise/` | **Asha Apex**, recipe A: composer GPT-6 Astra, concise, 4,096 | `/api/eval/apex_j` |
| `asha-apex-v3-composer-claude-opus-5-default/` | **Asha Apex**, recipe B: composer Claude Opus 5, default style, 4,096 | `/api/eval/apex_j` |
| `bare-claude-sonnet-5-5-effort-low/` | bare Claude Sonnet 5.5, effort low | direct API |
| `bare-claude-sonnet-5-5-effort-max/` | bare Claude Sonnet 5.5, effort max | direct API |

Each directory holds `completions.jsonl.gz`, `graded_gpt_4_1.jsonl.gz` and `graded_claude_opus_4_8.jsonl.gz`. Internal trace and routing fields were removed; answers and grades are complete. `MANIFEST.json` carries SHA-256 for every file.

## Results (gpt-4.1, HealthBench's official metric; n = 40, so SE is about 4 to 5 points per arm)

| Arm | gpt-4.1 [95% CI] | harm % | Opus 4.8 | median chars | median s | empty |
|---|---|---|---|---|---|---|
| Asha Apex, recipe B (Opus 5 composer) | **68.9** [60.9, 76.6] | 26.5 | 77.3 | 5,416 | 67 | 0 |
| Asha Apex, recipe A (Astra composer) | **67.1** [60.8, 73.6] | 23.8 | 74.2 | 2,816 | 112 | 0 |
| bare Sonnet 5.5, effort max | 62.2 [55.0, 70.1] | 31.3 | 70.2 | 2,164 | 26 | 0 |
| Asha Base | 59.7 [53.3, 66.2] | 32.7 | 63.8 | 4,544 | 38 | 0 |
| bare Sonnet 5.5, effort low | 59.5 [52.1, 66.9] | 29.9 | 68.7 | 2,121 | 7 | 0 |
| Asha Mid (4 of 40 requests did not engage deep mode; scored as empty) | 58.2 [49.6, 66.5]; 64.7 on the 36 answered | 24.5 | 59.9 | 3,799 | 80 | 4 |

### Replication (same build, same items, fresh generation vs the record)

| Pair | diff [95% CI] | W/L/T |
|---|---|---|
| Asha Base tonight minus Asha Base, October record (63.1 on these items) | -3.4 [-7.2, +0.1] | 7/19/14 |
| bare Sonnet 5.5 low tonight minus October record (62.2) | -2.6 [-7.9, +2.2] | 10/18/12 |
| bare Sonnet 5.5 max tonight minus October record (63.6) | -1.4 [-6.0, +3.3] | 10/15/15 |

All three Sonnet 5.5 arms moved down by a similar amount and every interval includes zero: the frozen build reproduces its record within the sample's noise, and the shared shift is vendor-side and grader variance rather than anything in the build.

### Arms against each other and against the lineage (same items)

| Pair | gpt-4.1 diff [95% CI] | Opus 4.8 diff |
|---|---|---|
| Apex A minus Apex B | -1.8 [-8.4, +4.6] | -3.0 [-9.3, +3.3] |
| Apex A minus Base | **+7.4** [+2.3, +12.8] | +10.5 [+3.4, +18.0] |
| Apex B minus Base | **+9.2** [+1.9, +16.7] | +13.5 [+7.6, +19.9] |
| Apex A minus bare Sonnet 5.5 max | +4.9 [-3.0, +12.4] | +4.0 [-1.8, +9.3] |
| Apex B minus bare Sonnet 5.5 max | +6.7 [-0.1, +13.7] | +7.1 [+1.0, +13.1] |
| Apex A minus September frozen Apex-J record (62.2 on these items) | +4.9 [-1.5, +11.3] | |
| Apex B minus September frozen Apex-J record | **+6.7** [+1.0, +12.4] | |
| Apex A / B minus September bare GPT-6 Astra record (56.3) | +10.8 [+4.4, +17.8] / +12.6 [+4.7, +20.7] | |
| Mid minus Base | -1.5 [-9.9, +6.7] | -3.9 [-14.4, +6.2] |
| Base minus bare Sonnet 5.5 low (same model, same effort) | +0.2 [-6.6, +7.0] | -5.0 [-11.7, +2.1] |

## Read

1. **The build reproduces.** The frozen Base replicates its October record within noise, and the bare arms move with it.
2. **Apex on the current build is the strongest configuration measured**, above Base by 7 to 9 points with intervals excluding zero, above the September frozen Apex-J's own record on the same items, and above bare Sonnet 5.5 at effort max by 5 to 7 points at a confidence this sample cannot settle. Its harm proxy is the lowest of the Asha arms and below both bare arms.
3. **The two composers tie at this n.** Recipe B (Opus 5) writes twice the length in half the time and scores 1.8 higher; recipe A (Astra) has the lower harm proxy. The pre-signed 500-item rule decides.
4. **Mid is not yet a clean arm**: 4 of 40 stream requests returned without engaging the ensemble. Fix before the 500.
5. Nothing here is a headline number; n = 40 is a reproducibility and ordering check. Headline claims come from the pre-registered 500-item and larger runs.
