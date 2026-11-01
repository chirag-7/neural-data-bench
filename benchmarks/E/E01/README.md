# E01 — Neural rate inference and co-smoothing

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** Neural Latents Benchmark 2021

**State:** measured. Current status for this exact task-resource slice; current global best remains unverified.

## Scientific use

Input: Binned spike-count tensors

Target/ground truth: Held-out observed spikes; behavioral covariates

Mapped specialist candidates (not all evaluated): LFADS/AutoLFADS; GPFA; NDT; strong current local baseline

General-model route: General sequence model with nonnegative rate readout

## Execution and performance

**Executed slice:** Neural Latents Benchmark: MC_Maze_Small, Area2_Bump and DMFC_RSG; held-in to held-out neuron readout using unchanged generated programs.

[Frozen protocol and artifacts](../../../experiments/E01). [Measured scores and references](../../../results/E01.json). [Central data](../../../results/measurements.csv). Missing or failed outputs are retained.

## Limitations

EvalAI closed Jan 2026; test data public; guard test overfitting

## Sources

- [https://neurallatents.github.io/](https://neurallatents.github.io/)
- [https://dandiarchive.org/dandiset/000140/0.220113.0408](https://dandiarchive.org/dandiset/000140/0.220113.0408)
- [https://github.com/neurallatents/nlb_tools](https://github.com/neurallatents/nlb_tools)

Source associations include historical alternatives; actual acquired files are identified in the executed protocol/manifest.

## Historical v0.4 admission and execution

Decision: **measured** (2026-10-30). Acquired published DANDI000140 version0.220113.0408 NWBs and pinned official2026released test targets.99train/100test trials,107heldin/35heldout neurons,20ms bins. Unmodified officialtensor code, explicit lasttrainingtrial199 exclusion, exactNLB bits/spike scorer. Custom supervised diagnostic, not complete leaderboard reproduction.

[Source-linked admission evidence](../../../literature/admission-v04-behavior-population.json). [Actual protocol and artifacts](../../../experiments/E01). [Central task results](../../../results/E01.json).

## Current admission and execution

Preview 0.11: measured. Acquired published DANDI000140 version0.220113.0408 NWBs and pinned official2026released test targets.99train/100test trials,107heldin/35heldout neurons,20ms bins. Unmodified officialtensor code, explicit lasttrainingtrial199 exclusion, exactNLB bits/spike scorer. Custom supervised diagnostic, not complete leaderboard reproduction.

[Admission/source evidence](../../../literature/admission-v04-behavior-population.json). [Actual protocol/worklog](../../../experiments/E01). [Task measurements](../../../results/E01.json).

## Current specialists and repair sensitivity — 1 November 2026

[Current specialist review](../../../literature/specialist-review-2026-11-01/E01.json) · [Native version trajectories and practical interpretation](../../../analysis/practical-review-2026-11-01/report.md). The review distinguishes tested references from unexecuted newer candidates; no matched current global winner is certified.
