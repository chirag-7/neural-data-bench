# A04 — Single-animal 3D pose

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** Rat7M / DANNCE

**State:** not evaluated; candidate_pending_validation. Mapped resource only; license, acquisition, split, scorer and baseline gates are not yet all validated.

## Scientific use

Input: Calibrated multiview rat videos

Target/ground truth: Motion-capture landmarks; incomplete frames

Specialist candidates: DANNCE; published 3D pose baselines

General-model route: Generic visual features plus triangulation or pose head

## Execution and performance

No experiment admitted yet. All measurements are centralized in [results](../../../results/). Current best: **not verified**. Missing scores are unknown, not zero. Literature resources are not newly executed results.

## Limitations

Dense frames are correlated; mocap missingness

## Sources

- [https://figshare.com/collections/Rat_7M/5295370/3](https://figshare.com/collections/Rat_7M/5295370/3)
- [https://www.nature.com/articles/s41592-025-02893-y](https://www.nature.com/articles/s41592-025-02893-y)

## v0.4 admission and execution

Decision: **candidate_pending_validation** (2026-10-30). Real Rat7M mocap labels acquired through DISK for A14. This does not admit 3D pose-from-video: its synchronized six-camera inputs and calibrations have not been downloaded or evaluated. Share dataset group with A14 for independence accounting.

[Source-linked admission evidence](../../../literature/admission-v04-behavior-population.json). This endpoint was not run in this release; absence is unknown, not zero or proof of poor data.
