# D01 — Voltage imaging spike and subthreshold extraction

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** VolPy evaluation corpus

**State:** deferred. Current status for this exact task-resource slice; current global best remains unverified.

## Scientific use

Input: Fast voltage movies

Target/ground truth: ROI labels; paired ephys and simulations on subsets

Mapped specialist candidates (not all evaluated): VolPy; published voltage extraction baselines

General-model route: Generic video denoising/source separation

## Execution and performance

No experiment admitted yet. All measurements are centralized in [results](../../../results/). Current best: **not verified**. Missing scores are unknown, not zero. Literature resources are not newly executed results.

## Limitations

Not every movie has ephys truth; distinguish segmentation and spike scoring

## Sources

- [https://pmc.ncbi.nlm.nih.gov/articles/PMC8075204/](https://pmc.ncbi.nlm.nih.gov/articles/PMC8075204/)
- [https://github.com/flatironinstitute/CaImAn/tree/main/caiman/source_extraction/volpy](https://github.com/flatironinstitute/CaImAn/tree/main/caiman/source_extraction/volpy)

Source associations include historical alternatives; actual acquired files are identified in the executed protocol/manifest.

## Historical v0.4 admission and execution

Decision: **deferred** (2026-10-30). Paired voltage movie/ephys extraction needs validated movie-to-truth alignment, ROI policy, and sampling-time scorer. Primary PMC article web access returned recaptcha in this screening; CaImAn VolPy source documentation located. No acquisition/fit was completed; this is a protocol/resource limitation of this batch, not evidence of bad data.

[Source-linked admission evidence](../../../literature/admission-v04-cell-workflow.json). This endpoint was not run in this release; absence is unknown, not zero or proof of poor data.

## Current admission and execution

Preview 0.6: deferred. Paired voltage movie/ephys extraction needs validated movie-to-truth alignment, ROI policy, and sampling-time scorer. Primary PMC article web access returned recaptcha in this screening; CaImAn VolPy source documentation located. No acquisition/fit was completed; this is a protocol/resource limitation of this batch, not evidence of bad data.

[Admission/source evidence](../../../literature/admission-v04-cell-workflow.json).
