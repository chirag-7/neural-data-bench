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
