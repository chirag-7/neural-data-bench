# F04 — Retinal or other sensory encoding

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** CRCNS retinal datasets; selected sensory collections

**State:** measured. Current status for this exact task-resource slice; current global best remains unverified.

## Scientific use

Input: Stimulus movies and retinal spike trains

Target/ground truth: Measured spike trains with aligned stimuli

Mapped specialist candidates (not all evaluated): LN/GLM; specialized retina CNN

General-model route: General video/time-series representations

## Execution and performance

**Executed slice:** Goldin 2022 retina: 3,160 training images and 30 test images repeated 30 times; 41 neurons, one preparation.

[Frozen protocol and artifacts](../../../experiments/F04). [Measured scores and references](../../../results/F04.json). [Central data](../../../results/measurements.csv). Missing or failed outputs are retained.

## Limitations

Verify stimulus licensing and download terms per dataset

## Sources

- [https://crcns.org/data-sets](https://crcns.org/data-sets)
- [https://open-retina.org/api_reference/data_io/goldin_2022/](https://open-retina.org/api_reference/data_io/goldin_2022/)
- [https://doi.org/10.5281/zenodo.6868362](https://doi.org/10.5281/zenodo.6868362)
- [https://doi.org/10.1038/s41467-022-33242-8](https://doi.org/10.1038/s41467-022-33242-8)
- [https://huggingface.co/datasets/open-retina/open-retina/blob/fc7b91e93c9bd4e76d4e3205fcbcc6a31601985a/README.md](https://huggingface.co/datasets/open-retina/open-retina/blob/fc7b91e93c9bd4e76d4e3205fcbcc6a31601985a/README.md)
- [https://huggingface.co/datasets/open-retina/open-retina](https://huggingface.co/datasets/open-retina/open-retina)

Source associations include historical alternatives; actual acquired files are identified in the executed protocol/manifest.

## Historical v0.4 admission and execution

Decision: **measured** (2026-10-30). Prepared custom real retinal static-image encoding slice from Goldin2022 mouse session via OpenRetina:3160 training images,30 unique held-out images with30 measured repeats and all41 neurons; exact image hashes disjoint, targets verified nonnegative integer counts. This is not an official CRCNS/full-image CNN/temporal-flicker benchmark.

[Source-linked admission evidence](../../../literature/admission-v04-cell-workflow.json). [Actual protocol and artifacts](../../../experiments/F04). [Central task results](../../../results/F04.json).

## Current admission and execution

Preview 0.10: measured. Prepared custom real retinal static-image encoding slice from Goldin2022 mouse session via OpenRetina:3160 training images,30 unique held-out images with30 measured repeats and all41 neurons; exact image hashes disjoint, targets verified nonnegative integer counts. This is not an official CRCNS/full-image CNN/temporal-flicker benchmark.

[Admission/source evidence](../../../literature/admission-v04-cell-workflow.json). [Actual protocol/worklog](../../../experiments/F04). [Task measurements](../../../results/F04.json).
