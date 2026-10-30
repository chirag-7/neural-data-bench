# I07 — fNIRS motor/hemodynamic decoding

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** FRESH Motor dataset

**State:** not evaluated; candidate_pending_validation. Mapped resource only; license, acquisition, split, scorer and baseline gates are not yet all validated.

## Scientific use

Input: Optical hemodynamic time series and task events

Target/ground truth: Experimental event labels

Specialist candidates: GLM; linear classifier; fNIRS pipeline

General-model route: General time-series model

## Execution and performance

No experiment admitted yet. All measurements are centralized in [results](../../../results/). Current best: **not verified**. Missing scores are unknown, not zero. Literature resources are not newly executed results.

## Limitations

Needs benchmark wrapper; hemodynamic lag and motion confounding

## Sources

- [https://www.nemar.org/dataset/on005963](https://www.nemar.org/dataset/on005963)

## v0.4 admission and execution

Decision: **measured** (2026-10-30). Original FRESH organizer description resolves left/right2s finger tapping. CC0 versioned SNIRF data acquired/prepared with subject-disjoint2s condition decoding and optical-density conversion; explicit session/condition confounding, no Hb or cortical-activation gold-standard claim.

[Source-linked admission evidence](../../../literature/admission-v04-electrical.json). [Actual protocol and artifacts](../../../experiments/I07). [Central task results](../../../results/I07.json).

## v0.5 execution status

measured. Original FRESH organizer description resolves left/right2s finger tapping. CC0 versioned SNIRF data acquired/prepared with subject-disjoint2s condition decoding and optical-density conversion; explicit session/condition confounding, no Hb or cortical-activation gold-standard claim.

[Admission/source evidence](../../../literature/admission-v04-electrical.json). [Actual protocol/worklog](../../../experiments/I07). [Task measurements](../../../results/I07.json).
