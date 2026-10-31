# N05 — NWB data loading, units and reproducibility

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** DANDI selected dandisets / IBL data

**State:** measured. Current status for this exact task-resource slice; current global best remains unverified.

## Scientific use

Input: NWB neurophysiology and metadata

Target/ground truth: Metadata invariants; known deterministic reference outputs

Mapped specialist candidates (not all evaluated): NWB/ONE loading scripts; expert QC

General-model route: General coding agent

## Execution and performance

**Executed slice:** One real legacy Allen NWB file, shared with D02: extract 61 deterministic fields covering six sweeps.

[Frozen protocol and artifacts](../../../experiments/N05). [Measured scores and references](../../../results/N05.json). [Central data](../../../results/measurements.csv). Missing or failed outputs are retained.

## Limitations

Archive is not benchmark; need curated cases and hidden answers

## Sources

- [https://about.dandiarchive.org/](https://about.dandiarchive.org/)
- [https://www.internationalbrainlab.com/data](https://www.internationalbrainlab.com/data)
- [https://brain-map.org/support/documentation/cell-types-database-api](https://brain-map.org/support/documentation/cell-types-database-api)
- [https://alleninstitute.github.io/AllenSDK/cell_types.html](https://alleninstitute.github.io/AllenSDK/cell_types.html)

Source associations include historical alternatives; actual acquired files are identified in the executed protocol/manifest.

## Historical v0.4 admission and execution

Decision: **measured** (2026-10-30). Constructed and validated deterministic loader/unit/timing audit using actual Allen NWB shared withD02, six sweeps and61 leaf fields; reference crosschecked with official EphysSweep metadata plus independent block-averaged D02 arrays. No claim of DANDI archive benchmark, format-general robustness, or scientific discovery.

[Source-linked admission evidence](../../../literature/admission-v04-cell-workflow.json). [Actual protocol and artifacts](../../../experiments/N05). [Central task results](../../../results/N05.json).

## Current admission and execution

Preview 0.10: measured. Constructed and validated deterministic loader/unit/timing audit using actual Allen NWB shared withD02, six sweeps and61 leaf fields; reference crosschecked with official EphysSweep metadata plus independent block-averaged D02 arrays. No claim of DANDI archive benchmark, format-general robustness, or scientific discovery.

[Admission/source evidence](../../../literature/admission-v04-cell-workflow.json). [Actual protocol/worklog](../../../experiments/N05). [Task measurements](../../../results/N05.json).
