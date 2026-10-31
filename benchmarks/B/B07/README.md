# B07 — Raw neural data compression

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** AIND electrophysiology compression benchmark

**State:** candidate_pending_validation. Current status for this exact task-resource slice; current global best remains unverified.

## Scientific use

Input: Neuropixels voltage recordings

Target/ground truth: Original bytes or original downstream output

Mapped specialist candidates (not all evaluated): WavPack; Zstd/Blosc codecs

General-model route: Generic learned compression model

## Execution and performance

No experiment admitted yet. All measurements are centralized in [results](../../../results/). Current best: **not verified**. Missing scores are unknown, not zero. Literature resources are not newly executed results.

## Limitations

Lossless byte equality differs from downstream-preserving lossy compression

## Sources

- [https://allenneuraldynamics.github.io/data.html](https://allenneuraldynamics.github.io/data.html)
- [https://github.com/awslabs/open-data-registry/blob/main/datasets/allen-nd-ephys-compression.yaml](https://github.com/awslabs/open-data-registry/blob/main/datasets/allen-nd-ephys-compression.yaml)

Source associations include historical alternatives; actual acquired files are identified in the executed protocol/manifest.

## Historical v0.4 admission and execution

Decision: **candidate_pending_validation** (2026-10-30). Lossless compression is executable with small frozen raw ephys segments, exactbyte reconstruction and compression/runtime metrics. Need immutable raw-file URI, acquisition terms and canonical codec reference; no raw acquisition attempted here. Avoid different dtype or discarded channels confounding ratio.

[Source-linked admission evidence](../../../literature/admission-v04-behavior-population.json). This endpoint was not run in this release; absence is unknown, not zero or proof of poor data.

## Current admission and execution

Preview 0.9: candidate_pending_validation. Original public S3 listing and binary metadata acquired;16 experimental raw sources identified and CC BY4.0 recorded by original AWS registry. Raw chunks, lossless byte-exact codec contract/scorer and specialist execution remain unfrozen; no compression scores claimed.

[Admission/source evidence](../../../literature/admission-v04-behavior-population.json).
