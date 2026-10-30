# D02 — Current-to-voltage prediction

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** Allen Cell Types Database

**State:** not evaluated; candidate_pending_validation. Mapped resource only; license, acquisition, split, scorer and baseline gates are not yet all validated.

## Scientific use

Input: Patch clamp voltage/current sweeps

Target/ground truth: Measured voltage and recorded stimulation

Specialist candidates: GLIF/biophysical fits; linear dynamical baseline

General-model route: General time-series model

## Execution and performance

No experiment admitted yet. All measurements are centralized in [results](../../../results/). Current best: **not verified**. Missing scores are unknown, not zero. Literature resources are not newly executed results.

## Limitations

Future current input may be known, future measured voltage is not

## Sources

- [https://brain-map.org/support/documentation/documentation-cell-types-database](https://brain-map.org/support/documentation/documentation-cell-types-database)
- [https://alleninstitute.github.io/AllenSDK/cell_types.html](https://alleninstitute.github.io/AllenSDK/cell_types.html)

## v0.4 admission and execution

Decision: **measured** (2026-10-30). Acquired and hashed one 61,980,832-byte official Allen NWB, specimen and sweep annotations; prepared four train/two held-out negative-amplitude sweeps from cell464212183. Explicitly conditional PRE-stimulus-rest-relative 500Hz passive deflection prediction only, no spiking or cross-cell claim. Adapter/protocol and train-only reference ready.

[Source-linked admission evidence](../../../literature/admission-v04-cell-workflow.json). [Actual protocol and artifacts](../../../experiments/D02). [Central task results](../../../results/D02.json).

## v0.5 execution status

measured. Acquired and hashed one 61,980,832-byte official Allen NWB, specimen and sweep annotations; prepared four train/two held-out negative-amplitude sweeps from cell464212183. Explicitly conditional PRE-stimulus-rest-relative 500Hz passive deflection prediction only, no spiking or cross-cell claim. Adapter/protocol and train-only reference ready.

[Admission/source evidence](../../../literature/admission-v04-cell-workflow.json). [Actual protocol/worklog](../../../experiments/D02). [Task measurements](../../../results/D02.json).
