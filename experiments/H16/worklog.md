# H16 data and preparation worklog

2026-10-30:

1. Located the original EEGdenoiseNet repository and paper, then used GitHub's public API to resolve master to immutable commit `8d290661146c7189c98cc04812d37371d4b9426c`. Inspected the original file tree and MIT license.
2. Read the paper's acquisition, preprocessing, mixture and temporal-RRMSE definitions. Verified the original `data_prepare.py` uses `10**(0.1*SNR)` in its **RMS** ratio. Preserved that convention explicitly rather than silently interpreting it as ordinary power-SNR dB.
3. Froze a component-disjoint seeded split, equal SNR allocation, paired mixture normalization, primary mean per-segment RRMSE and a training-only stationary Wiener reference before evaluated-model calls.
4. Implemented pinned-file acquisition, source SHA-256 manifests, source-index and duplicate-byte split assertions, finite-value checks and exact shape checks. No original physiological recordings or derived arrays are added to tracked source.

Model submissions and scores are maintained by the release evaluator. This data-preparation subtask did not call evaluated models.

5. Preparation completed with 2000 training pairs and 600 evaluation pairs. Split and exact duplicate-component checks passed. Temporal-RRMSE zero-prediction identity is exactly 1; uncorrected mixture error agrees with the analytic SNR-derived expectation. Frozen Wiener reference RRMSE was 0.6539532789440188. No parameters were changed after scoring; see verification.json.

## v 0.4 execution record

Frozen task prompt/run-spec and adapter/fixture hashes were recorded before generation. Three exact requested model IDs, high reasoning, one no-tool CLI submission each, no test labels or execution feedback. Programs were reviewed and run unchanged with 180 sprocess limit/one numerical thread. All generated code and sanitized usage/tool events retained.

- gpt-5.6-sol: temporal_rrmse=0.461606651545; formatting compliant.
- gpt-6-sol: temporal_rrmse=0.526478350163; formatting compliant.
- gpt-6.1-sol: temporal_rrmse=0.453383594751; formatting compliant.

Reference: task-baseline; Local conventional task baseline; strongest specialist unverified. Current strongest specialist unverified. [Full result records](../../results/H16.json), [execution logs](../../results/execution/), [prediction artifacts](../../results/predictions/H16/). No statistical significance claim.
