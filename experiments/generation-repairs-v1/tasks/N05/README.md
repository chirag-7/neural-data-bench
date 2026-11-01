# N05: manual repair record

These are manually repaired usability results. Original outputs and failures remain in the [API study](../../../generation-extension-v1/tasks/N05/). No new generation or test-score-based algorithm selection was used.

| Model | Revision | Slice | Status | Native score | Evidence |
|---|---|---|---|---:|---|
| gpt-5-2025-08-07 | r1 | expansion-v1 | failed | not scored | [Result](../../../../experiments/generation-repairs-v1/artifacts/N05/gpt-5-2025-08-07/r1/expansion-v1/result.json) |
| gpt-4.1-2025-04-14 | format-r1 | expansion-v1 | measured | 0.0 | [Result](../../../../experiments/generation-repairs-v1/artifacts/N05/gpt-4.1-2025-04-14/format-r1/expansion-v1/result.json) |
| gpt-5.6-sol | format-r1 | expansion-v1 | measured | 1.0 | [Result](../../../../experiments/generation-repairs-v1/artifacts/N05/gpt-5.6-sol/format-r1/expansion-v1/result.json) |
| gpt-5-2025-08-07 | r2 | expansion-v1 | measured | 1.0 | [Result](../../../../experiments/generation-repairs-v1/artifacts/N05/gpt-5-2025-08-07/r2/expansion-v1/result.json) |
| gpt-5-2025-08-07 | r3 | expansion-v1 | measured | 1.0 | [Result](../../../../experiments/generation-repairs-v1/artifacts/N05/gpt-5-2025-08-07/r3/expansion-v1/result.json) |

## Revision details

- **gpt-5-2025-08-07 / r1:** Classify time-series groups by the visit path (including stimulus/acquisition hard-link aliases), rather than a resolved object name. Preserve the returned schema and extraction algorithm.
- **gpt-4.1-2025-04-14 / format-r1:** Mechanical AST-preserving reformat; no estimator, parameter, operation, literal or statement order changes. Original line violation remains historical.
- **gpt-5.6-sol / format-r1:** Mechanical AST-preserving reformat; no estimator, parameter, operation, literal or statement order changes. Original line violation remains historical.
- **gpt-5-2025-08-07 / r2:** Classify time-series groups by the visit path (including stimulus/acquisition hard-link aliases), rather than a resolved object name. Preserve the returned schema and extraction algorithm. Traverse stimulus and acquisition aliases independently with ancestor-cycle protection; visititems skips previously visited hard-linked objects. Parse actual supplied-file metadata, never expected answers. Normalize visit paths to absolute form before prefix classification.
- **gpt-5-2025-08-07 / r3:** Classify time-series groups by the visit path (including stimulus/acquisition hard-link aliases), rather than a resolved object name. Preserve the returned schema and extraction algorithm. Traverse stimulus and acquisition aliases independently with ancestor-cycle protection; visititems skips previously visited hard-linked objects. Parse actual supplied-file metadata, never expected answers. Normalize visit paths to absolute form before prefix classification. Mechanical AST-identical physical-line formatting; original format violation remains historical.

The consolidated record identifies the latest audited successful revision per slice. Earlier failures remain intact. [Full plan](../../plan.json), [overall policy](../../README.md), [current macro report](../../../../analysis/generation-patterns-v1/report.md).
