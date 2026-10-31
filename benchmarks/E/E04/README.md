# E04 — Masked/future neural activity prediction

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** BrainWideBench TS2

**State:** candidate_pending_validation. Current status for this exact task-resource slice; current global best remains unverified.

## Scientific use

Input: IBL spike counts across brain regions

Target/ground truth: Held-out observed spikes

Mapped specialist candidates (not all evaluated): Released BWB neural prediction baselines

General-model route: General sequence/world model with rate head

## Execution and performance

No experiment admitted yet. All measurements are centralized in [results](../../../results/). Current best: **not verified**. Missing scores are unknown, not zero. Literature resources are not newly executed results.

## Limitations

Do not conflate acausal infilling with causal forecasting

## Sources

- [https://brainbench-org.github.io/ibl-bwb/](https://brainbench-org.github.io/ibl-bwb/)
- [https://arxiv.org/abs/2609.22064](https://arxiv.org/abs/2609.22064)

Source associations include historical alternatives; actual acquired files are identified in the executed protocol/manifest.

## Historical v0.4 admission and execution

Decision: **candidate_pending_validation** (2026-10-30). BrainWideBench TS2 masked/future prediction has exact protocol and public recordings, but causal future prediction versus bidirectional masking must be separate. Need exact bins/neurons/session split and official heldout targets. Not acquired here; E01 does not cover this transfer setting.

[Source-linked admission evidence](../../../literature/admission-v04-behavior-population.json). This endpoint was not run in this release; absence is unknown, not zero or proof of poor data.

## Current admission and execution

Preview 0.8: candidate_pending_validation. BrainWideBench TS2 masked/future prediction has exact protocol and public recordings, but causal future prediction versus bidirectional masking must be separate. Need exact bins/neurons/session split and official heldout targets. Not acquired here; E01 does not cover this transfer setting.

[Admission/source evidence](../../../literature/admission-v04-behavior-population.json).
