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
