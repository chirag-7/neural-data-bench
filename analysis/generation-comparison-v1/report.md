# Four-model generation comparison

Four-model comparison across 30 tasks and 14 categories. Native score trajectories and six model pairs are descriptive; incomplete attempts remain visible.

Final usability scores apply the documented repair overlay to selected existing Sol procedures. Original frozen measurements are unchanged. New GPT-4.1/GPT-5 calls use the API; existing Sol runs used Codex, a provider/wrapper confound.

## Descriptive pairwise results

| Earlier | Later | Better | Worse | Numerical tie | Incomplete | Family-balanced direction |
|---|---|---:|---:|---:|---:|---:|
| gpt-4.1-2025-04-14 | gpt-5-2025-08-07 | 17 | 6 | 0 | 7 | 0.5758 |
| gpt-4.1-2025-04-14 | gpt-5.6-sol | 21 | 4 | 0 | 5 | 0.7639 |
| gpt-4.1-2025-04-14 | gpt-6.1-sol | 23 | 2 | 0 | 5 | 0.9028 |
| gpt-5-2025-08-07 | gpt-5.6-sol | 22 | 3 | 0 | 5 | 0.7778 |
| gpt-5-2025-08-07 | gpt-6.1-sol | 21 | 4 | 0 | 5 | 0.7222 |
| gpt-5.6-sol | gpt-6.1-sol | 20 | 9 | 1 | 0 | 0.3452 |

## Strict-format sensitivity

Both model procedures must meet their original line limits and have numeric scores on every slice. Format-ineligible numeric pairs remain visible in the main table; this sensitivity excludes them.

| Earlier | Later | Eligible tasks | Better | Worse | Tie | Incomplete | Format-ineligible |
|---|---|---:|---:|---:|---:|---:|---:|
| gpt-4.1-2025-04-14 | gpt-5-2025-08-07 | 21 | 16 | 5 | 0 | 7 | 2 |
| gpt-4.1-2025-04-14 | gpt-5.6-sol | 22 | 19 | 3 | 0 | 5 | 3 |
| gpt-4.1-2025-04-14 | gpt-6.1-sol | 24 | 22 | 2 | 0 | 5 | 1 |
| gpt-5-2025-08-07 | gpt-5.6-sol | 22 | 19 | 3 | 0 | 5 | 3 |
| gpt-5-2025-08-07 | gpt-6.1-sol | 23 | 19 | 4 | 0 | 5 | 2 |
| gpt-5.6-sol | gpt-6.1-sol | 26 | 18 | 8 | 0 | 0 | 4 |

Positive family-balanced direction means more improvements than regressions after equalizing category weights; it is descriptive, with incomplete task-pairs excluded and coverage reported. It does not measure effect size or probability of superiority.

## Findings

- gpt-5-2025-08-07 versus gpt-4.1-2025-04-14: 17 task improvements, 6 regressions, 0 numerical ties and 7 incomplete comparisons in the final usability track.
- gpt-5.6-sol versus gpt-4.1-2025-04-14: 21 task improvements, 4 regressions, 0 numerical ties and 5 incomplete comparisons in the final usability track.
- gpt-6.1-sol versus gpt-4.1-2025-04-14: 23 task improvements, 2 regressions, 0 numerical ties and 5 incomplete comparisons in the final usability track.
- gpt-5.6-sol versus gpt-5-2025-08-07: 22 task improvements, 3 regressions, 0 numerical ties and 5 incomplete comparisons in the final usability track.
- gpt-6.1-sol versus gpt-5-2025-08-07: 21 task improvements, 4 regressions, 0 numerical ties and 5 incomplete comparisons in the final usability track.
- gpt-6.1-sol versus gpt-5.6-sol: 20 task improvements, 9 regressions, 1 numerical ties and 0 incomplete comparisons in the final usability track.
- 9 of 30 tasks improve at every adjacent model step; failures prevent trajectory classification where incomplete. This is descriptive and does not establish a scaling law.
- Quantitative: counts describe these fixed tasks, not a random sample of neuroscience problems; task and family weighting answer different questions.
- Qualitative: specialist candidates vary by modality and input requirements. Wins over a conventional local reference are insufficient grounds to replace the current best specialist.
- Quantitative + qualitative: investigate reversals and near-ceiling tasks individually; native score differences, calibration and runtime can change practical conclusions.
- No extrapolation of future crossover dates, compute scaling or universal newer-model superiority is supported.

## Practical interpretation

A win over our fixed tested reference is not a win over the best current specialist. The thirty specialist reviews retain their source links and input/split limitations. No blanket replacement recommendation follows. Inspect each task’s native score, line-limit compliance and current-specialist review.

## Files and audit trail

- [Methods](methods.md)
- [Native task scores](task-scores.csv)
- [All slice records](comparison-measurements.jsonl)
- [Six pairwise task comparisons](task-pairs.csv)
- [First-attempt sensitivity](first-attempt-pairs.csv)
- [Machine-readable trajectories](generation-comparison.json)
- [Frozen historical three-model analysis](../practical-review-2026-11-01/report.md)

Original GPT-6 Sol data remain in the historical ledger and report; GPT-6 Sol is excluded from the current four-model display.
