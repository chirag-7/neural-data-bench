# J08 — Fluorescent synaptic puncta segmentation and quantification

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** SynAPSeg training and multi-rater benchmark datasets

**State:** not evaluated; deferred. Current release excludes execution: new research construction, uncertain release/rights, or setup outside lightweight budget.

## Scientific use

Input: 2D/3D confocal synaptic marker images

Target/ground truth: Pixel-wise instance annotations; five raters for three held-out benchmark images

Specialist candidates: Published custom StarDist and Cellpose comparisons

General-model route: Generic microscopy/vision segmentation model; bounded code agent

## Execution and performance

No experiment admitted yet. All measurements are centralized in [results](../../../results/). Current best: **not verified**. Missing scores are unknown, not zero. Literature resources are not newly executed results.

## Limitations

Tiny benchmark image count limits independent sampling; synaptic puncta are marker-based proxies for synapses; data license field was not resolved in rendered record

## Sources

- [https://pmc.ncbi.nlm.nih.gov/articles/PMC13432752/](https://pmc.ncbi.nlm.nih.gov/articles/PMC13432752/)
- [https://github.com/pascalschamber/SynAPSeg](https://github.com/pascalschamber/SynAPSeg)
- [https://zenodo.org/records/18988899](https://zenodo.org/records/18988899)

## v0.4 admission and execution

Decision: **deferred** (2026-10-30). Dataset license unresolved in earlier mapping and only three fully held-out benchmark images with multiple raters. Code license does not resolve image-data terms. Do not redistribute or execute until authoritative dataset terms and scorer are verified.

[Source-linked admission evidence](../../../literature/admission-v04-behavior-population.json). This endpoint was not run in this release; absence is unknown, not zero or proof of poor data.

## v0.5 execution status

measured. Source-specific rights/data/scorer checks and frozen model procedure completed for the explicit custom slice; no broader resource or current-SOTA claim.

[Admission/source evidence](../../../experiments/J08/protocol.md). [Actual protocol/worklog](../../../experiments/J08). [Task measurements](../../../results/J08.json).
