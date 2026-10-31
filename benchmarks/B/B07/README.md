# B07 — Raw neural data compression

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** AIND original ephys-compression benchmark; fixed real Neuropixels shortchunks

**State:** measured. Current status for this exact task-resource slice; current global best remains unverified.

## Scientific use

Input: Original time-major little-endian int16 ADC bytes; no resampling, filtering or training/calibration set

Target/ground truth: Exact original numerical bytes,not neural labels or biological interpretation

Mapped specialist candidates (not all evaluated): WavPack; Zstd/Blosc codecs

General-model route: Generic learned compression model

## Execution and performance

**Executed slice:** All 16 original AIND/IBL recordings: one fixed 4,096-sample chunk, all 384 channels and original int16 bytes per recording; 14 source animals.

[Frozen protocol and artifacts](../../../experiments/B07). [Measured scores and references](../../../results/B07.json). [Central data](../../../results/measurements.csv). Missing or failed outputs are retained.

## Limitations

One roughly 0.137-second chunk per recording; 16 recordings from 14 animals. This tests short-chunk lossless storage, not full streaming or neural interpretation. Fixed local WavPack/delta–Blosc references have unequal implementation/library effort; current global best remains unverified.

## Sources

- [https://allenneuraldynamics.github.io/data.html](https://allenneuraldynamics.github.io/data.html)
- [https://github.com/awslabs/open-data-registry/blob/main/datasets/allen-nd-ephys-compression.yaml](https://github.com/awslabs/open-data-registry/blob/main/datasets/allen-nd-ephys-compression.yaml)
- [https://github.com/AllenNeuralDynamics/ephys-compression/tree/c89e8e481435f39e3bf041bfc0eaac5ef6d93900](https://github.com/AllenNeuralDynamics/ephys-compression/tree/c89e8e481435f39e3bf041bfc0eaac5ef6d93900)
- [https://www.wavpack.com/](https://www.wavpack.com/)
- [https://numcodecs.readthedocs.io/en/stable/compression/blosc.html](https://numcodecs.readthedocs.io/en/stable/compression/blosc.html)
- [https://doi.org/10.1088/1741-2552/acf5a4](https://doi.org/10.1088/1741-2552/acf5a4)
- [https://www.biorxiv.org/content/10.1101/2023.05.22.541700v2](https://www.biorxiv.org/content/10.1101/2023.05.22.541700v2)

Source associations include historical alternatives; actual acquired files are identified in the executed protocol/manifest.

## Historical v0.4 admission and execution

Decision: **candidate_pending_validation** (2026-10-30). Lossless compression is executable with small frozen raw ephys segments, exactbyte reconstruction and compression/runtime metrics. Need immutable raw-file URI, acquisition terms and canonical codec reference; no raw acquisition attempted here. Avoid different dtype or discarded channels confounding ratio.

[Source-linked admission evidence](../../../literature/admission-v04-behavior-population.json). This endpoint was not run in this release; absence is unknown, not zero or proof of poor data.

## Current admission and execution

Preview 0.10: measured. Source-specific rights/data/scorer checks and frozen model procedure completed for the explicit custom slice; no broader resource or current-SOTA claim.

[Admission/source evidence](../../../experiments/B07/protocol.md). [Actual protocol/worklog](../../../experiments/B07). [Task measurements](../../../results/B07.json).
