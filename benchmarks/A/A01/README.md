# A01 — 2D lab keypoints and pupil/paw tracking

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** Lightning Pose datasets: IBL-pupil, IBL-paw, mirror-mouse/fish, CRIM13

**State:** candidate_pending_validation. Current status for this exact task-resource slice; current global best remains unverified.

## Scientific use

Input: RGB/IR videos; labeled keypoints

Target/ground truth: Human keypoint annotations

Mapped specialist candidates (not all evaluated): Lightning Pose; DLC; SLEAP; EKS

General-model route: Frozen vision features plus head; VLM coordinate outputs

## Execution and performance

No experiment admitted yet. All measurements are centralized in [results](../../../results/). Current best: **not verified**. Missing scores are unknown, not zero. Literature resources are not newly executed results.

## Limitations

Frame-adjacent train/test leakage; pupil occlusion

## Sources

- [https://pmc.ncbi.nlm.nih.gov/articles/PMC12087009/](https://pmc.ncbi.nlm.nih.gov/articles/PMC12087009/)

Source associations include historical alternatives; actual acquired files are identified in the executed protocol/manifest.

## Historical v0.4 admission and execution

Decision: **candidate_pending_validation** (2026-10-30). Human-labeled pose images are a valid endpoint. Need pin image/label archive, verify published session split and matched coordinate scorer; no image adapter or vision submission interface acquired in this bounded expansion. Not rejected as bad data.

[Source-linked admission evidence](../../../literature/admission-v04-behavior-population.json). This endpoint was not run in this release; absence is unknown, not zero or proof of poor data.

## Current admission and execution

Preview 0.9: candidate_pending_validation. Human-labeled pose images are a valid endpoint. Need pin image/label archive, verify published session split and matched coordinate scorer; no image adapter or vision submission interface acquired in this bounded expansion. Not rejected as bad data.

[Admission/source evidence](../../../literature/admission-v04-behavior-population.json).
