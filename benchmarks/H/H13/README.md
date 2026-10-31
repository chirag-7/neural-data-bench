# H13 — Neuromotor pose and typing from muscle signals

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** emg2pose; related emg2qwerty resources

**State:** deferred. Current status for this exact task-resource slice; current global best remains unverified.

## Scientific use

Input: Wrist surface EMG and hand pose

Target/ground truth: Motion capture or keypress labels

Mapped specialist candidates (not all evaluated): Released neuromotor baselines

General-model route: General time-series model

## Execution and performance

No experiment admitted yet. All measurements are centralized in [results](../../../results/). Current best: **not verified**. Missing scores are unknown, not zero. Literature resources are not newly executed results.

## Limitations

Peripheral interface extension; EMG is not a brain recording

## Sources

- [https://github.com/facebookresearch/emg2pose](https://github.com/facebookresearch/emg2pose)

Source associations include historical alternatives; actual acquired files are identified in the executed protocol/manifest.

## Historical v0.4 admission and execution

Decision: **deferred** (2026-10-30). Original emg2pose repo reports full data431GiB and a ~600MiB sanity-check subset. Full held-out-user benchmark not downloaded; sanity subset cannot substitute for population evaluation without verifying participants and split metadata. EMG is explicitly peripheral.

[Source-linked admission evidence](../../../literature/admission-v04-electrical.json). This endpoint was not run in this release; absence is unknown, not zero or proof of poor data.

## Current admission and execution

Preview 0.9: deferred. Original emg2pose repo reports full data431GiB and a ~600MiB sanity-check subset. Full held-out-user benchmark not downloaded; sanity subset cannot substitute for population evaluation without verifying participants and split metadata. EMG is explicitly peripheral.

[Admission/source evidence](../../../literature/admission-v04-electrical.json).
