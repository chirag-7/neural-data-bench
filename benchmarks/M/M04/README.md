# M04 — Cognitive model and parameter recovery

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** Wilson–Collins modeling guide and example code

**State:** measured. Current status for this exact task-resource slice; current global best remains unverified.

## Scientific use

Input: Synthetic choices from known behavioral models

Target/ground truth: Known simulated generating model and parameters

Mapped specialist candidates (not all evaluated): Known RL/DDM/bandit model fitted by established optimizer

General-model route: General code agent or sequence inference model

## Execution and performance

**Executed slice:** Synthetic two-choice Q-learning agents: recover learning rate and inverse temperature from choices and rewards.

[Frozen protocol and artifacts](../../../experiments/M04). [Measured scores and references](../../../results/M04.json). [Central data](../../../results/measurements.csv). Missing or failed outputs are retained.

## Limitations

Prediction alone does not establish identifiability

## Sources

- [https://elifesciences.org/articles/49547](https://elifesciences.org/articles/49547)

Source associations include historical alternatives; actual acquired files are identified in the executed protocol/manifest.

## Historical v0.4 admission and execution

Decision: **measured** (2026-10-30). Previously measured24agent synthetic Q-learning recovery. Author guide supports recovery checks; local implementation and posterior-vs-MLE objective difference explicit. Not biological data or a released leaderboard.

[Source-linked admission evidence](../../../literature/admission-v04-inference-control.json). [Actual protocol and artifacts](../../../experiments/M04). [Central task results](../../../results/M04.json).

## Current admission and execution

Preview 0.8: measured. Previously measured24agent synthetic Q-learning recovery. Author guide supports recovery checks; local implementation and posterior-vs-MLE objective difference explicit. Not biological data or a released leaderboard.

[Admission/source evidence](../../../literature/admission-v04-inference-control.json). [Actual protocol/worklog](../../../experiments/M04). [Task measurements](../../../results/M04.json).
