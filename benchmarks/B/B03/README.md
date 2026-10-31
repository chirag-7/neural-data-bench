# B03 — Probe motion estimation

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** SpikeInterface motion benchmarks / DREDge

**State:** candidate_pending_validation. Current status for this exact task-resource slice; current global best remains unverified.

## Scientific use

Input: Spike localizations or LFP with probe coordinates

Target/ground truth: Known imposed/simulated displacement

Mapped specialist candidates (not all evaluated): DREDge; Kilosort motion correction

General-model route: Generic registration or signal model

## Execution and performance

No experiment admitted yet. All measurements are centralized in [results](../../../results/). Current best: **not verified**. Missing scores are unknown, not zero. Literature resources are not newly executed results.

## Limitations

Real motion estimates are often proxy truth

## Sources

- [https://spikeinterface.readthedocs.io/en/stable/modules/benchmark.html](https://spikeinterface.readthedocs.io/en/stable/modules/benchmark.html)
- [https://github.com/evarol/dredge](https://github.com/evarol/dredge)

Source associations include historical alternatives; actual acquired files are identified in the executed protocol/manifest.

## Historical v0.4 admission and execution

Decision: **candidate_pending_validation** (2026-10-30). Synthetic drift with known displacement supports motion-estimation error; real DREDge drift estimates themselves are not groundtruth. Need fixed simulator/probe mapping and matched motion pipeline; no acquisition/execution attempted here.

[Source-linked admission evidence](../../../literature/admission-v04-behavior-population.json). This endpoint was not run in this release; absence is unknown, not zero or proof of poor data.

## Current admission and execution

Preview 0.9: candidate_pending_validation. Synthetic drift with known displacement supports motion-estimation error; real DREDge drift estimates themselves are not groundtruth. Need fixed simulator/probe mapping and matched motion pipeline; no acquisition/execution attempted here.

[Admission/source evidence](../../../literature/admission-v04-behavior-population.json).
