# K05 worklog

- 2026-10-30 — Resource mapped; source URLs and proposed metrics/splits recorded. Evidence: Primary paper/project documentation reviewed; download, installation and scorer not run in this extension audit
- 2026-10-30 — Admission decision: **candidate_pending_validation**. Mapped resource only; license, acquisition, split, scorer and baseline gates are not yet all validated.
- Acquisition, license audit, scorer implementation, specialist reproduction and model execution: **not completed**.

## v0.4 admission and execution

Decision: **candidate_pending_validation** (2026-10-30). Primary DeconvoBuddies fetch documentation identifies bulk 110x21k (41 MB), snRNA 77kx36k (172 MB) and example 10kx557. Need match orthogonal IF/RNAScope fractions to bulk samples, donor/tissue blocks and fixed reference/marker policy. Bioconductor S4 readers absent and ground-truth alignment not completed. Data size itself is manageable; do not call impossible or bad.

[Source-linked admission evidence](../../../literature/admission-v04-cell-workflow.json). This endpoint was not run in this release; absence is unknown, not zero or proof of poor data.

## Current admission and execution

Preview 0.11: measured. Source-specific rights/data/scorer checks and frozen model procedure completed for the explicit custom slice; no broader resource or current-SOTA claim.

[Admission/source evidence](../../../experiments/K05/protocol.md). [Actual protocol/worklog](../../../experiments/K05). [Task measurements](../../../results/K05.json).
