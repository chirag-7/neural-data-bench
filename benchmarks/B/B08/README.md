# B08 — Spike train compression

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** FALCON M2 events / original Spikepack; custom timing-lossy storage

**State:** measured. Current status for this exact task-resource slice; current global best remains unverified.

## Scientific use

Input: Sorted float64 spike times and int32 unit labels; complete recordings

Target/ground truth: Exact labels/order/count, nondecreasing decoded times and ≤50 μs event timing error

Mapped specialist candidates (not all evaluated): Spikepack; generic integer codecs

General-model route: General sequence entropy model

## Execution and performance

**Executed slice:** All seven original G01 FALCON M2 recordings: 1,052,545 events, four days, one monkey.

[Frozen protocol and artifacts](../../../experiments/B08). [Measured scores and references](../../../results/B08.json). [Central data](../../../results/measurements.csv). Missing or failed outputs are retained.

## Limitations

Shares G01 source, one monkey. Timing is intentionally lossy; all metadata bytes count. Frozen whitelist rejects heapq used by two models while prompt permits ambiguously described ordinary utilities: failures retained but task excluded retrospectively from aggregate capability/version comparisons. Original Spikepack local execution, not global best.

## Sources

- [https://github.com/int-brain-lab/spikepack](https://github.com/int-brain-lab/spikepack)
- [https://www.internationalbrainlab.com/data](https://www.internationalbrainlab.com/data)
- [https://dandiarchive.org/dandiset/000953](https://dandiarchive.org/dandiset/000953)

Source associations include historical alternatives; actual acquired files are identified in the executed protocol/manifest.

## Historical v0.4 admission and execution

Decision: **candidate_pending_validation** (2026-10-30). IBL spike trains could support lossless integer/event compression; reconstruction must preserve exact event times/unitIDs. Need exact release/chunk bounds and bits/event denominator; shared IBL recordings must not count twice as independent datasets. Not acquired here.

[Source-linked admission evidence](../../../literature/admission-v04-behavior-population.json). This endpoint was not run in this release; absence is unknown, not zero or proof of poor data.

## Current admission and execution

Preview 0.11: measured. Source-specific rights/data/scorer checks and frozen model procedure completed for the explicit custom slice; no broader resource or current-SOTA claim.

[Admission/source evidence](../../../experiments/B08/protocol.md). [Actual protocol/worklog](../../../experiments/B08). [Task measurements](../../../results/B08.json).
