# A08 — Animal identity tracking through occlusions

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** idtracker.ai 2026 benchmark

**State:** not evaluated; candidate_pending_validation. Mapped resource only; license, acquisition, split, scorer and baseline gates are not yet all validated.

## Scientific use

Input: Multi-animal laboratory videos

Target/ground truth: Human-validated trajectories

Specialist candidates: idtracker.ai; TRex

General-model route: Generic segmentation/tracking and re-identification

## Execution and performance

No experiment admitted yet. All measurements are centralized in [results](../../../results/). Current best: **not verified**. Missing scores are unknown, not zero. Literature resources are not newly executed results.

## Limitations

Mask tracking does not establish persistent identity

## Sources

- [https://doi.org/10.7554/eLife.107602.3](https://doi.org/10.7554/eLife.107602.3)

## v0.4 admission and execution

Decision: **candidate_pending_validation** (2026-10-30). Complete-video identity assignments require persistent IDs and track-matching scorer. No reference trajectories/video pair acquired. Random frame classification would not be a valid substitute.

[Source-linked admission evidence](../../../literature/admission-v04-behavior-population.json). This endpoint was not run in this release; absence is unknown, not zero or proof of poor data.

## v0.5 execution status

candidate_pending_validation. Complete-video identity assignments require persistent IDs and track-matching scorer. No reference trajectories/video pair acquired. Random frame classification would not be a valid substitute.

[Admission/source evidence](../../../literature/admission-v04-behavior-population.json).
