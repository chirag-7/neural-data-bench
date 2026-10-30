# N06 — Data integrity fault detection

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** Proposed blinded scientific data-integrity cases

**State:** not evaluated; deferred. Current release excludes execution: new research construction, uncertain release/rights, or setup outside lightweight budget.

## Scientific use

Input: NWB/BIDS files with controlled metadata/timing faults

Target/ground truth: Injected sampling-rate, timestamp, channel or unit faults

Specialist candidates: Schema validators; prespecified QC tests

General-model route: General code agent

## Execution and performance

No experiment admitted yet. All measurements are centralized in [results](../../../results/). Current best: **not verified**. Missing scores are unknown, not zero. Literature resources are not newly executed results.

## Limitations

Needs an independently validated corruption generator and scorer

## Sources

- [https://about.dandiarchive.org/](https://about.dandiarchive.org/)

## v0.4 admission and execution

Decision: **deferred** (2026-10-30). Proposed data-integrity task has no independently validated corruption generator/hidden fault suite or prespecified detection thresholds yet. DANDI is an archive, not the fault benchmark. N05 clean-file parsing does not establish detection of metadata/timing/unit corruption.

[Source-linked admission evidence](../../../literature/admission-v04-cell-workflow.json). This endpoint was not run in this release; absence is unknown, not zero or proof of poor data.
