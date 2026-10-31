# K06 — Extracellular cell-type inference from ground-truth cell metrics

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** CellExplorer ground-truth cell metrics

**State:** candidate_pending_validation. Current status for this exact task-resource slice; current global best remains unverified.

## Scientific use

Input: Waveform/firing metrics and optotagged/identified cell classes

Target/ground truth: Curated PV, SST, pyramidal, axo-axonic, VGAT and VIP identities

Mapped specialist candidates (not all evaluated): CellExplorer feature-based classification; declared supervised baseline

General-model route: Generic tabular estimator or code agent

## Execution and performance

No experiment admitted yet. All measurements are centralized in [results](../../../results/). Current best: **not verified**. Missing scores are unknown, not zero. Literature resources are not newly executed results.

## Limitations

Optotagging can include indirect responses; class labels are uneven and partly nested; small class counts and uncertain raw-data provenance need inspection

## Sources

- [https://cellexplorer.org/publicdata/ground-truth-data/](https://cellexplorer.org/publicdata/ground-truth-data/)
- [https://cellexplorer.org/tutorials/ground-truth-tutorial/](https://cellexplorer.org/tutorials/ground-truth-tutorial/)
- [https://alleninstitute.github.io/openscope_databook/optotagging/](https://alleninstitute.github.io/openscope_databook/optotagging/)
- [https://api.github.com/repos/petersenpeter/CellExplorer/contents/%2BgroundTruthData](https://api.github.com/repos/petersenpeter/CellExplorer/contents/%2BgroundTruthData)

Source associations include historical alternatives; actual acquired files are identified in the executed protocol/manifest.

## Historical v0.4 admission and execution

Decision: **candidate_pending_validation** (2026-10-30). Primary ground-truth tutorial and GitHub folder inspected; 87 files total ~500 MB. Downloaded one 189 kB cell metrics example and consolidated 2.83 MB gt list; MATLAB v7.3 HDF5 parsed with isolated h5py3.15.1. Consolidated list has 430 entries and animal/session/truth labels, but no predictor feature matrix; example has Juxta tag (not a molecular cell class). Must select nonnested independently tagged classes, extract only scalar physiology/waveform metrics from session files, group animals, resolve contributor data terms, and exclude putativeCellType/geneticLine/brainRegion proxies. No validated table yet.

[Source-linked admission evidence](../../../literature/admission-v04-cell-workflow.json). This endpoint was not run in this release; absence is unknown, not zero or proof of poor data.

## Current admission and execution

Preview 0.10: candidate_pending_validation. Primary ground-truth tutorial and GitHub folder inspected; 87 files total ~500 MB. Downloaded one 189 kB cell metrics example and consolidated 2.83 MB gt list; MATLAB v7.3 HDF5 parsed with isolated h5py3.15.1. Consolidated list has 430 entries and animal/session/truth labels, but no predictor feature matrix; example has Juxta tag (not a molecular cell class). Must select nonnested independently tagged classes, extract only scalar physiology/waveform metrics from session files, group animals, resolve contributor data terms, and exclude putativeCellType/geneticLine/brainRegion proxies. No validated table yet.

[Admission/source evidence](../../../literature/admission-v04-cell-workflow.json).
