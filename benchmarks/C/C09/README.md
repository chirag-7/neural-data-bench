# C09 — One-photon microendoscopic demixing

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** CNMF-E published evaluation datasets

**State:** not evaluated; candidate_pending_validation. Mapped resource only; license, acquisition, split, scorer and baseline gates are not yet all validated.

## Scientific use

Input: Miniscope fluorescence movies with strong background

Target/ground truth: Simulated truth and expert/paired validation on selected examples

Specialist candidates: CNMF-E; PCA/ICA; supported one-photon pipelines

General-model route: General video source-separation model

## Execution and performance

No experiment admitted yet. All measurements are centralized in [results](../../../results/). Current best: **not verified**. Missing scores are unknown, not zero. Literature resources are not newly executed results.

## Limitations

Strong out-of-focus background differs from two-photon data; truth varies

## Sources

- [https://elifesciences.org/articles/28728](https://elifesciences.org/articles/28728)

## v0.4 admission and execution

Decision: **candidate_pending_validation** (2026-10-30). CNMF-E onephoton examples may support ROI and source extraction endpoints; require independent masks/timecourse labels, background model definition and frozen recording split. No real labeled movie acquired here. Specialized outputs cannot serve as unquestioned true signals.

[Source-linked admission evidence](../../../literature/admission-v04-behavior-population.json). This endpoint was not run in this release; absence is unknown, not zero or proof of poor data.
