# Best observed general procedure versus specialist: methods v1

This study evaluates **neuroscience analysis code generation**: a general model writes a program, which runs locally and may fit a task-specific model. It does not evaluate direct pretrained-model prediction on neural data. This new analysis is separate from the retained model-generation/lag studies and does not modify them.

[Data and source hashes](comparison.json) · [60 task/scope rows](task-comparisons.csv) · [Builder](../../scripts/analyze_specialist_frontier.py) · [Independent checker](../../scripts/check_specialist_frontier.py)

## Selection unit and eligible comparators

The unit is a whole task with its existing equal-slice mean and native better-score direction. Best general is the preferred test-score mean among the four retained repair-assisted procedures (GPT-4.1, GPT-5, GPT-5.6 Sol, GPT-6.1 Sol). Other generations/replication attempts are not added. Best specialist is the preferred complete-method mean among the scored specialist candidates, not an average of per-slice winners.

Eligibility follows explicit specialist identities and the existing historical/local/pretrained-specialist classes. A09 includes all 20 archived VASSI runs, selected post hoc; this differs intentionally from the original preselected run00. B07 considers both scored specialist codecs. C05 considers complete archived specialists/OASIS and excludes Deneux/Speiser where required predictions are missing; it does not synthesize their missing outputs. H02 additionally includes the stronger training-CV xDAWN reference from its same-source follow-up (AUC 0.7785407674558235), without adding extra general-model attempts. Its prediction hashes and group-level score are independently checked by the retained repository checks. This reference supplement is explicit in the new audit and leaves the old comparison unchanged.

Specialist records must cover every original slice exactly once with finite measured scores and the same task metric/direction. On C05, this changes the question from the old per-slice reference envelope to the best complete single method. The old envelope is not a single deployable procedure. Incomplete candidates are recorded with reasons.

Only **14/30 tasks** have an eligible measured specialist. A secondary **all-available-reference** comparison uses all complete scored controls, including conventional baselines, source-inspired domain references, an objective-aligned post-hoc posterior reference and deterministic correctness checks. That secondary table covers 30 tasks and must not be described as 30 specialist comparisons. M01's domain GLM and constant baseline are both eligible there; the lower-loss GLM is selected using the metric's preferred direction. E06 NLinear is retained as a conventional/domain reference rather than relabeled a specialist. No unmatched published leaderboard score is imported.

## Raw and IQR tables

Raw means no size filter, not the absolute value of a difference. The signed native difference is general minus comparator; direction adjustment multiplies it by +1 for higher-is-better and −1 for lower-is-better. Positive is a general-procedure win. Absolute native differences retain their task units in the CSV and cannot be pooled across metrics. Numerical ties use the retained 1e−9 native tolerance.

For each task, compute Q1 and Q3 of the **same four general-model task means**, using inclusive linear interpolation. Keep this scale identical to the prior lag study. The ratio is:

`R = direction-adjusted (best general − best comparator) / (Q3 − Q1)`.

The comparator is not included in the quartiles. For thresholds 0.1 and 0.5, general wins above the positive threshold, comparator wins below the negative threshold, and remaining cases are within band. Boundaries use a 1e−12 ratio tolerance. A raw numerical tie remains within band. Zero IQR with a nonzero difference is not estimable; no epsilon is introduced. Missing specialists remain unavailable and are never scored zero. Each summary explicitly retains the 30-task coverage denominator and the available-comparison count.

The denominator depends on the selected general-model panel. An early failed or poor model can widen IQR and make a real specialist gap look small; tightly clustered general models can make a modest native gap look large. For example, B01's spike-sorting gap is inside 0.1 IQR despite a roughly 0.066 native score deficit. I10's MRIQC ratio is large because the general-model spread is narrow; it is not a universal scientific effect size. Read native values alongside every band.

## Interpretation boundaries

- Both sides are chosen after inspecting test scores. This is an observed frontier/envelope, not prospective selection, an unbiased estimate of future best performance, or a single universally best general model.
- Candidate counts are unequal (four general procedures versus varying specialist pools); training, pretraining, inputs, time budgets and manual debugging differ. Test-set selection can favor either side and is not corrected here.
- All bands are post-hoc descriptive sensitivities, not uncertainty intervals, statistical tests, equivalence margins or measures of randomness. A within-band result does not establish parity.
- Most tasks have limited source and generation replication. Filtered groups are small, overlapping and dependent. No pooled accuracy, scaling law or causal category advantage is estimated.
- L06 retains the existing C2ST lower-is-better convention, but the diagnostic target is 0.5. The 0.4941 versus 0.5056 ordering does not establish sampler superiority. Interpret that row only as a frozen-metric sensitivity; an exclusion sensitivity is included in the report.
- None of the selected comparator scores is verified as the current global best. Historical MRIQC, archived StarDist, unequal-feature VASSI and offline-adapted EEG references require their original caveats. No blanket specialist-replacement claim follows.

## Reproduction

Run `python3 scripts/analyze_specialist_frontier.py`, `python3 scripts/check_specialist_frontier.py`, and `node scripts/check_site.mjs`. No new model calls, fitting, data acquisition or changed benchmark results are involved. The website applies the existing task facets to these saved rows, preserving whole-task aggregation and fixed IQR scales.
