# B07 worklog

- 2026-10-30 — Resource mapped; source URLs and proposed metrics/splits recorded. Evidence: Primary documentation/paper located; downloads and execution not tested
- 2026-10-30 — Admission decision: **candidate_pending_validation**. Mapped resource only; license, acquisition, split, scorer and baseline gates are not yet all validated.
- Acquisition, license audit, scorer implementation, specialist reproduction and model execution: **not completed**.

## v0.4 admission and execution

Decision: **candidate_pending_validation** (2026-10-30). Lossless compression is executable with small frozen raw ephys segments, exactbyte reconstruction and compression/runtime metrics. Need immutable raw-file URI, acquisition terms and canonical codec reference; no raw acquisition attempted here. Avoid different dtype or discarded channels confounding ratio.

[Source-linked admission evidence](../../../literature/admission-v04-behavior-population.json). This endpoint was not run in this release; absence is unknown, not zero or proof of poor data.

## Current admission and execution

Preview 0.9: candidate_pending_validation. Original public S3 listing and binary metadata acquired;16 experimental raw sources identified and CC BY4.0 recorded by original AWS registry. Raw chunks, lossless byte-exact codec contract/scorer and specialist execution remain unfrozen; no compression scores claimed.

[Admission/source evidence](../../../literature/admission-v04-behavior-population.json).
