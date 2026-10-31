# B02 — Drift-aware spike sorting

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** SpikeInterface drifting generators / MEArec integration

**State:** candidate_pending_validation. Current status for this exact task-resource slice; current global best remains unverified.

## Scientific use

Input: Simulated/hybrid raw multichannel voltage

Target/ground truth: Known spike times, units and simulated motion

Mapped specialist candidates (not all evaluated): Kilosort4; DARTsort

General-model route: General multichannel time-series model

## Execution and performance

No experiment admitted yet. All measurements are centralized in [results](../../../results/). Current best: **not verified**. Missing scores are unknown, not zero. Literature resources are not newly executed results.

## Limitations

Simulation-to-real gap; do not reuse templates in test

## Sources

- [https://spikeinterface.readthedocs.io/en/stable/modules/benchmark.html](https://spikeinterface.readthedocs.io/en/stable/modules/benchmark.html)
- [https://github.com/cwindolf/dartsort](https://github.com/cwindolf/dartsort)

Source associations include historical alternatives; actual acquired files are identified in the executed protocol/manifest.

## Historical v0.4 admission and execution

Decision: **candidate_pending_validation** (2026-10-30). SpikeInterface/MEArec generators can supply exact drift and unit truth without restricted real data. Needs frozen simulation seed, geometry, waveform/noise/drift regime and event-matching scorer. This would be explicitly synthetic, not real in-vivo drift validation.

[Source-linked admission evidence](../../../literature/admission-v04-behavior-population.json). This endpoint was not run in this release; absence is unknown, not zero or proof of poor data.

## Current admission and execution

Preview 0.8: candidate_pending_validation. SpikeInterface/MEArec generators can supply exact drift and unit truth without restricted real data. Needs frozen simulation seed, geometry, waveform/noise/drift regime and event-matching scorer. This would be explicitly synthetic, not real in-vivo drift validation.

[Admission/source evidence](../../../literature/admission-v04-behavior-population.json).
