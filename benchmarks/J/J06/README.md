# J06 — Whole-brain neuron detection, identity and tracking

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** WormID-Benchmark / WormND

**State:** not evaluated; candidate_pending_validation. Mapped resource only; license, acquisition, split, scorer and baseline gates are not yet all validated.

## Scientific use

Input: 3D worm microscopy and calcium videos

Target/ground truth: Neuron positions, identities and tracks

Specialist candidates: Worm-specific detectors/identity models

General-model route: Generic 3D segmentation and assignment

## Execution and performance

No experiment admitted yet. All measurements are centralized in [results](../../../results/). Current best: **not verified**. Missing scores are unknown, not zero. Literature resources are not newly executed results.

## Limitations

Dense whole-brain labeling and worm posture variation

## Sources

- [https://github.com/focolab/WormND](https://github.com/focolab/WormND)

## v0.4 admission and execution

Decision: **candidate_pending_validation** (2026-10-30). WormND provides detection/identity tracks, but crossworm split, template annotations and exact organism normalization remain unvalidated. No3D image adapter acquired. Candidate remains eligible for later execution.

[Source-linked admission evidence](../../../literature/admission-v04-behavior-population.json). This endpoint was not run in this release; absence is unknown, not zero or proof of poor data.

## v0.5 execution status

candidate_pending_validation. WormND provides detection/identity tracks, but crossworm split, template annotations and exact organism normalization remain unvalidated. No3D image adapter acquired. Candidate remains eligible for later execution.

[Admission/source evidence](../../../literature/admission-v04-behavior-population.json).
