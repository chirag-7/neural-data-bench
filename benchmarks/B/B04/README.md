# B04 — Collision recovery and sorting robustness

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** SpikeInterface collision/hybrid evaluation

**State:** candidate_pending_validation. Current status for this exact task-resource slice; current global best remains unverified.

## Scientific use

Input: Hybrid/simulated overlapping spikes

Target/ground truth: Injected events and templates

Mapped specialist candidates (not all evaluated): Template matching sorters; DARTsort

General-model route: General denoising/source-separation model

## Execution and performance

No experiment admitted yet. All measurements are centralized in [results](../../../results/). Current best: **not verified**. Missing scores are unknown, not zero. Literature resources are not newly executed results.

## Limitations

Injected waveforms may make evaluation easier than real data

## Sources

- [https://spikeinterface.readthedocs.io/en/stable/modules/comparison.html](https://spikeinterface.readthedocs.io/en/stable/modules/comparison.html)
- [https://spikeinterface.readthedocs.io/en/stable/modules/benchmark.html](https://spikeinterface.readthedocs.io/en/stable/modules/benchmark.html)

Source associations include historical alternatives; actual acquired files are identified in the executed protocol/manifest.

## Historical v0.4 admission and execution

Decision: **candidate_pending_validation** (2026-10-30). Hybrid insertion can provide known collision times, but must freeze inserted templates and distinguish synthetic labels from unknown endogenous spikes. Requires event-matching tolerance and collision definitions. Adapter not prepared.

[Source-linked admission evidence](../../../literature/admission-v04-behavior-population.json). This endpoint was not run in this release; absence is unknown, not zero or proof of poor data.

## Current admission and execution

Preview 0.6: candidate_pending_validation. Hybrid insertion can provide known collision times, but must freeze inserted templates and distinguish synthetic labels from unknown endogenous spikes. Requires event-matching tolerance and collision definitions. Adapter not prepared.

[Admission/source evidence](../../../literature/admission-v04-behavior-population.json).
