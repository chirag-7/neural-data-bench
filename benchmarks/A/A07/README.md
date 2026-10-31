# A07 — Data-efficient calibrated 3D lab pose

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** Lightning Pose 3D evaluation datasets

**State:** candidate_pending_validation. Current status for this exact task-resource slice; current global best remains unverified.

## Scientific use

Input: Synchronized calibrated views

Target/ground truth: Labeled 3D/multiview landmarks

Mapped specialist candidates (not all evaluated): Lightning Pose 3D; DANNCE

General-model route: General multiview encoder with matched labels

## Execution and performance

No experiment admitted yet. All measurements are centralized in [results](../../../results/). Current best: **not verified**. Missing scores are unknown, not zero. Literature resources are not newly executed results.

## Limitations

Requires calibrations and synchronized cameras

## Sources

- [https://pmc.ncbi.nlm.nih.gov/articles/PMC13131684/](https://pmc.ncbi.nlm.nih.gov/articles/PMC13131684/)

Source associations include historical alternatives; actual acquired files are identified in the executed protocol/manifest.

## Historical v0.4 admission and execution

Decision: **candidate_pending_validation** (2026-10-30). Synchronized camera and landmark/calibration release must be pinned with official holdout. No multiview visual adapter prepared; numerical mocap imputation A14 cannot count as this task.

[Source-linked admission evidence](../../../literature/admission-v04-behavior-population.json). This endpoint was not run in this release; absence is unknown, not zero or proof of poor data.

## Current admission and execution

Preview 0.11: candidate_pending_validation. Synchronized camera and landmark/calibration release must be pinned with official holdout. No multiview visual adapter prepared; numerical mocap imputation A14 cannot count as this task.

[Admission/source evidence](../../../literature/admission-v04-behavior-population.json).
