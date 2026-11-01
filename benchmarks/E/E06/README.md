# E06 — Whole-brain neural activity forecasting

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** ZAPBench fixed 256-neuron temporal and unseen-taxis slices

**State:** measured. Current status for this exact task-resource slice; current global best remains unverified.

## Scientific use

Input: 64 observed past frames by 256 response-independently selected neurons

Target/ground truth: Next 32 observed calcium frames in native dF/F units

Mapped specialist candidates (not all evaluated): Published naive, time-series and volumetric video baselines

General-model route: General time-series/world/video models; code agents in separate track

## Execution and performance

**Executed slice:** One zebrafish brain/session; 272 training windows, 43 temporal-tail tests and 12 unseen-taxis tests; same programs reused.

[Frozen protocol and artifacts](../../../experiments/E06). [Measured scores and references](../../../results/E06.json). [Central data](../../../results/measurements.csv). Missing or failed outputs are retained.

## Limitations

One brain/session and two dependent slices; later observed contexts may contain earlier test-period history, so not free-running forecasting. NLinear architecture locally fit with fixed analytical ridge is a conventional domain reference, not official trained weights/full-neuron leaderboard or global best.

## Sources

- [https://google-research.github.io/zapbench/](https://google-research.github.io/zapbench/)
- [https://arxiv.org/abs/2503.02618](https://arxiv.org/abs/2503.02618)
- [https://zapbench-release.storage.googleapis.com/volumes/README.html](https://zapbench-release.storage.googleapis.com/volumes/README.html)
- [https://github.com/google-research/zapbench/tree/7347b3b21a3f332e281b774c945f1505dd966abf](https://github.com/google-research/zapbench/tree/7347b3b21a3f332e281b774c945f1505dd966abf)

Source associations include historical alternatives; actual acquired files are identified in the executed protocol/manifest.

## Historical v0.4 admission and execution

Decision: **candidate_pending_validation** (2026-10-30). ZAPBench real larval zebrafish wholebrain activity forecasting is a distinct real task. Needs pinned release, official heldout temporal blocks and neuron mappings; complete brain arrays may be large. No acquisition attempted here, so no permanent infeasibility claim.

[Source-linked admission evidence](../../../literature/admission-v04-behavior-population.json). This endpoint was not run in this release; absence is unknown, not zero or proof of poor data.

## Current admission and execution

Preview 0.11: measured. Source-specific rights/data/scorer checks and frozen model procedure completed for the explicit custom slice; no broader resource or current-SOTA claim.

[Admission/source evidence](../../../experiments/E06/protocol.md). [Actual protocol/worklog](../../../experiments/E06). [Task measurements](../../../results/E06.json).

## Current specialists and repair sensitivity — 1 November 2026

[Current specialist review](../../../literature/specialist-review-2026-11-01/E06.json) · [Native version trajectories and practical interpretation](../../../analysis/practical-review-2026-11-01/report.md). The review distinguishes tested references from unexecuted newer candidates; no matched current global winner is certified.
