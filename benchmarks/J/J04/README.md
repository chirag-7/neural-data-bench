# J04 — Histology-to-atlas registration

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** DeepSlice evaluation data

**State:** not evaluated; candidate_pending_validation. Mapped resource only; license, acquisition, split, scorer and baseline gates are not yet all validated.

## Scientific use

Input: Coronal histology sections and atlas

Target/ground truth: Expert alignment/landmarks

Specialist candidates: DeepSlice; atlas registration workflow

General-model route: Generic image correspondence features

## Execution and performance

No experiment admitted yet. All measurements are centralized in [results](../../../results/). Current best: **not verified**. Missing scores are unknown, not zero. Literature resources are not newly executed results.

## Limitations

Expert alignment uncertainty; orientation mistakes can dominate

## Sources

- [https://pmc.ncbi.nlm.nih.gov/articles/PMC10514056/](https://pmc.ncbi.nlm.nih.gov/articles/PMC10514056/)

## v0.4 admission and execution

Decision: **candidate_pending_validation** (2026-10-30). DeepSlice histology registration needs expert reference transforms/landmarks paired with source sections and animal IDs. Those pairs and train/test protocol have not been downloaded/validated. No substitute score from image metadata or atlas-derived pseudo-labels.

[Source-linked admission evidence](../../../literature/admission-v04-behavior-population.json). This endpoint was not run in this release; absence is unknown, not zero or proof of poor data.

## v0.5 execution status

candidate_pending_validation. DeepSlice histology registration needs expert reference transforms/landmarks paired with source sections and animal IDs. Those pairs and train/test protocol have not been downloaded/validated. No substitute score from image metadata or atlas-derived pseudo-labels.

[Admission/source evidence](../../../literature/admission-v04-behavior-population.json).
