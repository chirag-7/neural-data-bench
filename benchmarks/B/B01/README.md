# B01 — Spike sorting and event detection

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** Standard SpikeInterface/MEArec fixture; MountainSort5 reference

**State:** measured. Current status for this exact task-resource slice; current global best remains unverified.

## Scientific use

Input: Simulated filtered extracellular voltage32kHz,32channels; hidden generated spike events

Target/ground truth: Known simulation spike events and neuron IDs; not paired biological truth

Mapped specialist candidates (not all evaluated): Kilosort4; DARTsort; other SpikeInterface sorters

General-model route: General signal model or coding agent

## Execution and performance

**Executed slice:** Blind unsupervised spike sorting of one 10-second, 32-channel stationary MEArec simulation; official unit/event matching.

[Frozen protocol and artifacts](../../../experiments/B01). [Measured scores and references](../../../results/B01.json). [Central data](../../../results/measurements.csv). Missing or failed outputs are retained.

## Limitations

Short stationary public simulation, no drift/real paired/animal generalization. Extra unit diagnostics required.

## Sources

- [https://github.com/flatironinstitute/spikeforest](https://github.com/flatironinstitute/spikeforest)
- [https://elifesciences.org/articles/55167](https://elifesciences.org/articles/55167)
- [https://spikeinterface.readthedocs.io/en/stable/modules/benchmark.html](https://spikeinterface.readthedocs.io/en/stable/modules/benchmark.html)
- [https://gin.g-node.org/NeuralEnsemble/ephy_testing_data](https://gin.g-node.org/NeuralEnsemble/ephy_testing_data)
- [https://spikeinterface.readthedocs.io/en/0.96.1/modules/comparison/plot_3_compare_sorter_with_ground_truth.html](https://spikeinterface.readthedocs.io/en/0.96.1/modules/comparison/plot_3_compare_sorter_with_ground_truth.html)
- [https://github.com/flatironinstitute/mountainsort5](https://github.com/flatironinstitute/mountainsort5)

Source associations include historical alternatives; actual acquired files are identified in the executed protocol/manifest.

## Historical v0.4 admission and execution

Decision: **candidate_pending_validation** (2026-10-30). SpikeForest offers paired/curated groundtruth recordings, but exact accessible recording URI, agreement threshold, sorting scorer and matched sorter have not been acquired here. Do not claim hidden true neuron labels from ordinary extracellular recording.

[Source-linked admission evidence](../../../literature/admission-v04-behavior-population.json). This endpoint was not run in this release; absence is unknown, not zero or proof of poor data.

## Current admission and execution

Preview 0.8: measured. Source-specific rights/data/scorer checks and frozen model procedure completed for the explicit custom slice; no broader resource or current-SOTA claim.

[Admission/source evidence](../../../literature/admission-v05-extracellular.json). [Actual protocol/worklog](../../../experiments/B01). [Task measurements](../../../results/B01.json).
