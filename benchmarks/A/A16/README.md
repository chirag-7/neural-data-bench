# A16 — Caller localization and vocalization attribution

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** Vocal Call Locator (VCL) Benchmark

**State:** candidate_pending_validation. Current status for this exact task-resource slice; current global best remains unverified.

## Scientific use

Input: Synchronized multi-microphone audio with overhead video-derived source positions

Target/ground truth: 2D source positions, including controlled speaker conditions

Mapped specialist candidates (not all evaluated): VCL localization models; classical sound source localization

General-model route: Generic audio model or code-agent localization under fixed calibration information

## Execution and performance

No experiment admitted yet. All measurements are centralized in [results](../../../results/). Current best: **not verified**. Missing scores are unknown, not zero. Literature resources are not newly executed results.

## Limitations

Speaker-ground-truth and freely moving animals are distinct conditions; paper revisions report differing event totals, so pin release

## Sources

- [https://proceedings.nips.cc/paper_files/paper/2024/hash/c00d37d6b04d73b870b963a4d70051c1-Abstract-Datasets_and_Benchmarks_Track.html](https://proceedings.nips.cc/paper_files/paper/2024/hash/c00d37d6b04d73b870b963a4d70051c1-Abstract-Datasets_and_Benchmarks_Track.html)
- [https://pmc.ncbi.nlm.nih.gov/articles/PMC11430026/](https://pmc.ncbi.nlm.nih.gov/articles/PMC11430026/)
- [https://github.com/neurostatslab/vocalocator](https://github.com/neurostatslab/vocalocator)

Source associations include historical alternatives; actual acquired files are identified in the executed protocol/manifest.

## Historical v0.4 admission and execution

Decision: **candidate_pending_validation** (2026-10-30). VCL controlled speaker localization supplies positions, but multi-mic calibration/time synchronization and recording-group split must be acquired. Do not infer source identity solely from event detection; no adapter prepared.

[Source-linked admission evidence](../../../literature/admission-v04-behavior-population.json). This endpoint was not run in this release; absence is unknown, not zero or proof of poor data.

## Current admission and execution

Preview 0.11: candidate_pending_validation. VCL controlled speaker localization supplies positions, but multi-mic calibration/time synchronization and recording-group split must be acquired. Do not infer source identity solely from event detection; no adapter prepared.

[Admission/source evidence](../../../literature/admission-v04-behavior-population.json).
