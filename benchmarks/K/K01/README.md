# K01 — Electrophysiological cell-type classification

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** Allen Cell Types / Patch-seq resources

**State:** measured. Current status for this exact task-resource slice; current global best remains unverified.

## Scientific use

Input: Patch clamp features, morphology, labels

Target/ground truth: Published cell taxonomy labels

Mapped specialist candidates (not all evaluated): Feature+RF/XGBoost; domain cell classifiers

General-model route: Tabular foundation model; multimodal embeddings

## Execution and performance

**Executed slice:** Allen mouse electrophysiology: 11 features predict spiny/aspiny morphology; donor-disjoint 1,356 training and 457 test cells.

[Frozen protocol and artifacts](../../../experiments/K01). [Measured scores and references](../../../results/K01.json). [Central data](../../../results/measurements.csv). Missing or failed outputs are retained.

## Limitations

Taxonomy label uncertainty; donor and acquisition batch confounds

## Sources

- [https://brain-map.org/our-research/cell-types-taxonomies](https://brain-map.org/our-research/cell-types-taxonomies)
- [https://brain-map.org/support/documentation/documentation-cell-types-database](https://brain-map.org/support/documentation/documentation-cell-types-database)
- [https://brain-map.org/support/documentation/cell-types-database-api](https://brain-map.org/support/documentation/cell-types-database-api)
- [https://celltypes.brain-map.org/](https://celltypes.brain-map.org/)
- [https://alleninstitute.org/terms-of-use/](https://alleninstitute.org/terms-of-use/)

Source associations include historical alternatives; actual acquired files are identified in the executed protocol/manifest.

## Historical v0.4 admission and execution

Decision: **measured** (2026-10-30). Real primary API data acquired and hashed; independent morphology endpoint, ephys-only whitelist, donor-disjoint split and train-only baseline protocol frozen. Prepared n_train=1356 and n_test=457, 11 features; 678/226 disjoint mouse donors. Adapter ready for root model evaluation.

[Source-linked admission evidence](../../../literature/admission-v04-cell-workflow.json). [Actual protocol and artifacts](../../../experiments/K01). [Central task results](../../../results/K01.json).

## Current admission and execution

Preview 0.8: measured. Real primary API data acquired and hashed; independent morphology endpoint, ephys-only whitelist, donor-disjoint split and train-only baseline protocol frozen. Prepared n_train=1356 and n_test=457, 11 features; 678/226 disjoint mouse donors. Adapter ready for root model evaluation.

[Admission/source evidence](../../../literature/admission-v04-cell-workflow.json). [Actual protocol/worklog](../../../experiments/K01). [Task measurements](../../../results/K01.json).
