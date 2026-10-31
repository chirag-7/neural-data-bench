# K02 — Transcriptomic cell mapping and integration

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** Allen Brain Cell Atlas plus scIB evaluation tools

**State:** candidate_pending_validation. Current status for this exact task-resource slice; current global best remains unverified.

## Scientific use

Input: Brain scRNA/scATAC or spatial cell profiles

Target/ground truth: Reference taxonomy and biological annotations

Mapped specialist candidates (not all evaluated): scVI/scANVI; reference mapping; scIB baselines

General-model route: Generic tabular/gene-token model

## Execution and performance

No experiment admitted yet. All measurements are centralized in [results](../../../results/). Current best: **not verified**. Missing scores are unknown, not zero. Literature resources are not newly executed results.

## Limitations

Gene foundation models are domain-pretrained comparators; batch mixing alone is insufficient

## Sources

- [https://brain-map.org/our-research/cell-types-taxonomies](https://brain-map.org/our-research/cell-types-taxonomies)
- [https://scib.readthedocs.io/en/latest/](https://scib.readthedocs.io/en/latest/)

Source associations include historical alternatives; actual acquired files are identified in the executed protocol/manifest.

## Historical v0.4 admission and execution

Decision: **candidate_pending_validation** (2026-10-30). scIB is a general cell-integration toolkit, not one uniquely frozen brain dataset task. Need select brain donor cohorts/taxonomy and independent label-transfer policy, fit batch handling on allowed data, preserve rare classes, and reproduce biology AND mixing scorers. No unique dataset/split/rights package selected; do not inflate coverage from toolkit installation.

[Source-linked admission evidence](../../../literature/admission-v04-cell-workflow.json). This endpoint was not run in this release; absence is unknown, not zero or proof of poor data.

## Current admission and execution

Preview 0.9: candidate_pending_validation. scIB is a general cell-integration toolkit, not one uniquely frozen brain dataset task. Need select brain donor cohorts/taxonomy and independent label-transfer policy, fit batch handling on allowed data, preserve rare classes, and reproduce biology AND mixing scorers. No unique dataset/split/rights package selected; do not inflate coverage from toolkit installation.

[Admission/source evidence](../../../literature/admission-v04-cell-workflow.json).
