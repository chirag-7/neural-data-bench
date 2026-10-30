# K04 — Spatial cortical-domain assignment

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** spatialLIBD DLPFC cortical-layer annotations

**State:** not evaluated; candidate_pending_validation. Mapped resource only; license, acquisition, split, scorer and baseline gates are not yet all validated.

## Scientific use

Input: Human DLPFC Visium gene counts, spot positions and histology

Target/ground truth: Expert layer/white-matter annotation informed by cytoarchitecture and marker genes

Specialist candidates: Published spatial clustering methods; simple non-spatial clustering baseline

General-model route: Generic tabular/spatial model or code-generated pipeline

## Execution and performance

No experiment admitted yet. All measurements are centralized in [results](../../../results/). Current best: **not verified**. Missing scores are unknown, not zero. Literature resources are not newly executed results.

## Limitations

Only three original donors; labels partially derived from expression, limiting independence; specify whether histology is available to each method

## Sources

- [https://research.libd.org/spatialLIBD/](https://research.libd.org/spatialLIBD/)
- [https://github.com/LieberInstitute/spatialLIBD](https://github.com/LieberInstitute/spatialLIBD)
- [https://doi.org/10.1038/s42003-024-07001-y](https://doi.org/10.1038/s42003-024-07001-y)

## v0.4 admission and execution

Decision: **candidate_pending_validation** (2026-10-30). Primary spatialLIBD downloader and source located. Original study has three donors, adjacent sections must remain grouped. Local R 4.4.1 is present but SingleCellExperiment, SummarizedExperiment, ExperimentHub and spatialLIBD are absent. Data parsing/independent layer-label policy and spatial specialist scoring are not validated. Small examples/pseudobulks cannot silently stand in for held-out-donor spatial spot benchmark.

[Source-linked admission evidence](../../../literature/admission-v04-cell-workflow.json). This endpoint was not run in this release; absence is unknown, not zero or proof of poor data.
