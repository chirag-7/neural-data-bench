# Macro patterns after repair and exclusion review

GPT-6.1 versus GPT-4.1: **27 better, 2 worse, 0 numerical ties, 1 incomplete** out of 30 tasks. 27/29 comparable task means (93.1%) favor GPT-6.1. This is a task-count fraction, not model accuracy or a probability for all neuroscience problems.

Before these macros, 9/10 original API-runtime failures were recovered and independently audited. The remaining model/task case is explicitly unscored within the original 180-second limit. Original failed runs remain intact. Physical-line repairs preserve the exact AST; they demonstrate manually formatted compliance, not original model brevity. No new API calls were made.

## Quantitative findings

| Four-model trajectory | Tasks |
|---|---:|
| strictly improving | 9 |
| mixed reversals | 19 |
| numerically flat | 0 |
| strictly declining | 0 |
| nondecreasing with ties | 1 |
| nonincreasing with ties | 0 |
| incomplete | 1 |

9/29 complete trajectories (31.0%; 9/30 of the attempted panel) improve at every adjacent step, spanning 6 categories: C05, E01, F04, H01, H02, K01, K06, L04, L06.

Strict-format sensitivity has 29 complete trajectories: {'mixed_reversals': 19, 'strictly_improving': 9, 'nondecreasing_with_ties': 1}. All manual formatting is still excluded from original model-compliance claims.

Endpoint sensitivities (better / worse / numerical tie / incomplete): strict-format 27 / 2 / 0 / 1, with 0 additionally format-ineligible; observed-data 21 / 2 / 0 / 1; untouched first attempts 23 / 2 / 0 / 5. These scopes and repair histories answer different questions.

| Adjacent sign pattern (+ = improvement) | Complete tasks |
|---|---:|
| + + + | 9 |
| + + - | 6 |
| + - + | 2 |
| + = = | 1 |
| - + + | 7 |
| - + - | 2 |
| - - + | 2 |

Among 9 strictly improving trajectories, 5 have successively smaller gains (C05, F04, K06, L04, L06); 8 have a smaller final than first gain. These are within-task native score gaps. Versions are not equally spaced compute/time measurements. This conditional post-hoc pattern cannot establish diminishing returns or a scaling exponent.

Endpoint regressions relative to GPT-4.1: B07, K05. All task IDs, directions, category denominators and six model pairs are retained in the data files.

## Qualitative findings

Mixed changes are reversals, not established randomness. No validated four-model generation-noise model or prospective equivalence margins exist. Zero numerical endpoint ties does not imply no practically equivalent or statistically unresolved outcomes. A small gap is not evidence of equality; a nonmonotonic curve is not proof of random performance. Chance classifier accuracy is a separate concept.

Untouched failures involved library compatibility, grouped-CV misuse, syntax, array indexing/shapes, legacy HDF5 aliases and time limits. Repairs enable usable procedures; same-objective optimizer replacements can still change numerical convergence and predictions. Thus the final panel combines model-written programs with explicit manual engineering. It cannot isolate autonomous debugging or causal generation effects.

The monotonic trajectories span calcium inference, population inference, sensory encoding, EEG decoding, cell classification and statistical inference. Behavior/movement and extracellular tasks have reversals in every complete trajectory in those categories. This retrospective observation has small and overlapping source samples; representation, estimator choice and task structure are hypotheses, not identified causal explanations.

## Quantitative + qualitative findings

- **P300 (H02):** 0.5731 → 0.7458 → 0.7572 → 0.7885 AUC; the ordering is consistent, but the last gain exceeds the middle one. Ten held-out people are not independent model-generation replicates.
- **Encoding/inference:** C05, F04, K06, L04 and L06 have shrinking adjacent score gains. L06 approaches the C2ST target 0.5; finite classifier noise limits interpreting near-chance ordering.
- **Method/representation hypothesis:** E01 changes from poor negative bits/spike to positive values. Investigate rate calibration and estimator choices before interpreting this as general neural understanding.
- **Ceiling ties:** N05 now follows 0 → 1 → 1 → 1 after explicit parser repairs; later models tie on 61 fields from one file. That plateau is a bounded task ceiling, not evidence of general model stagnation.
- **Tiny gaps:** A15 endpoint gain is about 0.000119 F1 and I10 about 0.005263 balanced accuracy. The signs are positive, but practical relevance and statistical equivalence are unestablished.
- **Exceptions:** GPT-4.1 wins B07 compression and K05 marker-fraction calibration against GPT-6.1. GPT-5 peaks on I07/I10. These counterexamples support task-level validation rather than an always-newest rule.
- **Repairs are not capabilities:** Recovering an execution failure improves usability coverage. It is not evidence that the untouched model could produce or debug the repaired program without help.

## Metric direction and graph conventions

All 30 tasks and reference rows pass an explicit direction audit: 18 higher-is-better, 12 lower-is-better primary metrics. Every line plot puts better native scores higher on the page; lower-is-better vertical axes are reversed and labeled. Bars retain native values with an explicit direction key. Negative values make bar length alone misleading. C2ST retains the frozen lower-is-better convention with an explicit target-0.5 caveat.

## Reproduce and audit

Run `python3 scripts/analyze_generation_patterns.py` and `python3 scripts/check_generation_patterns.py`. No new generation or score fitting occurs. Original measurements and previous macro snapshots remain intact.

- [Methods and limits](methods.json)
- [All per-task classifications](task-patterns.csv)
- [Category counts](category-patterns.csv)
- [Metric-direction audit](metric-direction-audit.csv)
- [Derived data and input hashes](patterns.json)
- [Current native scores](../generation-comparison-v2/task-scores.csv)
- [Current four-model report and first-attempt sensitivity](../generation-comparison-v2/report.md)
- [Every repair, failed revision and exclusion](../../experiments/generation-repairs-v1/README.md)
- [Original four-model snapshot](../generation-comparison-v1/report.md)
- [Thirty specialist source reviews](../../literature/specialist-review-2026-11-01/)
