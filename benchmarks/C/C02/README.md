# C02 — Activity extraction and demixing

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** CaImAn annotated nine-dataset corpus

**State:** not evaluated; candidate_pending_validation. Mapped resource only; license, acquisition, split, scorer and baseline gates are not yet all validated.

## Scientific use

Input: Two-photon calcium movies

Target/ground truth: Consensus ROI annotations; not full true activity

Specialist candidates: CNMF/CaImAn; Suite2p

General-model route: General image/video source separation

## Execution and performance

No experiment admitted yet. All measurements are centralized in [results](../../../results/). Current best: **not verified**. Missing scores are unknown, not zero. Literature resources are not newly executed results.

## Limitations

Human masks do not establish correct recovered time courses

## Sources

- [https://pmc.ncbi.nlm.nih.gov/articles/PMC6342523/](https://pmc.ncbi.nlm.nih.gov/articles/PMC6342523/)

## v0.4 admission and execution

Decision: **candidate_pending_validation** (2026-10-30). CaImAn annotated data can support ROI/timecourse evaluation but labels and quality annotations are incomplete; must pin exact nine-dataset release and per-endpoint valid annotations. No movies acquired here; neuron masks alone do not establish full demixing groundtruth.

[Source-linked admission evidence](../../../literature/admission-v04-behavior-population.json). This endpoint was not run in this release; absence is unknown, not zero or proof of poor data.

## v0.5 execution status

candidate_pending_validation. CaImAn annotated data can support ROI/timecourse evaluation but labels and quality annotations are incomplete; must pin exact nine-dataset release and per-endpoint valid annotations. No movies acquired here; neuron masks alone do not establish full demixing groundtruth.

[Admission/source evidence](../../../literature/admission-v04-behavior-population.json).
