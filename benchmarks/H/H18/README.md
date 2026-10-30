# H18 — Sleep microevent detection

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** DREAMS microevent annotations; MODA consensus as a separately versioned extension

**State:** not evaluated; candidate_pending_validation. Mapped resource only; license, acquisition, split, scorer and baseline gates are not yet all validated.

## Scientific use

Input: Human EEG with spindle and K-complex intervals

Target/ground truth: Individual expert labels with disagreement

Specialist candidates: SUMO/SUMOv2; published spindle detector baselines

General-model route: General signal/audio feature or code-agent event detector

## Execution and performance

No experiment admitted yet. All measurements are centralized in [results](../../../results/). Current best: **not verified**. Missing scores are unknown, not zero. Literature resources are not newly executed results.

## Limitations

DREAMS repository explicitly warns expert 1 spindle counts stop after 1000 seconds; censor unannotated periods rather than scoring them negative; MODA and DREAMS are not interchangeable

## Sources

- [https://zenodo.org/records/2650142](https://zenodo.org/records/2650142)
- [https://www.nature.com/articles/s41598-026-53891-9](https://www.nature.com/articles/s41598-026-53891-9)
- [https://pmc.ncbi.nlm.nih.gov/articles/PMC10762090/](https://pmc.ncbi.nlm.nih.gov/articles/PMC10762090/)

## v0.4 admission and execution

Decision: **deferred** (2026-10-30). Original DREAMS Zenodo record explicitly warns Expert1 spindle annotations stop after1000s. A naive full-1800s negative-label benchmark is excluded. A masked interval/Expert2 consensus protocol remains feasible but has not been validated, and original DREAMS noncommercial/no-adaptation terms need an appropriate data handling policy.

[Source-linked admission evidence](../../../literature/admission-v04-electrical.json). This endpoint was not run in this release; absence is unknown, not zero or proof of poor data.

## v0.5 execution status

deferred. Original DREAMS Zenodo record explicitly warns Expert1 spindle annotations stop after1000s. A naive full-1800s negative-label benchmark is excluded. A masked interval/Expert2 consensus protocol remains feasible but has not been validated, and original DREAMS noncommercial/no-adaptation terms need an appropriate data handling policy.

[Admission/source evidence](../../../literature/admission-v04-electrical.json).
