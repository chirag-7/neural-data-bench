# A14 — Missing pose imputation

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** DISK evaluation datasets

**State:** measured. Current status for this exact task-resource slice; current global best remains unverified.

## Scientific use

Input: Partially observed 2D/3D skeleton time series

Target/ground truth: Observed positions hidden under known masks

Mapped specialist candidates (not all evaluated): DISK; interpolation; Kalman smoother

General-model route: General time-series foundation model

## Execution and performance

**Executed slice:** Rat7M: six-landmark, 31-frame windows with an artificial seven-frame HeadF gap; three training and two test rats.

[Frozen protocol and artifacts](../../../experiments/A14). [Measured scores and references](../../../results/A14.json). [Central data](../../../results/measurements.csv). Missing or failed outputs are retained.

## Limitations

Artificial missingness may understate occlusion difficulty

## Sources

- [https://www.nature.com/articles/s41592-025-02893-y](https://www.nature.com/articles/s41592-025-02893-y)
- [https://zenodo.org/records/18405201](https://zenodo.org/records/18405201)

Source associations include historical alternatives; actual acquired files are identified in the executed protocol/manifest.

## Historical v0.4 admission and execution

Decision: **measured** (2026-10-30). Rat7M raw measured mocap246MB archive acquired from immutable DISK Zenodo18405201 CC BY4.0; seven original recordings, real measured targets and controlled synthetic gaps. Three trainingrats versus two test rats, six head/spine landmarks, nonoverlapping31frame windows. Custom endpoint, not official DISK full distribution.

[Source-linked admission evidence](../../../literature/admission-v04-behavior-population.json). [Actual protocol and artifacts](../../../experiments/A14). [Central task results](../../../results/A14.json).

## Current admission and execution

Preview 0.10: measured. Rat7M raw measured mocap246MB archive acquired from immutable DISK Zenodo18405201 CC BY4.0; seven original recordings, real measured targets and controlled synthetic gaps. Three trainingrats versus two test rats, six head/spine landmarks, nonoverlapping31frame windows. Custom endpoint, not official DISK full distribution.

[Admission/source evidence](../../../literature/admission-v04-behavior-population.json). [Actual protocol/worklog](../../../experiments/A14). [Task measurements](../../../results/A14.json).
