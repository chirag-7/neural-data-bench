# K06 — Extracellular cell-type inference from ground-truth cell metrics

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** CellExplorer ground-truth cell metrics

**State:** not evaluated; candidate_pending_validation. Mapped resource only; license, acquisition, split, scorer and baseline gates are not yet all validated.

## Scientific use

Input: Waveform/firing metrics and optotagged/identified cell classes

Target/ground truth: Curated PV, SST, pyramidal, axo-axonic, VGAT and VIP identities

Specialist candidates: CellExplorer feature-based classification; declared supervised baseline

General-model route: Generic tabular estimator or code agent

## Execution and performance

No experiment admitted yet. All measurements are centralized in [results](../../../results/). Current best: **not verified**. Missing scores are unknown, not zero. Literature resources are not newly executed results.

## Limitations

Optotagging can include indirect responses; class labels are uneven and partly nested; small class counts and uncertain raw-data provenance need inspection

## Sources

- [https://cellexplorer.org/publicdata/ground-truth-data/](https://cellexplorer.org/publicdata/ground-truth-data/)
- [https://cellexplorer.org/tutorials/ground-truth-tutorial/](https://cellexplorer.org/tutorials/ground-truth-tutorial/)
- [https://alleninstitute.github.io/openscope_databook/optotagging/](https://alleninstitute.github.io/openscope_databook/optotagging/)
