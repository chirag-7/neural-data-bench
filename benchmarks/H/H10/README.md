# H10 — EEG abnormality, events, cognition and state

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** Task subsets in NeuralBench / OmniEEG-Bench

**State:** not evaluated; candidate_pending_validation. Mapped resource only; license, acquisition, split, scorer and baseline gates are not yet all validated.

## Scientific use

Input: Clinical/task EEG plus metadata

Target/ground truth: Expert/experimental labels depending on task

Specialist candidates: EEGNet; EEGConformer; domain FM

General-model route: General signal model

## Execution and performance

No experiment admitted yet. All measurements are centralized in [results](../../../results/). Current best: **not verified**. Missing scores are unknown, not zero. Literature resources are not newly executed results.

## Limitations

Abnormality is not disease diagnosis; demographic/site confounds

## Sources

- [https://facebookresearch.github.io/neuroai/neuralbench/index.html](https://facebookresearch.github.io/neuroai/neuralbench/index.html)
- [https://arxiv.org/abs/2606.00815](https://arxiv.org/abs/2606.00815)

## v0.4 admission and execution

Decision: **candidate_pending_validation** (2026-10-30). Broad abnormality/events/cognition/state umbrella overlaps H05/H06 and mixes distinct clinical targets. Requires a specific task, label definition, subject/site split and data-use agreement before an executable benchmark can be admitted.

[Source-linked admission evidence](../../../literature/admission-v04-electrical.json). This endpoint was not run in this release; absence is unknown, not zero or proof of poor data.
