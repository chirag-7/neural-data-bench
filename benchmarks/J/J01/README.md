# J01 — EM neurite segmentation

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** CREMI segmentation

**State:** not evaluated; candidate_pending_validation. Mapped resource only; license, acquisition, split, scorer and baseline gates are not yet all validated.

## Scientific use

Input: Serial-section EM volumes

Target/ground truth: Expert instance labels

Specialist candidates: 3D U-Net/affinity segmentation

General-model route: Generic segmentation features with matched prompts

## Execution and performance

No experiment admitted yet. All measurements are centralized in [results](../../../results/). Current best: **not verified**. Missing scores are unknown, not zero. Literature resources are not newly executed results.

## Limitations

2D masks alone do not preserve 3D neuron topology

## Sources

- [https://cremi.janelia.org/](https://cremi.janelia.org/)
