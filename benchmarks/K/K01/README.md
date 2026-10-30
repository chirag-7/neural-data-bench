# K01 — Electrophysiological cell-type classification

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** Allen Cell Types / Patch-seq resources

**State:** not evaluated; candidate_pending_validation. Mapped resource only; license, acquisition, split, scorer and baseline gates are not yet all validated.

## Scientific use

Input: Patch clamp features, morphology, labels

Target/ground truth: Published cell taxonomy labels

Specialist candidates: Feature+RF/XGBoost; domain cell classifiers

General-model route: Tabular foundation model; multimodal embeddings

## Execution and performance

No experiment admitted yet. All measurements are centralized in [results](../../../results/). Current best: **not verified**. Missing scores are unknown, not zero. Literature resources are not newly executed results.

## Limitations

Taxonomy label uncertainty; donor and acquisition batch confounds

## Sources

- [https://brain-map.org/our-research/cell-types-taxonomies](https://brain-map.org/our-research/cell-types-taxonomies)
- [https://brain-map.org/support/documentation/documentation-cell-types-database](https://brain-map.org/support/documentation/documentation-cell-types-database)

## v0.4 admission and execution

Decision: **measured** (2026-10-30). Real primary API data acquired and hashed; independent morphology endpoint, ephys-only whitelist, donor-disjoint split and train-only baseline protocol frozen. Prepared n_train=1356 and n_test=457, 11 features; 678/226 disjoint mouse donors. Adapter ready for root model evaluation.

[Source-linked admission evidence](../../../literature/admission-v04-cell-workflow.json). [Actual protocol and artifacts](../../../experiments/K01). [Central task results](../../../results/K01.json).
