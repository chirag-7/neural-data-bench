# H16 — EEG ocular/muscle artifact repair

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** EEGdenoiseNet

**State:** measured. Current status for this exact task-resource slice; current global best remains unverified.

## Scientific use

Input: Curated EEG and artifact segments; synthetic mixtures

Target/ground truth: Curated clean reference under controlled synthetic contamination

Mapped specialist candidates (not all evaluated): Published artifact-denoising baselines

General-model route: General restoration/time-series model

## Execution and performance

**Executed slice:** EEGdenoiseNet: 2,000 training and 600 test clean-plus-EOG mixtures, with disjoint source components.

[Frozen protocol and artifacts](../../../experiments/H16). [Measured scores and references](../../../results/H16.json). [Central data](../../../results/measurements.csv). Missing or failed outputs are retained.

## Limitations

Semi-synthetic clean signal is not pristine biological truth

## Sources

- [https://doi.org/10.1088/1741-2552/ac2bf8](https://doi.org/10.1088/1741-2552/ac2bf8)
- [https://github.com/ncclabsustech/EEGdenoiseNet](https://github.com/ncclabsustech/EEGdenoiseNet)
- [https://arxiv.org/html/2009.11662v4](https://arxiv.org/html/2009.11662v4)
- [https://raw.githubusercontent.com/ncclabsustech/EEGdenoiseNet/master/LICENSE](https://raw.githubusercontent.com/ncclabsustech/EEGdenoiseNet/master/LICENSE)
- [https://raw.githubusercontent.com/ncclabsustech/EEGdenoiseNet/8d290661146c7189c98cc04812d37371d4b9426c/code/benchmark_networks/data_prepare.py](https://raw.githubusercontent.com/ncclabsustech/EEGdenoiseNet/8d290661146c7189c98cc04812d37371d4b9426c/code/benchmark_networks/data_prepare.py)

Source associations include historical alternatives; actual acquired files are identified in the executed protocol/manifest.

## Historical v0.4 admission and execution

Decision: **measured** (2026-10-30). Pinned original EEG/EOG pools and literal original RMS-ratio SNR convention; component-disjoint semisynthetic repair slice prepared with exact temporal RRMSE. Clean target is algorithmically cleaned/expert-inspected, not pristine physiology. Source participant IDs absent; no subject-generalization claim.

[Source-linked admission evidence](../../../literature/admission-v04-electrical.json). [Actual protocol and artifacts](../../../experiments/H16). [Central task results](../../../results/H16.json).

## Current admission and execution

Preview 0.10: measured. Pinned original EEG/EOG pools and literal original RMS-ratio SNR convention; component-disjoint semisynthetic repair slice prepared with exact temporal RRMSE. Clean target is algorithmically cleaned/expert-inspected, not pristine physiology. Source participant IDs absent; no subject-generalization claim.

[Admission/source evidence](../../../literature/admission-v04-electrical.json). [Actual protocol/worklog](../../../experiments/H16). [Task measurements](../../../results/H16.json).
