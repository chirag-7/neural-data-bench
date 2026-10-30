# H05 — Broad EEG model comparison

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** NeuralBench-EEG Core / Full

**State:** not evaluated; candidate_pending_validation. Mapped resource only; license, acquisition, split, scorer and baseline gates are not yet all validated.

## Scientific use

Input: EEG datasets across many paradigms

Target/ground truth: Task-specific recorded labels

Specialist candidates: Published task-specific and EEG-foundation models

General-model route: General time-series features with the same head

## Execution and performance

No experiment admitted yet. All measurements are centralized in [results](../../../results/). Current best: **not verified**. Missing scores are unknown, not zero. Literature resources are not newly executed results.

## Limitations

Core is manageable subset; Full has large storage requirements

## Sources

- [https://facebookresearch.github.io/neuroai/neuralbench/index.html](https://facebookresearch.github.io/neuroai/neuralbench/index.html)

## v0.4 admission and execution

Decision: **candidate_pending_validation** (2026-10-30). Original NeuralBench documentation accessible. Full/Core suites require selecting task cards, resolving per-dataset licenses and canonical overlap. Avoid counting this suite and its contained EEGMMI-like datasets as independent experiments.

[Source-linked admission evidence](../../../literature/admission-v04-electrical.json). This endpoint was not run in this release; absence is unknown, not zero or proof of poor data.
