# H09 — Seizure detection with useful event scoring

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** SzCORE / CHB-MIT and supported corpora

**State:** not evaluated; candidate_pending_validation. Mapped resource only; license, acquisition, split, scorer and baseline gates are not yet all validated.

## Scientific use

Input: Long EEG recordings and seizure annotations

Target/ground truth: Expert event intervals

Specialist candidates: Published seizure detector; simple spectral baseline

General-model route: General signal encoder or analysis agent

## Execution and performance

No experiment admitted yet. All measurements are centralized in [results](../../../results/). Current best: **not verified**. Missing scores are unknown, not zero. Literature resources are not newly executed results.

## Limitations

Epoch accuracy can hide unacceptable false-alarm rates

## Sources

- [https://epilepsybenchmarks.com/framework/](https://epilepsybenchmarks.com/framework/)

## v0.4 admission and execution

Decision: **deferred** (2026-10-30). SzCORE primary framework explicitly distinguishes sample/event scoring and participant independence. CHB-MIT/Siena require long continuous recordings to estimate false alarms/hour; no cherry-picked balanced seizure clips admitted as replacement. Full event pipeline and sufficient recording duration not yet prepared.

[Source-linked admission evidence](../../../literature/admission-v04-electrical.json). This endpoint was not run in this release; absence is unknown, not zero or proof of poor data.
