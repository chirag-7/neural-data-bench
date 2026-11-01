# K05 — Bulk brain transcriptome cellular deconvolution

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** LieberInstitute orthogonal marker-fraction calibration

**State:** measured. Current status for this exact task-resource slice; current global best remains unverified.

## Scientific use

Input: 2,000 outer-training-selected log2(1+CPM) genes; equal donor/block metadata access

Target/ground truth: Orthogonal Circle GFAP/CLDN5/GAD1 positive-cell fractions with all Circle cells in denominator; targets do not sum to one

Mapped specialist candidates (not all evaluated): Six published algorithms including Bisque and hspe; reproduce exact reference/marker policy

General-model route: General constrained regression/tabular method; code agent

## Execution and performance

**Executed slice:** 63 eligible bulk samples: 39 train/24 test, five/three donors and seven/four blocks.

[Frozen protocol and artifacts](../../../experiments/K05). [Measured scores and references](../../../results/K05.json). [Central data](../../../results/measurements.csv). Missing or failed outputs are retained.

## Limitations

Supervised fraction calibration, not reference-only deconvolution; only three marker-defined fractions. Frozen protocol says gene identities supplied but actual numeric-only interface omits them equally from all methods. Conventional donor-CV ridge is not verified global best.

## Sources

- [https://doi.org/10.1186/s13059-025-03552-3](https://doi.org/10.1186/s13059-025-03552-3)
- [https://pmc.ncbi.nlm.nih.gov/articles/PMC11978107/](https://pmc.ncbi.nlm.nih.gov/articles/PMC11978107/)
- [https://github.com/LieberInstitute/Human_DLPFC_Deconvolution](https://github.com/LieberInstitute/Human_DLPFC_Deconvolution)
- [https://research.libd.org/DeconvoBuddies/reference/fetch_deconvo_data.html](https://research.libd.org/DeconvoBuddies/reference/fetch_deconvo_data.html)
- [https://zenodo.org/records/14969244](https://zenodo.org/records/14969244)

Source associations include historical alternatives; actual acquired files are identified in the executed protocol/manifest.

## Historical v0.4 admission and execution

Decision: **candidate_pending_validation** (2026-10-30). Primary DeconvoBuddies fetch documentation identifies bulk 110x21k (41 MB), snRNA 77kx36k (172 MB) and example 10kx557. Need match orthogonal IF/RNAScope fractions to bulk samples, donor/tissue blocks and fixed reference/marker policy. Bioconductor S4 readers absent and ground-truth alignment not completed. Data size itself is manageable; do not call impossible or bad.

[Source-linked admission evidence](../../../literature/admission-v04-cell-workflow.json). This endpoint was not run in this release; absence is unknown, not zero or proof of poor data.

## Current admission and execution

Preview 0.11: measured. Source-specific rights/data/scorer checks and frozen model procedure completed for the explicit custom slice; no broader resource or current-SOTA claim.

[Admission/source evidence](../../../experiments/K05/protocol.md). [Actual protocol/worklog](../../../experiments/K05). [Task measurements](../../../results/K05.json).

## Current specialists and repair sensitivity — 1 November 2026

[Current specialist review](../../../literature/specialist-review-2026-11-01/K05.json) · [Native version trajectories and practical interpretation](../../../analysis/practical-review-2026-11-01/report.md). The review distinguishes tested references from unexecuted newer candidates; no matched current global winner is certified.
