# H16 data and preparation worklog

2026-10-30:

1. Located the original EEGdenoiseNet repository and paper, then used GitHub's public API to resolve master to immutable commit `8d290661146c7189c98cc04812d37371d4b9426c`. Inspected the original file tree and MIT license.
2. Read the paper's acquisition, preprocessing, mixture and temporal-RRMSE definitions. Verified the original `data_prepare.py` uses `10**(0.1*SNR)` in its **RMS** ratio. Preserved that convention explicitly rather than silently interpreting it as ordinary power-SNR dB.
3. Froze a component-disjoint seeded split, equal SNR allocation, paired mixture normalization, primary mean per-segment RRMSE and a training-only stationary Wiener reference before evaluated-model calls.
4. Implemented pinned-file acquisition, source SHA-256 manifests, source-index and duplicate-byte split assertions, finite-value checks and exact shape checks. No original physiological recordings or derived arrays are added to tracked source.

Model submissions and scores are maintained by the release evaluator. This data-preparation subtask did not call evaluated models.
