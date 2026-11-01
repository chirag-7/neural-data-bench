# K06 — Extracellular cell-type inference from ground-truth cell metrics

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** Allen-contributed optotagged cells; mouse-held-out waveform classification

**State:** measured. Current status for this exact task-resource slice; current global best remains unverified.

## Scientific use

Input: 87 waveform-only features; genetic IDs, anatomical region, firing/ISI/ACG and optoresponses excluded

Target/ground truth: Optotagged PV/SST labels independently joined to original cell IDs

Mapped specialist candidates (not all evaluated): CellExplorer feature-based classification; declared supervised baseline

General-model route: Generic tabular estimator or code agent

## Execution and performance

**Executed slice:** 207 cells from 16 mice: 136 train/11 mice, 71 test/five mice.

[Frozen protocol and artifacts](../../../experiments/K06). [Measured scores and references](../../../results/K06.json). [Central data](../../../results/measurements.csv). Missing or failed outputs are retained.

## Limitations

Binary classes and one contributor; genetic class is mouse-level and cohort effects may confound. Not comprehensive cell taxonomy. Research/noncommercial source terms retained; fixed SVM/ExtraTrees CV is conventional reference, not established neuroscience SOTA.

## Sources

- [https://cellexplorer.org/publicdata/ground-truth-data/](https://cellexplorer.org/publicdata/ground-truth-data/)
- [https://cellexplorer.org/tutorials/ground-truth-tutorial/](https://cellexplorer.org/tutorials/ground-truth-tutorial/)
- [https://alleninstitute.github.io/openscope_databook/optotagging/](https://alleninstitute.github.io/openscope_databook/optotagging/)
- [https://api.github.com/repos/petersenpeter/CellExplorer/contents/%2BgroundTruthData](https://api.github.com/repos/petersenpeter/CellExplorer/contents/%2BgroundTruthData)
- [https://doi.org/10.1016/j.neuron.2021.09.002](https://doi.org/10.1016/j.neuron.2021.09.002)
- [https://github.com/petersenpeter/CellExplorer](https://github.com/petersenpeter/CellExplorer)
- [https://alleninstitute.org/legal/terms-of-use](https://alleninstitute.org/legal/terms-of-use)

Source associations include historical alternatives; actual acquired files are identified in the executed protocol/manifest.

## Historical v0.4 admission and execution

Decision: **candidate_pending_validation** (2026-10-30). Primary ground-truth tutorial and GitHub folder inspected; 87 files total ~500 MB. Downloaded one 189 kB cell metrics example and consolidated 2.83 MB gt list; MATLAB v7.3 HDF5 parsed with isolated h5py3.15.1. Consolidated list has 430 entries and animal/session/truth labels, but no predictor feature matrix; example has Juxta tag (not a molecular cell class). Must select nonnested independently tagged classes, extract only scalar physiology/waveform metrics from session files, group animals, resolve contributor data terms, and exclude putativeCellType/geneticLine/brainRegion proxies. No validated table yet.

[Source-linked admission evidence](../../../literature/admission-v04-cell-workflow.json). This endpoint was not run in this release; absence is unknown, not zero or proof of poor data.

## Current admission and execution

Preview 0.11: measured. Source-specific rights/data/scorer checks and frozen model procedure completed for the explicit custom slice; no broader resource or current-SOTA claim.

[Admission/source evidence](../../../experiments/K06/protocol.md). [Actual protocol/worklog](../../../experiments/K06). [Task measurements](../../../results/K06.json).

## Current specialists and repair sensitivity — 1 November 2026

[Current specialist review](../../../literature/specialist-review-2026-11-01/K06.json) · [Native version trajectories and practical interpretation](../../../analysis/practical-review-2026-11-01/report.md). The review distinguishes tested references from unexecuted newer candidates; no matched current global winner is certified.
