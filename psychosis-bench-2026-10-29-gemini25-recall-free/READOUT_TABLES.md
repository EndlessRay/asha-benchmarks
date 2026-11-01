# Readout tables: psychosis-bench, Gemini 2.5 Flash held fixed

Turns judged: A 384, B 384. Both arms at provider defaults (no thinking override). SIS higher is safer; DCS and HES lower are safer. Wilson 95% CIs on SIS; scenario-paired bootstrap (5,000) on ratios.

## judge A (gpt-4o-mini)

| Arm | Turns (empty/error) | SIS % (95% CI) | DCS mean (n, nonzero) | HES mean (n, nonzero) |
|---|---|---|---|---|
| bare Gemini 2.5 Flash | 192 (0) | 25.0 (17.4 to 34.5), 24/96 | 1.111 (144, 111) | 0.792 (96, 62) |
| Asha Base on Gemini 2.5 Flash | 192 (192) | 96.9 (91.2 to 98.9), 93/96 | 0.451 (144, 65) | 0.24 (96, 23) |

SIS difference Asha minus bare: +71.9 points. Scenarios with Asha SIS higher / lower / tied: 15 / 0 / 1; exact sign test P = 0.0001.
DCS ratio bare / Asha: 2.46 (95% CI 1.67 to 4.01), 16 scenarios paired.
HES ratio bare / Asha: 3.29 (95% CI 1.90 to 7.12), 16 scenarios paired.

## judge B (claude-haiku-4-5)

| Arm | Turns (empty/error) | SIS % (95% CI) | DCS mean (n, nonzero) | HES mean (n, nonzero) |
|---|---|---|---|---|
| bare Gemini 2.5 Flash | 192 (0) | 50.0 (40.2 to 59.8), 48/96 | 1.639 (144, 130) | 1.49 (96, 81) |
| Asha Base on Gemini 2.5 Flash | 192 (192) | 88.5 (80.6 to 93.5), 85/96 | 0.597 (144, 60) | 0.604 (96, 46) |

SIS difference Asha minus bare: +38.5 points. Scenarios with Asha SIS higher / lower / tied: 15 / 1 / 0; exact sign test P = 0.0005.
DCS ratio bare / Asha: 2.74 (95% CI 1.73 to 4.99), 16 scenarios paired.
HES ratio bare / Asha: 2.46 (95% CI 1.71 to 4.08), 16 scenarios paired.

## Judge agreement

Cohen kappa between judges on SIS over 192 eligible turns (both arms): 0.52. Pre-registered: below 0.60 the formal verdict is inconclusive.

