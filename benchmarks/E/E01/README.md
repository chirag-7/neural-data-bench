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
