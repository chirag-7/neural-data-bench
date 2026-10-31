# I07 — fNIRS motor/hemodynamic decoding

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** FRESH Motor dataset

**State:** measured. Current status for this exact task-resource slice; current global best remains unverified.

## Scientific use

Input: Optical hemodynamic time series and task events

Target/ground truth: Experimental event labels

Mapped specialist candidates (not all evaluated): GLM; linear classifier; fNIRS pipeline

General-model route: General time-series model

## Execution and performance

**Executed slice:** FRESH optical-density tapping classification: seven training and three test people; condition and session remain confounded.

[Frozen protocol and artifacts](../../../experiments/I07). [Measured scores and references](../../../results/I07.json). [Central data](../../../results/measurements.csv). Missing or failed outputs are retained.

## Limitations

Needs benchmark wrapper; hemodynamic lag and motion confounding

## Sources

- [https://www.nemar.org/dataset/on005963](https://www.nemar.org/dataset/on005963)
- [https://openfnirs.org/community/fresh/welcome-to-the-fnirs-fresh-project/](https://openfnirs.org/community/fresh/welcome-to-the-fnirs-fresh-project/)
- [https://data.nemar.org/on005963/v1.0.0/dataset_description.json](https://data.nemar.org/on005963/v1.0.0/dataset_description.json)
- [https://data.nemar.org/on005963/v1.0.0/manifest.json](https://data.nemar.org/on005963/v1.0.0/manifest.json)
- [https://data.nemar.org/on005963/v1.0.0/code/validation.ipynb](https://data.nemar.org/on005963/v1.0.0/code/validation.ipynb)
- [https://openneuro.org/datasets/ds005963/versions/1.0.0](https://openneuro.org/datasets/ds005963/versions/1.0.0)
- [https://doi.org/10.1038/s42003-025-08412-1](https://doi.org/10.1038/s42003-025-08412-1)

Source associations include historical alternatives; actual acquired files are identified in the executed protocol/manifest.

## Historical v0.4 admission and execution

Decision: **measured** (2026-10-30). Original FRESH organizer description resolves left/right2s finger tapping. CC0 versioned SNIRF data acquired/prepared with subject-disjoint2s condition decoding and optical-density conversion; explicit session/condition confounding, no Hb or cortical-activation gold-standard claim.

[Source-linked admission evidence](../../../literature/admission-v04-electrical.json). [Actual protocol and artifacts](../../../experiments/I07). [Central task results](../../../results/I07.json).

## Current admission and execution

Preview 0.11: measured. Original FRESH organizer description resolves left/right2s finger tapping. CC0 versioned SNIRF data acquired/prepared with subject-disjoint2s condition decoding and optical-density conversion; explicit session/condition confounding, no Hb or cortical-activation gold-standard claim.

[Admission/source evidence](../../../literature/admission-v04-electrical.json). [Actual protocol/worklog](../../../experiments/I07). [Task measurements](../../../results/I07.json).
