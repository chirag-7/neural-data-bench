# B01 — Spike sorting and event detection

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** SpikeForest available subset

**State:** not evaluated; candidate_pending_validation. Mapped resource only; license, acquisition, split, scorer and baseline gates are not yet all validated.

## Scientific use

Input: Raw extracellular voltage and probe geometry

Target/ground truth: Paired recordings and/or simulated known spikes

Specialist candidates: Kilosort4; DARTsort; other SpikeInterface sorters

General-model route: General signal model or coding agent

## Execution and performance

No experiment admitted yet. All measurements are centralized in [results](../../../results/). Current best: **not verified**. Missing scores are unknown, not zero. Literature resources are not newly executed results.

## Limitations

Current repo exposes subset; paired truth often only one neuron

## Sources

- [https://github.com/flatironinstitute/spikeforest](https://github.com/flatironinstitute/spikeforest)
- [https://elifesciences.org/articles/55167](https://elifesciences.org/articles/55167)
- [https://spikeinterface.readthedocs.io/en/stable/modules/benchmark.html](https://spikeinterface.readthedocs.io/en/stable/modules/benchmark.html)

## v0.4 admission and execution

Decision: **candidate_pending_validation** (2026-10-30). SpikeForest offers paired/curated groundtruth recordings, but exact accessible recording URI, agreement threshold, sorting scorer and matched sorter have not been acquired here. Do not claim hidden true neuron labels from ordinary extracellular recording.

[Source-linked admission evidence](../../../literature/admission-v04-behavior-population.json). This endpoint was not run in this release; absence is unknown, not zero or proof of poor data.

## v0.5 execution status

measured. Source-specific rights/data/scorer checks and frozen model procedure completed for the explicit custom slice; no broader resource or current-SOTA claim.

[Admission/source evidence](../../../literature/admission-v05-extracellular.json). [Actual protocol/worklog](../../../experiments/B01). [Task measurements](../../../results/B01.json).
