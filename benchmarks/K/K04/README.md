# K04 — Spatial cortical-domain assignment

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** Maynard2021 DLPFC HumanPilot; donor-held-out supervised layer transfer

**State:** measured. Current status for this exact task-resource slice; current global best remains unverified.

## Scientific use

Input: Prepared float32 log-normalized expression for 500 training-selected non-mitochondrial genes; no spatial coordinates or images

Target/ground truth: Curated L1–L6/white-matter annotations with expression and histology assistance; not fully orthogonal molecular truth

Mapped specialist candidates (not all evaluated): Published spatial clustering methods; simple non-spatial clustering baseline

General-model route: Generic tabular/spatial model or code-generated pipeline

## Execution and performance

**Executed slice:** HumanPilot DLPFC: 33,086 training spots from two donors/eight sections; 14,243 test spots from one donor/four sections; 500 training-selected genes.

[Frozen protocol and artifacts](../../../experiments/K04). [Measured scores and references](../../../results/K04.json). [Central data](../../../results/measurements.csv). Missing or failed outputs are retained.

## Limitations

Only one test donor; four sections are correlated. Curated labels use expression assistance, shared feature selection uses all outer-training spots, and no spatial context is supplied. Supervised transfer is not unsupervised spatial-domain discovery; global best unverified.

## Sources

- [https://research.libd.org/spatialLIBD/](https://research.libd.org/spatialLIBD/)
- [https://github.com/LieberInstitute/spatialLIBD](https://github.com/LieberInstitute/spatialLIBD)
- [https://doi.org/10.1038/s42003-024-07001-y](https://doi.org/10.1038/s42003-024-07001-y)
- [https://research.libd.org/spatialLIBD/reference/fetch_data.html](https://research.libd.org/spatialLIBD/reference/fetch_data.html)
- [https://raw.githubusercontent.com/LieberInstitute/spatialLIBD/master/R/fetch_data.R](https://raw.githubusercontent.com/LieberInstitute/spatialLIBD/master/R/fetch_data.R)
- [https://doi.org/10.1038/s41593-020-00787-0](https://doi.org/10.1038/s41593-020-00787-0)
- [https://github.com/LieberInstitute/HumanPilot/tree/044446d6bd8fc154aa74f7be62ec67effb1ec376](https://github.com/LieberInstitute/HumanPilot/tree/044446d6bd8fc154aa74f7be62ec67effb1ec376)
- [https://singler-inc.github.io/singler-py/api/singler.html](https://singler-inc.github.io/singler-py/api/singler.html)
- [https://github.com/SingleR-inc/singler-py](https://github.com/SingleR-inc/singler-py)

Source associations include historical alternatives; actual acquired files are identified in the executed protocol/manifest.

## Historical v0.4 admission and execution

Decision: **candidate_pending_validation** (2026-10-30). Primary spatialLIBD downloader and source located. Original study has three donors, adjacent sections must remain grouped. Local R 4.4.1 is present but SingleCellExperiment, SummarizedExperiment, ExperimentHub and spatialLIBD are absent. Data parsing/independent layer-label policy and spatial specialist scoring are not validated. Small examples/pseudobulks cannot silently stand in for held-out-donor spatial spot benchmark.

[Source-linked admission evidence](../../../literature/admission-v04-cell-workflow.json). This endpoint was not run in this release; absence is unknown, not zero or proof of poor data.

## Current admission and execution

Preview 0.8: measured. Source-specific rights/data/scorer checks and frozen model procedure completed for the explicit custom slice; no broader resource or current-SOTA claim.

[Admission/source evidence](../../../experiments/K04/protocol.md). [Actual protocol/worklog](../../../experiments/K04). [Task measurements](../../../results/K04.json).
