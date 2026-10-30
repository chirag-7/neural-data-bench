# J09 — Multiscale X-ray brain region and microstructure classification

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** MTNeuro

**State:** not evaluated; candidate_pending_validation. Mapped resource only; license, acquisition, split, scorer and baseline gates are not yet all validated.

## Scientific use

Input: Mouse brain X-ray microtomography with regional and pixel labels

Target/ground truth: Brain-region and cell/axon/vasculature labels

Specialist candidates: Published supervised and self-supervised 2D/3D baselines

General-model route: Generic vision embeddings/readout or 3D segmentation

## Execution and performance

No experiment admitted yet. All measurements are centralized in [results](../../../results/). Current best: **not verified**. Missing scores are unknown, not zero. Literature resources are not newly executed results.

## Limitations

Same underlying sample across endpoints; count shared dataset once for macro independence; X-ray contrasts differ from EM/fluorescence

## Sources

- [https://mtneuro.github.io/](https://mtneuro.github.io/)
- [https://github.com/MTNeuro/MTNeuro](https://github.com/MTNeuro/MTNeuro)

## v0.4 admission and execution

Decision: **candidate_pending_validation** (2026-10-30). MTNeuro released region/semantic labels and dataCC BY4.0 make it plausible. Need exact volume-block split and image-to-label adapter; no acquisition attempted here. Region and pixel tasks share samples and must not count as independent datasets.

[Source-linked admission evidence](../../../literature/admission-v04-behavior-population.json). This endpoint was not run in this release; absence is unknown, not zero or proof of poor data.

## v0.5 execution status

candidate_pending_validation. MTNeuro released region/semantic labels and dataCC BY4.0 make it plausible. Need exact volume-block split and image-to-label adapter; no acquisition attempted here. Region and pixel tasks share samples and must not count as independent datasets.

[Admission/source evidence](../../../literature/admission-v04-behavior-population.json).
