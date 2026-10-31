# D02 — Current-to-voltage prediction

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** Allen Cell Types Database

**State:** measured. Current status for this exact task-resource slice; current global best remains unverified.

## Scientific use

Input: Patch clamp voltage/current sweeps

Target/ground truth: Measured voltage and recorded stimulation

Mapped specialist candidates (not all evaluated): GLIF/biophysical fits; linear dynamical baseline

General-model route: General time-series model

## Execution and performance

**Executed slice:** One Allen cell: four training and two test negative-current sweeps; 500 Hz passive voltage interpolation.

[Frozen protocol and artifacts](../../../experiments/D02). [Measured scores and references](../../../results/D02.json). [Central data](../../../results/measurements.csv). Missing or failed outputs are retained.

## Limitations

Future current input may be known, future measured voltage is not

## Sources

- [https://brain-map.org/support/documentation/documentation-cell-types-database](https://brain-map.org/support/documentation/documentation-cell-types-database)
- [https://alleninstitute.github.io/AllenSDK/cell_types.html](https://alleninstitute.github.io/AllenSDK/cell_types.html)
- [https://brain-map.org/support/documentation/cell-types-database-api](https://brain-map.org/support/documentation/cell-types-database-api)

Source associations include historical alternatives; actual acquired files are identified in the executed protocol/manifest.

## Historical v0.4 admission and execution

Decision: **measured** (2026-10-30). Acquired and hashed one 61,980,832-byte official Allen NWB, specimen and sweep annotations; prepared four train/two held-out negative-amplitude sweeps from cell464212183. Explicitly conditional PRE-stimulus-rest-relative 500Hz passive deflection prediction only, no spiking or cross-cell claim. Adapter/protocol and train-only reference ready.

[Source-linked admission evidence](../../../literature/admission-v04-cell-workflow.json). [Actual protocol and artifacts](../../../experiments/D02). [Central task results](../../../results/D02.json).

## Current admission and execution

Preview 0.10: measured. Acquired and hashed one 61,980,832-byte official Allen NWB, specimen and sweep annotations; prepared four train/two held-out negative-amplitude sweeps from cell464212183. Explicitly conditional PRE-stimulus-rest-relative 500Hz passive deflection prediction only, no spiking or cross-cell claim. Adapter/protocol and train-only reference ready.

[Admission/source evidence](../../../literature/admission-v04-cell-workflow.json). [Actual protocol/worklog](../../../experiments/D02). [Task measurements](../../../results/D02.json).
