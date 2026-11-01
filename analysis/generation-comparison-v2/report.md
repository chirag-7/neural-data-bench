# Four-model generation comparison

Four-model comparison across 30 tasks and 14 categories. Native score trajectories and six model pairs are descriptive; incomplete attempts remain visible.

Final usability scores include explicitly versioned manual runtime, optimizer and format repairs across model generations. Original submissions and first-attempt outcomes remain unchanged. GPT-4.1/GPT-5 use the API; Sol runs use Codex. These are repaired analysis procedures, not an unbiased generation ranking.

## Descriptive pairwise results

| Earlier | Later | Better | Worse | Numerical tie | Incomplete | Family-balanced direction |
|---|---|---:|---:|---:|---:|---:|
| gpt-4.1-2025-04-14 | gpt-5-2025-08-07 | 18 | 11 | 0 | 1 | 0.3205 |
| gpt-4.1-2025-04-14 | gpt-5.6-sol | 24 | 5 | 0 | 1 | 0.7564 |
| gpt-4.1-2025-04-14 | gpt-6.1-sol | 27 | 2 | 0 | 1 | 0.9231 |
| gpt-5-2025-08-07 | gpt-5.6-sol | 25 | 4 | 1 | 0 | 0.7143 |
| gpt-5-2025-08-07 | gpt-6.1-sol | 24 | 5 | 1 | 0 | 0.6786 |
| gpt-5.6-sol | gpt-6.1-sol | 20 | 9 | 1 | 0 | 0.3452 |

## Strict-format sensitivity

Both model procedures must meet their original line limits and have numeric scores on every slice. Format-ineligible numeric pairs remain visible in the main table; this sensitivity excludes them.

| Earlier | Later | Eligible tasks | Better | Worse | Tie | Incomplete | Format-ineligible |
|---|---|---:|---:|---:|---:|---:|---:|
| gpt-4.1-2025-04-14 | gpt-5-2025-08-07 | 29 | 18 | 11 | 0 | 1 | 0 |
| gpt-4.1-2025-04-14 | gpt-5.6-sol | 29 | 24 | 5 | 0 | 1 | 0 |
| gpt-4.1-2025-04-14 | gpt-6.1-sol | 29 | 27 | 2 | 0 | 1 | 0 |
| gpt-5-2025-08-07 | gpt-5.6-sol | 30 | 25 | 4 | 1 | 0 | 0 |
| gpt-5-2025-08-07 | gpt-6.1-sol | 30 | 24 | 5 | 1 | 0 | 0 |
| gpt-5.6-sol | gpt-6.1-sol | 30 | 20 | 9 | 1 | 0 | 0 |

Positive family-balanced direction means more improvements than regressions after equalizing category weights; it is descriptive, with incomplete task-pairs excluded and coverage reported. It does not measure effect size or probability of superiority.

## Findings

- gpt-5-2025-08-07 versus gpt-4.1-2025-04-14: 18 task improvements, 11 regressions, 0 numerical ties and 1 incomplete comparisons in the final usability track.
- gpt-5.6-sol versus gpt-4.1-2025-04-14: 24 task improvements, 5 regressions, 0 numerical ties and 1 incomplete comparisons in the final usability track.
- gpt-6.1-sol versus gpt-4.1-2025-04-14: 27 task improvements, 2 regressions, 0 numerical ties and 1 incomplete comparisons in the final usability track.
- gpt-5.6-sol versus gpt-5-2025-08-07: 25 task improvements, 4 regressions, 1 numerical ties and 0 incomplete comparisons in the final usability track.
- gpt-6.1-sol versus gpt-5-2025-08-07: 24 task improvements, 5 regressions, 1 numerical ties and 0 incomplete comparisons in the final usability track.
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
