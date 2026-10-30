# C08 — Fiber photometry cleanup and event analysis

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** GuPPy sample data with artifacts

**State:** not evaluated; candidate_pending_validation. Mapped resource only; license, acquisition, split, scorer and baseline gates are not yet all validated.

## Scientific use

Input: Signal/reference fluorescence; behavioral events

Target/ground truth: Known analysis outputs; injected artifacts for stronger truth

Specialist candidates: GuPPy pipeline; fixed regression/detrending

General-model route: General sequence model or analysis agent

## Execution and performance

No experiment admitted yet. All measurements are centralized in [results](../../../results/). Current best: **not verified**. Missing scores are unknown, not zero. Literature resources are not newly executed results.

## Limitations

Reference-channel correction can remove biology; samples are not a biological benchmark

## Sources

- [https://github.com/LernerLab/GuPPy](https://github.com/LernerLab/GuPPy)

## v0.4 admission and execution

Decision: **candidate_pending_validation** (2026-10-30). GuPPy example traces demonstrate photometry workflow, but a true artifact-free neural trace or blinded artifact/event annotations are needed for accuracy measurement. Synthetic artifact injection into observed signals is possible if explicitly semi-synthetic. No reference annotations acquired here.

[Source-linked admission evidence](../../../literature/admission-v04-behavior-population.json). This endpoint was not run in this release; absence is unknown, not zero or proof of poor data.
