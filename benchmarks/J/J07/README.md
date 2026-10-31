# J07 — Multi-neuron instance segmentation in light microscopy

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** FISBe / FlyLight Instance Segmentation Benchmark

**State:** deferred. Current status for this exact task-resource slice; current global best remains unverified.

## Scientific use

Input: 3D multicolor fruit-fly neuronal microscopy volumes

Target/ground truth: Expert pixel-wise neuron instances

Mapped specialist candidates (not all evaluated): PatchPerPix; flood-filling networks; color clustering

General-model route: General vision segmentation backbone; 3D generic model; code-agent pipeline

## Execution and performance

No experiment admitted yet. All measurements are centralized in [results](../../../results/). Current best: **not verified**. Missing scores are unknown, not zero. Literature resources are not newly executed results.

## Limitations

Thin interwoven neurites require topology-sensitive scoring; pixel Dice alone insufficient; full dataset ~21.6 GB

## Sources

- [https://kainmueller-lab.github.io/fisbe/](https://kainmueller-lab.github.io/fisbe/)
- [https://zenodo.org/records/10875063](https://zenodo.org/records/10875063)
- [https://github.com/Kainmueller-Lab/evaluate-instance-segmentation](https://github.com/Kainmueller-Lab/evaluate-instance-segmentation)

Source associations include historical alternatives; actual acquired files are identified in the executed protocol/manifest.

## Historical v0.4 admission and execution

Decision: **deferred** (2026-10-30). Mapped FISBe release is approximately21.6GB. Thin-neurite3D instance segmentation needs valid masks for partly labeled images and topology-sensitive scorer. No GPU3D pipeline prepared; not a valid tiny-patch substitute without protocol.

[Source-linked admission evidence](../../../literature/admission-v04-behavior-population.json). This endpoint was not run in this release; absence is unknown, not zero or proof of poor data.

## Current admission and execution

Preview 0.6: deferred. Mapped FISBe release is approximately21.6GB. Thin-neurite3D instance segmentation needs valid masks for partly labeled images and topology-sensitive scorer. No GPU3D pipeline prepared; not a valid tiny-patch substitute without protocol.

[Admission/source evidence](../../../literature/admission-v04-behavior-population.json).
