# B03 — Probe motion estimation

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** SpikeInterface procedural drifting voltage; processed localization-count rasters

**State:** measured. Current status for this exact task-resource slice; current global best remains unverified.

## Scientific use

Input: Observed-voltage peak detection and localization summarized as 1 s by 5 μm depth count rasters

Target/ground truth: Known injected synthetic physical displacement averaged to 1 s; not real biological drift

Mapped specialist candidates (not all evaluated): DREDge; Kilosort motion correction

General-model route: Generic registration or signal model

## Execution and performance

**Executed slice:** Eight independent 90-second simulations, 64 contacts/neurons; four train and four test recordings.

[Frozen protocol and artifacts](../../../experiments/B03). [Measured scores and references](../../../results/B03.json). [Central data](../../../results/measurements.csv). Missing or failed outputs are retained.

## Limitations

Fully synthetic, fixed front-end and rigid motion only. Simulations are Monte Carlo instances, not independent animals. Same raster supplied to fixed SpikeInterface decentralized reference. No real drift, raw voltage inference, nonrigid recovery or global-best claim.

## Sources

- [https://spikeinterface.readthedocs.io/en/stable/modules/benchmark.html](https://spikeinterface.readthedocs.io/en/stable/modules/benchmark.html)
- [https://github.com/evarol/dredge](https://github.com/evarol/dredge)
- [https://spikeinterface.readthedocs.io/en/latest/api.html](https://spikeinterface.readthedocs.io/en/latest/api.html)
- [https://github.com/SpikeInterface/spikeinterface](https://github.com/SpikeInterface/spikeinterface)
- [https://proceedings.neurips.cc/paper/2021/hash/b950ea26ca12daae142bd74dba4427c8-Abstract.html](https://proceedings.neurips.cc/paper/2021/hash/b950ea26ca12daae142bd74dba4427c8-Abstract.html)

Source associations include historical alternatives; actual acquired files are identified in the executed protocol/manifest.

## Historical v0.4 admission and execution

Decision: **candidate_pending_validation** (2026-10-30). Synthetic drift with known displacement supports motion-estimation error; real DREDge drift estimates themselves are not groundtruth. Need fixed simulator/probe mapping and matched motion pipeline; no acquisition/execution attempted here.

[Source-linked admission evidence](../../../literature/admission-v04-behavior-population.json). This endpoint was not run in this release; absence is unknown, not zero or proof of poor data.

## Current admission and execution

Preview 0.11: measured. Source-specific rights/data/scorer checks and frozen model procedure completed for the explicit custom slice; no broader resource or current-SOTA claim.

[Admission/source evidence](../../../experiments/B03/protocol.md). [Actual protocol/worklog](../../../experiments/B03). [Task measurements](../../../results/B03.json).
