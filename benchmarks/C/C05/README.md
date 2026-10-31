# C05 — Calcium-to-spike inference

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** Spikefinder

**State:** measured. Current status for this exact task-resource slice; current global best remains unverified.

## Scientific use

Input: Fluorescence traces plus electrophysiology

Target/ground truth: Simultaneous electrophysiological spike recordings

Mapped specialist candidates (not all evaluated): OASIS; MLspike; published challenge models

General-model route: General time-series model; LLM-written estimator

## Execution and performance

**Executed slice:** Spikefinder: calcium-to-spike inference on five preparations; median 40 ms correlation per preparation.

[Frozen protocol and artifacts](../../../experiments/C05). [Measured scores and references](../../../results/C05.json). [Central data](../../../results/measurements.csv). Missing or failed outputs are retained.

## Limitations

Published correlation is not millisecond spike-time accuracy

## Sources

- [https://github.com/codeneuro/spikefinder-datasets](https://github.com/codeneuro/spikefinder-datasets)
- [https://github.com/berenslab/spikefinder_analysis](https://github.com/berenslab/spikefinder_analysis)

Source associations include historical alternatives; actual acquired files are identified in the executed protocol/manifest.

## Historical v0.4 admission and execution

Decision: **measured** (2026-10-30). Root repository already contains measured Spikefinder preparation slices for all three Sol programs, predictions and archived references. This screening task did not rerun them; officialchallenge aggregate/currentSOTA remain distinct.

[Source-linked admission evidence](../../../literature/admission-v04-behavior-population.json). [Actual protocol and artifacts](../../../experiments/C05). [Central task results](../../../results/C05.json).

## Current admission and execution

Preview 0.9: measured. Root repository already contains measured Spikefinder preparation slices for all three Sol programs, predictions and archived references. This screening task did not rerun them; officialchallenge aggregate/currentSOTA remain distinct.

[Admission/source evidence](../../../literature/admission-v04-behavior-population.json). [Actual protocol/worklog](../../../experiments/C05). [Task measurements](../../../results/C05.json).
