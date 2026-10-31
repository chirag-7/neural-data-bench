# B08 — Spike train compression

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** Spikepack plus public IBL spike trains

**State:** candidate_pending_validation. Current status for this exact task-resource slice; current global best remains unverified.

## Scientific use

Input: Integer event times and unit identifiers

Target/ground truth: Original integer event arrays

Mapped specialist candidates (not all evaluated): Spikepack; generic integer codecs

General-model route: General sequence entropy model

## Execution and performance

No experiment admitted yet. All measurements are centralized in [results](../../../results/). Current best: **not verified**. Missing scores are unknown, not zero. Literature resources are not newly executed results.

## Limitations

Codec/tool, not an established model benchmark; preserve timing

## Sources

- [https://github.com/int-brain-lab/spikepack](https://github.com/int-brain-lab/spikepack)
- [https://www.internationalbrainlab.com/data](https://www.internationalbrainlab.com/data)

Source associations include historical alternatives; actual acquired files are identified in the executed protocol/manifest.

## Historical v0.4 admission and execution

Decision: **candidate_pending_validation** (2026-10-30). IBL spike trains could support lossless integer/event compression; reconstruction must preserve exact event times/unitIDs. Need exact release/chunk bounds and bits/event denominator; shared IBL recordings must not count twice as independent datasets. Not acquired here.

[Source-linked admission evidence](../../../literature/admission-v04-behavior-population.json). This endpoint was not run in this release; absence is unknown, not zero or proof of poor data.

## Current admission and execution

Preview 0.6: candidate_pending_validation. IBL spike trains could support lossless integer/event compression; reconstruction must preserve exact event times/unitIDs. Need exact release/chunk bounds and bits/event denominator; shared IBL recordings must not count twice as independent datasets. Not acquired here.

[Admission/source evidence](../../../literature/admission-v04-behavior-population.json).
