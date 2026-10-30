# M04 — Cognitive model and parameter recovery

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** Wilson–Collins modeling guide and example code

**State:** measured exploratory slice; measured. A frozen local protocol, data, scorer, predictions and baseline exist; limits are documented.

## Scientific use

Input: Synthetic choices from known behavioral models

Target/ground truth: Known simulated generating model and parameters

Specialist candidates: Known RL/DDM/bandit model fitted by established optimizer

General-model route: General code agent or sequence inference model

## Execution and performance

[Experiment protocol](../../../experiments/M04/protocol.md) All measurements are centralized in [results](../../../results/). Current best: **not verified; canonical local fitting baseline available**. Missing scores are unknown, not zero. Literature resources are not newly executed results.

## Limitations

Prediction alone does not establish identifiability

## Sources

- [https://elifesciences.org/articles/49547](https://elifesciences.org/articles/49547)
