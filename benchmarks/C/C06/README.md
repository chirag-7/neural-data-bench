# C06 — Cross-preparation calcium deconvolution

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** CASCADE DS04 native-rate held-out-fish inference

**State:** measured. Current status for this exact task-resource slice; current global best remains unverified.

## Scientific use

Input: Native-rate dF/F, valid-frame mask and frame interval; no resampling

Target/ground truth: Simultaneous electrical spike counts smoothed at 200 ms and binned to native optical support

Mapped specialist candidates (not all evaluated): CASCADE; OASIS

General-model route: General time-series adaptation

## Execution and performance

**Executed slice:** All 15 neurons / 45 recordings, 81.66 minutes; two training and two held-out test fish.

[Frozen protocol and artifacts](../../../experiments/C06). [Measured scores and references](../../../results/C06.json). [Central data](../../../results/measurements.csv). Missing or failed outputs are retained.

## Limitations

Only two test fish; Pearson ignores amplitude calibration and all models show substantial count error. Fixed training-scaled OASIS AR1 is not CASCADE or strongest verified specialist; global released CASCADE weights include test source. Repository GPL-3.0 with no separate data-specific declaration located; raw cache kept local.

## Sources

- [https://pmc.ncbi.nlm.nih.gov/articles/PMC7611618/](https://pmc.ncbi.nlm.nih.gov/articles/PMC7611618/)
- [https://github.com/HelmchenLabSoftware/Cascade/tree/1f9f98bf93b9b554ab68d6304aa365ab7c7ee34f](https://github.com/HelmchenLabSoftware/Cascade/tree/1f9f98bf93b9b554ab68d6304aa365ab7c7ee34f)
- [https://github.com/HelmchenLabSoftware/Cascade/blob/1f9f98bf93b9b554ab68d6304aa365ab7c7ee34f/cascade2p/utils.py](https://github.com/HelmchenLabSoftware/Cascade/blob/1f9f98bf93b9b554ab68d6304aa365ab7c7ee34f/cascade2p/utils.py)
- [https://github.com/HelmchenLabSoftware/Cascade/blob/1f9f98bf93b9b554ab68d6304aa365ab7c7ee34f/LICENSE](https://github.com/HelmchenLabSoftware/Cascade/blob/1f9f98bf93b9b554ab68d6304aa365ab7c7ee34f/LICENSE)

Source associations include historical alternatives; actual acquired files are identified in the executed protocol/manifest.

## Historical v0.4 admission and execution

Decision: **candidate_pending_validation** (2026-10-30). CASCADE paired fluorescence/electrophysiology is a credible additional deconvolution source. Need exact indicator/preparation noise/rate matching, neuron/recording-disjointsplit and baseline. Shared Spikefinder cells must be deduplicated, not counted as new independent recordings. Not acquired here.

[Source-linked admission evidence](../../../literature/admission-v04-behavior-population.json). This endpoint was not run in this release; absence is unknown, not zero or proof of poor data.

## Current admission and execution

Preview 0.11: measured. Source-specific rights/data/scorer checks and frozen model procedure completed for the explicit custom slice; no broader resource or current-SOTA claim.

[Admission/source evidence](../../../experiments/C06/protocol.md). [Actual protocol/worklog](../../../experiments/C06). [Task measurements](../../../results/C06.json).

## Current specialists and repair sensitivity — 1 November 2026

[Current specialist review](../../../literature/specialist-review-2026-11-01/C06.json) · [Native version trajectories and practical interpretation](../../../analysis/practical-review-2026-11-01/report.md). The review distinguishes tested references from unexecuted newer candidates; no matched current global winner is certified.
