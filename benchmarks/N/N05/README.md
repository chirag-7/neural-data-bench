# N05 — NWB data loading, units and reproducibility

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** DANDI selected dandisets / IBL data

**State:** not evaluated; candidate_pending_validation. Mapped resource only; license, acquisition, split, scorer and baseline gates are not yet all validated.

## Scientific use

Input: NWB neurophysiology and metadata

Target/ground truth: Metadata invariants; known deterministic reference outputs

Specialist candidates: NWB/ONE loading scripts; expert QC

General-model route: General coding agent

## Execution and performance

No experiment admitted yet. All measurements are centralized in [results](../../../results/). Current best: **not verified**. Missing scores are unknown, not zero. Literature resources are not newly executed results.

## Limitations

Archive is not benchmark; need curated cases and hidden answers

## Sources

- [https://about.dandiarchive.org/](https://about.dandiarchive.org/)
- [https://www.internationalbrainlab.com/data](https://www.internationalbrainlab.com/data)

## v0.4 admission and execution

Decision: **measured** (2026-10-30). Constructed and validated deterministic loader/unit/timing audit using actual Allen NWB shared withD02, six sweeps and61 leaf fields; reference crosschecked with official EphysSweep metadata plus independent block-averaged D02 arrays. No claim of DANDI archive benchmark, format-general robustness, or scientific discovery.

[Source-linked admission evidence](../../../literature/admission-v04-cell-workflow.json). [Actual protocol and artifacts](../../../experiments/N05). [Central task results](../../../results/N05.json).

## v0.5 execution status

measured. Constructed and validated deterministic loader/unit/timing audit using actual Allen NWB shared withD02, six sweeps and61 leaf fields; reference crosschecked with official EphysSweep metadata plus independent block-averaged D02 arrays. No claim of DANDI archive benchmark, format-general robustness, or scientific discovery.

[Admission/source evidence](../../../literature/admission-v04-cell-workflow.json). [Actual protocol/worklog](../../../experiments/N05). [Task measurements](../../../results/N05.json).
