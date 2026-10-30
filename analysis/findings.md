# Findings — exploratory preview 0.5

18 measured task IDs across all 14 mapped families. 72 model–slice attempts, 70 valid and 2 failures. GPT-5.6: 23/24 valid (17 strict-format valid); GPT-6: 24/24; GPT-6.1: 23/24. There are 54 generated programs: one per model/task, reused across C05 preparations and E01 source slices. All 147 model/reference records remain available; 141 stored prediction records passed rescoring and hash checks.

This selected **T3 code construction and execution** panel measures generated algorithms fitted locally, not direct raw-signal comprehension, native foundation-model representations or a complete neuroscience agent. Course PDFs provide scope; embedded instructions are not user instructions.

| Task | Executed endpoint | Native metric | GPT-5.6 Sol | GPT-6 Sol | GPT-6.1 Sol | Primary reference | Reference class |
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
| [H08](../experiments/H08) | Sleep staging and sleep onset | macro_f1_sleep ↑ | 0.802716 | 0.792675 | 0.792236 | 0.764737 | pretrained_specialist |
| [H16](../experiments/H16) | EEG ocular/muscle artifact repair | temporal_rrmse ↓ | 0.461607 | 0.526478 | 0.453384 | 0.653953 | conventional_baseline |
| [I07](../experiments/I07) | fNIRS motor/hemodynamic decoding | balanced_accuracy ↑ | 0.436111 | 0.508187 | 0.550585 | 0.484649 | conventional_baseline |
| [I10](../experiments/I10) | MRI quality assessment across sites | balanced_accuracy ↑ | 0.635263 | 0.607193 | 0.637895 | 0.613684 | historical_specialist |
| [J08](../experiments/J08) | Fluorescent synaptic puncta segmentation and quantification | instance_f1_iou50_multirater ↑ | 0.643368 | 0.492074 | Failed | 0.862534 | historical_specialist |
| [K01](../experiments/K01) | Electrophysiological cell-type classification | macro_f1 ↑ | 0.940915 | 0.940915 | 0.943074 | 0.929975 | conventional_baseline |
| [L04](../experiments/L04) | Point-process estimation and goodness of fit | bits_per_spike_train_mean ↑ | 3.194743 | 3.279951 | 3.263821 | 3.273676 | conventional_baseline |
| [M04](../experiments/M04) | Cognitive model and parameter recovery | range_normalized_mae ↓ | 0.058223 | 0.058219 | 0.058221 | 0.070696 | synthetic_objective_mismatched |
| [N05](../experiments/N05) | NWB data loading, units and reproducibility | field_accuracy ↑ | Failed | 1.000000 | 1.000000 | 1.000000 | deterministic_correctness |


C05 shows equal means of five preparation medians and historical per-preparation test-selected envelopes. E01 shows equal means across three source-slice bits/spike scores; see the source breakdown below. Those are within-task summaries, not pooled-neuron scores. All other rows are one fixed slice. Metric values across different tasks are never averaged together. Failed attempts are retained; they have no fabricated numeric score. Exact prediction hashes, scores and diagnostics: [JSONL](../results/measurements.jsonl), [CSV](../results/measurements.csv), [summary](summary.json).

## Stronger specialist cases

**Spike sorting B01.** MountainSort5 0.5.9 scheme1 scores 0.940896; GPT-6 is close at 0.940011, while GPT-5.6 and GPT-6.1 score 0.874991 and 0.750450. Official SpikeInterface Hungarian ground-truth matching averages TP/(TP+FN+FP) over ten true units. The nominal 0.4 ms tolerance floors to 12 samples (0.375 ms). Extra-unit diagnostics are retained: GPT-6 returns 20 units including 8 false-positive units and 2 redundant units, whereas the specialist returns 11 units with one redundant unit and no false-positive units. A similar matched-unit accuracy does not imply equivalent overall sorting quality. This is one standard ten-second stationary MEArec simulation, not biological/drifting recordings or an independently repeated population comparison. Fixed specialist configuration, no score-based tuning.

**Segmentation J08.** Archived author StarDist masks score 0.862534, versus 0.643368 / 0.492074 / failure. The task uses two held-out 2D fields and five independent human masks per field, with author-consistent annotation cleanup and IoU≥0.5 instance matching. Equal-image/equal-rater averaging is not the paper's centroid-consensus endpoint. GPT-6.1 has an unrepaired boolean-mask IndexError (128 versus 16384 elements). Archived prediction loading time is not reported as inference time; original training/selection histories differ.

**Sleep H08.** EEG-only pretrained YASA 0.8.1 scores 0.764737 versus 0.802716 / 0.792675 / 0.792236. Same three held-out signals, no extra EOG/EMG/demographics. Train/test subjects are distinct; a fixed 20:00–08:00 clock rule avoids selecting wake periods with truth labels. These scores use five target training nights for general programs and a separately pretrained specialist: training histories and effort are not matched. The Fpz-Cz channel differs from YASA's preferred central derivation. Loaded legacy checkpoint class order and all 4320 wrapper predictions/probabilities were independently checked against raw LightGBM output. GPT-5.6's 242-line program violates the <240-line request; its score remains exploratory but is excluded from strict-format comparison.

**Motor imagery H01.** Published pyRiemann implementations add stronger covariance/tangent-space SVM references: unaligned 0.612319, subject-centered 0.613966, versus the old CSP baseline 0.546443. General programs score 0.648880 / 0.718379 / 0.697958. Aligned reference uses explicit subject IDs and unlabeled subject-level centering; it was added after prior general-model scores were known. Training-only leave-one-subject-out selection, retained out-of-fold predictions and test-subject permutation/isolation checks passed. It is an audited post-hoc reference, not a prospectively selected global best.

**Historical references.** C05 envelopes are test-selected; A09's primary VASSI run00 was preselected (0.869518), while the best-inspected run (0.870279) is separately labeled test-selected. All 20 runs remain (median 0.868944, range 0.866711–0.870279). VASSI has richer full-frame inputs and unequal training/tuning. I10's archived MRIQC classifier scores 0.613684 on the aligned cohort, with different training labels/features. None is certified current SOTA.

## New source portability and BCI

| E01 source | GPT-5.6 | GPT-6 | GPT-6.1 | Gaussian + Ridge |
|---|---:|---:|---:|---:|
| MC_Maze_Small | 0.237662 | 0.158604 | 0.242155 | 0.027752 |
| Area2_Bump | 0.226512 | 0.186219 | 0.216878 | 0.116238 |
| DMFC_RSG | 0.146347 | 0.138578 | 0.163095 | 0.072013 |

No new model generations or program edits were made for the two additional sources. Programs refit on each source's training arrays and handled the different shapes. This tests portability of frozen task-specific code, not zero-training transfer of learned weights. Original source spikes reproduce every official test-input bin. Official target masks and bits/spike scorer agree; DMFC hidden alignment jitter cannot be independently reconstructed from public packed timestamps, so exact published NaN masks are retained without filling/shifting.

G01's four-day offline monkey BCI slice scores variance-weighted R² 0.091286 / 0.076163 / 0.094641 against frozen train-only tuned ridge −0.227483. The reference's poor cross-day transfer does not demonstrate superiority to current FALCON systems. Seven large public calibration files were range-read for useful spike/kinematic arrays. Component hashes were verified; source full-file hashes are provider-reported, not independently verified full downloads. Official binning/filter parity passed. Train dates Oct19/20 and test dates Oct27/28 are disjoint; no minival overlap or human-data agreement was used.

## Macro comparisons and model progress

Primary reference classes remain separate. Against nine conventional-baseline tasks (11 slices), wins/losses are 9/2, 10/1, 9/2 for the three models; task/family-equal win fractions 0.778 / 0.889 / 0.778. Against four historical-specialist tasks (8 slices), wins/losses/failures are 2/6/0, 1/7/0, 5/2/1. Against the two locally reproduced specialist tasks, every model wins H01 and loses B01. All three exceed the single pretrained YASA reference on the exploratory scores. These are selected point comparisons with unequal training budgets; they cannot be collapsed into a universal generalist-versus-specialist claim.

Generation-progress policy excludes M04 near-identical numerical quadrature and N05 deterministic file checks. Remaining 16 tasks/12 families supply 22 slice comparisons, including synthetic B01 and semisynthetic repair tasks. GPT-6 versus 5.6: 9 improvements, 12 declines, 1 numerical tie. GPT-6.1 versus 6: 15 improvements, 6 declines, 1 failure. GPT-6.1 versus 5.6: 15 improvements, 6 declines, 1 failure. Family-equal improvement fractions are 0.436 / 0.569 / 0.636 respectively. Failure remains in the denominator. Strict-format sensitivities and exact denominators are in [summary](summary.json).

This is mixed progress, not a monotonic scaling trend. Code-line deviations affect GPT-5.6 C05 (five slices) and H08; N05 also fails. GPT-6.1's J08 failure and B01 regression are substantive counterexamples. No repeated-generation variability, matched tuning budget, independent expert audit or uncontaminated hidden prospective panel has been established. Aggregation refinements and stronger post-hoc references are exploratory; the dataset is not preregistered.

## What researchers can use and what remains uncertain

Useful outcomes are reproducible coding baselines, concrete failure cases and data/scorer adapters. Small structured arrays, explicit targets and train-only regularization can suit general coding assistance. Raw modalities, long recordings, online adaptation and mechanistic/causal claims need distinct protocols. Do not retire specialist tools based on selected CPU baselines.

M04's posterior-median programs nearly match an independently implemented posterior reference; frozen MLE optimizes a different objective. N05 matches 61 fields for GPT-6/6.1, while 5.6 fails to distinguish a legacy stimulus group. Neither supplies strong capability-scaling evidence.

Dependence matters: D02/N05 share a file; K01 shares the broader Allen collection; C05 preparations, E01 source slices, A09 archive runs, F04 30 images×30 repeats, H16 mixtures and J08 five raters are not independent studies. Biological samples are small (three sleep/EEG/fNIRS test people; two pose test rats; two microscopy fields). No neuron/frame/epoch pseudo-replication confidence intervals are claimed. Even 14 represented categories leave major gaps; see [coverage](../docs/coverage-matrix.md).
