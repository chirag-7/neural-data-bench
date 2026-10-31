# H02 — ERP/P300 target decoding

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** Brain Invaders2012 v3 / Zenodo2649069; custom subject-held-out ERP diagnostic

**State:** measured. Current status for this exact task-resource slice; current global best remains unverified.

## Scientific use

Input: Stimulus-locked16channel EEG epochs,128Hz,0–1s afterflash; EEG only, groundFz removed

Target/ground truth: Original all-flash/target event markers; higher score denotes target

Mapped specialist candidates (not all evaluated): xDAWN/LDA; Riemannian classifier

General-model route: Generic signal encoder or agent

## Execution and performance

**Executed slice:** Brain Invaders2012 calibration runs: 15 training and10 held-out people; 11,481/7,663 epochs,16 EEG channels; equal-person ROC-AUC.

[Frozen protocol and artifacts](../../../experiments/H02). [Measured scores and references](../../../results/H02.json). [Central data](../../../results/measurements.csv). Missing or failed outputs are retained.

[Separate three-generation follow-up](../../../experiments/H02/replication-v1/results.md); repeated attempts are excluded from first-submission macro totals.

## Limitations

One public source/fixedIDsplit, offline filtering and overlapping trials. No cross-lab,online control,currentSOTA or matched-total-effort claim.

## Sources

- [https://moabb.neurotechx.com/](https://moabb.neurotechx.com/)
- [https://bnci-horizon-2020.eu/database/data-sets](https://bnci-horizon-2020.eu/database/data-sets)
- [https://moabb.neurotechx.com/docs/generated/moabb.datasets.BNCI2014_008.html](https://moabb.neurotechx.com/docs/generated/moabb.datasets.BNCI2014_008.html)
- [https://zenodo.org/records/2649069](https://zenodo.org/records/2649069)
- [https://arxiv.org/abs/1905.05182](https://arxiv.org/abs/1905.05182)
- [https://github.com/plcrodrigues/py.BI.EEG.2012-GIPSA](https://github.com/plcrodrigues/py.BI.EEG.2012-GIPSA)
- [https://pyriemann.readthedocs.io/en/latest/auto_examples/biosignal-erp/plot_classify_EEG_tangentspace.html](https://pyriemann.readthedocs.io/en/latest/auto_examples/biosignal-erp/plot_classify_EEG_tangentspace.html)

Source associations include historical alternatives; actual acquired files are identified in the executed protocol/manifest.

## Historical v0.4 admission and execution

Decision: **deferred** (2026-10-30). Screened BNCI2014_008 original BNCI terms (CC BY-NC-ND4.0) and MOABB loader/context. Data are real and useful, but derivative-array distribution and the exact cross-subject ERP preparation protocol have not been validated for this release. Alternate openly licensed ERP resources can be admitted later; no claim of bad quality.

[Source-linked admission evidence](../../../literature/admission-v04-electrical.json). This endpoint was not run in this release; absence is unknown, not zero or proof of poor data.

## Current admission and execution

Preview 0.9: measured. Source-specific rights/data/scorer checks and frozen model procedure completed for the explicit custom slice; no broader resource or current-SOTA claim.

[Admission/source evidence](../../../experiments/H02/protocol.md). [Actual protocol/worklog](../../../experiments/H02). [Task measurements](../../../results/H02.json).
