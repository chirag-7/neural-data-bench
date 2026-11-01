# A15 — Animal vocalization event segmentation and syllable labeling

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** DAS Bengalesefinch / Nicholson; held-out-bird annotated-song segmentation

**State:** measured. Current status for this exact task-resource slice; current global best remains unverified.

## Scientific use

Input: Original 32 kHz monaural waveforms, NaN padding; training 1 ms binary activity labels

Target/ground truth: Source annotated song intervals, not exhaustive contact-call or vocalization labels

Mapped specialist candidates (not all evaluated): DAS; TweetyNet; WhisperSeg (separate domain-adapted pretrained comparator)

General-model route: General audio features/readout or bounded code synthesis; audio-native foundation model

## Execution and performance

**Executed slice:** 80 whole recordings: 60 from three training birds, 20 from one unseen test bird; 1,519 test annotated events.

[Frozen protocol and artifacts](../../../experiments/A15). [Measured scores and references](../../../results/A15.json). [Central data](../../../results/measurements.csv). Missing or failed outputs are retained.

## Limitations

One test bird; annotation boundaries originated from amplitude segmentation with human syllable labels. Custom binary event endpoint, no verified global best; source annotation milliseconds independently resolved against original archive before freeze. GPT-5.6 output exceeds 240-line contract and remains numerically measured but noncompliant.

## Sources

- [https://elifesciences.org/articles/68837](https://elifesciences.org/articles/68837)
- [https://data.goettingen-research-online.de/dataverse/das](https://data.goettingen-research-online.de/dataverse/das)
- [https://janclemenslab.org/das/](https://janclemenslab.org/das/)
- [https://github.com/nianlonggu/WhisperSeg](https://github.com/nianlonggu/WhisperSeg)
- [https://doi.org/10.25625/ENKMJS](https://doi.org/10.25625/ENKMJS)
- [https://doi.org/10.6084/m9.figshare.4805749](https://doi.org/10.6084/m9.figshare.4805749)
- [https://www.vocalpy.org/bfsongrepo/](https://www.vocalpy.org/bfsongrepo/)
- [https://figshare.com/articles/dataset/4805749](https://figshare.com/articles/dataset/4805749)

Source associations include historical alternatives; actual acquired files are identified in the executed protocol/manifest.

## Historical v0.4 admission and execution

Decision: **candidate_pending_validation** (2026-10-30). DAS annotated raw audio can support real event-segmentation evaluation. Still need pinned species/recording slice, sampling rate and official event-matching tolerance; no audio acquisition attempted here. Temporal bouts must remain grouped.

[Source-linked admission evidence](../../../literature/admission-v04-behavior-population.json). This endpoint was not run in this release; absence is unknown, not zero or proof of poor data.

## Current admission and execution

Preview 0.11: measured. Source-specific rights/data/scorer checks and frozen model procedure completed for the explicit custom slice; no broader resource or current-SOTA claim.

[Admission/source evidence](../../../experiments/A15/protocol.md). [Actual protocol/worklog](../../../experiments/A15). [Task measurements](../../../results/A15.json).

## Current specialists and repair sensitivity — 1 November 2026

[Current specialist review](../../../literature/specialist-review-2026-11-01/A15.json) · [Native version trajectories and practical interpretation](../../../analysis/practical-review-2026-11-01/report.md). The review distinguishes tested references from unexecuted newer candidates; no matched current global winner is certified.
