# K06 worklog

- 2026-10-30 — Resource mapped; source URLs and proposed metrics/splits recorded. Evidence: Primary paper/project documentation reviewed; download, installation and scorer not run in this extension audit
- 2026-10-30 — Admission decision: **candidate_pending_validation**. Mapped resource only; license, acquisition, split, scorer and baseline gates are not yet all validated.
- Acquisition, license audit, scorer implementation, specialist reproduction and model execution: **not completed**.

## v0.4 admission and execution

Decision: **candidate_pending_validation** (2026-10-30). Primary ground-truth tutorial and GitHub folder inspected; 87 files total ~500 MB. Downloaded one 189 kB cell metrics example and consolidated 2.83 MB gt list; MATLAB v7.3 HDF5 parsed with isolated h5py3.15.1. Consolidated list has 430 entries and animal/session/truth labels, but no predictor feature matrix; example has Juxta tag (not a molecular cell class). Must select nonnested independently tagged classes, extract only scalar physiology/waveform metrics from session files, group animals, resolve contributor data terms, and exclude putativeCellType/geneticLine/brainRegion proxies. No validated table yet.

[Source-linked admission evidence](../../../literature/admission-v04-cell-workflow.json). This endpoint was not run in this release; absence is unknown, not zero or proof of poor data.

## Current admission and execution

Preview 0.6: candidate_pending_validation. Primary ground-truth tutorial and GitHub folder inspected; 87 files total ~500 MB. Downloaded one 189 kB cell metrics example and consolidated 2.83 MB gt list; MATLAB v7.3 HDF5 parsed with isolated h5py3.15.1. Consolidated list has 430 entries and animal/session/truth labels, but no predictor feature matrix; example has Juxta tag (not a molecular cell class). Must select nonnested independently tagged classes, extract only scalar physiology/waveform metrics from session files, group animals, resolve contributor data terms, and exclude putativeCellType/geneticLine/brainRegion proxies. No validated table yet.

[Admission/source evidence](../../../literature/admission-v04-cell-workflow.json).
