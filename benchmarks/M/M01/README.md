# M01 — Behavioral decision-model fitting

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** IBL Dec2019 behavior archive / Figshare11636748; custom mouse-held-out slice

**State:** measured. Current status for this exact task-resource slice; current global best remains unverified.

## Scientific use

Input: Current contrasts/known experimenter block prior plus five past choice/feedback lags;13 features, no current/future response fields

Target/ground truth: Recorded binary mouse turn choices, not latent cognitive parameter labels

Mapped specialist candidates (not all evaluated): Psychometric/logistic/RL models; Centaur as domain comparator

General-model route: General language/sequence models

## Execution and performance

**Executed slice:** IBL Dec2019 choice data: all100 source mice, 83 train/17 held-out; 7,696/1,842 nonoverlapping conditional examples from latest archived sessions.

[Frozen protocol and artifacts](../../../experiments/M01). [Measured scores and references](../../../results/M01.json). [Central data](../../../results/measurements.csv). Missing or failed outputs are retained.

## Limitations

Conditional one-step forecast with observed history and known block prior; no autonomous rollout or held-out-lab claim. One historical beta-quality archive; prior target choices never reappear in another scored input. Paper-inspired pooled GLM is not original peranimal fits or established global best.

## Sources

- [https://www.internationalbrainlab.com/data](https://www.internationalbrainlab.com/data)
- [https://www.nature.com/articles/s41586-025-09215-4](https://www.nature.com/articles/s41586-025-09215-4)
- [https://figshare.com/articles/dataset/11636748](https://figshare.com/articles/dataset/11636748)
- [https://api.figshare.com/v2/articles/11636748](https://api.figshare.com/v2/articles/11636748)
- [https://elifesciences.org/articles/63711](https://elifesciences.org/articles/63711)
- [https://github.com/int-brain-lab/paper-behavior/blob/24b094226a84c8609c97cfd36c8387ea7c5d61e0/figure5_GLM_modelfit.py](https://github.com/int-brain-lab/paper-behavior/blob/24b094226a84c8609c97cfd36c8387ea7c5d61e0/figure5_GLM_modelfit.py)

Source associations include historical alternatives; actual acquired files are identified in the executed protocol/manifest.

## Historical v0.4 admission and execution

Decision: **candidate_pending_validation** (2026-10-30). IBL data and Psych-101/Centaur primary resource mapped. Real choice prediction requires participant/animal-held-out chronology, a bounded task selection and data-specific terms; M04 synthetic parameter recovery does not complete this endpoint.

[Source-linked admission evidence](../../../literature/admission-v04-inference-control.json). This endpoint was not run in this release; absence is unknown, not zero or proof of poor data.

## Current admission and execution

Preview 0.9: measured. Source-specific rights/data/scorer checks and frozen model procedure completed for the explicit custom slice; no broader resource or current-SOTA claim.

[Admission/source evidence](../../../experiments/M01/protocol.md). [Actual protocol/worklog](../../../experiments/M01). [Task measurements](../../../results/M01.json).
