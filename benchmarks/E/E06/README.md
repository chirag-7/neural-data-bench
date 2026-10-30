# E06 — Whole-brain neural activity forecasting

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** ZAPBench (ICLR 2025)

**State:** not evaluated; candidate_pending_validation. Mapped resource only; license, acquisition, split, scorer and baseline gates are not yet all validated.

## Scientific use

Input: Larval zebrafish light-sheet volumes and extracted cellular traces

Target/ground truth: Future measured calcium activity

Specialist candidates: Published naive, time-series and volumetric video baselines

General-model route: General time-series/world/video models; code agents in separate track

## Execution and performance

No experiment admitted yet. All measurements are centralized in [results](../../../results/). Current best: **not verified**. Missing scores are unknown, not zero. Literature resources are not newly executed results.

## Limitations

One brain cannot establish cross-animal generalization; 70k neurons do not equal 70k independent subjects; anatomical pairing was future-facing in original paper

## Sources

- [https://google-research.github.io/zapbench/](https://google-research.github.io/zapbench/)
- [https://arxiv.org/abs/2503.02618](https://arxiv.org/abs/2503.02618)
- [https://zapbench-release.storage.googleapis.com/volumes/README.html](https://zapbench-release.storage.googleapis.com/volumes/README.html)
