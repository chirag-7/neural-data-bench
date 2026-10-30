# F01 — Static visual encoding

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** Sensorium 2022

**State:** not evaluated; candidate_pending_validation. Mapped resource only; license, acquisition, split, scorer and baseline gates are not yet all validated.

## Scientific use

Input: Images with mouse calcium responses

Target/ground truth: Measured neural responses

Specialist candidates: Sensorium baseline CNN/readout

General-model route: Frozen generic image encoder with matched readout

## Execution and performance

No experiment admitted yet. All measurements are centralized in [results](../../../results/). Current best: **not verified**. Missing scores are unknown, not zero. Literature resources are not newly executed results.

## Limitations

ImageNet features plus neural head are adapted models

## Sources

- [https://sensorium-competition.net/](https://sensorium-competition.net/)

## v0.4 admission and execution

Decision: **deferred** (2026-10-30). Sensorium2022 stimulus-response encoding is feasible with official split and responses, but current CPU numerical-code interface lacks reproducible visualstimulus decoding/encoder and a matched published model. Need exact response availability and heldoutanimal protocol before execution.

[Source-linked admission evidence](../../../literature/admission-v04-behavior-population.json). This endpoint was not run in this release; absence is unknown, not zero or proof of poor data.
