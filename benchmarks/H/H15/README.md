# H15 — EEG/MEG source localization

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** MNE / Brainstorm phantom protocols

**State:** not evaluated; candidate_pending_validation. Mapped resource only; license, acquisition, split, scorer and baseline gates are not yet all validated.

## Scientific use

Input: Physical phantom sensor measurements and known dipoles

Target/ground truth: Known physical phantom dipole position/orientation

Specialist candidates: MNE inverse solutions; dipole fitting

General-model route: General inverse model or scientific coding agent

## Execution and performance

No experiment admitted yet. All measurements are centralized in [results](../../../results/). Current best: **not verified**. Missing scores are unknown, not zero. Literature resources are not newly executed results.

## Limitations

Phantom localization is different from in-vivo source truth

## Sources

- [https://mne.tools/stable/auto_tutorials/inverse/80_brainstorm_phantom_elekta.html](https://mne.tools/stable/auto_tutorials/inverse/80_brainstorm_phantom_elekta.html)

## v0.4 admission and execution

Decision: **deferred** (2026-10-30). Original MNE/Brainstorm phantom tutorial accessible. Known dipole positions make this scientifically useful, but needs sensor geometry, forward model, filtering and localization scorer adapter. No arbitrary simulated coordinate regression substituted.

[Source-linked admission evidence](../../../literature/admission-v04-electrical.json). This endpoint was not run in this release; absence is unknown, not zero or proof of poor data.
