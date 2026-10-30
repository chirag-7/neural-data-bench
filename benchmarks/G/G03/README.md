# G03 — Attempted speech to text

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** Brain-to-Text 2024 resources and 2025 competition

**State:** not evaluated; candidate_pending_validation. Mapped resource only; license, acquisition, split, scorer and baseline gates are not yet all validated.

## Scientific use

Input: Intracortical activity with speech targets

Target/ground truth: Prompted attempted-speech text/phonemes

Specialist candidates: Released speechBCI neural decoder and language model

General-model route: General sequence model plus separately controlled language decoder

## Execution and performance

No experiment admitted yet. All measurements are centralized in [results](../../../results/). Current best: **not verified**. Missing scores are unknown, not zero. Literature resources are not newly executed results.

## Limitations

Report neural-only/no-neural controls; competition access/rules may apply

## Sources

- [https://github.com/fwillett/speechBCI](https://github.com/fwillett/speechBCI)
- [https://www.kaggle.com/competitions/brain-to-text-25/overview](https://www.kaggle.com/competitions/brain-to-text-25/overview)

## v0.4 admission and execution

Decision: **deferred** (2026-10-30). Brain-to-Text speech decoding needs sequence/phoneme/texttargets, CTC/language-model decoding rules and speech-rate/word-error scorer, with substantial data and training. ThreeSol numerical code snippets are not speechsequence models. No data acquisition attempted; retain valid futurecandidate.

[Source-linked admission evidence](../../../literature/admission-v04-behavior-population.json). This endpoint was not run in this release; absence is unknown, not zero or proof of poor data.

## v0.5 execution status

deferred. Brain-to-Text speech decoding needs sequence/phoneme/texttargets, CTC/language-model decoding rules and speech-rate/word-error scorer, with substantial data and training. ThreeSol numerical code snippets are not speechsequence models. No data acquisition attempted; retain valid futurecandidate.

[Admission/source evidence](../../../literature/admission-v04-behavior-population.json).
