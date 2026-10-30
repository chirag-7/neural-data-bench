# A12 — Behavioral features for neural prediction

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** BEAST released evaluation tasks

**State:** not evaluated; candidate_pending_validation. Mapped resource only; license, acquisition, split, scorer and baseline gates are not yet all validated.

## Scientific use

Input: Behavior video aligned with neural activity

Target/ground truth: Keypoints/actions and measured neural responses

Specialist candidates: BEAST; PS-VAE; task-specific pose features

General-model route: DINO/video features with a fixed neural readout

## Execution and performance

No experiment admitted yet. All measurements are centralized in [results](../../../results/). Current best: **not verified**. Missing scores are unknown, not zero. Literature resources are not newly executed results.

## Limitations

Method evaluation suite needs a frozen common wrapper

## Sources

- [https://arxiv.org/abs/2507.09513](https://arxiv.org/abs/2507.09513)

## v0.4 admission and execution

Decision: **candidate_pending_validation** (2026-10-30). Need raw or published fixed behavior features jointly aligned to neural recordings and recording-level heldout responses. No common numerical endpoint independently acquired; do not score predicted behavior labels as neural encoding.

[Source-linked admission evidence](../../../literature/admission-v04-behavior-population.json). This endpoint was not run in this release; absence is unknown, not zero or proof of poor data.

## v0.5 execution status

candidate_pending_validation. Need raw or published fixed behavior features jointly aligned to neural recordings and recording-level heldout responses. No common numerical endpoint independently acquired; do not score predicted behavior labels as neural encoding.

[Admission/source evidence](../../../literature/admission-v04-behavior-population.json).
