# C07 — Longitudinal calcium cell registration

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** CellReg examples and released study data

**State:** candidate_pending_validation. Current status for this exact task-resource slice; current global best remains unverified.

## Scientific use

Input: Spatial footprints across sessions

Target/ground truth: Curated/proxy cell matches

Mapped specialist candidates (not all evaluated): CellReg; CaImAn registration

General-model route: Generic image registration/embedding

## Execution and performance

No experiment admitted yet. All measurements are centralized in [results](../../../results/). Current best: **not verified**. Missing scores are unknown, not zero. Literature resources are not newly executed results.

## Limitations

No universal true cell identity labels; add curated subset

## Sources

- [https://github.com/zivlab/CellReg](https://github.com/zivlab/CellReg)

Source associations include historical alternatives; actual acquired files are identified in the executed protocol/manifest.

## Historical v0.4 admission and execution

Decision: **candidate_pending_validation** (2026-10-30). CellReg examples contain multi-session ROI images, but cell-identity scoring needs independent manuallyvalidated crossday pairs; CellReg matching outputs cannot serve as truth for evaluating a competing matcher. Verify identity groundtruth before admission.

[Source-linked admission evidence](../../../literature/admission-v04-behavior-population.json). This endpoint was not run in this release; absence is unknown, not zero or proof of poor data.

## Current admission and execution

Preview 0.6: candidate_pending_validation. CellReg examples contain multi-session ROI images, but cell-identity scoring needs independent manuallyvalidated crossday pairs; CellReg matching outputs cannot serve as truth for evaluating a competing matcher. Verify identity groundtruth before admission.

[Admission/source evidence](../../../literature/admission-v04-behavior-population.json).
