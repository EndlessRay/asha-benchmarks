# Vishwanath et al. 500: Apex-J with retrieval for every panel agent (Nov 2026)

An exploratory run of a later Apex-J configuration (code of 25 November 2026) on the 500-item HealthBench sample of
Vishwanath et al. (seed 62, the same file as `../healthbench-5000-2026-09-20/vishwanath_seed62_500_items.jsonl`),
graded by the study's three-judge panel (Claude Opus 4.6, Gemini 3.1 Pro Preview, GPT-5.2; majority per criterion)
and paired item by item with the frozen September answers under the same panel. There was no pre-registered
hypothesis; the analysis was fixed in the run script before generation.

## Result (the study's pooled metric, 5,000 item-bootstrap resamples)

| Set | September (frozen) | This run | Difference (95% CI) | Better / worse | Sign test P |
|---|---:|---:|---|---|---:|
| All 500 | 63.77 | 65.14 | +1.37 (+0.03 to +2.67) | 153 / 136 | 0.35 |
| 426 rows where September's answer included Asha's draft | 64.38 | 66.04 | +1.65 (+0.16 to +3.14) | 134 / 114 | 0.23 |
| 74 rows where it did not | 60.22 | 59.91 | -0.31 (-2.71 to +2.10) | 19 / 22 | 0.76 |

## Reproduce

```bash
bash reproduce.sh
```

It checks every file against `MANIFEST.json`, recomputes the readout from this folder and the September panel file,
and exits non-zero on any difference.

## Contents

| Path | What it is |
|---|---|
| `completions.jsonl.gz` | 500 answers with per-answer run fields (merged, late and failed agents, fingerprint, composer settings) |
| `run_pin.json` | The server's pin at the start of the run (fingerprint, module hashes, configuration) |
| `panel/panel.json.gz` | Three-judge panel verdicts and scores |
| `noasha74_ids.json` | The 74 rows whose September answer lacked Asha's draft |
| `results/READOUT_panel.json` | Readout above |
| `scripts/panel_readout.py` | Readout code, standard library only |
| `MANIFEST.json` | SHA-256 of every file here |
| `reproduce.sh` | Checks the manifest and recomputes the readout |

## Notes

- What differs from September: the composer, its 4,096-token budget, concise style and disabled live search are the
  same (GPT-6 Astra). The panel changed in several ways at once, so no single change is credited:
  - every panel agent retrieves from the knowledge layer (bench setting `AGENT_KIL_ALL=true`);
  - each agent's query is the latest user message, with earlier turns passed as conversation history and the rules
    of engagement passed separately (in September the agents received the rules and the whole folded conversation
    as one message);
  - straggler and domain waits 150 s, composer timeout 600 s: every answer merged all 11 drafts, none late;
  - later retrieval and source-gate changes on the main branch up to the run's code.
- Code identity: process fingerprint `d1bece7dd72a72b6` (`run_pin.json`, recorded per answer), whose 12 module
  hashes equal the files of Citadel commit `968f84b43`. One process served all 500 answers. The pin's `git_sha`
  field comes from the image build variable and is stale.
- As a mean of per-row scores: +1.57 on all 500; on the 74 rows +1.11 (pooled -0.31).
- No panel criterion lacked three clean votes.
