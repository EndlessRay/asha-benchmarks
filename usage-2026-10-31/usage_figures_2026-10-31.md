# Usage figures for Research Square v2 (query run 2026-10-31)

Script: `scripts/audits/usage_paper_figures.py` (branch `docs/nonmaleficence-v1.4-edit-pass`), read-only against the production ledger over SSH, with `scripts/audits/bench_prompt_hashes.txt` (10,788 benchmark-prompt fingerprints) beside it. Human filter: `traction_chart.human_where()` plus `bench_prelude_sql()`. Staff removed: `users.email LIKE %@dnai.systems` and, from 2026-10-31, `users.role IN (admin, system)` (two team accounts on personal webmail addresses, 676 Asha questions this year). Window YTD = messages 2026-01-01 to 2026-10-29 inclusive; SINCE_LAUNCH starts 2025-12-01. The 29 Oct run (9,460 questions, 5,366 conversations) removed only company-domain staff and ran before 29 October ended.

| Window | Population | Staff | Questions | Sessions | Registered askers | Median chars | Sessions with follow-up | Emergency flag (replies) | Replies with gravity | <0.70 | 0.70-0.88 | 0.88-0.95 | >=0.95 | at 0.50 |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| YTD | all_human | staff_in | 11,016 | 6,143 | 758 | 70 | 26.3% | 1.10% of 13,068 | 8,629 | 85.9% | 12.4% | 0.8% | 0.8% | 75.4% |
| YTD | all_human | staff_out | 8,831 | 5,016 | 741 | 73 | 26.1% | 1.22% of 9,872 | 7,492 | 86.7% | 11.5% | 0.9% | 0.9% | 75.4% |
| YTD | registered | staff_out | 3,878 | 1,426 | 741 | 74 | 49.6% | 1.09% of 4,575 | 3,156 | 83.7% | 13.9% | 1.6% | 0.9% | 68.5% |
| SINCE_LAUNCH | all_human | staff_in | 11,168 | 6,292 | 758 | 69 | 25.7% | 1.13% of 13,190 | 8,629 | 85.9% | 12.4% | 0.8% | 0.8% | 75.4% |
| SINCE_LAUNCH | all_human | staff_out | 8,983 | 5,165 | 741 | 72 | 25.4% | 1.25% of 9,994 | 7,492 | 86.7% | 11.5% | 0.9% | 0.9% | 75.4% |
| SINCE_LAUNCH | registered | staff_out | 3,878 | 1,426 | 741 | 74 | 49.6% | 1.09% of 4,575 | 3,156 | 83.7% | 13.9% | 1.6% | 0.9% | 68.5% |
