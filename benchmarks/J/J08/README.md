# J08 — Fluorescent synaptic puncta segmentation and quantification

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** SynAPSeg Zenodo18988899; 2D multi-rater instance-segmentation slice

**State:** measured. Current status for this exact task-resource slice; current global best remains unverified.

## Scientific use

Input: Normalized microscopy intensities and known training annotation ROI/geometry masks

Target/ground truth: Five independent human instance annotations per held-out field; no majority oracle

Mapped specialist candidates (not all evaluated): Published custom StarDist and Cellpose comparisons

General-model route: Generic microscopy/vision segmentation model; bounded code agent

## Execution and performance

**Executed slice:** SynAPSeg 2D puncta: 27 training fields yielding 1,262 crops; two held-out whole fields, five expert masks each; archived StarDist reference.

[Frozen protocol and artifacts](../../../experiments/J08). [Measured scores and references](../../../results/J08.json). [Central data](../../../results/measurements.csv). Missing or failed outputs are retained.

## Limitations

Only two testfields and unresolved animal identities. Archived StarDist optimization history differs; no inference timing or currentSOTAclaim.

## Sources

- [https://pmc.ncbi.nlm.nih.gov/articles/PMC13432752/](https://pmc.ncbi.nlm.nih.gov/articles/PMC13432752/)
- [https://github.com/pascalschamber/SynAPSeg](https://github.com/pascalschamber/SynAPSeg)
- [https://zenodo.org/records/18988899](https://zenodo.org/records/18988899)
- [https://doi.org/10.1371/journal.pcbi.1014571](https://doi.org/10.1371/journal.pcbi.1014571)

Source associations include historical alternatives; actual acquired files are identified in the executed protocol/manifest.

## Historical v0.4 admission and execution

Decision: **deferred** (2026-10-30). Dataset license unresolved in earlier mapping and only three fully held-out benchmark images with multiple raters. Code license does not resolve image-data terms. Do not redistribute or execute until authoritative dataset terms and scorer are verified.

[Source-linked admission evidence](../../../literature/admission-v04-behavior-population.json). This endpoint was not run in this release; absence is unknown, not zero or proof of poor data.

## Current admission and execution

Preview 0.8: measured. Source-specific rights/data/scorer checks and frozen model procedure completed for the explicit custom slice; no broader resource or current-SOTA claim.

[Admission/source evidence](../../../experiments/J08/protocol.md). [Actual protocol/worklog](../../../experiments/J08). [Task measurements](../../../results/J08.json).
