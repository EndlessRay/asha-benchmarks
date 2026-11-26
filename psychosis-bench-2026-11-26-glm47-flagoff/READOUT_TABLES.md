# Readout tables: psychosis-bench, GLM-4.7-Flash held fixed

Turns judged: A 384, B 384. Both arms generated with thinking disabled (see PREREGISTRATION.md, Deviations). SIS higher is safer; DCS and HES lower are safer. Wilson 95% CIs on SIS; scenario-paired bootstrap (5,000) on ratios.

## judge A (gpt-4o-mini)

| Arm | Turns (empty/error) | SIS % (95% CI) | DCS mean (n, nonzero) | HES mean (n, nonzero) |
|---|---|---|---|---|
| bare GLM-4.7-Flash | 192 (0) | 17.7 (11.4 to 26.5), 17/96 | 1.569 (144, 130) | 1.375 (96, 84) |
| Asha Base on GLM-4.7-Flash | 192 (6) | 96.9 (91.2 to 98.9), 93/96 | 0.84 (144, 106) | 0.469 (96, 42) |

SIS difference Asha minus bare: +79.2 points. Scenarios with Asha SIS higher / lower / tied: 14 / 0 / 2; exact sign test P = 0.0001.
DCS ratio bare / Asha: 1.87 (95% CI 1.48 to 2.41), 16 scenarios paired.
HES ratio bare / Asha: 2.93 (95% CI 2.09 to 4.90), 16 scenarios paired.

## judge B (claude-haiku-4-5)

| Arm | Turns (empty/error) | SIS % (95% CI) | DCS mean (n, nonzero) | HES mean (n, nonzero) |
|---|---|---|---|---|
| bare GLM-4.7-Flash | 192 (0) | 36.5 (27.5 to 46.4), 35/96 | 1.91 (144, 141) | 1.948 (96, 96) |
| Asha Base on GLM-4.7-Flash | 192 (6) | 81.2 (72.3 to 87.8), 78/96 | 0.951 (144, 95) | 0.854 (96, 65) |

SIS difference Asha minus bare: +44.7 points. Scenarios with Asha SIS higher / lower / tied: 14 / 1 / 1; exact sign test P = 0.0010.
DCS ratio bare / Asha: 2.01 (95% CI 1.56 to 2.78), 16 scenarios paired.
HES ratio bare / Asha: 2.28 (95% CI 1.74 to 3.20), 16 scenarios paired.

## Judge agreement

Cohen kappa between judges on SIS over 192 eligible turns (both arms): 0.37. Pre-registered: below 0.60 the formal verdict is inconclusive.

