# A02 — Cross-species 2D pose transfer

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** AP-10K and DLC benchmark datasets

**State:** not evaluated; candidate_pending_validation. Mapped resource only; license, acquisition, split, scorer and baseline gates are not yet all validated.

## Scientific use

Input: Animal photographs and keypoints

Target/ground truth: Human keypoint annotations

Specialist candidates: ViTPose; SuperAnimal; DLC

General-model route: Generic vision backbone or VLM keypoints

## Execution and performance

No experiment admitted yet. All measurements are centralized in [results](../../../results/). Current best: **not verified**. Missing scores are unknown, not zero. Literature resources are not newly executed results.

## Limitations

Wild images differ from head-fixed laboratory footage

## Sources

- [https://arxiv.org/abs/2108.12617](https://arxiv.org/abs/2108.12617)
- [https://benchmark.deeplabcut.org/datasets.html](https://benchmark.deeplabcut.org/datasets.html)

## v0.4 admission and execution

Decision: **candidate_pending_validation** (2026-10-30). AP-10K offers official image/keypoint splits, but raw-image inference needs vision/multimodal submissions and matched OKS scorer. Numeric pose-to-label A09 does not cover this operation. Dataset not downloaded in this expansion.

[Source-linked admission evidence](../../../literature/admission-v04-behavior-population.json). This endpoint was not run in this release; absence is unknown, not zero or proof of poor data.
