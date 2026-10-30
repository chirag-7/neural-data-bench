# C05 — Calcium-to-spike inference

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** Spikefinder

**State:** measured exploratory slice; measured. A frozen local protocol, data, scorer, predictions and baseline exist; limits are documented.

## Scientific use

Input: Fluorescence traces plus electrophysiology

Target/ground truth: Simultaneous electrophysiological spike recordings

Specialist candidates: OASIS; MLspike; published challenge models

General-model route: General time-series model; LLM-written estimator

## Execution and performance

[Experiment protocol](../../../experiments/C05/phase2-protocol.md) All measurements are centralized in [results](../../../results/). Current best: **not verified; archived same-slice and local default references available**. Missing scores are unknown, not zero. Literature resources are not newly executed results.

## Limitations

Published correlation is not millisecond spike-time accuracy

## Sources

- [https://github.com/codeneuro/spikefinder-datasets](https://github.com/codeneuro/spikefinder-datasets)
- [https://github.com/berenslab/spikefinder_analysis](https://github.com/berenslab/spikefinder_analysis)
