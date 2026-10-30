# J02 — Synapse detection and partner identification

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** CREMI synapse/connectivity categories

**State:** not evaluated; candidate_pending_validation. Mapped resource only; license, acquisition, split, scorer and baseline gates are not yet all validated.

## Scientific use

Input: EM images and neuron instances

Target/ground truth: Synapse and pre/post partner annotations

Specialist candidates: Specialist synapse/partner networks

General-model route: Generic 3D vision representation

## Execution and performance

No experiment admitted yet. All measurements are centralized in [results](../../../results/). Current best: **not verified**. Missing scores are unknown, not zero. Literature resources are not newly executed results.

## Limitations

Detection and correct synaptic partners are different tasks

## Sources

- [https://cremi.janelia.org/](https://cremi.janelia.org/)

## v0.4 admission and execution

Decision: **candidate_pending_validation** (2026-10-30). CREMI synapse detection requires actual pre/post partner instance annotations, separate from image segmentation labels. No synapse manifest or partner matching scorer acquired. Do not substitute arbitrary voxel classification.

[Source-linked admission evidence](../../../literature/admission-v04-behavior-population.json). This endpoint was not run in this release; absence is unknown, not zero or proof of poor data.
