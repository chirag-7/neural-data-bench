# F04 — Retinal or other sensory encoding

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** CRCNS retinal datasets; selected sensory collections

**State:** not evaluated; candidate_pending_validation. Mapped resource only; license, acquisition, split, scorer and baseline gates are not yet all validated.

## Scientific use

Input: Stimulus movies and retinal spike trains

Target/ground truth: Measured spike trains with aligned stimuli

Specialist candidates: LN/GLM; specialized retina CNN

General-model route: General video/time-series representations

## Execution and performance

No experiment admitted yet. All measurements are centralized in [results](../../../results/). Current best: **not verified**. Missing scores are unknown, not zero. Literature resources are not newly executed results.

## Limitations

Verify stimulus licensing and download terms per dataset

## Sources

- [https://crcns.org/data-sets](https://crcns.org/data-sets)

## v0.4 admission and execution

Decision: **measured** (2026-10-30). Prepared custom real retinal static-image encoding slice from Goldin2022 mouse session via OpenRetina:3160 training images,30 unique held-out images with30 measured repeats and all41 neurons; exact image hashes disjoint, targets verified nonnegative integer counts. This is not an official CRCNS/full-image CNN/temporal-flicker benchmark.

[Source-linked admission evidence](../../../literature/admission-v04-cell-workflow.json). [Actual protocol and artifacts](../../../experiments/F04). [Central task results](../../../results/F04.json).
