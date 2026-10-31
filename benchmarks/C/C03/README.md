# C03 — Synthetic calcium pipeline with full truth

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** NAOMi

**State:** candidate_pending_validation. Current status for this exact task-resource slice; current global best remains unverified.

## Scientific use

Input: Simulated calcium movies and spikes

Target/ground truth: Simulated masks, fluorescence, spikes and motion

Mapped specialist candidates (not all evaluated): NoRMCorre; CNMF; Suite2p

General-model route: Generic restoration/segmentation/sequence models

## Execution and performance

No experiment admitted yet. All measurements are centralized in [results](../../../results/). Current best: **not verified**. Missing scores are unknown, not zero. Literature resources are not newly executed results.

## Limitations

Simulator truth may not capture real tissue/indicator shift

## Sources

- [https://pmc.ncbi.nlm.nih.gov/articles/PMC8217135/](https://pmc.ncbi.nlm.nih.gov/articles/PMC8217135/)

Source associations include historical alternatives; actual acquired files are identified in the executed protocol/manifest.

## Historical v0.4 admission and execution

Decision: **candidate_pending_validation** (2026-10-30). NAOMi can provide full synthetic calcium movie truth. Requires frozen physicalsimulation parameters and randomseeds, compute budget and exact ROI/timecourse scoring. Clearly synthetic; simulator outputs do not validate real in-vivo robustness.

[Source-linked admission evidence](../../../literature/admission-v04-behavior-population.json). This endpoint was not run in this release; absence is unknown, not zero or proof of poor data.

## Current admission and execution

Preview 0.9: candidate_pending_validation. NAOMi can provide full synthetic calcium movie truth. Requires frozen physicalsimulation parameters and randomseeds, compute budget and exact ROI/timecourse scoring. Clearly synthetic; simulator outputs do not validate real in-vivo robustness.

[Admission/source evidence](../../../literature/admission-v04-behavior-population.json).
