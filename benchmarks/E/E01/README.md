# E01 — Neural rate inference and co-smoothing

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** Neural Latents Benchmark 2021

**State:** not evaluated; candidate_pending_validation. Mapped resource only; license, acquisition, split, scorer and baseline gates are not yet all validated.

## Scientific use

Input: Binned spike-count tensors

Target/ground truth: Held-out observed spikes; behavioral covariates

Specialist candidates: LFADS/AutoLFADS; GPFA; NDT; strong current local baseline

General-model route: General sequence model with nonnegative rate readout

## Execution and performance

No experiment admitted yet. All measurements are centralized in [results](../../../results/). Current best: **not verified**. Missing scores are unknown, not zero. Literature resources are not newly executed results.

## Limitations

EvalAI closed Jan 2026; test data public; guard test overfitting

## Sources

- [https://neurallatents.github.io/](https://neurallatents.github.io/)

## v0.4 admission and execution

Decision: **measured** (2026-10-30). Acquired published DANDI000140 version0.220113.0408 NWBs and pinned official2026released test targets.99train/100test trials,107heldin/35heldout neurons,20ms bins. Unmodified officialtensor code, explicit lasttrainingtrial199 exclusion, exactNLB bits/spike scorer. Custom supervised diagnostic, not complete leaderboard reproduction.

[Source-linked admission evidence](../../../literature/admission-v04-behavior-population.json). [Actual protocol and artifacts](../../../experiments/E01). [Central task results](../../../results/E01.json).

## v0.5 execution status

measured. Acquired published DANDI000140 version0.220113.0408 NWBs and pinned official2026released test targets.99train/100test trials,107heldin/35heldout neurons,20ms bins. Unmodified officialtensor code, explicit lasttrainingtrial199 exclusion, exactNLB bits/spike scorer. Custom supervised diagnostic, not complete leaderboard reproduction.

[Admission/source evidence](../../../literature/admission-v04-behavior-population.json). [Actual protocol/worklog](../../../experiments/E01). [Task measurements](../../../results/E01.json).
