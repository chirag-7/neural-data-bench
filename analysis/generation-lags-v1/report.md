# Model-generation lag and change-size sensitivities

Six comparisons across 30 tasks / 14 categories, grouped into three lag-1, two lag-2 and one lag-3 comparisons. Lag is ordinal, not elapsed time or training compute. No new model calls, fitted predictions or score changes.

**These are descriptive, repair-assisted results. IQR bands are exploratory panel-relative gaps, not statistically established small/large changes, significance tests or practical equivalence.**

## Methods

`R = direction-adjusted native score change / IQR(four model task means)`.

IQR of the same four model task means; inclusive linear quantiles (Hyndman-Fan type 7). With sorted a<=b<=c<=d: Q1=.25a+.75b; Q3=.75c+.25d.

Absolute normalized gap at or below threshold (plus boundary tolerance), including raw numerical ties. Not evidence of equivalence or randomness.

Missing four-model scores: normalization not estimable. Zero IQR: no ratio; numerical pair ties within band, other pairs not estimable. Never add epsilon to the denominator.

The native tie tolerance is 1e-9; normalized threshold comparisons allow 1e-12 numerical tolerance. The thresholds 0.1 and 0.5 were selected after inspecting this panel and are sensitivity choices, not accepted universal effect-size standards.

## Any numerical change

| Lag | Earlier → later | Better | Worse | Numerical tie | Incomplete |
|---|---|---:|---:|---:|---:|
| 1 | gpt-4.1-2025-04-14 → gpt-5-2025-08-07 | 19 | 11 | 0 | 0 |
| 1 | gpt-5-2025-08-07 → gpt-5.6-sol | 25 | 4 | 1 | 0 |
| 1 | gpt-5.6-sol → gpt-6.1-sol | 20 | 9 | 1 | 0 |
| 2 | gpt-4.1-2025-04-14 → gpt-5.6-sol | 25 | 5 | 0 | 0 |
| 2 | gpt-5-2025-08-07 → gpt-6.1-sol | 24 | 5 | 1 | 0 |
| 3 | gpt-4.1-2025-04-14 → gpt-6.1-sol | 28 | 2 | 0 | 0 |

## Changes exceeding 0.1 panel IQR

| Lag | Earlier → later | Better | Worse | Within band | Not estimable |
|---|---|---:|---:|---:|---:|
| 1 | gpt-4.1-2025-04-14 → gpt-5-2025-08-07 | 19 | 8 | 3 | 0 |
| 1 | gpt-5-2025-08-07 → gpt-5.6-sol | 24 | 4 | 2 | 0 |
| 1 | gpt-5.6-sol → gpt-6.1-sol | 14 | 6 | 10 | 0 |
| 2 | gpt-4.1-2025-04-14 → gpt-5.6-sol | 25 | 5 | 0 | 0 |
| 2 | gpt-5-2025-08-07 → gpt-6.1-sol | 24 | 4 | 2 | 0 |
| 3 | gpt-4.1-2025-04-14 → gpt-6.1-sol | 27 | 2 | 1 | 0 |

## Changes exceeding 0.5 panel IQR

| Lag | Earlier → later | Better | Worse | Within band | Not estimable |
|---|---|---:|---:|---:|---:|
| 1 | gpt-4.1-2025-04-14 → gpt-5-2025-08-07 | 16 | 8 | 6 | 0 |
| 1 | gpt-5-2025-08-07 → gpt-5.6-sol | 18 | 4 | 8 | 0 |
| 1 | gpt-5.6-sol → gpt-6.1-sol | 6 | 3 | 21 | 0 |
| 2 | gpt-4.1-2025-04-14 → gpt-5.6-sol | 22 | 4 | 4 | 0 |
| 2 | gpt-5-2025-08-07 → gpt-6.1-sol | 20 | 1 | 9 | 0 |
| 3 | gpt-4.1-2025-04-14 → gpt-6.1-sol | 25 | 2 | 3 | 0 |

## Interpretation and limits

The endpoint direction survives both filters: 28/2/0 numerical better/worse/ties becomes 27/2/1 and 25/2/3 better/worse/within-band at 0.1 and 0.5 IQR. The 5.6→6.1 comparison changes from 20/9/1 to 14/6/10 and 6/3/21. These are conditional descriptions of this selected panel, not evidence for a scaling exponent or a causal slowdown.

- Only four selected model points define each spread: estimates can be unstable and change with the model roster.
- A large ratio can still be a tiny or practically unimportant native difference. This is not Cohen d, biological variability, error reduction, a z-score or a signal-to-noise ratio.
- IQR is a robust spread statistic in general; that does not make this four-point application a robust inferential result.
- Lags share tasks/models and are not independent repetitions. No pooled lag p-values, significance, confidence intervals or scaling-law fit are claimed.
- Convenience tasks, overlapping sources, unequal wrappers and selective repairs limit generalization. J08 GPT-4.1 has a documented manual training-budget adaptation.
- C2ST retains the original lower-is-better direction, but the diagnostic target is 0.5; near-chance ordering need not indicate a better sampler.

The standardized gaps are sensitive to metric choice, particularly nonlinear transformations, and to which four models are included. Positive affine unit changes cancel in the ratio. Native scores remain the basis for practical decisions.

## Stronger inference

Predeclare task-specific worthwhile-effect/equivalence margins; rescore with paired resampling of independent people, animals or recordings; preserve hierarchy and metric aggregation; repeat model generations under matched conditions. Report unresolved intervals rather than forcing small/large labels.

## Audit and reproduce

`python3 scripts/analyze_generation_lags.py` followed by `python3 scripts/check_generation_lags.py`. No raw data loading, fitting or API calls.

- [Full methods](methods.json)
- [Every native difference, IQR, ratio and classification](task-pairs.csv)
- [All comparison counts](comparison-counts.csv)
- [Machine-readable evidence, task IDs and source hashes](lag-analysis.json)
- [Current four-model source scores](../generation-comparison-v2/task-scores.csv)
- [Macro patterns and original-attempt sensitivity](../generation-patterns-v1/report.md)
- [Manual repairs](../../experiments/generation-repairs-v1/README.md)
- [NIST: Measures of Scale](https://www.itl.nist.gov/div898/handbook/eda/section3/eda356.htm) (supports the scale statistic; not these thresholds).
