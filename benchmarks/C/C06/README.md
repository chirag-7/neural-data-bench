# C06 — Cross-preparation calcium deconvolution

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** CASCADE ground-truth database

**State:** candidate_pending_validation. Current status for this exact task-resource slice; current global best remains unverified.

## Scientific use

Input: Calcium traces and paired spikes

Target/ground truth: Simultaneous electrophysiology

Mapped specialist candidates (not all evaluated): CASCADE; OASIS

General-model route: General time-series adaptation

## Execution and performance

No experiment admitted yet. All measurements are centralized in [results](../../../results/). Current best: **not verified**. Missing scores are unknown, not zero. Literature resources are not newly executed results.

## Limitations

CASCADE is domain trained; compare equal adaptation budgets

## Sources

- [https://pmc.ncbi.nlm.nih.gov/articles/PMC7611618/](https://pmc.ncbi.nlm.nih.gov/articles/PMC7611618/)

Source associations include historical alternatives; actual acquired files are identified in the executed protocol/manifest.

## Historical v0.4 admission and execution

Decision: **candidate_pending_validation** (2026-10-30). CASCADE paired fluorescence/electrophysiology is a credible additional deconvolution source. Need exact indicator/preparation noise/rate matching, neuron/recording-disjointsplit and baseline. Shared Spikefinder cells must be deduplicated, not counted as new independent recordings. Not acquired here.

[Source-linked admission evidence](../../../literature/admission-v04-behavior-population.json). This endpoint was not run in this release; absence is unknown, not zero or proof of poor data.

## Current admission and execution

Preview 0.9: candidate_pending_validation. CASCADE paired fluorescence/electrophysiology is a credible additional deconvolution source. Need exact indicator/preparation noise/rate matching, neuron/recording-disjointsplit and baseline. Shared Spikefinder cells must be deduplicated, not counted as new independent recordings. Not acquired here.

[Admission/source evidence](../../../literature/admission-v04-behavior-population.json).
