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

## v0.4 admission and execution

Decision: **deferred** (2026-10-30). Original NEMAR MSSV page accessible:92mice,five labs,CC0,~5.3GB archive/direct manifest. Promising public real sleep resource, not bad data. Need lab identifiers, stage epoch alignment and leave-lab-out acquisition adapter; no local raw arrays downloaded.

[Source-linked admission evidence](../../../literature/admission-v04-electrical.json). This endpoint was not run in this release; absence is unknown, not zero or proof of poor data.

## v0.5 execution status

deferred. Original NEMAR MSSV page accessible:92mice,five labs,CC0,~5.3GB archive/direct manifest. Promising public real sleep resource, not bad data. Need lab identifiers, stage epoch alignment and leave-lab-out acquisition adapter; no local raw arrays downloaded.

[Admission/source evidence](../../../literature/admission-v04-electrical.json).
