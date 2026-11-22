# Identity-masked physician rating of HealthBench harm criteria: readout

Kit version 2 (220 units, HealthBench Hard, reference rubric rendering). Raters: R1, R2, R3.

Analysed: 218 units. Excluded before unblinding: hb2_169, hb2_201. Their statements are about hepatitis B prophylaxis and are attached, in the benchmark file itself, to a conversation about Adderall.

## Completion

| Rater | Met | Not met | Cannot tell | Unrated |
|---|---:|---:|---:|---:|
| R1 | 104 | 114 | 0 | 0 |
| R2 | 109 | 108 | 1 | 0 |
| R3 | 150 | 62 | 6 | 0 |

## Agreement between the raters

| Raters | Stratum | Units both rated | Agreement | Cohen kappa |
|---|---|---:|---:|---:|
| R1 and R2 | all | 217 | 79.7% | 0.59 |
| R1 and R2 | disputed | 117 | 77.8% | 0.56 |
| R1 and R2 | concordant | 60 | 83.3% | 0.67 |
| R1 and R2 | severe | 40 | 80.0% | 0.60 |
| R1 and R2 | asks for context | 34 | 73.5% | 0.43 |
| R1 and R2 | other statements | 183 | 80.9% | 0.62 |
| R1 and R3 | all | 212 | 61.8% | 0.26 |
| R1 and R3 | disputed | 114 | 57.0% | 0.16 |
| R1 and R3 | concordant | 59 | 69.5% | 0.41 |
| R1 and R3 | severe | 39 | 64.1% | 0.30 |
| R1 and R3 | asks for context | 34 | 73.5% | 0.38 |
| R1 and R3 | other statements | 178 | 59.6% | 0.23 |
| R2 and R3 | all | 211 | 63.5% | 0.27 |
| R2 and R3 | disputed | 113 | 55.8% | 0.12 |
| R2 and R3 | concordant | 59 | 71.2% | 0.43 |
| R2 and R3 | severe | 39 | 74.4% | 0.48 |
| R2 and R3 | asks for context | 34 | 82.4% | 0.56 |
| R2 and R3 | other statements | 177 | 59.9% | 0.22 |

Fleiss kappa across the 3 raters, on the 211 units all of them rated decisively: 0.36.

Rows below use the majority of the 3 raters: 216 of 218 units.

## Concordant units (all three graders agree)

Clinicians matched the graders' shared verdict on 54 of 59 (91.5%; 95% CI 81.6 to 96.3).

## Disputed units (the official grader differs from both others)

| Subset | Clinicians side with the official grader |
|---|---|
| all disputed | 52 of 117 (44.4%; 95% CI 35.8 to 53.5) |
| official says met | 31 of 60 (51.7%; 95% CI 39.3 to 63.8) |
| official says not met | 21 of 57 (36.8%; 95% CI 25.5 to 49.8) |
| Asha Apex-J | 23 of 60 (38.3%; 95% CI 27.1 to 51.0) |
| GPT-6 Astra alone | 29 of 57 (50.9%; 95% CI 38.3 to 63.4) |
| statement asks for context | 3 of 10 (30.0%; 95% CI 10.8 to 60.3) |
| other statements | 49 of 107 (45.8%; 95% CI 36.7 to 55.2) |

On these units GPT-5.4 and Claude Opus 4.8 agree with each other, so the remainder side with them.

"Asks for context": the 34 statements about the answer asking the user for information. The rating page did not say whether advice that covers the possibilities without asking counts, so these are shown apart.

## Share of rated criteria the clinicians call met, by arm

| Stratum | Asha Apex-J | GPT-6 Astra alone |
|---|---|---|
| disputed | 35 of 60 (58.3%; 95% CI 45.7 to 69.9) | 32 of 57 (56.1%; 95% CI 43.3 to 68.2) |
| concordant | 16 of 30 (53.3%; 95% CI 36.1 to 69.8) | 14 of 29 (48.3%; 95% CI 31.4 to 65.6) |
| severe | 6 of 20 (30.0%; 95% CI 14.5 to 51.9) | 17 of 20 (85.0%; 95% CI 64.0 to 94.8) |

These are rates within a stratified sample, not estimates for HealthBench Hard as a whole.

## Severe-harm conversations

| Graders flagged only | Conversations | Confirmed by clinicians | Flagged arm cleared | Both arms met | Not settled |
|---|---:|---:|---:|---:|---:|
| GPT-6 Astra alone | 17 | 11 | 2 | 4 | 0 |
| Asha Apex-J | 2 | 1 | 0 | 1 | 0 |

Confirmed: clinicians rate a severe criterion met in the flagged arm's answer and in none of the other arm's. Not settled: the raters differ, or one could not tell, on a unit of that conversation.
