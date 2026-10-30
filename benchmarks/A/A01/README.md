# A01 — 2D lab keypoints and pupil/paw tracking

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** Lightning Pose datasets: IBL-pupil, IBL-paw, mirror-mouse/fish, CRIM13

**State:** not evaluated; candidate_pending_validation. Mapped resource only; license, acquisition, split, scorer and baseline gates are not yet all validated.

## Scientific use

Input: RGB/IR videos; labeled keypoints

Target/ground truth: Human keypoint annotations

Specialist candidates: Lightning Pose; DLC; SLEAP; EKS

General-model route: Frozen vision features plus head; VLM coordinate outputs

## Execution and performance

No experiment admitted yet. All measurements are centralized in [results](../../../results/). Current best: **not verified**. Missing scores are unknown, not zero. Literature resources are not newly executed results.

## Limitations

Frame-adjacent train/test leakage; pupil occlusion

## Sources

- [https://pmc.ncbi.nlm.nih.gov/articles/PMC12087009/](https://pmc.ncbi.nlm.nih.gov/articles/PMC12087009/)
