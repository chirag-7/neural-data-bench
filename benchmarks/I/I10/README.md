# I10 — MRI quality assessment across sites

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** MRIQC

**State:** not evaluated; candidate_pending_validation. Mapped resource only; license, acquisition, split, scorer and baseline gates are not yet all validated.

## Scientific use

Input: MRI scans, quality metrics and expert ratings

Target/ground truth: Expert quality ratings with label disagreement

Specialist candidates: MRIQC classifier and image quality metrics

General-model route: General VLM or code agent

## Execution and performance

No experiment admitted yet. All measurements are centralized in [results](../../../results/). Current best: **not verified**. Missing scores are unknown, not zero. Literature resources are not newly executed results.

## Limitations

Quality assessment differs from lesion detection and diagnosis

## Sources

- [https://doi.org/10.1371/journal.pone.0184661](https://doi.org/10.1371/journal.pone.0184661)

## v0.4 admission and execution

Decision: **measured** (2026-10-30). Acquired original MRIQC0.10.5 tables and2017 classifier predictions;600ABIDEtrain/265DS030test rater1 labels and68IQMs. One-to-one archived prediction alignment and exclude1 label convention verified. Original classifier used different training/rater/features, currentbest unresolved.

[Source-linked admission evidence](../../../literature/admission-v04-inference-control.json). [Actual protocol and artifacts](../../../experiments/I10). [Central task results](../../../results/I10.json).

## v0.5 execution status

measured. Acquired original MRIQC0.10.5 tables and2017 classifier predictions;600ABIDEtrain/265DS030test rater1 labels and68IQMs. One-to-one archived prediction alignment and exclude1 label convention verified. Original classifier used different training/rater/features, currentbest unresolved.

[Admission/source evidence](../../../literature/admission-v04-inference-control.json). [Actual protocol/worklog](../../../experiments/I10). [Task measurements](../../../results/I10.json).
