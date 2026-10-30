# G01 — Robust cross-day motor decoding

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** FALCON motor tracks

**State:** not evaluated; candidate_pending_validation. Mapped resource only; license, acquisition, split, scorer and baseline gates are not yet all validated.

## Scientific use

Input: Intracortical neural activity and kinematics

Target/ground truth: Recorded kinematics on held-out days

Specialist candidates: FALCON baseline decoders; NDT3 if compatible

General-model route: General sequence model or analysis agent

## Execution and performance

No experiment admitted yet. All measurements are centralized in [results](../../../results/). Current best: **not verified**. Missing scores are unknown, not zero. Literature resources are not newly executed results.

## Limitations

Offline acausal prediction cannot count as online BCI control

## Sources

- [https://snel-repo.github.io/falcon/](https://snel-repo.github.io/falcon/)

## v0.4 admission and execution

Decision: **candidate_pending_validation** (2026-10-30). FALCON motor tracks provide official crossday interfaces and labels. Need exacttrack acquisition terms, trial/sessionnormalization, allowed adaptation and online/offline constraints. No data request attempted here. Same-session E01 cannot establish crossday BCIperformance.

[Source-linked admission evidence](../../../literature/admission-v04-behavior-population.json). This endpoint was not run in this release; absence is unknown, not zero or proof of poor data.
