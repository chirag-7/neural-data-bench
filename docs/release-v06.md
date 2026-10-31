# Preview 0.6 — bounded review, clearer references and continued execution

This release performs one focused scientific/readability review, then executes one additional admitted task. It avoids repeated redesign or score-driven retries. Exact counts/results are in the derived central summary and current findings.

## Issues identified and actions

| Issue | Action | Boundary |
|---|---|---|
| Horizontal specialist lines lacked visible method/value labels | Add full named numeric reference cards, direct line callouts, and an explicit solid/dashed/dotted reading key | Specialists, conventional references and test-selected envelopes remain distinct |
| B01'sper-unit primary score can omit unmatched output events | Add a post-hoc all-output event precision/recall/F1 sensitivity using the same predictions and unit mapping | Original primary scores, code, matching/tolerance and macro policy are unchanged |
| Methodology page appended releases and mixed historical/current counts | Consolidate the current method; move the earlier text to a dated archive | Preserve all historical amendments and limitations |
| ERP/P300 remained deferred because the earlier source had rights/preparation gates | Admit a separate original CC BY 4.0 Brain Invaders 2012 release with person-disjoint split and grouped validation input | No retroactive assertion that the old BNCI source was admitted |

## First-principles finding: metric choice matters

B01'soriginal mean-per-GT-unit accuracy is 0.940011 for GPT-6 and 0.940896 for MountainSort5. Yet all-output event F1 is 0.599751 versus 0.962060. GPT-6 emits 1, 664 events, with 723 true positives and 941 false positives under the original one-to-one unit mapping. The other event-F1 scores are GPT-5.6=0.900000 and GPT-6.1=0.868051. Two of the three pairwise model-version directional conclusions change between these two metrics on this slice. Neither scalar alone establishes real biological sorting utility.

This is a **post-hoc sensitivity**, not a new frozen primary benchmark or a prospective discovery claim. It uses event-weighting rather than equal true-unit weighting, including redundant/unmatched clusters. Source event conservation, independent event-match counts and three hand-checkable fixtures passed. [Amendment](../experiments/B01/secondary-amendment.md), [code/results](../experiments/B01/secondary-audit.json). The website permits selecting either metric for the two plots; the directory and macro summaries retain the frozen primary.

## New experiment: H02 P300 target ranking

All 25 Brain Invaders 2012 participants, calibration runs only. People 01–15 train, 16–25 test; 11, 481 training and 7, 663 test epochs, 16 EEG channels×128 samples. Source CC BY 4.0 is explicitly reported by the original Zenodo record, all 25 archives match publisher MD 5 s, and independent MAT/CSV event-marker checks pass. The fixed preprocessing excludes groundFz and only geometric boundary events; no outcome-based artifact rejection.

The contract passes training-person IDs equally to all three general programs and references, enabling person-held-out validation. Primary metric is mean of ten held-out person ROC-AUCs. The fixed xDAWN/tangent-space/logistic specialist and shrinkage-LDA reference use the same source/split; all supervised fitting is train-only. This is an offline custom diagnostic, not online symbol selection or a global-SOTA comparison. [Protocol](../experiments/H02/protocol.md), [preparation/scorer checks](../experiments/H02/scorer-verification.json), [worklog](../experiments/H02/worklog.md).

## Review limits and next useful iteration

This review checks traceability, input/target separation, grouping, reference policy, metrics and current documentation. It does not establish a completed independent expert audit, exhaustive literature coverage, adversarial sandboxing, uncontaminated pretraining or repeated-generation uncertainty. The panel remains selected toward bounded CPU-friendly T3 code construction.

The next useful expansion should prioritize an independently grouped source or a stronger matched specialist, not another cosmetic pass. A later controlled replication should preserve all attempts and examine generation variability. Do not silently relabel a post-hoc diagnostic as the original endpoint or remove losses/failures.

## Completed results and verification

H02 completed with person-equal ROC-AUC **0.757195 / 0.730548 / 0.788537** for GPT-5.6 / 6 / 6.1; fixed xDAWN **0.761230**, conventional LDA **0.721891**. All three programs obey the execution/line constraints. GPT-6.1 exceeds this fixed specialist on all ten held-out people, a descriptive result on one source rather than a stable generation/SOTA claim. Independent person-level rank-sum rescoring reproduces all five methods.

The current panel has **19 task IDs, 75 model–slice attempts, 73 valid, two unchanged failures, 152 total records, 146 stored prediction records rescored**. There are 57 generated programs. Active catalog: 96 entries, 19 measured, 49 pending validation, 28 deferred; 77 remain unrun. Existing 18 archival decisions remain intact. The bounded review also corrected measured-task READMEs, method pages, data/source pointers and stale current-status headers while preserving dated historical decisions.

[Findings](../analysis/findings.md), [central summary](../analysis/summary.json), [prediction validation](../analysis/validation-expansion.json), [source-render checks](../analysis/site-source-checks.json). Publication/browser evidence is recorded after deployment.
