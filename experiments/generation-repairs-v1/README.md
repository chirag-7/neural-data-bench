# Manual repair and exclusion audit

Recovered **9 of 10** original older-model runtime failures. **1** remain unscored under the original task requirements. No new API calls were made. Original attempts and previous macro reports are preserved.

Physical-line violations were separately repaired by mechanically preserving the complete Python AST. This does not establish original model brevity or compliance; original violations remain in the first-attempt panel. Formats were rerun, audited and required to retain scores where an earlier numeric comparison exists.

| Task | Model | Revision | Outcome | Native score | Patch |
|---|---|---|---|---:|---|
| B07 | gpt-5-2025-08-07 | r1 | measured | 7.210052490234375 | Restore the declared (time, channel) shape before inverse channel cumulative sum; retain bitstream algorithm. |
| C06 | gpt-4.1-2025-04-14 | r1 | measured | 0.5283479568442431 | Materialize the original GroupKFold splits using provided training groups; clip roundoff-negative rolling variances before sqrt. No label/test feedback or estimator replacement. |
| G01 | gpt-4.1-2025-04-14 | r1 | measured | 0.08219552785158157 | Restore missing indentation of the existing alpha list inside fit_predict. |
| H08 | gpt-4.1-2025-04-14 | r1 | failed | unscored | Use NumPy 2-compatible np.ptp; remove removed multi_class keyword where present, retaining multinomial-capable original solver. |
| H08 | gpt-5-2025-08-07 | r1 | measured | 0.6783412614813794 | Use NumPy 2-compatible np.ptp; remove removed multi_class keyword where present, retaining multinomial-capable original solver. |
| J08 | gpt-4.1-2025-04-14 | r1 | failed | unscored | Remove invalid hash-based caching of mutable ndarray instance labels. |
| J08 | gpt-5-2025-08-07 | r1 | measured | 0.24323205422323543 | Request only EDT index arrays, rather than indexing the default distances-and-indices tuple. |
| K04 | gpt-4.1-2025-04-14 | r1 | failed | unscored | Remove removed multi_class keyword; retain original multinomial-capable solver and train-only model selection. |
| K04 | gpt-5-2025-08-07 | r1 | failed | unscored | Remove removed multi_class keyword; retain original multinomial-capable solver and train-only model selection. |
| N05 | gpt-5-2025-08-07 | r1 | failed | unscored | Classify time-series groups by the visit path (including stimulus/acquisition hard-link aliases), rather than a resolved object name. Preserve the returned schema and extraction algorithm. |
| H08 | gpt-4.1-2025-04-14 | r2 | measured | 0.7252734503405033 | Use NumPy 2-compatible np.ptp; remove removed multi_class keyword where present, retaining multinomial-capable original solver. Correct the allocated feature width to the actual 17 features; feature formulas unchanged. |
| A15 | gpt-5-2025-08-07 | format-r1 | measured | 0.979201212547653 | Mechanical AST-preserving reformat; no estimator, parameter, operation, literal or statement order changes. Original line violation remains historical. |
| B01 | gpt-5-2025-08-07 | format-r1 | measured | 0.0803921568627451 | Mechanical AST-preserving reformat; no estimator, parameter, operation, literal or statement order changes. Original line violation remains historical. |
| N05 | gpt-4.1-2025-04-14 | format-r1 | measured | 0.0 | Mechanical AST-preserving reformat; no estimator, parameter, operation, literal or statement order changes. Original line violation remains historical. |
| A15 | gpt-5.6-sol | format-r1 | measured | 0.9863118287200278 | Mechanical AST-preserving reformat; no estimator, parameter, operation, literal or statement order changes. Original line violation remains historical. |
| C05 | gpt-5.6-sol | format-r1 | measured | 0.5789139103635804 | Mechanical AST-preserving reformat; no estimator, parameter, operation, literal or statement order changes. Original line violation remains historical. |
| C05 | gpt-5.6-sol | format-r1 | measured | 0.4078136910603323 | Mechanical AST-preserving reformat; no estimator, parameter, operation, literal or statement order changes. Original line violation remains historical. |
| C05 | gpt-5.6-sol | format-r1 | measured | 0.408966150564502 | Mechanical AST-preserving reformat; no estimator, parameter, operation, literal or statement order changes. Original line violation remains historical. |
| C05 | gpt-5.6-sol | format-r1 | measured | 0.38975891067537416 | Mechanical AST-preserving reformat; no estimator, parameter, operation, literal or statement order changes. Original line violation remains historical. |
| C05 | gpt-5.6-sol | format-r1 | measured | 0.47552792525592424 | Mechanical AST-preserving reformat; no estimator, parameter, operation, literal or statement order changes. Original line violation remains historical. |
| H08 | gpt-5.6-sol | format-r1 | measured | 0.8027158427646084 | Mechanical AST-preserving reformat; no estimator, parameter, operation, literal or statement order changes. Original line violation remains historical. |
| N05 | gpt-5.6-sol | format-r1 | measured | 1.0 | Mechanical AST-preserving reformat; no estimator, parameter, operation, literal or statement order changes. Original line violation remains historical. |
| K04 | gpt-4.1-2025-04-14 | r2 | measured | 0.5290441742064551 | Remove removed multi_class keyword; retain original multinomial-capable solver and train-only model selection. Use the deterministic LBFGS optimizer for the same multinomial L2 logistic objective, preserving original regularization grid, group folds, weights and input transforms, after SAGA timed out. No test-score tuning. |
| K04 | gpt-5-2025-08-07 | r2 | measured | 0.5175064764639699 | Remove removed multi_class keyword; retain original multinomial-capable solver and train-only model selection. Use the deterministic LBFGS optimizer for the same multinomial L2 logistic objective, preserving original regularization grid, group folds, weights and input transforms, after SAGA timed out. No test-score tuning. |
| J08 | gpt-4.1-2025-04-14 | r2 | failed | unscored | Remove invalid hash-based caching of mutable ndarray instance labels. Cache identical training-patch probabilities outside the existing threshold loop. Same training forest, thresholds and predictions; remove repeated work after timeout. |
| N05 | gpt-5-2025-08-07 | r2 | measured | 1.0 | Classify time-series groups by the visit path (including stimulus/acquisition hard-link aliases), rather than a resolved object name. Preserve the returned schema and extraction algorithm. Traverse stimulus and acquisition aliases independently with ancestor-cycle protection; visititems skips previously visited hard-linked objects. Parse actual supplied-file metadata, never expected answers. Normalize visit paths to absolute form before prefix classification. |
| N05 | gpt-5-2025-08-07 | r3 | measured | 1.0 | Classify time-series groups by the visit path (including stimulus/acquisition hard-link aliases), rather than a resolved object name. Preserve the returned schema and extraction algorithm. Traverse stimulus and acquisition aliases independently with ancestor-cycle protection; visititems skips previously visited hard-linked objects. Parse actual supplied-file metadata, never expected answers. Normalize visit paths to absolute form before prefix classification. Mechanical AST-identical physical-line formatting; original format violation remains historical. |

## Exclusions

- J08 / gpt-4.1-2025-04-14: Not scored within the 180-second computation limit after compatibility and exact-caching repairs. This is an implementation/budget exclusion, not proof that the model is intrinsically inapplicable to the modality.

## Interpretation

These points measure manually repaired procedures. Optimizer changes preserve the stated training objective but may change numerical convergence and predictions; they are not byte-identical executions. Compatibility/shape fixes may enable an original method without improving its scientific quality. A valid low score stays low: no test-score-driven algorithm replacement was performed. The repaired panel cannot establish that an untouched model would debug itself or outperform specialists autonomously.

[Plan and patch descriptions](plan.json), [consolidated attempts and hashes](../../results/generation-repairs-v1.json), [original API study](../generation-extension-v1/), [original four-model report](../../analysis/generation-comparison-v1/report.md).


[Per-task repair pages](tasks/). The four incomplete historical C05 reference archives remain unavailable; they are not assigned zero or represented as completed reference runs. The existing source ledger preserves those archive gaps separately from the model-runtime repairs above.
