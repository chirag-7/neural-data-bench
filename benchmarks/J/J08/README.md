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
