# A09 — Frame-level social behavior labels

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** CalMS21

**State:** not evaluated; candidate_pending_validation. Mapped resource only; license, acquisition, split, scorer and baseline gates are not yet all validated.

## Scientific use

Input: Mouse video and/or tracked poses

Target/ground truth: Expert behavioral labels

Specialist candidates: CalMS21 baselines; supervised temporal classifier

General-model route: Video VLM; frozen video embeddings; general time-series model

## Execution and performance

No experiment admitted yet. All measurements are centralized in [results](../../../results/). Current best: **not verified**. Missing scores are unknown, not zero. Literature resources are not newly executed results.

## Limitations

Annotator definitions differ; rare behaviors

## Sources

- [https://arxiv.org/abs/2104.02710](https://arxiv.org/abs/2104.02710)

## v0.4 admission and execution

Decision: **measured** (2026-10-30). Official Task1 pose/behavior archive acquired and publisher MD5 verified; current-record/paper license discrepancy documented, raw data cache only. Real expert labels, all70train19test recordings retained in fixed3Hz custom slice, official animal split. Adapter and baseline ready; not full benchmark or SOTA.

[Source-linked admission evidence](../../../literature/admission-v04-behavior-population.json). [Actual protocol and artifacts](../../../experiments/A09). [Central task results](../../../results/A09.json).

## v0.5 execution status

measured. Official Task1 pose/behavior archive acquired and publisher MD5 verified; current-record/paper license discrepancy documented, raw data cache only. Real expert labels, all70train19test recordings retained in fixed3Hz custom slice, official animal split. Adapter and baseline ready; not full benchmark or SOTA.

[Admission/source evidence](../../../literature/admission-v04-behavior-population.json). [Actual protocol/worklog](../../../experiments/A09). [Task measurements](../../../results/A09.json).
