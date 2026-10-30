# H16 — EEG ocular/muscle artifact repair

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** EEGdenoiseNet

**State:** not evaluated; candidate_pending_validation. Mapped resource only; license, acquisition, split, scorer and baseline gates are not yet all validated.

## Scientific use

Input: Curated EEG and artifact segments; synthetic mixtures

Target/ground truth: Curated clean reference under controlled synthetic contamination

Specialist candidates: Published artifact-denoising baselines

General-model route: General restoration/time-series model

## Execution and performance

No experiment admitted yet. All measurements are centralized in [results](../../../results/). Current best: **not verified**. Missing scores are unknown, not zero. Literature resources are not newly executed results.

## Limitations

Semi-synthetic clean signal is not pristine biological truth

## Sources

- [https://doi.org/10.1088/1741-2552/ac2bf8](https://doi.org/10.1088/1741-2552/ac2bf8)

## v0.4 admission and execution

Decision: **measured** (2026-10-30). Pinned original EEG/EOG pools and literal original RMS-ratio SNR convention; component-disjoint semisynthetic repair slice prepared with exact temporal RRMSE. Clean target is algorithmically cleaned/expert-inspected, not pristine physiology. Source participant IDs absent; no subject-generalization claim.

[Source-linked admission evidence](../../../literature/admission-v04-electrical.json). [Actual protocol and artifacts](../../../experiments/H16). [Central task results](../../../results/H16.json).

## v0.5 execution status

measured. Pinned original EEG/EOG pools and literal original RMS-ratio SNR convention; component-disjoint semisynthetic repair slice prepared with exact temporal RRMSE. Clean target is algorithmically cleaned/expert-inspected, not pristine physiology. Source participant IDs absent; no subject-generalization claim.

[Admission/source evidence](../../../literature/admission-v04-electrical.json). [Actual protocol/worklog](../../../experiments/H16). [Task measurements](../../../results/H16.json).
