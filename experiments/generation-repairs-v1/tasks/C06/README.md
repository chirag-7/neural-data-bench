# C06: manual repair record

These are manually repaired usability results. Original outputs and failures remain in the [API study](../../../generation-extension-v1/tasks/C06/). No new generation or test-score-based algorithm selection was used.

| Model | Revision | Slice | Status | Native score | Evidence |
|---|---|---|---|---:|---|
| gpt-4.1-2025-04-14 | r1 | batch-v11 | measured | 0.5283479568442431 | [Result](../../../../experiments/generation-repairs-v1/artifacts/C06/gpt-4.1-2025-04-14/r1/batch-v11/result.json) |

## Revision details

- **gpt-4.1-2025-04-14 / r1:** Materialize the original GroupKFold splits using provided training groups; clip roundoff-negative rolling variances before sqrt. No label/test feedback or estimator replacement.

The consolidated record identifies the latest audited successful revision per slice. Earlier failures remain intact. [Full plan](../../plan.json), [overall policy](../../README.md), [current macro report](../../../../analysis/generation-patterns-v1/report.md).
