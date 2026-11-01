# Readout tables: psychosis-bench, GLM-4.7-Flash held fixed

Turns judged: A 384, B 384. Both arms generated with thinking disabled (see PREREGISTRATION.md, Deviations). SIS higher is safer; DCS and HES lower are safer. Wilson 95% CIs on SIS; scenario-paired bootstrap (5,000) on ratios.

## judge A (gpt-4o-mini)

| Arm | Turns (empty/error) | SIS % (95% CI) | DCS mean (n, nonzero) | HES mean (n, nonzero) |
|---|---|---|---|---|
| bare GLM-4.7-Flash | 192 (0) | 18.8 (12.2 to 27.7), 18/96 | 1.674 (144, 127) | 1.469 (96, 81) |
| Asha Base on GLM-4.7-Flash | 192 (10) | 97.9 (92.7 to 99.4), 94/96 | 1.014 (144, 112) | 0.812 (96, 67) |

SIS difference Asha minus bare: +79.1 points. Scenarios with Asha SIS higher / lower / tied: 14 / 0 / 2; exact sign test P = 0.0001.
DCS ratio bare / Asha: 1.65 (95% CI 1.29 to 2.27), 16 scenarios paired.
HES ratio bare / Asha: 1.81 (95% CI 1.38 to 2.53), 16 scenarios paired.

## judge B (claude-haiku-4-5)

| Arm | Turns (empty/error) | SIS % (95% CI) | DCS mean (n, nonzero) | HES mean (n, nonzero) |
|---|---|---|---|---|
| bare GLM-4.7-Flash | 192 (0) | 35.4 (26.6 to 45.4), 34/96 | 1.854 (144, 136) | 1.885 (96, 93) |
| Asha Base on GLM-4.7-Flash | 192 (10) | 80.2 (71.1 to 86.9), 77/96 | 1.271 (144, 114) | 1.26 (96, 88) |

SIS difference Asha minus bare: +44.8 points. Scenarios with Asha SIS higher / lower / tied: 13 / 1 / 2; exact sign test P = 0.0018.
DCS ratio bare / Asha: 1.46 (95% CI 1.22 to 1.82), 16 scenarios paired.
HES ratio bare / Asha: 1.50 (95% CI 1.30 to 1.72), 16 scenarios paired.

## Judge agreement

Cohen kappa between judges on SIS over 192 eligible turns (both arms): 0.50. Pre-registered: below 0.60 the formal verdict is inconclusive.

