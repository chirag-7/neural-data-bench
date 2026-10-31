# H18 — Sleep microevent detection

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** DREAMS microevent annotations; MODA consensus as a separately versioned extension

**State:** deferred. Current status for this exact task-resource slice; current global best remains unverified.

## Scientific use

Input: Human EEG with spindle and K-complex intervals

Target/ground truth: Individual expert labels with disagreement

Mapped specialist candidates (not all evaluated): SUMO/SUMOv2; published spindle detector baselines

General-model route: General signal/audio feature or code-agent event detector

## Execution and performance

No experiment admitted yet. All measurements are centralized in [results](../../../results/). Current best: **not verified**. Missing scores are unknown, not zero. Literature resources are not newly executed results.

## Limitations

DREAMS repository explicitly warns expert 1 spindle counts stop after 1000 seconds; censor unannotated periods rather than scoring them negative; MODA and DREAMS are not interchangeable

## Sources

- [https://zenodo.org/records/2650142](https://zenodo.org/records/2650142)
- [https://www.nature.com/articles/s41598-026-53891-9](https://www.nature.com/articles/s41598-026-53891-9)
- [https://pmc.ncbi.nlm.nih.gov/articles/PMC10762090/](https://pmc.ncbi.nlm.nih.gov/articles/PMC10762090/)
- [https://zenodo.org/records/2650142/files/Dreams%20License.txt?download=1](https://zenodo.org/records/2650142/files/Dreams%20License.txt?download=1)

Source associations include historical alternatives; actual acquired files are identified in the executed protocol/manifest.

## Historical v0.4 admission and execution

Decision: **deferred** (2026-10-30). Original DREAMS Zenodo record explicitly warns Expert1 spindle annotations stop after1000s. A naive full-1800s negative-label benchmark is excluded. A masked interval/Expert2 consensus protocol remains feasible but has not been validated, and original DREAMS noncommercial/no-adaptation terms need an appropriate data handling policy.

[Source-linked admission evidence](../../../literature/admission-v04-electrical.json). This endpoint was not run in this release; absence is unknown, not zero or proof of poor data.

## Current admission and execution

Preview 0.10: deferred. MODA annotations/code are public, but raw MASS PSG requires a project/ethics access request. Annotation-only inputs cannot evaluate EEG detection; DREAMS remains a separate deferred alternative.

[Admission/source evidence](../../../literature/admission-v04-electrical.json).
