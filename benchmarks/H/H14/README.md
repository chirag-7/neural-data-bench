# H14 — LFP oscillation and burst quantification

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** Bycycle examples plus selected public LFP and synthetic controls

**State:** not evaluated; candidate_pending_validation. Mapped resource only; license, acquisition, split, scorer and baseline gates are not yet all validated.

## Scientific use

Input: LFP/field time series with labeled or injected events

Target/ground truth: Injected known bursts; expert/proxy annotations for real events

Specialist candidates: Bycycle; spectral threshold/bandpass baseline

General-model route: General time-series model or analysis agent

## Execution and performance

No experiment admitted yet. All measurements are centralized in [results](../../../results/). Current best: **not verified**. Missing scores are unknown, not zero. Literature resources are not newly executed results.

## Limitations

Oscillation/burst definitions are method dependent; real ground truth is limited

## Sources

- [https://github.com/bycycle-tools/bycycle](https://github.com/bycycle-tools/bycycle)
- [https://about.dandiarchive.org/](https://about.dandiarchive.org/)

## v0.4 admission and execution

Decision: **candidate_pending_validation** (2026-10-30). Original bycycle code/documentation accessible. Tool features computed from real LFP are not independent gold labels; need expert burst annotations or separately labeled synthetic calibration. Do not grade generic code against bycycle output and label it physiological truth.

[Source-linked admission evidence](../../../literature/admission-v04-electrical.json). This endpoint was not run in this release; absence is unknown, not zero or proof of poor data.
