# C04 — Calcium movie denoising

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** DeepCAD / DeepCAD-RT evaluation data

**State:** not evaluated; candidate_pending_validation. Mapped resource only; license, acquisition, split, scorer and baseline gates are not yet all validated.

## Scientific use

Input: Noisy fluorescence videos

Target/ground truth: Simulated clean reference or paired acquisition proxy

Specialist candidates: DeepCAD; PMD; conventional denoisers

General-model route: Generic video restoration model

## Execution and performance

No experiment admitted yet. All measurements are centralized in [results](../../../results/). Current best: **not verified**. Missing scores are unknown, not zero. Literature resources are not newly executed results.

## Limitations

Pleasing denoised movies can erase weak events

## Sources

- [https://github.com/cabooster/DeepCAD/blob/master/dataset/README.md](https://github.com/cabooster/DeepCAD/blob/master/dataset/README.md)
- [https://pmc.ncbi.nlm.nih.gov/articles/PMC8217135/](https://pmc.ncbi.nlm.nih.gov/articles/PMC8217135/)

## v0.4 admission and execution

Decision: **candidate_pending_validation** (2026-10-30). DeepCAD release offers real movies and trained denoisers, but a paired independent low-noise reference or declared self-supervised scorer is needed. Denoised outputs cannot silently become target truth. Movie/clean reference pair not acquired here.

[Source-linked admission evidence](../../../literature/admission-v04-behavior-population.json). This endpoint was not run in this release; absence is unknown, not zero or proof of poor data.
