# A15: manual repair record

These are manually repaired usability results. Original outputs and failures remain in the [API study](../../../generation-extension-v1/tasks/A15/). No new generation or test-score-based algorithm selection was used.

| Model | Revision | Slice | Status | Native score | Evidence |
|---|---|---|---|---:|---|
| gpt-5-2025-08-07 | format-r1 | batch-v11 | measured | 0.979201212547653 | [Result](../../../../experiments/generation-repairs-v1/artifacts/A15/gpt-5-2025-08-07/format-r1/batch-v11/result.json) |
| gpt-5.6-sol | format-r1 | batch-v11 | measured | 0.9863118287200278 | [Result](../../../../experiments/generation-repairs-v1/artifacts/A15/gpt-5.6-sol/format-r1/batch-v11/result.json) |

## Revision details

- **gpt-5-2025-08-07 / format-r1:** Mechanical AST-preserving reformat; no estimator, parameter, operation, literal or statement order changes. Original line violation remains historical.
- **gpt-5.6-sol / format-r1:** Mechanical AST-preserving reformat; no estimator, parameter, operation, literal or statement order changes. Original line violation remains historical.

The consolidated record identifies the latest audited successful revision per slice. Earlier failures remain intact. [Full plan](../../plan.json), [overall policy](../../README.md), [current macro report](../../../../analysis/generation-patterns-v1/report.md).
