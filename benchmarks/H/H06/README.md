# H06 — EEG foundation model transfer roadmap

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** OmniEEG-Bench

**State:** not evaluated; candidate_pending_validation. Mapped resource only; license, acquisition, split, scorer and baseline gates are not yet all validated.

## Scientific use

Input: EEG across six task families

Target/ground truth: Dataset-specific signal/state/clinical/task labels

Specialist candidates: Published EEG FM baselines; supervised EEG models

General-model route: Generic sequence model or coding agent

## Execution and performance

No experiment admitted yet. All measurements are centralized in [results](../../../results/). Current best: **not verified**. Missing scores are unknown, not zero. Literature resources are not newly executed results.

## Limitations

Overlaps other EEG suites; do not count duplicates as independent evidence

## Sources

- [https://arxiv.org/abs/2606.00815](https://arxiv.org/abs/2606.00815)

## v0.4 admission and execution

Decision: **candidate_pending_validation** (2026-10-30). Original OmniEEG-Bench paper accessible; 54-dataset suite. Must resolve individual task-card preprocessing/splits/licenses and duplicates before execution. Domain EEG foundation-model tables cannot be imported as scores of the evaluated general code generators.

[Source-linked admission evidence](../../../literature/admission-v04-electrical.json). This endpoint was not run in this release; absence is unknown, not zero or proof of poor data.
