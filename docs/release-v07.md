# Preview 0.7: measure variability before widening claims

The suite is a useful, traceable pilot, not yet a paper-ready general-versus-specialist comparison. The [progress assessment](progress-assessment.md) identifies the remaining evidence gaps. This release strengthens one existing endpoint instead of increasing task or category counts.

## H02: repeated code generation and a stronger reference

The original Brain Invaders 2012 split and explicit prompt are unchanged. After inspecting the original results, we froze a [retrospective amendment](../experiments/H02/replication-v1/amendment.md) and its runner/reference hashes in local commit `9c67ae9`, before any of the new generations or tuned-reference fits. Exactly two new submissions per requested model were generated in fresh contexts, without tools or execution feedback. All six pass the 180-second fitting and fewer-than-240-line requirements. No repairs, failed attempts hidden, or best-of-three selection.

Equal-person test ROC-AUC, across the original plus two new submissions:

| Model | Mean | Generation range | Strict valid | Attempts above tuned specialist |
|---|---:|---:|---:|---:|
| gpt-5.6-sol | 0.752374 | 0.746444–0.757195 | 3/3 | 0/3 |
| gpt-6-sol | 0.744027 | 0.730548–0.761932 | 3/3 | 0/3 |
| gpt-6.1-sol | 0.784685 | 0.779295–0.788537 | 3/3 | 3/3 |

The fixed original xDAWN score is **0.761230**. Five-fold training-person validation over 12 xDAWN/template/logistic configurations selects **0.778541** on test, using `{"nfilter": 4, "classes": [0, 1], "C": 10}`. Complete selection/refit/inference takes 56.72 seconds on one numerical thread. Fold covariances, tangent reference and scaling never fit on validation or test people. All candidate OOF scores and the chosen configuration are retained; choice is persisted before test inference/scoring.

GPT-6.1 exceeds the tuned reference on each of its three attempts, but its smallest margin is only 0.000754. Its mean advantage is 0.006145. These are descriptive point differences, not significance or a practical superiority claim. GPT-6 remains below GPT-5.6 in generation mean, so the version trend is not monotonic on this task.

## Denominators and interpretation

- Original suite remains **19 measured tasks, 14 families, 75 model–slice attempts, 73 valid and two failures**. Its reference policy and macro ledger are byte-identical to 0.6.
- Follow-up adds **six model generations and one tuned-reference attempt**. All succeed. There are now 63 generated programs overall, but only H02 has three attempts per model. Do not call these 21 tasks or three new cohorts.
- Independent rank-based rescoring verifies 12 H02 prediction records (nine programs, fixed/tuned specialists and LDA), including seven new files. All 12 candidate training-only OOF validation scores and group-fold separation pass. Combined unique stored prediction files verified across original and follow-up releases: **153**, not 158 (five H02 originals overlap).
- Three generation values support descriptive means/ranges only. Original attempt 1 predates follow-up design. Provider instructions and backend snapshots cannot be fully controlled. Task selection and this sensitivity study are retrospective.
- Specialist search effort, code development and general-model tuning are not matched merely because both have a 180-second numerical timeout. Current global SOTA remains unestablished.

## Website and documentation

H02 has separate **Original results** and **Generation replication** tabs. The follow-up line and bar plots show generation means with min–max whiskers, with fixed and tuned specialists directly named and numerically labeled. Every individual score, valid/strict count and downloadable ledger is available. Whiskers are explicitly not confidence intervals. Cross-task analysis links to the follow-up and retains its original denominators.

All 19 measured task worklogs now lead with current execution status and identify their original mapping statements as historical. This corrects misleading opening text without erasing the audit trail. No frozen scientific contracts or original submissions changed.

[Follow-up results](../experiments/H02/replication-v1/results.md) · [Combined separate ledger](../results/replications/H02.json) · [Verification](../experiments/H02/replication-v1/verification.json) · [Reproduction](reproduce.md) · [Original 0.6 review](release-v06.md)
