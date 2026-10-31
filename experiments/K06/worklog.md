Preparation date: 2026-10-31. Status: prepared and independently verified for parent admission/freeze review. No model calls, predictive method execution, real-slice scores, git commits, central registry or website changes.

Reused prior CellExplorer 430-entry ground-truth list and license inspection. New downloads are pinned to reviewed upstream revisions and all source bytes remain in ignored local caches. The acquisition script validates expected SHA256 and bytes before preparation. `verify.py` independently reconstructs source joins and supplied features, checks disjoint groups, and checks scorer aggregation on toy arrays only. `verification.json` records results. Parent must freeze exact source/adapter/data/context hashes before dispatching generations.

Generic model signature includes actual outer-training group IDs for validation/weight construction only; hidden test IDs/labels stay with scorer. Baseline remains a three-argument reference and reads equivalent canonical training grouping from cache. All models receive identical task/units/scorer contract. Batch integration only after parent review.


Final fourth-argument contract: train_groups is a dict with group_ids (actual training mouse IDs) and cv_fold (same-length fixed three-fold mouse-stratified CV assignment vector). Use these only for train validation and weights; all test identifiers and labels remain hidden; never biological predictors.

## Batch 0.11 completed outcome update

31 October 2026. This dated append follows the preparation-only notes above; it does not modify the frozen contract, programs, source arrays or scores.

Allen-only optotagged PV/SST classes: 136 train/71 test cells in 11/5 disjoint mice. Six waveform scalars plus 81 normalized waveform samples. No genotype, IDs, putative types, opto responses or firing/ACG/ISI predictors. Binary genetic cohort task, not full molecular taxonomy; only 5 PV mice in source, brain-area metadata incomplete. Allen research/noncommercial terms retained separately from CellExplorer code BSD license.

| Model/slice | Numeric status | Exact score | Lines / compliance |
|---|---|---:|---|
| gpt-5.6-sol/batch-v11 | measured | 0.8777777777777778 | 214 / True |
| gpt-6-sol/batch-v11 | measured | 0.8694444444444445 | 125 / True |
| gpt-6.1-sol/batch-v11 | measured | 0.8902777777777777 | 194 / True |
| task-baseline/batch-v11 | measured | 0.8381944444444444 | Reference or pre-execution rejection |

Saved-output/source audit: results/audits/cells-batch-v11.json. Read-only score-blinded static review: literature/batch-v11-code-review.json (21 total submissions). No predictive method was rerun for this documentation.

Current-global-best and matched-effort superiority remain unestablished. One code generation/model and bounded/cohort-dependent source coverage limit interpretation. Central integration is once for all seven tasks; no per-task release or commit.
