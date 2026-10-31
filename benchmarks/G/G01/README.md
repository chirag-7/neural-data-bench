# G01 — Robust cross-day motor decoding

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** FALCON M2 public calibration NWBs; custom chronological split

**State:** measured. Current status for this exact task-resource slice; current global best remains unverified.

## Scientific use

Input: Intracortical neural activity and kinematics

Target/ground truth: Recorded kinematics on held-out days

Mapped specialist candidates (not all evaluated): FALCON baseline decoders; NDT3 if compatible

General-model route: General sequence model or analysis agent

## Execution and performance

**Executed slice:** FALCON M2 custom cross-day decoding: 1,169 training and 754 test trials, 96 causal features, two finger-velocity outputs, one monkey.

[Frozen protocol and artifacts](../../../experiments/G01). [Measured scores and references](../../../results/G01.json). [Central data](../../../results/measurements.csv). Missing or failed outputs are retained.

## Limitations

One monkey,two testdays; fixed causal features but no closed-loop/online latency evaluation. Full sourceSHAreported,partial extractedbufferhashesverified.

## Sources

- [https://snel-repo.github.io/falcon/](https://snel-repo.github.io/falcon/)
- [https://dandiarchive.org/dandiset/000953](https://dandiarchive.org/dandiset/000953)
- [https://github.com/snel-repo/falcon-challenge](https://github.com/snel-repo/falcon-challenge)

Source associations include historical alternatives; actual acquired files are identified in the executed protocol/manifest.

## Historical v0.4 admission and execution

Decision: **candidate_pending_validation** (2026-10-30). FALCON motor tracks provide official crossday interfaces and labels. Need exacttrack acquisition terms, trial/sessionnormalization, allowed adaptation and online/offline constraints. No data request attempted here. Same-session E01 cannot establish crossday BCIperformance.

[Source-linked admission evidence](../../../literature/admission-v04-behavior-population.json). This endpoint was not run in this release; absence is unknown, not zero or proof of poor data.

## Current admission and execution

Preview 0.11: measured. Source-specific rights/data/scorer checks and frozen model procedure completed for the explicit custom slice; no broader resource or current-SOTA claim.

[Admission/source evidence](../../../literature/admission-v05-bci.json). [Actual protocol/worklog](../../../experiments/G01). [Task measurements](../../../results/G01.json).
