# K05 — Bulk brain transcriptome cellular deconvolution

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** Human DLPFC multi-assay deconvolution benchmark / DeconvoBuddies

**State:** candidate_pending_validation. Current status for this exact task-resource slice; current global best remains unverified.

## Scientific use

Input: Bulk RNA-seq, reference snRNA-seq and orthogonal RNAScope/IF fractions

Target/ground truth: Cell fractions estimated by orthogonal RNAScope/IF from matched tissue blocks

Mapped specialist candidates (not all evaluated): Six published algorithms including Bisque and hspe; reproduce exact reference/marker policy

General-model route: General constrained regression/tabular method; code agent

## Execution and performance

No experiment admitted yet. All measurements are centralized in [results](../../../results/). Current best: **not verified**. Missing scores are unknown, not zero. Literature resources are not newly executed results.

## Limitations

Adjacent-section proxy truth has measurement error; 110 RNA-seq samples do not imply 110 independent donors; same DLPFC resource family overlaps K04

## Sources

- [https://doi.org/10.1186/s13059-025-03552-3](https://doi.org/10.1186/s13059-025-03552-3)
- [https://pmc.ncbi.nlm.nih.gov/articles/PMC11978107/](https://pmc.ncbi.nlm.nih.gov/articles/PMC11978107/)
- [https://github.com/LieberInstitute/Human_DLPFC_Deconvolution](https://github.com/LieberInstitute/Human_DLPFC_Deconvolution)
- [https://research.libd.org/DeconvoBuddies/reference/fetch_deconvo_data.html](https://research.libd.org/DeconvoBuddies/reference/fetch_deconvo_data.html)

Source associations include historical alternatives; actual acquired files are identified in the executed protocol/manifest.

## Historical v0.4 admission and execution

Decision: **candidate_pending_validation** (2026-10-30). Primary DeconvoBuddies fetch documentation identifies bulk 110x21k (41 MB), snRNA 77kx36k (172 MB) and example 10kx557. Need match orthogonal IF/RNAScope fractions to bulk samples, donor/tissue blocks and fixed reference/marker policy. Bioconductor S4 readers absent and ground-truth alignment not completed. Data size itself is manageable; do not call impossible or bad.

[Source-linked admission evidence](../../../literature/admission-v04-cell-workflow.json). This endpoint was not run in this release; absence is unknown, not zero or proof of poor data.

## Current admission and execution

Preview 0.10: candidate_pending_validation. Primary DeconvoBuddies fetch documentation identifies bulk 110x21k (41 MB), snRNA 77kx36k (172 MB) and example 10kx557. Need match orthogonal IF/RNAScope fractions to bulk samples, donor/tissue blocks and fixed reference/marker policy. Bioconductor S4 readers absent and ground-truth alignment not completed. Data size itself is manageable; do not call impossible or bad.

[Admission/source evidence](../../../literature/admission-v04-cell-workflow.json).
