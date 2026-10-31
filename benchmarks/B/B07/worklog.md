# B07 worklog

- 2026-10-30 — Resource mapped; source URLs and proposed metrics/splits recorded. Evidence: Primary documentation/paper located; downloads and execution not tested
- 2026-10-30 — Admission decision: **candidate_pending_validation**. Mapped resource only; license, acquisition, split, scorer and baseline gates are not yet all validated.
- Acquisition, license audit, scorer implementation, specialist reproduction and model execution: **not completed**.

## v0.4 admission and execution

Decision: **candidate_pending_validation** (2026-10-30). Lossless compression is executable with small frozen raw ephys segments, exactbyte reconstruction and compression/runtime metrics. Need immutable raw-file URI, acquisition terms and canonical codec reference; no raw acquisition attempted here. Avoid different dtype or discarded channels confounding ratio.

[Source-linked admission evidence](../../../literature/admission-v04-behavior-population.json). This endpoint was not run in this release; absence is unknown, not zero or proof of poor data.

## Current admission and execution

Preview 0.11: measured. Source-specific rights/data/scorer checks and frozen model procedure completed for the explicit custom slice; no broader resource or current-SOTA claim.

[Admission/source evidence](../../../experiments/B07/protocol.md). [Actual protocol/worklog](../../../experiments/B07). [Task measurements](../../../results/B07.json).
