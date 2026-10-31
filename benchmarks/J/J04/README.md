# J04 — Histology-to-atlas registration

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** DeepSlice evaluation data

**State:** candidate_pending_validation. Current status for this exact task-resource slice; current global best remains unverified.

## Scientific use

Input: Coronal histology sections and atlas

Target/ground truth: Expert alignment/landmarks

Mapped specialist candidates (not all evaluated): DeepSlice; atlas registration workflow

General-model route: Generic image correspondence features

## Execution and performance

No experiment admitted yet. All measurements are centralized in [results](../../../results/). Current best: **not verified**. Missing scores are unknown, not zero. Literature resources are not newly executed results.

## Limitations

Expert alignment uncertainty; orientation mistakes can dominate

## Sources

- [https://pmc.ncbi.nlm.nih.gov/articles/PMC10514056/](https://pmc.ncbi.nlm.nih.gov/articles/PMC10514056/)

Source associations include historical alternatives; actual acquired files are identified in the executed protocol/manifest.

## Historical v0.4 admission and execution

Decision: **candidate_pending_validation** (2026-10-30). DeepSlice histology registration needs expert reference transforms/landmarks paired with source sections and animal IDs. Those pairs and train/test protocol have not been downloaded/validated. No substitute score from image metadata or atlas-derived pseudo-labels.

[Source-linked admission evidence](../../../literature/admission-v04-behavior-population.json). This endpoint was not run in this release; absence is unknown, not zero or proof of poor data.

## Current admission and execution

Preview 0.6: candidate_pending_validation. DeepSlice histology registration needs expert reference transforms/landmarks paired with source sections and animal IDs. Those pairs and train/test protocol have not been downloaded/validated. No substitute score from image metadata or atlas-derived pseudo-labels.

[Admission/source evidence](../../../literature/admission-v04-behavior-population.json).
