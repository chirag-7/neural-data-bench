# B07: manual repair record

These are manually repaired usability results. Original outputs and failures remain in the [API study](../../../generation-extension-v1/tasks/B07/). No new generation or test-score-based algorithm selection was used.

| Model | Revision | Slice | Status | Native score | Evidence |
|---|---|---|---|---:|---|
| gpt-5-2025-08-07 | r1 | compression-v1 | measured | 7.210052490234375 | [Result](../../../../experiments/generation-repairs-v1/artifacts/B07/gpt-5-2025-08-07/r1/compression-v1/result.json) |

## Revision details

- **gpt-5-2025-08-07 / r1:** Restore the declared (time, channel) shape before inverse channel cumulative sum; retain bitstream algorithm.

The consolidated record identifies the latest audited successful revision per slice. Earlier failures remain intact. [Full plan](../../plan.json), [overall policy](../../README.md), [current macro report](../../../../analysis/generation-patterns-v1/report.md).
