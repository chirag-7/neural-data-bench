# K05 — Bulk brain transcriptome cellular deconvolution

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** Human DLPFC multi-assay deconvolution benchmark / DeconvoBuddies

**State:** not evaluated; candidate_pending_validation. Mapped resource only; license, acquisition, split, scorer and baseline gates are not yet all validated.

## Scientific use

Input: Bulk RNA-seq, reference snRNA-seq and orthogonal RNAScope/IF fractions

Target/ground truth: Cell fractions estimated by orthogonal RNAScope/IF from matched tissue blocks

Specialist candidates: Six published algorithms including Bisque and hspe; reproduce exact reference/marker policy

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
