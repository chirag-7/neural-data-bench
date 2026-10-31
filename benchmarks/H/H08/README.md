# H08 — Sleep staging and sleep onset

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** Sleep-EDF Expanded1.0.0; custom subject-held-out diagnostic with YASA checkpoint

**State:** measured. Current status for this exact task-resource slice; current global best remains unverified.

## Scientific use

Input: Raw EEG Fpz-Cz,1440consecutive30second epochs/night

Target/ground truth: Independent technician R&K stages; stages3/4merged,unknown/movement excluded

Mapped specialist candidates (not all evaluated): Sleep-specific model; EEGNet where appropriate

General-model route: General sequence model

## Execution and performance

**Executed slice:** Sleep-EDF first nights, fixed 20:00–08:00 windows: five training and three held-out people; 100 Hz Fpz-Cz EEG, five sleep stages.

[Frozen protocol and artifacts](../../../experiments/H08). [Measured scores and references](../../../results/H08.json). [Central data](../../../results/measurements.csv). Missing or failed outputs are retained.

## Limitations

Three testpeople;singlederivation;customclockwindow not officialSleepEDF20protocol;YASANSRRpretraining differs from five targettrainingnights.

## Sources

- [https://facebookresearch.github.io/neuroai/neuralbench/index.html](https://facebookresearch.github.io/neuroai/neuralbench/index.html)
- [https://neural-interfaces26.github.io/](https://neural-interfaces26.github.io/)
- [https://physionet.org/content/sleep-edfx/1.0.0/](https://physionet.org/content/sleep-edfx/1.0.0/)
- [https://doi.org/10.13026/C2X676](https://doi.org/10.13026/C2X676)
- [https://doi.org/10.7554/eLife.70092](https://doi.org/10.7554/eLife.70092)
- [https://github.com/raphaelvallat/yasa_classifier](https://github.com/raphaelvallat/yasa_classifier)

Source associations include historical alternatives; actual acquired files are identified in the executed protocol/manifest.

## Historical v0.4 admission and execution

Decision: **deferred** (2026-10-30). NeuralBench/challenge primary sites accessible. 2026 challenge final phase starts in November after this review date, so no final winner exists yet. Need a pinned accessible sleep dataset, subject/night-disjoint scorer, full-context policy and expert staging labels; no adjacent-epoch shortcut experiment admitted.

[Source-linked admission evidence](../../../literature/admission-v04-electrical.json). This endpoint was not run in this release; absence is unknown, not zero or proof of poor data.

## Current admission and execution

Preview 0.8: measured. Source-specific rights/data/scorer checks and frozen model procedure completed for the explicit custom slice; no broader resource or current-SOTA claim.

[Admission/source evidence](../../../experiments/H08/protocol.md). [Actual protocol/worklog](../../../experiments/H08). [Task measurements](../../../results/H08.json).
