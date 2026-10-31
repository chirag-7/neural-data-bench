# Findings — exploratory preview 0.9

The first-submission panel has 22 measured tasks across 14 mapped families and 84 model–slice attempts: 82 valid predictions and two unrepaired failures. Its 66 generated programs are reused across source slices. All 167 model/reference records include 161 stored predictions/posteriors. The separate H02 follow-up adds six programs and seven prediction files without increasing these macro totals.

The estimand is performance of generated analysis code fitted locally under an exact T3 contract, not native neural representations or universal neuroscience understanding. Current selection, public labels, one generation and unequal reference histories make the results exploratory.

| Task | Executed endpoint | Native metric | GPT-5.6 Sol | GPT-6 Sol | GPT-6.1 Sol | Primary reference | Evidence class |
|---|---|---|---:|---:|---:|---:|---|
| [A09](../experiments/A09) | Frame-level social behavior labels | macro_f1 ↑ | 0.868972 | 0.875946 | 0.880696 | 0.869518 | historical_specialist |
| [A14](../experiments/A14) | Missing pose imputation | rmse_missing ↓ | 0.448549 | 0.436121 | 0.450595 | 2.437099 | conventional_baseline |
| [B01](../experiments/B01) | Spike sorting and event detection | mean_gt_accuracy ↑ | 0.874991 | 0.940011 | 0.750450 | 0.940896 | local_specialist |
| [C05](../experiments/C05) | Calcium-to-spike inference | median_pearson_40ms ↑ | 0.452196 | 0.443305 | 0.467896 | 0.475337 | historical_specialist |
| [D02](../experiments/D02) | Current-to-voltage prediction | rmse_mV ↓ | 0.217776 | 0.217705 | 0.235533 | 0.220786 | conventional_baseline |
| [E01](../experiments/E01) | Neural rate inference and co-smoothing | bits_per_spike ↑ | 0.203507 | 0.161134 | 0.207376 | 0.072001 | conventional_baseline |
| [F04](../experiments/F04) | Retinal or other sensory encoding | poisson_nll ↓ | 1.550632 | 1.624742 | 1.510801 | 1.551457 | conventional_baseline |
| [G01](../experiments/G01) | Robust cross-day motor decoding | r2_variance_weighted ↑ | 0.091286 | 0.076163 | 0.094641 | -0.227483 | conventional_baseline |
| [H01](../experiments/H01) | Motor imagery and noninvasive BCI | balanced_accuracy ↑ | 0.648880 | 0.718379 | 0.697958 | 0.613966 | local_specialist |
| [H02](../experiments/H02) | ERP/P300 target decoding | subject_equal_roc_auc ↑ | 0.757195 | 0.730548 | 0.788537 | 0.761230 | local_specialist |
| [H08](../experiments/H08) | Sleep staging and sleep onset | macro_f1_sleep ↑ | 0.802716 | 0.792675 | 0.792236 | 0.764737 | pretrained_specialist |
| [H16](../experiments/H16) | EEG ocular/muscle artifact repair | temporal_rrmse ↓ | 0.461607 | 0.526478 | 0.453384 | 0.653953 | conventional_baseline |
| [I07](../experiments/I07) | fNIRS motor/hemodynamic decoding | balanced_accuracy ↑ | 0.436111 | 0.508187 | 0.550585 | 0.484649 | conventional_baseline |
| [I10](../experiments/I10) | MRI quality assessment across sites | balanced_accuracy ↑ | 0.635263 | 0.607193 | 0.637895 | 0.613684 | historical_specialist |
| [J08](../experiments/J08) | Fluorescent synaptic puncta segmentation and quantification | instance_f1_iou50_multirater ↑ | 0.643368 | 0.492074 | **Failed** | 0.862534 | historical_specialist |
| [K01](../experiments/K01) | Electrophysiological cell-type classification | macro_f1 ↑ | 0.940915 | 0.940915 | 0.943074 | 0.929975 | conventional_baseline |
| [K04](../experiments/K04) | Cortical-layer label transfer | section_equal_macro_f1_7 classes ↑ | 0.505071 | 0.531942 | 0.550550 | 0.554585 | local_specialist |
| [L04](../experiments/L04) | Point-process estimation and goodness of fit | bits_per_spike_train_mean ↑ | 3.194743 | 3.279951 | 3.263821 | 3.273676 | conventional_baseline |
| [L06](../experiments/L06) | Likelihood-informed synthetic GLM posterior sampling | c2st_accuracy_2000 ↓ (chance 0.5) | 0.512500 | 0.497375 | 0.505600 | 0.494100 | local_specialist |
| [M01](../experiments/M01) | Conditional mouse-choice prediction | mouse_equal_binary_log_loss ↓ | 0.436515 | 0.437584 | 0.436634 | 0.463877 | conventional_domain_reference |
| [M04](../experiments/M04) | Cognitive model and parameter recovery | range_normalized_mae ↓ | 0.058223 | 0.058219 | 0.058221 | 0.070696 | synthetic_objective_mismatched |
| [N05](../experiments/N05) | NWB data loading, units and reproducibility | field_accuracy ↑ | **Failed** | 1.000000 | 1.000000 | 1.000000 | deterministic_correctness |


C05 shows equal means of five preparation medians and historical per-preparation envelopes. E01 shows equal means across three source-specific bits/spike scores. These within-task means are not pooled-neuron scores; no values across different rows are averaged together. Failed attempts receive no invented numeric score. Exact data, scores, units, predictions and errors: [JSONL](../results/measurements.jsonl), [CSV](../results/measurements.csv), [summary](summary.json).

## New posterior-sampling task

| Method | Primary C2ST accuracy ↓ | Secondary sliced W2 ↓ | Sampling seconds |
|---|---:|---:|---:|
| gpt-5.6-sol | 0.512500 | 0.014975 | 4.638 |
| gpt-6-sol | 0.497375 | 0.015708 | 0.867 |
| gpt-6.1-sol | 0.505600 | 0.016329 | 2.470 |
| Local Polya–Gamma Gibbs | 0.494100 | 0.016785 | 5.305 |
| Laplace approximation | 0.546250 | 0.078966 | 0.024 |

The mean primary is a classifier distribution diagnostic with chance target0.5, not prediction accuracy where higher is better. All three generated samplers finish within budget. Near-chance point differences are not evidence of stable superiority; the secondary distribution metric can tell a different story. [Exact task, verification and interpretation](../docs/release-v09.md).

## Two earlier real-data candidates

K04: SingleR 0.5.0 scores 0.554585 seven-class macro-F1, versus 0.505071 / 0.531942 / 0.550550 for Sol 5.6 / 6 / 6.1. The specialist leads all three on this custom donor-held-out split; only one held-out donor underlies four sections. Prepared expression lacks spatial coordinates, and curated layer labels use expression assistance. This is not an unsupervised spatial-clustering benchmark.

M01: mouse-equal binary log-loss is 0.436515 / 0.437584 / 0.436634, versus paper-inspired GLM 0.463877 (lower is better). All three improve over this local domain reference; tiny nonmonotonic version differences do not establish a meaningful ranking.Seventeen test mice share labs with 83 training mice. Known blockprior and observed five-trial histories define conditional forecasting, not autonomous rollout. Disjoint six-trial blocks ensure no test target leaks through a later history.

All ten new prediction files were independently rescored. The float32 GLM reference differs from float64 arithmetic by9.07e−9 mean/5.42e−8max-permouse, below one float32epsilon; frozen scores/predictions retained. Other new metrics agree to1e−12. [Release/source checks](../docs/release-v08.md), [K04 worklog](../experiments/K04/worklog.md), [M01 worklog](../experiments/M01/worklog.md).

## Spike sorting: a close primary score can hide a serious failure

| Method | Frozen mean GT-unit accuracy | Post-hoc all-output event F1 | All-event precision | TP / FP / FN |
|---|---:|---:|---:|---|
| GPT-5.6 Sol |0.874991|0.900000|0.998369|612 /1 /135|
| GPT-6 Sol |0.940011|0.599751|0.434495|723 /941 /24|
| GPT-6.1 Sol |0.750450|0.868051|0.868633|648 /98 /99|
| MountainSort5 |0.940896|0.962060|0.973937|710 /19 /37|

The primary metric averages accuracy over ten true units. Extra unmatched output clusters can emit many events without entering that average. GPT-6 returns 1, 664 events versus 747 true events, while MountainSort5 returns 729. The secondary audit keeps the original Hungarian mapping and 12 sample tolerance, counts every emitted event, and independently checks matching and conservation. Two of three model-version directional comparisons reverse between these metrics on this slice.

The audit was designed **after results were visible**. It is a sensitivity, not a changed frozen endpoint or a new independent experiment. Event F1 weights firing events; the original metric weights true units. Both have limitations. The website offers both plots for either metric, with direct specialist names/scores; directory/macro summaries retain the frozen primary. [Amendment and implementation](../experiments/B01/secondary-amendment.md). One 10 second stationary simulation supports no drift/real-recording/animal generalization or global-SOTA claim.

## New P300 task: ten independent held-out people

H02 uses original CC BY 4.0 Brain Invaders 2012 calibration data: 25 people, 15 train/10 test, 11, 481/7, 663 epochs. All publisher ZIP MD 5 s and independent MAT/CSV event markers agree. GroundFz is removed; no stimulus marker/time/identifier is a predictor. Only geometric boundary events are excluded. Training-person IDs are supplied equally for grouped validation; test people/labels are scorer-only.

Person-equal ROC-AUC is 0.757195 /0.730548 /0.788537, fixed xDAWN/tangent-space/logistic reference 0.761230, conventional shrinkage-LDA 0.721891. GPT-6.1 exceeds xDAWN on all ten sampled people; 5.6 does so on 6/10 despite a slightly lower mean, 6 on 2/10. These are descriptive paired outcomes, not an externally replicated significance claim. All three submissions obey the 240 line/180 second constraints. Independent float64 rank-sum rescoring agrees with every stored person AUC and mean to 1e−12.

The fixed specialist uses the same train/test signals and train-only fitting. General programs select among shrinkage/ensemble choices using training-person validation; total tuning and library effort are not matched. One public source, overlapping within-person epochs and one generation prevent a global-specialist or stable scaling conclusion. This tests offline target ranking, not online symbol selection or clinical BCI. [Protocol](../experiments/H02/protocol.md), [verification](../experiments/H02/result-verification.json).

## H02 follow-up: variability and reference sensitivity

Two further no-feedback submissions per model give three-attempt means **0.752374 / 0.744027 / 0.784685**. All nine H02 programs are numerically and strict-format valid. The additional xDAWN configuration selected by training-person-only five-fold CV scores **0.778541**, compared with fixed **0.761230**. All three GPT-6.1 attempts exceed the tuned reference, but the smallest margin is 0.000754. GPT-6's range is 0.730548–0.761932, illustrating why a single point was insufficient. Means/ranges over three generations do not establish stable rankings or significance.

This is a retrospective follow-up on the same 25-person source, not another dataset/task. Original attempt 1 predates follow-up design. All six new programs, all 12 specialist validation configurations, predictions, provenance and independent rank-AUC checks are retained. The original 75-attempt records remain unchanged; current summaries below add subsequent tasks and explicit data scopes. [Follow-up results and every attempt](../experiments/H02/replication-v1/results.md), [separate combined ledger](../results/replications/H02.json).

## Reference comparisons remain stratified

### Observed-data sources (website default)

| Reference class | Tasks / families / slices | GPT-5.6 win / loss / tie / failure | GPT-6 | GPT-6.1 |
|---|---|---|---|---|
| conventional_baseline | 9 / 9 / 11 | 9 / 2 / 0 / 0 | 10 / 1 / 0 / 0 | 9 / 2 / 0 / 0 |
| conventional_domain_reference | 1 / 1 / 1 | 1 / 0 / 0 / 0 | 1 / 0 / 0 / 0 | 1 / 0 / 0 / 0 |
| historical_specialist | 4 / 4 / 8 | 2 / 6 / 0 / 0 | 1 / 7 / 0 / 0 | 5 / 2 / 0 / 1 |
| local_specialist | 3 / 2 / 3 | 1 / 2 / 0 / 0 | 1 / 2 / 0 / 0 | 2 / 1 / 0 / 0 |
| pretrained_specialist | 1 / 1 / 1 | 1 / 0 / 0 / 0 | 1 / 0 / 0 / 0 | 1 / 0 / 0 / 0 |

### Including fully synthetic tasks

| Reference class | Tasks / families / slices | GPT-5.6 win / loss / tie / failure | GPT-6 | GPT-6.1 |
|---|---|---|---|---|
| conventional_baseline | 9 / 9 / 11 | 9 / 2 / 0 / 0 | 10 / 1 / 0 / 0 | 9 / 2 / 0 / 0 |
| conventional_domain_reference | 1 / 1 / 1 | 1 / 0 / 0 / 0 | 1 / 0 / 0 / 0 | 1 / 0 / 0 / 0 |
| deterministic_correctness | 1 / 1 / 1 | 0 / 0 / 0 / 1 | 0 / 0 / 1 / 0 | 0 / 0 / 1 / 0 |
| historical_specialist | 4 / 4 / 8 | 2 / 6 / 0 / 0 | 1 / 7 / 0 / 0 | 5 / 2 / 0 / 1 |
| local_specialist | 5 / 4 / 5 | 1 / 4 / 0 / 0 | 1 / 4 / 0 / 0 | 2 / 3 / 0 / 0 |
| pretrained_specialist | 1 / 1 / 1 | 1 / 0 / 0 / 0 | 1 / 0 / 0 / 0 | 1 / 0 / 0 / 0 |
| synthetic_objective_mismatched | 1 / 1 / 1 | 1 / 0 / 0 / 0 | 1 / 0 / 0 / 0 | 1 / 0 / 0 / 0 |

These are descriptive point counts, not significance or equivalence. Default scope excludes B01/L06/M04/N05; artificial corruptions of observed data remain included. The synthetic-inclusive table retains the frozen primary-reference policy. In particular, near-chance L06 C2ST point counts should not be interpreted as meaningful posterior-quality ordering. Exact task/family fractions and strict-format denominators are in [summary](summary.json). Historical envelopes, unequal inputs/pretraining and reference selection histories remain explicit per task. Current global SOTA and matched-total-effort superiority remain unestablished.

## Model-version progress remains mixed

### Observed-data sources (website default)

| Model pair | Improved | Declined | Numerical ties | Failed/missing | Slices / tasks / families | Family-equal improvement fraction |
|---|---:|---:|---:|---:|---|---:|
| gpt-5.6-sol → gpt-6-sol | 9 | 14 | 1 | 0 | 24 / 18 / 12 | 0.387500 |
| gpt-6-sol → gpt-6.1-sol | 18 | 5 | 0 | 1 | 24 / 18 / 12 | 0.666667 |
| gpt-5.6-sol → gpt-6.1-sol | 17 | 6 | 0 | 1 | 24 / 18 / 12 | 0.643056 |

### Including eligible fully synthetic tasks

| Model pair | Improved | Declined | Numerical ties | Failed/missing | Slices / tasks / families | Family-equal improvement fraction |
|---|---:|---:|---:|---:|---|---:|
| gpt-5.6-sol → gpt-6-sol | 11 | 14 | 1 | 0 | 26 / 20 / 13 | 0.434615 |
| gpt-6-sol → gpt-6.1-sol | 18 | 7 | 0 | 1 | 26 / 20 / 13 | 0.615385 |
| gpt-5.6-sol → gpt-6.1-sol | 18 | 7 | 0 | 1 | 26 / 20 / 13 | 0.593590 |

Both version-change views exclude M04 quadrature ordering and N05 deterministic correctness. The synthetic-inclusive view retains B01 and L06. Observed-data scope includes artificial corruption in A14/H16; it does not imply every target is wholly natural. Failures remain in the denominator. Directional fractions are not effect sizes, significance, practical-equivalence statements or causal scaling laws. Near-chance posterior C2ST values and B01 metric sensitivity limit interpretation.

## Other material task limits

| Task | Boundary that matters |
|---|---|
| A09 | Processed pose context; archived VASSI has richer full-frame inputs and unequal training.20 archive runs are not 20 tasks. |
| A14 | Artificial pose gaps in real motion, only two test rats; optional DISKweight ZIP was unusable despite matching publisher MD 5. |
| C05 | Historical 2017 test-selected envelopes; preparation 1 is prior development evidence; same code refitted on five preparations. |
| D02 | One cell, passive current interpolation; measured pre-stimulus rest is allowed; no spiking/cross-cell result. |
| E01 | Three official sources, frozen-program portability with first-source dimensions in the prompt. DMFCexact official NaNmask retained; hidden jitter cannot be reconstructed fully from packed public timestamps. |
| F04 | One retinal preparation, 30 test images repeated 30 times; identical images give identical expected rates.900 rows are not 900 independent images. |
| G01 | Four-day offline monkey BCI slice, not official FALCONleaderboard/closed-loop control; range-read components verified, full hashes provider-reported. |
| H01 | Three test people; post-hoc pyRiemann alignment reference has explicit group IDs/offline unlabeled adaptation. |
| H08 | Three test nights/people, Fpz-Cz rather than YASA's preferred central derivation; specialist pretraining differs; GPT-5.6 exceeds line limit. |
| H16 | Semisynthetic clean+EOGrepair, disjoint components but no participant IDs. |
| I07 | Condition/session confounding remains; three test people. |
| I10 | Processed IQMs, not raw MRI; historical classifier'straining labels/features differ. |
| J08 | Two 2 Dfields×fivehuman raters, unresolved independent animal identities; GPT-6.1's IndexError remains unrepaired. |
| K01 | Electrophysiology features predict morphology, not broad molecular/cell-type foundation-model performance. |
| L04 | One place-cell count-encoding task, not full goodness-of-fit/causal recovery. |
| M04 | Synthetic known Q-learning equations; posterior estimates nearly agree; frozen MLEoptimizes another objective. |
| N05 | One legacy NWBfile shared with D02, 61 fields; GPT-5.6 fails, 6/6.1 match all fields.61 fields are not 61 independent files. |

No frame/neuron/epoch pseudo-replication intervals are claimed. Open-weight/native image/video/world models, raw drifting voltage, clinical/general causal/control perspectives and much of molecular/anatomical neuroscience remain unexecuted. The[coverage map](../docs/coverage-matrix.md) is explicit about those gaps. Useful outputs are reproducible algorithm baselines, concrete failure modes and traceable data/scorers, not a universal model ranking or completed paper.

## Observed-data versus synthetic-inclusive summaries

The default website analysis now excludes fully synthetic B01/L06/M04 and deterministic N05; artificial corruption of observed inputs remains explicit. The synthetic-inclusive view is still available. This retrospective display change does not alter prior scores. All native deltas and task/family denominators are exported; no universal mixed-metric score or significance claim is made. [Policy](../docs/macro-analysis-plan.md).
