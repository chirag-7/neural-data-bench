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

## v0.4 admission and execution

Decision: **measured** (2026-10-30). Root repository already contains measured Spikefinder preparation slices for all three Sol programs, predictions and archived references. This screening task did not rerun them; officialchallenge aggregate/currentSOTA remain distinct.

[Source-linked admission evidence](../../../literature/admission-v04-behavior-population.json). [Actual protocol and artifacts](../../../experiments/C05). [Central task results](../../../results/C05.json).

## v0.5 execution status

measured. Root repository already contains measured Spikefinder preparation slices for all three Sol programs, predictions and archived references. This screening task did not rerun them; officialchallenge aggregate/currentSOTA remain distinct.

[Admission/source evidence](../../../literature/admission-v04-behavior-population.json). [Actual protocol/worklog](../../../experiments/C05). [Task measurements](../../../results/C05.json).
