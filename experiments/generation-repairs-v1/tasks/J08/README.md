# J08: manual repair record

These are manually repaired usability results. Original outputs and failures remain in the [API study](../../../generation-extension-v1/tasks/J08/). No new generation or test-score-based algorithm selection was used.

| Model | Revision | Slice | Status | Native score | Evidence |
|---|---|---|---|---:|---|
| gpt-4.1-2025-04-14 | r1 | expansion-v1 | failed | not scored | [Result](../../../../experiments/generation-repairs-v1/artifacts/J08/gpt-4.1-2025-04-14/r1/expansion-v1/result.json) |
| gpt-5-2025-08-07 | r1 | expansion-v1 | measured | 0.24323205422323543 | [Result](../../../../experiments/generation-repairs-v1/artifacts/J08/gpt-5-2025-08-07/r1/expansion-v1/result.json) |
| gpt-4.1-2025-04-14 | r2 | expansion-v1 | failed | not scored | [Result](../../../../experiments/generation-repairs-v1/artifacts/J08/gpt-4.1-2025-04-14/r2/expansion-v1/result.json) |

## Revision details

- **gpt-4.1-2025-04-14 / r1:** Remove invalid hash-based caching of mutable ndarray instance labels.
- **gpt-5-2025-08-07 / r1:** Request only EDT index arrays, rather than indexing the default distances-and-indices tuple.
- **gpt-4.1-2025-04-14 / r2:** Remove invalid hash-based caching of mutable ndarray instance labels. Cache identical training-patch probabilities outside the existing threshold loop. Same training forest, thresholds and predictions; remove repeated work after timeout.

The consolidated record identifies the latest audited successful revision per slice. Earlier failures remain intact. [Full plan](../../plan.json), [overall policy](../../README.md), [current macro report](../../../../analysis/generation-patterns-v1/report.md).
