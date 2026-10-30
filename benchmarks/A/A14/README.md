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

## v0.4 admission and execution

Decision: **measured** (2026-10-30). Rat7M raw measured mocap246MB archive acquired from immutable DISK Zenodo18405201 CC BY4.0; seven original recordings, real measured targets and controlled synthetic gaps. Three trainingrats versus two test rats, six head/spine landmarks, nonoverlapping31frame windows. Custom endpoint, not official DISK full distribution.

[Source-linked admission evidence](../../../literature/admission-v04-behavior-population.json). [Actual protocol and artifacts](../../../experiments/A14). [Central task results](../../../results/A14.json).

## v0.5 execution status

measured. Rat7M raw measured mocap246MB archive acquired from immutable DISK Zenodo18405201 CC BY4.0; seven original recordings, real measured targets and controlled synthetic gaps. Three trainingrats versus two test rats, six head/spine landmarks, nonoverlapping31frame windows. Custom endpoint, not official DISK full distribution.

[Admission/source evidence](../../../literature/admission-v04-behavior-population.json). [Actual protocol/worklog](../../../experiments/A14). [Task measurements](../../../results/A14.json).
