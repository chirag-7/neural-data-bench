# A14 — Missing pose imputation

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** DISK evaluation datasets

**State:** not evaluated; candidate_pending_validation. Mapped resource only; license, acquisition, split, scorer and baseline gates are not yet all validated.

## Scientific use

Input: Partially observed 2D/3D skeleton time series

Target/ground truth: Observed positions hidden under known masks

Specialist candidates: DISK; interpolation; Kalman smoother

General-model route: General time-series foundation model

## Execution and performance

No experiment admitted yet. All measurements are centralized in [results](../../../results/). Current best: **not verified**. Missing scores are unknown, not zero. Literature resources are not newly executed results.

## Limitations

Artificial missingness may understate occlusion difficulty

## Sources

- [https://www.nature.com/articles/s41592-025-02893-y](https://www.nature.com/articles/s41592-025-02893-y)
