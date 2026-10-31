# Cross-task analysis plan and interpretation

## Denominators before averages

Report mapped entries, executable admitted tasks, measured tasks, measured families, slices, biological units, generations and model failures separately. The evidence-map count cannot be a leaderboard denominator. Pairwise comparison uses the intersection of measured cases for the exact pair, track, split and budget class. Missing tasks are missing, not losses or zeros; publish coverage per model so selection is visible. Record deferred tasks as well as candidates.

## Planned summaries

1. **Reliability:** valid completion rate over attempted slices; format-compliant and numerical-valid rates separately. Failed attempts stay in the denominator. For future aggregate loss, define failure penalties prospectively, not after seeing scores.
2. **Within-task model progress:** native metric delta for GPT-6 vs 5.6 and 6.1 vs 6 on paired frozen cases. Show all deltas and reversals. Repeated generations and independent datasets are needed before a stable progress claim. Chronological model names alone do not identify parameter count, training compute, cost or a causal scaling law.
3. **General/reference comparison:** directional wins/losses/ties on matched endpoints, stratified by reference evidence class, supervision/budget and track. A numerical tie tolerance (1e-9 here) is not a scientifically established equivalence margin. Best-of-references selected using test scores is an oracle descriptive envelope; avoid inferential comparisons to it. Report each named reference too.
4. **Family-balanced progress:** average slices within a task, tasks within a family, then families equally. Do not let 94 EEG datasets or five Spikefinder preparations outweigh a single anatomical task. Only aggregate normalized utility if anchor and specialist were frozen and denominator is stable. Proposed utility: direction-adjusted (model-simple)/(specialist-simple); do not clip, skip near-zero denominators, report missingness. The current release deliberately does not produce a mixed-metric universal score.
5. **Practical utility:** Pareto plots for quality vs end-to-end time, labels, compute and memory; distinguish generation latency, fitting and inference. Current estimator timings omit generation and are not end-to-end deployment cost. Online tasks additionally need causal context and p 95 latency.
6. **Scientific validity:** calibrated intervals, type-I error/power, intervention generalization, identifiability and preservation of scientific conclusions. Accuracy cannot substitute for validity.
7. **Stratified hypotheses:** compare data modality/stage, supervision, context length, grouping shift, causal/online constraints, mechanistic equations supplied, and specialist-tool access. These are explanatory hypotheses until adequately sampled; this convenience-selected panel cannot support regression or moderator conclusions.

## Display policy

Bar charts show native task metrics; connected points show the three ordered Sol generations on the same task/slice, with a specialist reference line. X is **model generation order**, not release dates or measured compute. No connecting unrelated benchmarks as time points. Raw data and per-unit values are downloadable. Do not average Pearson, segmentation F1 and parameter MAE. The macro page exposes denominators and computed descriptive comparisons, and explicitly withholds a universal ranking.

## What would count as evidence for broad progress?

A common frozen panel across multiple independent modalities/labs and tasks, repeated generations, matched procedures and label/compute controls, uncertainty clustered by true study unit, and sensitivity to task/family weighting and failures. Preregister meaningful margins per endpoint and correct for multiple primary comparisons. Any published cross-model trend is conditional on tested models and availability; it cannot be extrapolated to all general models or all neuroscience.

## v 0.4 implemented exploratory policy

This amendment documents implemented summaries after some v 0.4 results were visible. It is not a preregistration. Native-score means across different endpoints remain forbidden. For directional win fractions, average slice indicators within task, tasks within family, then families equally. Publish both raw comparison counts and task/family denominators. Reference classes remain separate; C05's five preparations cannot outweigh an entire family. No ratio normalization is computed because strong matched specialist anchors are absent.

Within the admitted panel, failed/missing score pairs are explicitly `failed_or_missing`, kept in the attempted denominator and never imputed as a numerical score. Strict-format sensitivity excludes submitted formatting deviations and publishes the smaller denominator. Completely unrun catalog entries are outside the attempted panel and remain unknown. Thus this refinement distinguishes an admitted failure from an unrun mapped task; neither disappears silently.

Progress aggregates exclude M04 because tiny estimator differences are quadrature ordering, and N05 because deterministic file correctness has a separate denominator. The remaining 12 tasks span 9 families and 16 slices, including semisynthetic H16. One model generation per task and convenience selection do not support significance, causal model-scaling or reliable moderator regression. The 1e−9 tie tolerance is numerical only; meaningful endpoint-specific margins were not prospectively frozen. Biological-unit cluster intervals and repeated-generation uncertainty are withheld where identifiers/replicates are inadequate.

Charts connect only model versions on the same native endpoint. Native line axes adapt and may be truncated; bar axes include zero. A09 twentyarchive runs are retained but only preselected 00 is primary. C05 envelope uses test selection and I10 archived classifier has a different training history. Historical-reference counts must be read with those caveats.

## Preview 0.5 exploratory extension

The fixed primary-reference classes now include local specialists and pretrained specialists. E01 has three source slices averaged within one task; C05 retains five preparations. Model-progress comparisons exclude M04 and N05, and now include synthetic B01; never label this a purely biological aggregate. All comparisons remain descriptive, not preregistered. Failure stays in the denominator; strict-format results use explicit eligible denominators. No synthetic/biological population-wide inference or mixed-native-metric averaging.

## Preview 0.6 sensitivity boundary

H02 contributes one task/slice in existing family H. Its person-equal ROC-AUC is the frozen native primary; correlated epochs do not inflate task or person denominators. B01's post-hoc all-output event F1 is a separately labeled sensitivity; it never replaces the frozen per-GT-unit accuracy in existing reference or progress summaries. Two of three within-B01 model-version directions reverse under that sensitivity, demonstrating metric dependence rather than authorizing a preferred post-hoc primary. All three new H02 submissions are strict-format compliant. Current counts and derived weighting are in the summary JSON.

## Preview 0.9: fully synthetic posterior inference and visible scope control

L06 adds one task with ten shared-design synthetic observations, not ten independently weighted tasks. The fixed primary is their mean 2,000-draw classifier two-sample-test accuracy; secondary sliced Wasserstein-2 remains separate. It tests likelihood-informed posterior construction, not the original simulator-only SBI procedure. Small numerical C2ST wins near chance remain only descriptive point wins under the historical 1e−9 rule. No practical equivalence or significance threshold was set after observing results.

The synthetic-inclusive aggregate retains eligible B01/L06, and excludes M04/N05 from model-version progress as before. The new default observed-data view additionally excludes B01/L06; it also excludes M04/N05 from reference comparisons. A14/H16 still involve observed sources with artificial corruption, so the scope is named precisely and is not claimed to contain only wholly natural targets. Both reference and version-change tables respond to one scope selector. Denominators and computed task/family summaries are exported for both views. This scope display amendment is retrospective; all older records stay unchanged.

## Preview 0.11: batch analysis and contract sensitivity

Seven task IDs add eight slices; E06's temporal-tail and unseen-taxis endpoints reuse the same three programs and training arrays. They are averaged within one task before family weighting. B08 reuses G01 recordings, and A15 has one held-out bird despite twenty recordings. C06 has two test fish; K05 has three test donors and K06 five test mice. These denominators do not justify cross-lab population confidence intervals. B03 is fully synthetic and excluded from the default observed-data view, alongside B01/L06/M04 and deterministic N05.

B08 has a prompt/harness ambiguity: two submitted programs use heapq, rejected by the frozen whitelist although the prompt ambiguously permits ordinary utilities. Preserve both failures and native scores; exclude the entire task from reference and version aggregate claims. This is a retrospective analysis refinement after observing the validation failure, not a preregistered exemption. Raw comparison rows carry aggregate_eligible=false and remain exported for independent sensitivity analysis. Completion totals still include every attempt. No code, prompt or harness is repaired.

C06's predeclared count error and signed bias are reported beside its frozen Pearson primary; the website can switch native plots to relative count error. Amplitude calibration errors prevent interpreting high correlation as calibrated spike counts. This display does not replace the primary or select a favorable endpoint. E06 NLinear is a conventional domain reference with locally altered optimization. K05/K06/A15 references are conventional baselines; their scores cannot establish superiority to a best specialized method. Current global best remains unverified throughout.

Macro statistics are refreshed once per audited batch. Failed methods, format deviations, deferred candidates and archived source decisions stay traceable. The strict-format view excludes the 268-line A15 GPT-5.6 submission; its numerical result remains in the exploratory view. No new mixed-metric mean, significance claim or causal scaling inference is introduced.
