# I10 — MRI quality assessment across sites

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** MRIQC

**State:** measured. Current status for this exact task-resource slice; current global best remains unverified.

## Scientific use

Input: MRI scans, quality metrics and expert ratings

Target/ground truth: Expert quality ratings with label disagreement

Mapped specialist candidates (not all evaluated): MRIQC classifier and image quality metrics

General-model route: General VLM or code agent

## Execution and performance

**Executed slice:** MRIQC: 600 ABIDE training scans and 265 DS030 test scans; 68 numeric quality metrics and rater-1 exclusion labels.

[Frozen protocol and artifacts](../../../experiments/I10). [Measured scores and references](../../../results/I10.json). [Central data](../../../results/measurements.csv). Missing or failed outputs are retained.

## Limitations

Quality assessment differs from lesion detection and diagnosis

## Sources

- [https://doi.org/10.1371/journal.pone.0184661](https://doi.org/10.1371/journal.pone.0184661)
- [https://github.com/nipreps/mriqc/tree/c5767827abba6c1c01f7cc26b5fb1d0cd32a7fe8/mriqc/data/csv](https://github.com/nipreps/mriqc/tree/c5767827abba6c1c01f7cc26b5fb1d0cd32a7fe8/mriqc/data/csv)

Source associations include historical alternatives; actual acquired files are identified in the executed protocol/manifest.

## Historical v0.4 admission and execution

Decision: **measured** (2026-10-30). Acquired original MRIQC0.10.5 tables and2017 classifier predictions;600ABIDEtrain/265DS030test rater1 labels and68IQMs. One-to-one archived prediction alignment and exclude1 label convention verified. Original classifier used different training/rater/features, currentbest unresolved.

[Source-linked admission evidence](../../../literature/admission-v04-inference-control.json). [Actual protocol and artifacts](../../../experiments/I10). [Central task results](../../../results/I10.json).

## Current admission and execution

Preview 0.6: measured. Acquired original MRIQC0.10.5 tables and2017 classifier predictions;600ABIDEtrain/265DS030test rater1 labels and68IQMs. One-to-one archived prediction alignment and exclude1 label convention verified. Original classifier used different training/rater/features, currentbest unresolved.

[Admission/source evidence](../../../literature/admission-v04-inference-control.json). [Actual protocol/worklog](../../../experiments/I10). [Task measurements](../../../results/I10.json).
