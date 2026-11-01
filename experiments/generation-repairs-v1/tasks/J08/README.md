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

## Final runtime repair

Training-only profiling found 16,451,616 eligible pixel rows; feature extraction completed in about 2.8 seconds, leaving forest fitting as the bottleneck. Revision r3 capped each of the original 30 depth-9 trees at 250,000 bootstrap draws, with the original seed, one thread, features, threshold grid and inference unchanged. The cap was fixed before new test scoring; no score-based parameter search occurred. This changes the fitted procedure and is explicitly labeled a **manual training-budget adaptation**, not an exact compatibility fix or untouched GPT-4.1 capability.

Revision r3 then exposed a SciPy watershed marker-type error. A synthetic-array probe reproduced it; r4 uses signed int32 markers rather than uint8, as required by SciPy and to avoid truncating instance IDs.

| Revision | Outcome | Score | Evidence |
|---|---|---:|---|
| r3 | failed: watershed marker type | unscored | [Preserved result](../../artifacts/J08/gpt-4.1-2025-04-14/r3/expansion-v1/result.json) |
| r4 | measured and independently audited | 0.000 instance F1 | [Result](../../artifacts/J08/gpt-4.1-2025-04-14/r4/expansion-v1/result.json), [independent audit](../../artifacts/J08/gpt-4.1-2025-04-14/r4/expansion-v1/saved-output-audit.json) |

The procedure completed in **24.663 seconds**, within the unchanged 180-second computation limit. Both test-field F1 scores are zero. Direct inspection confirms the saved arrays contain no predicted foreground pixels or positive instance IDs; the repaired method failed to detect puncta. This is an actual scored output from the retained procedure, not a missing-value imputation or a substituted fallback. We retain the poor scientific result and do not tune the method against held-out scores. The center-versus-background learning target and original high threshold can suppress detections; this is a mechanism hypothesis, not a new fitted intervention. Original data, scorer and earlier failures are unchanged. No new API calls were made.
