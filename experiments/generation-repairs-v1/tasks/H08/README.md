# H08: manual repair record

These are manually repaired usability results. Original outputs and failures remain in the [API study](../../../generation-extension-v1/tasks/H08/). No new generation or test-score-based algorithm selection was used.

| Model | Revision | Slice | Status | Native score | Evidence |
|---|---|---|---|---:|---|
| gpt-4.1-2025-04-14 | r1 | expansion-v1 | failed | not scored | [Result](../../../../experiments/generation-repairs-v1/artifacts/H08/gpt-4.1-2025-04-14/r1/expansion-v1/result.json) |
| gpt-5-2025-08-07 | r1 | expansion-v1 | measured | 0.6783412614813794 | [Result](../../../../experiments/generation-repairs-v1/artifacts/H08/gpt-5-2025-08-07/r1/expansion-v1/result.json) |
| gpt-4.1-2025-04-14 | r2 | expansion-v1 | measured | 0.7252734503405033 | [Result](../../../../experiments/generation-repairs-v1/artifacts/H08/gpt-4.1-2025-04-14/r2/expansion-v1/result.json) |
| gpt-5.6-sol | format-r1 | expansion-v1 | measured | 0.8027158427646084 | [Result](../../../../experiments/generation-repairs-v1/artifacts/H08/gpt-5.6-sol/format-r1/expansion-v1/result.json) |

## Revision details

- **gpt-4.1-2025-04-14 / r1:** Use NumPy 2-compatible np.ptp; remove removed multi_class keyword where present, retaining multinomial-capable original solver.
- **gpt-5-2025-08-07 / r1:** Use NumPy 2-compatible np.ptp; remove removed multi_class keyword where present, retaining multinomial-capable original solver.
- **gpt-4.1-2025-04-14 / r2:** Use NumPy 2-compatible np.ptp; remove removed multi_class keyword where present, retaining multinomial-capable original solver. Correct the allocated feature width to the actual 17 features; feature formulas unchanged.
- **gpt-5.6-sol / format-r1:** Mechanical AST-preserving reformat; no estimator, parameter, operation, literal or statement order changes. Original line violation remains historical.

The consolidated record identifies the latest audited successful revision per slice. Earlier failures remain intact. [Full plan](../../plan.json), [overall policy](../../README.md), [current macro report](../../../../analysis/generation-patterns-v1/report.md).
