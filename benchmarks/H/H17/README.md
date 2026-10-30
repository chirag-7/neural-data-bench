# H17 — Cross-laboratory rodent sleep staging

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** Mouse Sleep Staging Validation dataset (MSSV), OpenNeuro ds006366

**State:** not evaluated; candidate_pending_validation. Mapped resource only; license, acquisition, split, scorer and baseline gates are not yet all validated.

## Scientific use

Input: Mouse EEG/EMG, expert stage annotations

Target/ground truth: Expert sleep scores from 92 healthy mice across five labs

Specialist candidates: Published mouse sleep staging methods; simple spectral-feature baseline

General-model route: General time-series features or code-generated classifier

## Execution and performance

No experiment admitted yet. All measurements are centralized in [results](../../../results/). Current best: **not verified**. Missing scores are unknown, not zero. Literature resources are not newly executed results.

## Limitations

Rodent stages, epoch lengths and recording setups must be specified; human sleep foundation-model scores cannot transfer directly

## Sources

- [https://nemar.org/dataset/on006366](https://nemar.org/dataset/on006366)
- [https://doi.org/10.18112/openneuro.ds006366.v1.0.1](https://doi.org/10.18112/openneuro.ds006366.v1.0.1)
