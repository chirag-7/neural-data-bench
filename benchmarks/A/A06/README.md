# A06 — 3D pose and shape from one image

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** Animal3D

**State:** candidate_pending_validation. Current status for this exact task-resource slice; current global best remains unverified.

## Scientific use

Input: Animal images with fitted shape labels

Target/ground truth: Annotated 2D/3D model-derived shape/pose

Mapped specialist candidates (not all evaluated): SMAL-based and published Animal3D methods

General-model route: Generic 3D reconstruction; frozen vision model

## Execution and performance

No experiment admitted yet. All measurements are centralized in [results](../../../results/). Current best: **not verified**. Missing scores are unknown, not zero. Literature resources are not newly executed results.

## Limitations

Fitted shape labels are not direct physical motion capture

## Sources

- [https://arxiv.org/abs/2308.11737](https://arxiv.org/abs/2308.11737)

Source associations include historical alternatives; actual acquired files are identified in the executed protocol/manifest.

## Historical v0.4 admission and execution

Decision: **candidate_pending_validation** (2026-10-30). Fitted 3D animal shape labels are a valid separate proxy-label endpoint, but need model parameter conventions and source image acquisition; do not equate fitted SMAL annotations to physical groundtruth. Not acquired.

[Source-linked admission evidence](../../../literature/admission-v04-behavior-population.json). This endpoint was not run in this release; absence is unknown, not zero or proof of poor data.

## Current admission and execution

Preview 0.9: candidate_pending_validation. Fitted 3D animal shape labels are a valid separate proxy-label endpoint, but need model parameter conventions and source image acquisition; do not equate fitted SMAL annotations to physical groundtruth. Not acquired.

[Admission/source evidence](../../../literature/admission-v04-behavior-population.json).
