# H17 — Cross-laboratory rodent sleep staging

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** Mouse Sleep Staging Validation dataset (MSSV), OpenNeuro ds006366

**State:** deferred. Current status for this exact task-resource slice; current global best remains unverified.

## Scientific use

Input: Mouse EEG/EMG, expert stage annotations

Target/ground truth: Expert sleep scores from 92 healthy mice across five labs

Mapped specialist candidates (not all evaluated): Published mouse sleep staging methods; simple spectral-feature baseline

General-model route: General time-series features or code-generated classifier

## Execution and performance

No experiment admitted yet. All measurements are centralized in [results](../../../results/). Current best: **not verified**. Missing scores are unknown, not zero. Literature resources are not newly executed results.

## Limitations

Rodent stages, epoch lengths and recording setups must be specified; human sleep foundation-model scores cannot transfer directly

## Sources

- [https://nemar.org/dataset/on006366](https://nemar.org/dataset/on006366)
- [https://doi.org/10.18112/openneuro.ds006366.v1.0.1](https://doi.org/10.18112/openneuro.ds006366.v1.0.1)

Source associations include historical alternatives; actual acquired files are identified in the executed protocol/manifest.

## Historical v0.4 admission and execution

Decision: **deferred** (2026-10-30). Original NEMAR MSSV page accessible:92mice,five labs,CC0,~5.3GB archive/direct manifest. Promising public real sleep resource, not bad data. Need lab identifiers, stage epoch alignment and leave-lab-out acquisition adapter; no local raw arrays downloaded.

[Source-linked admission evidence](../../../literature/admission-v04-electrical.json). This endpoint was not run in this release; absence is unknown, not zero or proof of poor data.

## Current admission and execution

Preview 0.9: deferred. Original NEMAR MSSV page accessible:92mice,five labs,CC0,~5.3GB archive/direct manifest. Promising public real sleep resource, not bad data. Need lab identifiers, stage epoch alignment and leave-lab-out acquisition adapter; no local raw arrays downloaded.

[Admission/source evidence](../../../literature/admission-v04-electrical.json).
