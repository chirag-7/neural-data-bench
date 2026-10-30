# B06 — Brain-region/probe localization from ephys

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** IBL Ephys Atlas feature release

**State:** not evaluated; candidate_pending_validation. Mapped resource only; license, acquisition, split, scorer and baseline gates are not yet all validated.

## Scientific use

Input: Channel features, waveforms, LFP and atlas labels

Target/ground truth: Histology-aligned region labels

Specialist candidates: Released XGBoost atlas decoder

General-model route: Tabular foundation model; generic features plus head

## Execution and performance

No experiment admitted yet. All measurements are centralized in [results](../../../results/). Current best: **not verified**. Missing scores are unknown, not zero. Literature resources are not newly executed results.

## Limitations

Histological alignment is uncertain; rare regions

## Sources

- [https://huggingface.co/int-brain-lab/ea-decoder-channel-xgboost](https://huggingface.co/int-brain-lab/ea-decoder-channel-xgboost)
