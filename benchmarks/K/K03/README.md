# K03 — Molecular/pathology cohort analysis

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** NeuroDiscoveryBench atlas/SEA-AD tasks

**State:** not evaluated; candidate_pending_validation. Mapped resource only; license, acquisition, split, scorer and baseline gates are not yet all validated.

## Scientific use

Input: Cell atlas tables, donors and pathology labels

Target/ground truth: Expert curated quantitative/text/figure answers

Specialist candidates: Reference expert analysis

General-model route: General coding agent

## Execution and performance

No experiment admitted yet. All measurements are centralized in [results](../../../results/). Current best: **not verified**. Missing scores are unknown, not zero. Literature resources are not newly executed results.

## Limitations

Donor is the experimental unit; cells are not independent patient replicates

## Sources

- [https://github.com/allenai/neurodiscoverybench](https://github.com/allenai/neurodiscoverybench)

## v0.4 admission and execution

Decision: **deferred** (2026-10-30). Primary NeuroDiscoveryBench includes existing workflow metadata, reference answers and figure/text scoring, but evaluates scientific-analysis agents rather than the fixed train/predict interface used for this execution batch. Large dataset downloader plus external evaluator/workflow budget not replicated; code/data licenses separate and rubric/judge provenance must be logged before admitting scores.

[Source-linked admission evidence](../../../literature/admission-v04-cell-workflow.json). This endpoint was not run in this release; absence is unknown, not zero or proof of poor data.
