# H01 — Motor imagery and noninvasive BCI

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** MOABB motor imagery datasets

**State:** measured. Current status for this exact task-resource slice; current global best remains unverified.

## Scientific use

Input: EEG epochs, montage and labels

Target/ground truth: Task labels

Mapped specialist candidates (not all evaluated): CSP+LDA; Riemannian methods; EEGNet

General-model route: Generic time-series model; coding agent

## Execution and performance

**Executed slice:** PhysioNet motor imagery: five training and three held-out people; 225 training and 135 test epochs.

[Frozen protocol and artifacts](../../../experiments/H01). [Measured scores and references](../../../results/H01.json). [Central data](../../../results/measurements.csv). Missing or failed outputs are retained.

## Limitations

Random epoch splits inflate subject generalization

## Sources

- [https://moabb.neurotechx.com/](https://moabb.neurotechx.com/)
- [https://physionet.org/content/eegmmidb/1.0.0/](https://physionet.org/content/eegmmidb/1.0.0/)
- [https://physionet.org/files/eegmmidb/1.0.0/S001/](https://physionet.org/files/eegmmidb/1.0.0/S001/)
- [https://moabb.neurotechx.com/docs/generated/moabb.datasets.PhysionetMI.html](https://moabb.neurotechx.com/docs/generated/moabb.datasets.PhysionetMI.html)
- [https://mne.tools/stable/auto_examples/decoding/decoding_csp_eeg.html](https://mne.tools/stable/auto_examples/decoding/decoding_csp_eeg.html)

Source associations include historical alternatives; actual acquired files are identified in the executed protocol/manifest.

## Historical v0.4 admission and execution

Decision: **measured** (2026-10-30). Real public PhysioNet EEGMMI EDF files acquired and validated; fixed subject-disjoint MI slice prepared. This admits one explicitly scoped slice, not the whole MOABB umbrella.

[Source-linked admission evidence](../../../literature/admission-v04-electrical.json). [Actual protocol and artifacts](../../../experiments/H01). [Central task results](../../../results/H01.json).

## Current admission and execution

Preview 0.11: measured. Real public PhysioNet EEGMMI EDF files acquired and validated; fixed subject-disjoint MI slice prepared. This admits one explicitly scoped slice, not the whole MOABB umbrella.

[Admission/source evidence](../../../literature/admission-v04-electrical.json). [Actual protocol/worklog](../../../experiments/H01). [Task measurements](../../../results/H01.json).

## Current specialists and repair sensitivity — 1 November 2026

[Current specialist review](../../../literature/specialist-review-2026-11-01/H01.json) · [Native version trajectories and practical interpretation](../../../analysis/practical-review-2026-11-01/report.md). The review distinguishes tested references from unexecuted newer candidates; no matched current global winner is certified.
