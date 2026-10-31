# A03 — Low-label lab pose adaptation

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** SuperAnimal leave-one-dataset-out releases

**State:** candidate_pending_validation. Current status for this exact task-resource slice; current global best remains unverified.

## Scientific use

Input: Animal videos and keypoints

Target/ground truth: Held-out human keypoints

Mapped specialist candidates (not all evaluated): SuperAnimal; task-trained DLC

General-model route: Generic vision features with same labels

## Execution and performance

No experiment admitted yet. All measurements are centralized in [results](../../../results/). Current best: **not verified**. Missing scores are unknown, not zero. Literature resources are not newly executed results.

## Limitations

SuperAnimal is animal-domain pretraining, not a general-purpose model

## Sources

- [https://www.nature.com/articles/s41467-024-48792-2](https://www.nature.com/articles/s41467-024-48792-2)

Source associations include historical alternatives; actual acquired files are identified in the executed protocol/manifest.

## Historical v0.4 admission and execution

Decision: **candidate_pending_validation** (2026-10-30). Needs exact leave-one-dataset-out weights and proof held-out training set was excluded from domain pretraining. Cannot treat animal-specialist SuperAnimal as a general-purpose baseline. Weights/splits not yet validated.

[Source-linked admission evidence](../../../literature/admission-v04-behavior-population.json). This endpoint was not run in this release; absence is unknown, not zero or proof of poor data.

## Current admission and execution

Preview 0.11: candidate_pending_validation. Needs exact leave-one-dataset-out weights and proof held-out training set was excluded from domain pretraining. Cannot treat animal-specialist SuperAnimal as a general-purpose baseline. Weights/splits not yet validated.

[Admission/source evidence](../../../literature/admission-v04-behavior-population.json).
