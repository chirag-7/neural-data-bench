# C01 — Calcium ROI detection

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** Neurofinder

**State:** not evaluated; candidate_pending_validation. Mapped resource only; license, acquisition, split, scorer and baseline gates are not yet all validated.

## Scientific use

Input: Two-photon movies

Target/ground truth: Human cell-region annotations

Specialist candidates: CaImAn; Suite2p; segmentation networks

General-model route: SAM-like masks; generic image features plus head

## Execution and performance

No experiment admitted yet. All measurements are centralized in [results](../../../results/). Current best: **not verified**. Missing scores are unknown, not zero. Literature resources are not newly executed results.

## Limitations

Old submission service not verified; silent/overlapping cells ambiguous

## Sources

- [https://github.com/codeneuro/neurofinder-datasets](https://github.com/codeneuro/neurofinder-datasets)
- [https://github.com/codeneuro/neurofinder](https://github.com/codeneuro/neurofinder)

## v0.4 admission and execution

Decision: **candidate_pending_validation** (2026-10-30). Neurofinder supplies true labeled calcium ROI masks and image stacks. Needs image/mask archive pinning, original heldout recording split and official ROI matching scorer. Segmentation image adapter not acquired in this expansion.

[Source-linked admission evidence](../../../literature/admission-v04-behavior-population.json). This endpoint was not run in this release; absence is unknown, not zero or proof of poor data.

## v0.5 execution status

candidate_pending_validation. Neurofinder supplies true labeled calcium ROI masks and image stacks. Needs image/mask archive pinning, original heldout recording split and official ROI matching scorer. Segmentation image adapter not acquired in this expansion.

[Admission/source evidence](../../../literature/admission-v04-behavior-population.json).
