# What the four-model results mean

The broad descriptive trend is improvement across model generations, with substantial task-specific exceptions. It is not a smooth scaling law, and it does not establish that laboratories should replace their specialist tools.

## Quantitative findings

| Comparison | Later model better | Later model worse | Numerical tie | Incomplete |
|---|---:|---:|---:|---:|
| GPT-5 versus GPT-4.1 | 17 | 6 | 0 | 7 |
| GPT-5.6 Sol versus GPT-5 | 22 | 3 | 0 | 5 |
| GPT-6.1 Sol versus GPT-5.6 Sol | 20 | 9 | 1 | 0 |
| GPT-6.1 Sol versus GPT-4.1 | 23 | 2 | 0 | 5 |
| GPT-6.1 Sol versus GPT-5 | 21 | 4 | 0 | 5 |

These are final-usability task means, including the separately documented historical Sol repairs. Each task counts once; its dependent slices are averaged equally in its own metric. Missing results are excluded from numeric comparisons and explicitly counted as incomplete. Native metric magnitudes are never averaged across tasks.

The large endpoint comparison is 23/25 complete task pairs in GPT-6.1's favor against GPT-4.1. Requiring both programs to meet their original line limits gives 22 better / 2 worse across 24 eligible pairs. Thus the endpoint direction survives this format sensitivity. It is still a description of this selected panel, not an estimate for all neuroscience tasks.

Nine of 30 tasks improve at all three adjacent model steps: C05, E01, F04, H01, H02, K01, K06, L04 and L06. Fourteen have a reversal or partial numerical tie, and seven have at least one missing model result. Among the 23 complete trajectories, nine are strictly monotonic. The same ordered model labels therefore do not yield a universal monotonic curve.

GPT-4.1 and GPT-5 each produce numeric outputs on 32/37 slices, with 31 and 30 meeting line limits respectively. The retained Sol usability results are 37/37 each, with 29 strict-format successes for GPT-5.6 and 37 for GPT-6.1. These usability totals include selective repairs for historical Sol failures. In the original first-attempt sensitivity, GPT-6.1 versus GPT-5.6 is 20 better / 7 worse / 3 incomplete, rather than 20 / 9 / 1. The direct endpoint comparisons versus GPT-4.1 and GPT-5 retain the same win/loss counts, because those models already fail on the repaired J08 task.

All family-balanced directional summaries are positive, including 0.9028 for GPT-6.1 versus GPT-4.1 and 0.3452 versus GPT-5.6. This statistic averages win/loss signs within categories and then categories equally; it is not an effect size, confidence level or probability that one model is better. Small, selected and partly dependent categories limit inference.

## Qualitative findings

Failure is partly a software reliability problem. Both older API models use removed NumPy array methods on H08; GPT-5 also calls an unsupported scikit-learn constructor argument on K04. Other failures involve indexing, malformed output or shape assumptions. This panel therefore measures the ability to deliver a working numerical procedure in the specified runtime, alongside algorithm choice. It does not isolate neural-data understanding from software compatibility.

The tasks expose different weaknesses. Compression, gene-expression calibration, imaging quality, neural encoding and segmentation cannot be reduced to one skill. Models can choose effective conventional estimators on one task and make a basic representation error on another. Model-size, training-compute and equally spaced time measurements are absent, and the API/Codex wrappers and reasoning settings differ. Fitting an exponent or extrapolating future specialist crossover dates would be unjustified.

## Quantitative + qualitative findings

- **Clear ordered example: P300 decoding (H02).** Held-out person-equal AUC is 0.5731 → 0.7458 → 0.7572 → 0.7885. GPT-6.1 exceeds the fixed tested xDAWN point score of 0.7612. Ten held-out people and one new program per older model do not establish a general replacement recommendation or current-best specialist superiority.
- **Neural co-smoothing (E01).** Native bits/spike means move from −4.2761 → −2.5475 → 0.2035 → 0.2074. The biggest observed transition is from very poor predictions to useful rate predictions, while the later change is much smaller. These three dependent source slices are not three independent generations or biological replications.
- **Exceptions matter.** GPT-4.1 beats GPT-6.1 on the tested B07 voltage-compression and K05 marker-fraction endpoints. GPT-5 beats GPT-6.1 on B03 drift recovery, B08 event compression, I07 fNIRS and I10 MRI quality. Those reversals rule out a blanket 'always use the newest model' rule.
- **Specialists still lead important endpoints.** The retained GPT-6.1 means remain below the tested references on spike sorting B01 (0.7505 versus 0.9409), puncta segmentation J08 (0.5756 versus 0.8625), calcium inference C05 (0.4679 versus 0.4753) and layer transfer K04 (0.5506 versus 0.5546). The last two small gaps are not demonstrated practical inferiority; J08 has only two test fields. Each comparison needs its own uncertainty and operational assessment.
- **Tiny differences are not laws.** A15 scores of 0.99196 and 0.99208 are extremely close; near-chance L06 classifier diagnostics have their own finite-sample noise. C06 correlation can improve while count calibration remains poor. A positive sign alone is insufficient for a practical claim.

A defensible operational recommendation is to evaluate general-model-generated procedures as task-specific candidates where they beat a relevant tested reference, then validate across independent sources, practical tolerances, runtime budgets and current specialist implementations. The specialist literature reviews cover all 30 tasks, but none certify the global strongest model on these custom contracts. Published scores on other splits were not inserted as matched measurements.

## Audit and scope

This extension covers the existing 30 tasks in 14 categories; it adds model generations, not new neuroscience coverage. Sixty API generations cost approximately $4.13 using conservative uncached-rate token accounting. All 74 attempts remain in the consolidated record, including ten failures; all 64 successful outputs passed saved-output rescoring or independent decoding.

[Exact report and strict-format sensitivity](report.md), [methods](methods.md), [all task scores](task-scores.csv), [six pairwise comparisons](task-pairs.csv), [first-attempt sensitivity](first-attempt-pairs.csv), [programs and per-task audit pages](../../experiments/generation-extension-v1/tasks/), [specialist reviews](../../literature/specialist-review-2026-11-01/).
