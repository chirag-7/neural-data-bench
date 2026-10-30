# H03 — SSVEP stimulus selection

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** MOABB SSVEP datasets

**State:** not evaluated; candidate_pending_validation. Mapped resource only; license, acquisition, split, scorer and baseline gates are not yet all validated.

## Scientific use

Input: EEG with frequency-tagged stimuli

Target/ground truth: Stimulus-frequency labels

Specialist candidates: CCA/filter-bank CCA; TRCA where supported

General-model route: General multichannel time-series encoder

## Execution and performance

No experiment admitted yet. All measurements are centralized in [results](../../../results/). Current best: **not verified**. Missing scores are unknown, not zero. Literature resources are not newly executed results.

## Limitations

Stimulus timing and frequency metadata can be shortcuts

## Sources

- [https://moabb.neurotechx.com/](https://moabb.neurotechx.com/)

## v0.4 admission and execution

Decision: **deferred** (2026-10-30). MOABB Nakanishi2015 primary documentation located. Need pinned original files/license and frequency/timing metadata, fixed subject split, verified CCA baseline. Generic MOABB umbrella is not one executable dataset; not rejected as infeasible.

[Source-linked admission evidence](../../../literature/admission-v04-electrical.json). This endpoint was not run in this release; absence is unknown, not zero or proof of poor data.
