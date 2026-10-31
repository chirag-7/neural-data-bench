# I06 — Brain MRI lesion segmentation

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** BraTS releases

**State:** deferred. Current status for this exact task-resource slice; current global best remains unverified.

## Scientific use

Input: Multicontrast MRI volumes

Target/ground truth: Expert tumor labels

Mapped specialist candidates (not all evaluated): nnU-Net; release-specific specialist

General-model route: Generic segmentation model with stated prompts/adaptation

## Execution and performance

No experiment admitted yet. All measurements are centralized in [results](../../../results/). Current best: **not verified**. Missing scores are unknown, not zero. Literature resources are not newly executed results.

## Limitations

Clinical imaging extension beyond course; access rules vary by release

## Sources

- [https://www.med.upenn.edu/cbica/brats/](https://www.med.upenn.edu/cbica/brats/)

Source associations include historical alternatives; actual acquired files are identified in the executed protocol/manifest.

## Historical v0.4 admission and execution

Decision: **deferred** (2026-10-30). Original CBICA BraTS page lists multiple separate Synapse challenge instances. Need choose task/release, dataset access terms, subject-level split and official tumor-region/Dice/HD95 rules. No raw records acquired or multiple releases mixed.

[Source-linked admission evidence](../../../literature/admission-v04-electrical.json). This endpoint was not run in this release; absence is unknown, not zero or proof of poor data.

## Current admission and execution

Preview 0.10: deferred. Original CBICA BraTS page lists multiple separate Synapse challenge instances. Need choose task/release, dataset access terms, subject-level split and official tumor-region/Dice/HD95 rules. No raw records acquired or multiple releases mixed.

[Admission/source evidence](../../../literature/admission-v04-electrical.json).
