# H09 — Seizure detection with useful event scoring

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** SzCORE / CHB-MIT and supported corpora

**State:** deferred. Current status for this exact task-resource slice; current global best remains unverified.

## Scientific use

Input: Long EEG recordings and seizure annotations

Target/ground truth: Expert event intervals

Mapped specialist candidates (not all evaluated): Published seizure detector; simple spectral baseline

General-model route: General signal encoder or analysis agent

## Execution and performance

No experiment admitted yet. All measurements are centralized in [results](../../../results/). Current best: **not verified**. Missing scores are unknown, not zero. Literature resources are not newly executed results.

## Limitations

Epoch accuracy can hide unacceptable false-alarm rates

## Sources

- [https://epilepsybenchmarks.com/framework/](https://epilepsybenchmarks.com/framework/)

Source associations include historical alternatives; actual acquired files are identified in the executed protocol/manifest.

## Historical v0.4 admission and execution

Decision: **deferred** (2026-10-30). SzCORE primary framework explicitly distinguishes sample/event scoring and participant independence. CHB-MIT/Siena require long continuous recordings to estimate false alarms/hour; no cherry-picked balanced seizure clips admitted as replacement. Full event pipeline and sufficient recording duration not yet prepared.

[Source-linked admission evidence](../../../literature/admission-v04-electrical.json). This endpoint was not run in this release; absence is unknown, not zero or proof of poor data.

## Current admission and execution

Preview 0.6: deferred. SzCORE primary framework explicitly distinguishes sample/event scoring and participant independence. CHB-MIT/Siena require long continuous recordings to estimate false alarms/hour; no cherry-picked balanced seizure clips admitted as replacement. Full event pipeline and sufficient recording duration not yet prepared.

[Admission/source evidence](../../../literature/admission-v04-electrical.json).
