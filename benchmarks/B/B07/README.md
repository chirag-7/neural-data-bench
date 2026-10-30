# B07 — Raw neural data compression

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** AIND electrophysiology compression benchmark

**State:** not evaluated; candidate_pending_validation. Mapped resource only; license, acquisition, split, scorer and baseline gates are not yet all validated.

## Scientific use

Input: Neuropixels voltage recordings

Target/ground truth: Original bytes or original downstream output

Specialist candidates: WavPack; Zstd/Blosc codecs

General-model route: Generic learned compression model

## Execution and performance

No experiment admitted yet. All measurements are centralized in [results](../../../results/). Current best: **not verified**. Missing scores are unknown, not zero. Literature resources are not newly executed results.

## Limitations

Lossless byte equality differs from downstream-preserving lossy compression

## Sources

- [https://allenneuraldynamics.github.io/data.html](https://allenneuraldynamics.github.io/data.html)

## v0.4 admission and execution

Decision: **candidate_pending_validation** (2026-10-30). Lossless compression is executable with small frozen raw ephys segments, exactbyte reconstruction and compression/runtime metrics. Need immutable raw-file URI, acquisition terms and canonical codec reference; no raw acquisition attempted here. Avoid different dtype or discarded channels confounding ratio.

[Source-linked admission evidence](../../../literature/admission-v04-behavior-population.json). This endpoint was not run in this release; absence is unknown, not zero or proof of poor data.
