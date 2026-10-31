# J01 — EM neurite segmentation

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** CREMI segmentation

**State:** deferred. Current status for this exact task-resource slice; current global best remains unverified.

## Scientific use

Input: Serial-section EM volumes

Target/ground truth: Expert instance labels

Mapped specialist candidates (not all evaluated): 3D U-Net/affinity segmentation

General-model route: Generic segmentation features with matched prompts

## Execution and performance

No experiment admitted yet. All measurements are centralized in [results](../../../results/). Current best: **not verified**. Missing scores are unknown, not zero. Literature resources are not newly executed results.

## Limitations

2D masks alone do not preserve 3D neuron topology

## Sources

- [https://cremi.janelia.org/](https://cremi.janelia.org/)

Source associations include historical alternatives; actual acquired files are identified in the executed protocol/manifest.

## Historical v0.4 admission and execution

Decision: **deferred** (2026-10-30). CREMI real volumetric image segmentation needs3D inputs and topology-sensitive adapted Rand/VI scoring. GPU specialist weights/scorer not prepared; a small randomvoxel classifier would not validate neurite segmentation.

[Source-linked admission evidence](../../../literature/admission-v04-behavior-population.json). This endpoint was not run in this release; absence is unknown, not zero or proof of poor data.

## Current admission and execution

Preview 0.10: deferred. CREMI real volumetric image segmentation needs3D inputs and topology-sensitive adapted Rand/VI scoring. GPU specialist weights/scorer not prepared; a small randomvoxel classifier would not validate neurite segmentation.

[Admission/source evidence](../../../literature/admission-v04-behavior-population.json).
