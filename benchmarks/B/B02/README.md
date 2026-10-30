# B02 — Drift-aware spike sorting

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** SpikeInterface drifting generators / MEArec integration

**State:** not evaluated; candidate_pending_validation. Mapped resource only; license, acquisition, split, scorer and baseline gates are not yet all validated.

## Scientific use

Input: Simulated/hybrid raw multichannel voltage

Target/ground truth: Known spike times, units and simulated motion

Specialist candidates: Kilosort4; DARTsort

General-model route: General multichannel time-series model

## Execution and performance

No experiment admitted yet. All measurements are centralized in [results](../../../results/). Current best: **not verified**. Missing scores are unknown, not zero. Literature resources are not newly executed results.

## Limitations

Simulation-to-real gap; do not reuse templates in test

## Sources

- [https://spikeinterface.readthedocs.io/en/stable/modules/benchmark.html](https://spikeinterface.readthedocs.io/en/stable/modules/benchmark.html)
- [https://github.com/cwindolf/dartsort](https://github.com/cwindolf/dartsort)
