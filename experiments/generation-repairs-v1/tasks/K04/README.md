# K04: manual repair record

These are manually repaired usability results. Original outputs and failures remain in the [API study](../../../generation-extension-v1/tasks/K04/). No new generation or test-score-based algorithm selection was used.

| Model | Revision | Slice | Status | Native score | Evidence |
|---|---|---|---|---:|---|
| gpt-4.1-2025-04-14 | r1 | expansion-v1 | failed | not scored | [Result](../../../../experiments/generation-repairs-v1/artifacts/K04/gpt-4.1-2025-04-14/r1/expansion-v1/result.json) |
| gpt-5-2025-08-07 | r1 | expansion-v1 | failed | not scored | [Result](../../../../experiments/generation-repairs-v1/artifacts/K04/gpt-5-2025-08-07/r1/expansion-v1/result.json) |
| gpt-4.1-2025-04-14 | r2 | expansion-v1 | measured | 0.5290441742064551 | [Result](../../../../experiments/generation-repairs-v1/artifacts/K04/gpt-4.1-2025-04-14/r2/expansion-v1/result.json) |
| gpt-5-2025-08-07 | r2 | expansion-v1 | measured | 0.5175064764639699 | [Result](../../../../experiments/generation-repairs-v1/artifacts/K04/gpt-5-2025-08-07/r2/expansion-v1/result.json) |

## Revision details

- **gpt-4.1-2025-04-14 / r1:** Remove removed multi_class keyword; retain original multinomial-capable solver and train-only model selection.
- **gpt-5-2025-08-07 / r1:** Remove removed multi_class keyword; retain original multinomial-capable solver and train-only model selection.
- **gpt-4.1-2025-04-14 / r2:** Remove removed multi_class keyword; retain original multinomial-capable solver and train-only model selection. Use the deterministic LBFGS optimizer for the same multinomial L2 logistic objective, preserving original regularization grid, group folds, weights and input transforms, after SAGA timed out. No test-score tuning.
- **gpt-5-2025-08-07 / r2:** Remove removed multi_class keyword; retain original multinomial-capable solver and train-only model selection. Use the deterministic LBFGS optimizer for the same multinomial L2 logistic objective, preserving original regularization grid, group folds, weights and input transforms, after SAGA timed out. No test-score tuning.

The consolidated record identifies the latest audited successful revision per slice. Earlier failures remain intact. [Full plan](../../plan.json), [overall policy](../../README.md), [current macro report](../../../../analysis/generation-patterns-v1/report.md).
