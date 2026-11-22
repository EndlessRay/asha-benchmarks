# Identity-masked physician rating of HealthBench harm criteria: supplement (post hoc)

The pre-specified readout is `READOUT_ratings.md`. Everything below was computed on 21 Nov 2026, after unblinding. Raters: R1 and R2 are the paper's authors; R3 is a physician who advises the company.

## 1. Recomputation by a second implementation

A second implementation reproduces the pre-specified readout on 8 of 8 headline numbers.

## 2. Each rater's tendency

| Rater | Called met | Yes where all graders say met | No where all graders say not met | Matches the graders |
|---|---|---|---|---|
| R1 | 104 of 218 (48%) | 25 of 30 | 27 of 30 | 52 of 60 |
| R2 | 109 of 217 (50%) | 25 of 30 | 27 of 30 | 52 of 60 |
| R3 | 150 of 212 (71%) | 26 of 30 | 17 of 30 | 43 of 60 |

Called met in each quarter of the kit, in page order (55 units each, all 220): R1 28, 24, 29, 24; R2 30, 29, 27, 23; R3 41, 37, 32, 40.

The third rater called criteria met more often than the two authors, and more often where every grader said not met. The third rater's share is level across the kit. Cohen's kappa is moderate between the authors and fair between each author and the third rater.

## 3. Disputed units

The raters' majority sided with the official grader on 52 of 117 (44.4%; 95% CI 35.8 to 53.5) and with the other two graders on 65. Exact test against an even split: P = 0.27.

| System | Official grader says | Raters' majority says met |
|---|---|---|
| Asha Apex-J | met | 14 of 30 (46.7%; 95% CI 30.2 to 63.9) |
| Asha Apex-J | not met | 21 of 30 (70.0%; 95% CI 52.1 to 83.3) |
| GPT-6 Astra alone | met | 17 of 30 (56.7%; 95% CI 39.2 to 72.6) |
| GPT-6 Astra alone | not met | 15 of 27 (55.6%; 95% CI 37.3 to 72.4) |

Siding with the official grader by system: Asha Apex-J 23 of 60, GPT-6 Astra alone 29 of 57 (Fisher exact P = 0.20). The raters do not show the official grader favouring either system.

## 4. Severe-harm conversations

The paper's count is conversations: 19 (20 criteria, each rated on both systems' answers). The graders flagged the model alone in 17 and Asha in 2.

| Raters' majority finds a severe criterion met in | Conversations |
|---|---:|
| only the model alone's answer | 11 |
| only Asha's answer | 1 |
| both answers | 5 |
| neither answer | 2 |

The graders' flag was confirmed in 12 of 19 conversations (11 of the 17 flagged on the model alone, 1 of the 2 flagged on Asha). Exact sign test on the 12 conversations where only one answer met a severe criterion: P = 0.0063. By the raters' majority the model alone's answer met a severe criterion in 16 of 19 conversations and Asha's in 6.

Read the sign test with care: the conversations were chosen because the graders flagged one answer and not the other (17 to 2), so raters who confirm flags at the same rate in both arms produce a lopsided split. They did: 11 of 17 and 1 of 2 (Fisher exact P = 1.00). The P value measures agreement with the flags, so the paper reports the counts and no P value.

Leaving out the 7 conversations whose severe criterion is about asking for context: {'only the model alone': 8, 'only Asha': 1, 'neither': 1, 'both': 2} over 12 conversations.

## 5. Other consensus rules

| Rule | Units with a verdict | Concordant: match the graders | Disputed: side with the official grader | Severe: only the model alone / only Asha / both / neither / not settled |
|---|---:|---|---|---|
| majority of three | 216 | 54 of 59 (91.5%; 95% CI 81.6 to 96.3) | 52 of 117 (44.4%; 95% CI 35.8 to 53.5) | 11 / 1 / 5 / 2 / 0 |
| two authors agree | 173 | 47 of 50 (94.0%; 95% CI 83.8 to 97.9) | 38 of 91 (41.8%; 95% CI 32.2 to 52.0) | 9 / 1 / 2 / 2 / 5 |
| all three agree | 111 | 35 of 37 (94.6%; 95% CI 82.3 to 98.5) | 21 of 51 (41.2%; 95% CI 28.8 to 54.8) | 4 / 0 / 2 / 1 / 12 |
| R1 alone | 218 | 52 of 60 (86.7%; 95% CI 75.8 to 93.1) | 51 of 118 (43.2%; 95% CI 34.6 to 52.2) | 10 / 1 / 3 / 5 / 0 |
| R2 alone | 217 | 52 of 60 (86.7%; 95% CI 75.8 to 93.1) | 52 of 117 (44.4%; 95% CI 35.8 to 53.5) | 12 / 1 / 4 / 2 / 0 |
| R3 alone | 212 | 43 of 59 (72.9%; 95% CI 60.4 to 82.6) | 56 of 114 (49.1%; 95% CI 40.1 to 58.2) | 5 / 0 / 10 / 3 / 1 |
| majority of three, without the 6 units one rater asked about and the unit paired with one of them | 209 | 53 of 58 (91.4%; 95% CI 81.4 to 96.3) | 50 of 113 (44.2%; 95% CI 35.4 to 53.4) | 12 / 1 / 4 / 2 / 0 |

With the two excluded units put back (both disputed), the disputed row reads 52 of 117 (44.4%; 95% CI 35.8 to 53.5); the concordant and severe rows do not change.

## 6. Time on task and the page each rater saw

Time stamps are not in these files. From the time-stamped files: active time 4.2, 4.8 and 3.2 hours; median 42, 56 and 40 seconds per case; no answer under 5 seconds.


The second author and the third rater began after every page change. The first author had answered his first few cases when the reading rules were added (three of his answers carry an earlier time stamp). While rating, the first author asked the study's AI assistant about eight cases (the two excluded units and hb2_005, hb2_020, hb2_026, hb2_075, hb2_080, hb2_127). The assistant had access to the key. It answered with reading rules and pointed him to the wording of the statement and the answer, and it commented on the reasoning he described in four cases. It told him to answer cannot tell on the two excluded units and that cannot tell did not fit one other case, and it offered the wording of one note. It did not choose between yes and no on any analysed case, and it revealed neither the system behind any answer nor any grade. One rule it gave him ("seeks context" means the answer asks) was not on the page, which is why the 34 context-seeking statements are reported apart in the pre-specified readout. Section 5 gives the headline rows without those units.

## 7. How common each grader pattern is (all Hard harm criteria)

| Pattern | Asha Apex-J | GPT-6 Astra alone |
|---|---:|---:|
| all met | 609 (14.7%) | 801 (19.4%) |
| all not met | 2683 (64.9%) | 2573 (62.3%) |
| official met, others not | 188 (4.5%) | 194 (4.7%) |
| official not met, others met | 187 (4.5%) | 195 (4.7%) |
| other split | 466 (11.3%) | 370 (9.0%) |
| total | 4133 | 4133 |

Official harm rate recomputed from these files: Asha Apex-J 23.8%, GPT-6 Astra alone 27.9%.

