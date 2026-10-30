# H12 — Image/object retrieval from EEG/MEG

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** THINGS EEG/MEG releases

**State:** not evaluated; candidate_pending_validation. Mapped resource only; license, acquisition, split, scorer and baseline gates are not yet all validated.

## Scientific use

Input: Neural responses to object images

Target/ground truth: Image/concept identity and repeated trials

Specialist candidates: Published neural encoder plus image embeddings

General-model route: Generic image/LLM embeddings with learned neural adapter

## Execution and performance

No experiment admitted yet. All measurements are centralized in [results](../../../results/). Current best: **not verified**. Missing scores are unknown, not zero. Literature resources are not newly executed results.

## Limitations

Closed image gallery is much easier than unrestricted reconstruction

## Sources

- [https://things-initiative.org/](https://things-initiative.org/)

## v0.4 admission and execution

Decision: **deferred** (2026-10-30). Original THINGS site accessible. Stimulus concept and image reuse complicate splitting; original image pool has academic-use restrictions and a separate CC0 subset. Need exact EEG/MEG release, retrieval gallery and held-out concepts/participants rather than an undefined image-reconstruction score.

[Source-linked admission evidence](../../../literature/admission-v04-electrical.json). This endpoint was not run in this release; absence is unknown, not zero or proof of poor data.
