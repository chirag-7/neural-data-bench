# A09 — Frame-level social behavior labels

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** CalMS21

**State:** measured. Current status for this exact task-resource slice; current global best remains unverified.

## Scientific use

Input: Mouse video and/or tracked poses

Target/ground truth: Expert behavioral labels

Mapped specialist candidates (not all evaluated): CalMS21 baselines; supervised temporal classifier

General-model route: Video VLM; frozen video embeddings; general time-series model

## Execution and performance

**Executed slice:** CalMS21 Task 1: processed pose context at 3 Hz; 70 training and 19 test recordings.

[Frozen protocol and artifacts](../../../experiments/A09). [Measured scores and references](../../../results/A09.json). [Central data](../../../results/measurements.csv). Missing or failed outputs are retained.

## Limitations

Annotator definitions differ; rare behaviors

## Sources

- [https://arxiv.org/abs/2104.02710](https://arxiv.org/abs/2104.02710)
- [https://doi.org/10.17617/3.3R0QYI](https://doi.org/10.17617/3.3R0QYI)

Source associations include historical alternatives; actual acquired files are identified in the executed protocol/manifest.

## Historical v0.4 admission and execution

Decision: **measured** (2026-10-30). Official Task1 pose/behavior archive acquired and publisher MD5 verified; current-record/paper license discrepancy documented, raw data cache only. Real expert labels, all70train19test recordings retained in fixed3Hz custom slice, official animal split. Adapter and baseline ready; not full benchmark or SOTA.

[Source-linked admission evidence](../../../literature/admission-v04-behavior-population.json). [Actual protocol and artifacts](../../../experiments/A09). [Central task results](../../../results/A09.json).

## Current admission and execution

Preview 0.11: measured. Official Task1 pose/behavior archive acquired and publisher MD5 verified; current-record/paper license discrepancy documented, raw data cache only. Real expert labels, all70train19test recordings retained in fixed3Hz custom slice, official animal split. Adapter and baseline ready; not full benchmark or SOTA.

[Admission/source evidence](../../../literature/admission-v04-behavior-population.json). [Actual protocol/worklog](../../../experiments/A09). [Task measurements](../../../results/A09.json).
