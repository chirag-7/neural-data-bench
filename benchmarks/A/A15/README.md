# A15 — Animal vocalization event segmentation and syllable labeling

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** DAS multi-species annotated acoustic datasets

**State:** not evaluated; candidate_pending_validation. Mapped resource only; license, acquisition, split, scorer and baseline gates are not yet all validated.

## Scientific use

Input: Single/multi-channel raw audio and human annotations

Target/ground truth: Manual acoustic events/segments

Specialist candidates: DAS; TweetyNet; WhisperSeg (separate domain-adapted pretrained comparator)

General-model route: General audio features/readout or bounded code synthesis; audio-native foundation model

## Execution and performance

No experiment admitted yet. All measurements are centralized in [results](../../../results/). Current best: **not verified**. Missing scores are unknown, not zero. Literature resources are not newly executed results.

## Limitations

Ultrasound sample rates exceed speech frontends; species and segment matching differ; tune thresholds only on validation

## Sources

- [https://elifesciences.org/articles/68837](https://elifesciences.org/articles/68837)
- [https://data.goettingen-research-online.de/dataverse/das](https://data.goettingen-research-online.de/dataverse/das)
- [https://janclemenslab.org/das/](https://janclemenslab.org/das/)
- [https://github.com/nianlonggu/WhisperSeg](https://github.com/nianlonggu/WhisperSeg)

## v0.4 admission and execution

Decision: **candidate_pending_validation** (2026-10-30). DAS annotated raw audio can support real event-segmentation evaluation. Still need pinned species/recording slice, sampling rate and official event-matching tolerance; no audio acquisition attempted here. Temporal bouts must remain grouped.

[Source-linked admission evidence](../../../literature/admission-v04-behavior-population.json). This endpoint was not run in this release; absence is unknown, not zero or proof of poor data.

## v0.5 execution status

candidate_pending_validation. DAS annotated raw audio can support real event-segmentation evaluation. Still need pinned species/recording slice, sampling rate and official event-matching tolerance; no audio acquisition attempted here. Temporal bouts must remain grouped.

[Admission/source evidence](../../../literature/admission-v04-behavior-population.json).
