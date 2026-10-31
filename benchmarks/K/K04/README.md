# K04 — Spatial cortical-domain assignment

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** spatialLIBD DLPFC cortical-layer annotations

**State:** candidate_pending_validation. Current status for this exact task-resource slice; current global best remains unverified.

## Scientific use

Input: Human DLPFC Visium gene counts, spot positions and histology

Target/ground truth: Expert layer/white-matter annotation informed by cytoarchitecture and marker genes

Mapped specialist candidates (not all evaluated): Published spatial clustering methods; simple non-spatial clustering baseline

General-model route: Generic tabular/spatial model or code-generated pipeline

## Execution and performance

No experiment admitted yet. All measurements are centralized in [results](../../../results/). Current best: **not verified**. Missing scores are unknown, not zero. Literature resources are not newly executed results.

## Limitations

Only three original donors; labels partially derived from expression, limiting independence; specify whether histology is available to each method

## Sources

- [https://research.libd.org/spatialLIBD/](https://research.libd.org/spatialLIBD/)
- [https://github.com/LieberInstitute/spatialLIBD](https://github.com/LieberInstitute/spatialLIBD)
- [https://doi.org/10.1038/s42003-024-07001-y](https://doi.org/10.1038/s42003-024-07001-y)
- [https://research.libd.org/spatialLIBD/reference/fetch_data.html](https://research.libd.org/spatialLIBD/reference/fetch_data.html)
- [https://raw.githubusercontent.com/LieberInstitute/spatialLIBD/master/R/fetch_data.R](https://raw.githubusercontent.com/LieberInstitute/spatialLIBD/master/R/fetch_data.R)
- [https://doi.org/10.1038/s41593-020-00787-0](https://doi.org/10.1038/s41593-020-00787-0)

Source associations include historical alternatives; actual acquired files are identified in the executed protocol/manifest.

## Historical v0.4 admission and execution

Decision: **candidate_pending_validation** (2026-10-30). Primary spatialLIBD downloader and source located. Original study has three donors, adjacent sections must remain grouped. Local R 4.4.1 is present but SingleCellExperiment, SummarizedExperiment, ExperimentHub and spatialLIBD are absent. Data parsing/independent layer-label policy and spatial specialist scoring are not validated. Small examples/pseudobulks cannot silently stand in for held-out-donor spatial spot benchmark.

[Source-linked admission evidence](../../../literature/admission-v04-cell-workflow.json). This endpoint was not run in this release; absence is unknown, not zero or proof of poor data.

## Current admission and execution

Preview 0.6: candidate_pending_validation. Primary spatialLIBD downloader and source located. Original study has three donors, adjacent sections must remain grouped. Local R 4.4.1 is present but SingleCellExperiment, SummarizedExperiment, ExperimentHub and spatialLIBD are absent. Data parsing/independent layer-label policy and spatial specialist scoring are not validated. Small examples/pseudobulks cannot silently stand in for held-out-donor spatial spot benchmark.

[Admission/source evidence](../../../literature/admission-v04-cell-workflow.json).
