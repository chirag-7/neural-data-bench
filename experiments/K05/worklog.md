Preparation date: 2026-10-31. Status: prepared and independently verified for parent admission/freeze review. No model calls, predictive method execution, real-slice scores, git commits, central registry or website changes.

Reused prior CellExplorer 430-entry ground-truth list and license inspection. New downloads are pinned to reviewed upstream revisions and all source bytes remain in ignored local caches. The acquisition script validates expected SHA256 and bytes before preparation. `verify.py` independently reconstructs source joins and supplied features, checks disjoint groups, and checks scorer aggregation on toy arrays only. `verification.json` records results. Parent must freeze exact source/adapter/data/context hashes before dispatching generations.

Generic model signature includes actual outer-training group IDs for validation/weight construction only; hidden test IDs/labels stay with scorer. Baseline remains a three-argument reference and reads equivalent canonical training grouping from cache. All models receive identical task/units/scorer contract. Batch integration only after parent review.


Final fourth-argument contract: train_groups is a dict with group_ids (actual training donor IDs) and block_ids (same-length tissue-block ID vector). Use these only for train validation and weights; all test identifiers and labels remain hidden; never biological predictors.

## Batch 0.11 completed outcome update

31 October 2026. This dated append follows the preparation-only notes above; it does not modify the frozen contract, programs, source arrays or scores.

Executed deviation: supervised anonymous bulk-expression-to-three Circle-panel IF/RNAScope fraction calibration, not full reference-only deconvolution. 5 train/3 test donors, 7/4 blocks, 39/24 bulk samples; technical replicates share block truth. Native logCPM2000 selected numeric columns; despite frozen protocol feature-ID wording, no gene IDs passed to either procedure. Source Confidence OK/High; targets are original prop, never prop_sn or adjusted compositional fractions. Three fractions need not sum 1.

| Model/slice | Numeric status | Exact score | Lines / compliance |
|---|---|---:|---|
| gpt-5.6-sol/batch-v11 | measured | 0.06742367203503653 | 216 / True |
| gpt-6-sol/batch-v11 | measured | 0.057937995627723386 | 154 / True |
| gpt-6.1-sol/batch-v11 | measured | 0.0552287462339175 | 178 / True |
| task-baseline/batch-v11 | measured | 0.05759104442612498 | Reference or pre-execution rejection |

Saved-output/source audit: results/audits/cells-batch-v11.json. Read-only score-blinded static review: literature/batch-v11-code-review.json (21 total submissions). No predictive method was rerun for this documentation.

The frozen protocol gene-ID disclosure statement does not match numerical interface: neither general nor reference receives gene IDs. Interpret as anonymous 2000-column supervised calibration; no identity-informed marker claim or post-score protocol repair.

Current-global-best and matched-effort superiority remain unestablished. One code generation/model and bounded/cohort-dependent source coverage limit interpretation. Central integration is once for all seven tasks; no per-task release or commit.
