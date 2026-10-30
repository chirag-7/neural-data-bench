# H08 — Sleep staging and sleep onset

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** Sleep tasks in NeuralBench; 2026 foundation challenge

**State:** not evaluated; candidate_pending_validation. Mapped resource only; license, acquisition, split, scorer and baseline gates are not yet all validated.

## Scientific use

Input: Continuous overnight EEG/PSG

Target/ground truth: Human sleep-stage labels

Specialist candidates: Sleep-specific model; EEGNet where appropriate

General-model route: General sequence model

## Execution and performance

No experiment admitted yet. All measurements are centralized in [results](../../../results/). Current best: **not verified**. Missing scores are unknown, not zero. Literature resources are not newly executed results.

## Limitations

PSG multimodal inputs must match; adjacent epoch leakage

## Sources

- [https://facebookresearch.github.io/neuroai/neuralbench/index.html](https://facebookresearch.github.io/neuroai/neuralbench/index.html)
- [https://neural-interfaces26.github.io/](https://neural-interfaces26.github.io/)

## v0.4 admission and execution

Decision: **deferred** (2026-10-30). NeuralBench/challenge primary sites accessible. 2026 challenge final phase starts in November after this review date, so no final winner exists yet. Need a pinned accessible sleep dataset, subject/night-disjoint scorer, full-context policy and expert staging labels; no adjacent-epoch shortcut experiment admitted.

[Source-linked admission evidence](../../../literature/admission-v04-electrical.json). This endpoint was not run in this release; absence is unknown, not zero or proof of poor data.
