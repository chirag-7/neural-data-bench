# H01 — Motor imagery and noninvasive BCI

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** MOABB motor imagery datasets

**State:** not evaluated; candidate_pending_validation. Mapped resource only; license, acquisition, split, scorer and baseline gates are not yet all validated.

## Scientific use

Input: EEG epochs, montage and labels

Target/ground truth: Task labels

Specialist candidates: CSP+LDA; Riemannian methods; EEGNet

General-model route: Generic time-series model; coding agent

## Execution and performance

No experiment admitted yet. All measurements are centralized in [results](../../../results/). Current best: **not verified**. Missing scores are unknown, not zero. Literature resources are not newly executed results.

## Limitations

Random epoch splits inflate subject generalization

## Sources

- [https://moabb.neurotechx.com/](https://moabb.neurotechx.com/)

## v0.4 admission and execution

Decision: **measured** (2026-10-30). Real public PhysioNet EEGMMI EDF files acquired and validated; fixed subject-disjoint MI slice prepared. This admits one explicitly scoped slice, not the whole MOABB umbrella.

[Source-linked admission evidence](../../../literature/admission-v04-electrical.json). [Actual protocol and artifacts](../../../experiments/H01). [Central task results](../../../results/H01.json).

## v0.5 execution status

measured. Real public PhysioNet EEGMMI EDF files acquired and validated; fixed subject-disjoint MI slice prepared. This admits one explicitly scoped slice, not the whole MOABB umbrella.

[Admission/source evidence](../../../literature/admission-v04-electrical.json). [Actual protocol/worklog](../../../experiments/H01). [Task measurements](../../../results/H01.json).
