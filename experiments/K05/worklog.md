Preparation date: 2026-10-31. Status: prepared and independently verified for parent admission/freeze review. No model calls, predictive method execution, real-slice scores, git commits, central registry or website changes.

Reused prior CellExplorer 430-entry ground-truth list and license inspection. New downloads are pinned to reviewed upstream revisions and all source bytes remain in ignored local caches. The acquisition script validates expected SHA256 and bytes before preparation. `verify.py` independently reconstructs source joins and supplied features, checks disjoint groups, and checks scorer aggregation on toy arrays only. `verification.json` records results. Parent must freeze exact source/adapter/data/context hashes before dispatching generations.

Generic model signature includes actual outer-training group IDs for validation/weight construction only; hidden test IDs/labels stay with scorer. Baseline remains a three-argument reference and reads equivalent canonical training grouping from cache. All models receive identical task/units/scorer contract. Batch integration only after parent review.


Final fourth-argument contract: train_groups is a dict with group_ids (actual training donor IDs) and block_ids (same-length tissue-block ID vector). Use these only for train validation and weights; all test identifiers and labels remain hidden; never biological predictors.
