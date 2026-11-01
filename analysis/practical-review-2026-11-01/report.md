# Version progress, repairs and practical model choice

Analysis revision 1 November 2026; original scientific snapshot 0.11. This is an exploratory study of **models generating analysis programs**, not direct neural-signal understanding. All 30 measured tasks / 14 families now have a fresh primary-source specialist review. No new model generations were made for this revision. Numerical recovery, format compliance, current-specialist evidence and production suitability remain separate questions.

## Quantitative findings: progress is uneven

GPT-6 is mixed relative to GPT-5.6. GPT-6.1 has more positive task-native point changes than either older version, but is worse on a substantial minority. Neither “all benchmarks improve” nor “everything is flat” describes the data. Aggregate cancellation can hide large opposing changes; a tie in win counts is not task-level equivalence.

The original first-attempt panel, including over-limit programs as numeric outcomes:

| Scope | Newer vs older | Better | Worse | Numerical tie | Incomplete |
|---|---|---:|---:|---:|---:|
| all_measured_tasks | gpt-6-sol vs gpt-5.6-sol | 14 | 13 | 1 | 2 |
| all_measured_tasks | gpt-6.1-sol vs gpt-5.6-sol | 20 | 7 | 0 | 3 |
| all_measured_tasks | gpt-6.1-sol vs gpt-6-sol | 17 | 10 | 1 | 2 |
| observed_data_tasks | gpt-6-sol vs gpt-5.6-sol | 11 | 12 | 1 | 0 |
| observed_data_tasks | gpt-6.1-sol vs gpt-5.6-sol | 18 | 5 | 0 | 1 |
| observed_data_tasks | gpt-6.1-sol vs gpt-6-sol | 17 | 6 | 0 | 1 |

Observed-data scope excludes B01/B03 synthetic fixtures, B08 ambiguous whitelist, L06 synthetic posterior diagnostic, M04 synthetic recovery and N05 deterministic correctness. It contains 24 tasks / 13 families. Each table cell counts the direction of one task's equal-slice native mean. This differs from the previous family-balanced mean of slice directions. Failures remain incomplete here, rather than being replaced by zero or silently removed. Tasks and sources are correlated; do not treat these counts as 30 independent experimental replications.

The original family-balanced analysis remains unchanged: net signed direction −0.0654 for 6 vs 5.6, +0.2154 for 6.1 vs 5.6 and +0.2179 for 6.1 vs 6. Conditional family sign-flip diagnostics give p=0.8086, 0.4155 and 0.4463; Holm adjustment gives 1.0 for all three. The diagnostics assume independent symmetric family contrasts, not random sampling of neuroscience tasks. These data do **not** establish a general improvement law; they also do not establish equivalence or absence of progress. [Full assumptions and strict-compliance sensitivities](../macro-patterns/methods.md).

### Where improvement is most consistent, and where it reverses

- **Cell and molecular tasks K01/K04/K05/K06:** all four have higher GPT-6.1 point performance than both older versions. This is a post-hoc category signal across four different endpoints, not a validated universal rule. SingleR still leads all three on K04. K05 is supervised fraction regression rather than standard unsupervised/reference-based deconvolution. K06 is waveform-only; a full pretrained cell-typing model may use additional information or overlapping source units.
- **Behavior:** A09 and A15 improve across both version steps; A14 pose imputation peaks at GPT-6. Acoustic interval detection is a narrow same-bird test, not general behavior recognition.
- **Electrical tasks:** B03 drift error increases from 3.604 to 4.418 to 5.275 µm on its synthetic fixture. B07 compression favors GPT-6. After the B08 harness correction, GPT-5.6 is best. These do not support monotonic electrical-task progress.
- **EEG:** H01 motor imagery peaks at GPT-6; H02 P300 favors 6.1; H08 staging declines across versions; H16 artifact repair favors 6.1. Individual tasks, not an EEG-wide recommendation, are supported.
- **Population/sensory/decoding:** E01, F04 and G01 favor 6.1 but dip at 6; E06 improves in its equal-slice mean, while its unseen taxis slice worsens from 6 to 6.1. Aggregate improvement does not mean robustness to each distribution shift.
- **Near-flat candidates:** M04 compares nearly identical known-equation numerical estimators. M01 log loss is 0.436515 / 0.437584 / 0.436634; such small differences need a prospective meaningful margin and independent repeats. N05 reaches the 1.0 correctness ceiling after repair. L06's C2ST is near chance; tiny ordering there does not establish posterior superiority.

### Slopes and flatness

The website shows all three native scores, both stepwise changes, and the direction-adjusted endpoint slope `(score_6.1 − score_5.6)/2` after orienting higher-is-better. Version labels use ordinal positions 0/1/2. Units are **native metric per ordinal version step**. These are descriptive slopes, not slopes per month, compute or dollar, and cannot forecast when specialists will be surpassed. Three versions, mostly one generated program each, are insufficient to fit a defensible scaling law. Different metrics' slopes are never pooled. Numerical equality uses 1e−9 only for display; practical or statistical equivalence has not been demonstrated.

## Quantitative + qualitative findings: when to try a general program

**No task currently supports an unconditional switch from the best available specialist.** This does not mean the general programs are useless. It means current-best matched comparison, source/generation replication and operational constraints have not all been established. Trial decisions can be narrower than a scientific claim of superiority.

At least one of the three general programs beats the declared primary reference in **23/30 original tasks**, or **24/30 with repairs**. Split by reference strength, this is **8/14 named historical/local/pretrained specialist tasks** originally, **9/14 with repairs**, and **14/14 ordinary conventional/domain-reference tasks** in both views. The remaining two tasks use an objective-mismatched synthetic mathematical reference and deterministic correctness. These are post-hoc any-of-three point wins, include numeric format deviations and B03's synthetic fixture, and are not the performance of a prospectively selected general model. The strong difference by reference class shows why “general beats specialist” cannot be inferred from the overall win fraction. [Exact denominators, classes and task IDs](reference-point-wins.csv).

1. **B07 offline compression is the strongest narrow engineering candidate.** GPT-6 uses 6.901698 bits/sample against pinned WavPack 7.690052: about 10.25% smaller on the 16 tested byte-exact chunks. All saved payloads were independently decoded. Encoding takes about 9.02 s vs 4.61 s in the recorded run, so smaller files cost about 1.96× the encode time. Only ~0.137 s from each recording is tested, making header/chunk effects important. Trial the fixed generated codec on held-out long recordings with storage/throughput/portability checks; retain WavPack until that succeeds. [Protocol and evidence](../../experiments/B07/protocol.md).
2. **B08 event compression:** after the harness-only fix, unchanged GPT-5.6/6 programs use 7.585598/7.693067 bits/event vs Spikepack 8.142312 and 6.1 8.636802. Every retained payload independently decodes (35/35). This is an input-matched pilot win over a named specialist on seven recordings from one monkey, not proof of a universally better spike format. Container metadata, longer recordings, exact unit/order preservation and time-error budget still matter.
3. **H02 P300 is a candidate for dataset-specific evaluation.** The separate three-generation follow-up gives mean AUC 0.784685 for 6.1 versus train-only-selected xDAWN 0.778541; all three 6.1 attempts exceed it, with minimum advantage only 0.000754. This is one public dataset, not independent confirmation across labs. Stronger ERP classifiers are now documented. [Follow-up](../../experiments/H02/replication-v1/results.md).
4. **C06 calcium inference demonstrates the importance of the target.** General programs beat the local OASIS reference on correlation and count error here, but their own relative count errors remain large. A high correlation does not justify calibrated spike-count use. Retrained, source-excluded CASCADE/ENS2/SpikeSSL is a stronger next comparison.
5. **A09 behavior, H08 sleep staging and I10 MRI quality:** wins are against archived or restricted-input specialist references. Reproduce modern methods under matched inputs and source-overlap controls before replacing tools. YASA restricted to this EEG channel is not a test against multimodal sleep staging.
6. **Keep specialist-first workflows for K04 cortical transfer, J08 puncta segmentation, C05 archived spike inference and L06 posterior inference.** Tested strong references lead all general programs on their primary endpoints; repaired J08 remains well behind archived StarDist. B01 also needs all-output spike accounting: nearly matching per-GT-unit accuracy hides many excess spikes.

The all-task matrix below identifies exactly which reference was beaten. An ordinary ridge/GLM/interpolation reference is not a certified strongest specialist. Source-specific recommendations and candidate information/compute mismatches are in every linked review.

| Task | Tested reference | General programs above tested reference | Next specialist comparison |
|---|---|---|---|
| [A09](../../literature/specialist-review-2026-11-01/A09.json) | vassi-run-00 (historical_specialist) | gpt-6-sol, gpt-6.1-sol | VASSI; MABe2021 Top-1 ensemble; TREBA + pose classifier |
| [A14](../../literature/specialist-review-2026-11-01/A14.json) | task-baseline (conventional_baseline) | gpt-5.6-sol, gpt-6-sol, gpt-6.1-sol | DISK Transformer / bidirectional GRU; MarkerBasedImputation / OptiPose / Keypoint-MoSeq; DANNCE |
| [A15](../../literature/specialist-review-2026-11-01/A15.json) | task-baseline (conventional_baseline) | gpt-5.6-sol, gpt-6-sol, gpt-6.1-sol | DAS; TweetyNet; WhisperSeg |
| [B01](../../literature/specialist-review-2026-11-01/B01.json) | mountainsort5 (local_specialist) | none | Kilosort4; DARTsort; MountainSort5 |
| [B03](../../literature/specialist-review-2026-11-01/B03.json) | task-baseline (local_specialist) | gpt-5.6-sol, gpt-6-sol | Current DREDge AP; MEDiCINe rigid; Kilosort4 datashift |
| [B07](../../literature/specialist-review-2026-11-01/B07.json) | wavpack-high (local_specialist) | gpt-5.6-sol, gpt-6-sol, gpt-6.1-sol | WavPack high/very-high with extra processing; FLAC; Blosc/Zstd with reversible time/space delta |
| [B08](../../literature/specialist-review-2026-11-01/B08.json) | spikepack (local_specialist) | none | Spikepack Blosc-shard; Spikepack Zarr container; Per-unit delta + entropy coding |
| [C05](../../literature/specialist-review-2026-11-01/C05.json) | deneux; friedrich; rupprecht (historical_specialist) | none | CASCADE / CascadeTorch; ENS2; SpikeSSL |
| [C06](../../literature/specialist-review-2026-11-01/C06.json) | task-baseline (local_specialist) | gpt-5.6-sol, gpt-6-sol, gpt-6.1-sol | CASCADE / CascadeTorch; ENS2; SpikeSSL |
| [D02](../../literature/specialist-review-2026-11-01/D02.json) | task-baseline (conventional_baseline) | gpt-5.6-sol, gpt-6-sol | Training-only passive RC / constrained multi-exponential response; Allen GLIF and perisomatic/all-active models; CoMParE |
| [E01](../../literature/specialist-review-2026-11-01/E01.json) | task-baseline (conventional_baseline) | gpt-5.6-sol, gpt-6-sol, gpt-6.1-sol | LangevinFlow; AutoLFADS / NDT / STNDT / RNN_F; S5 |
| [E06](../../literature/specialist-review-2026-11-01/E06.json) | task-baseline (conventional_domain_reference) | gpt-5.6-sol, gpt-6-sol, gpt-6.1-sol | POCO; Time-Mix / TSMixer / TiDE; Volumetric U-Net |
| [F04](../../literature/specialist-review-2026-11-01/F04.json) | task-baseline (conventional_baseline) | gpt-5.6-sol, gpt-6.1-sol | Goldin source CNN / contrast-sensitive encoding models; OpenRetina core/readout CNN; Regularized LN/Poisson GLM |
| [G01](../../literature/specialist-review-2026-11-01/G01.json) | task-baseline (conventional_baseline) | gpt-5.6-sol, gpt-6-sol, gpt-6.1-sol | NDT3 pretrained transformer; SPINT; APST |
| [H01](../../literature/specialist-review-2026-11-01/H01.json) | pyriemann-aligned (local_specialist) | gpt-5.6-sol, gpt-6-sol, gpt-6.1-sol | CBraMod; REVE; MIRepNet |
| [H02](../../literature/specialist-review-2026-11-01/H02.json) | xdawn-tslr (local_specialist) | gpt-6.1-sol | xDAWN covariance → tangent-space SVM; Riemannian Means Field classifier with xDAWN; CBraMod / REVE ERP fine-tuning |
| [H08](../../literature/specialist-review-2026-11-01/H08.json) | yasa-eeg (pretrained_specialist) | gpt-5.6-sol, gpt-6-sol, gpt-6.1-sol | SleepGPT; SleepFM-Clinical; SleepFM-2 |
| [H16](../../literature/specialist-review-2026-11-01/H16.json) | task-baseline (conventional_baseline) | gpt-5.6-sol, gpt-6-sol, gpt-6.1-sol | EEGdenoiseNet original CNN/RNN models; Gated WGAN with multi-scale/multi-domain features; FARU-Net |
| [I07](../../literature/specialist-review-2026-11-01/I07.json) | task-baseline (conventional_baseline) | gpt-6-sol, gpt-6.1-sol | MtReNIRS; 67-dataset fNIRS corpus/dataloaders; Training-only regularized OD temporal decoder / SVM |
| [I10](../../literature/specialist-review-2026-11-01/I10.json) | mriqc-rfc-2017 (historical_specialist) | gpt-5.6-sol, gpt-6.1-sol | Archived original MRIQC classifier, locally rescored; TabPFN-3.5; TabICLv2 |
| [J08](../../literature/specialist-review-2026-11-01/J08.json) | task-baseline (historical_specialist) | none | Archived SynAPSeg 2D StarDist predictions; SynAPSeg fine-tuned Cellpose-SAM; Cellpose-SAM v2 / CellposeDINO |
| [K01](../../literature/specialist-review-2026-11-01/K01.json) | task-baseline (conventional_baseline) | gpt-5.6-sol, gpt-6-sol, gpt-6.1-sol | TabPFN-3.5; TabICLv2; Regularized boosted-tree / kernel classifier panel |
| [K04](../../literature/specialist-review-2026-11-01/K04.json) | singler (local_specialist) | none | SingleR 0.5.0 frozen reference; later release/tuning separate; scGPT / Nicheformer expression representations; Novae / GraphST / spatial domain models |
| [K05](../../literature/specialist-review-2026-11-01/K05.json) | task-baseline (conventional_baseline) | gpt-6.1-sol | BisqueRNA / hspe with Mean Ratio markers; DECONVersation with Geneformer / Cell2Sentence embeddings; BayesPrism / InstaPrism, MuSiC, CIBERSORTx |
| [K06](../../literature/specialist-review-2026-11-01/K06.json) | task-baseline (conventional_baseline) | gpt-5.6-sol, gpt-6-sol, gpt-6.1-sol | WaveMAP plus training-only supervised label transfer; CEED waveform encoder; PhysMAP waveform-only ablation |
| [L04](../../literature/specialist-review-2026-11-01/L04.json) | task-baseline (conventional_baseline) | gpt-6-sol | NeMoS spline/tensor-product Poisson GLM; Poisson generalized additive model with direction interaction; Spike-history / population latent neural models |
| [L06](../../literature/specialist-review-2026-11-01/L06.json) | polya-gamma (local_specialist) | none | Independent NUTS/HMC on exact logistic likelihood; Longer independently initialized Polya–Gamma chains; sbi FMPE / NPSE / NPE |
| [M01](../../literature/specialist-review-2026-11-01/M01.json) | behavioral-glm (conventional_domain_reference) | gpt-5.6-sol, gpt-6-sol, gpt-6.1-sol | Regularized multi-lag task-specific behavioral GLM; IBL ActionKernel / StimulusKernel / OptimalBayesian models; PsyTrack / GLM-HMM strategy model |
| [M04](../../literature/specialist-review-2026-11-01/M04.json) | canonical-mle (synthetic_objective_mismatched) | gpt-5.6-sol, gpt-6-sol, gpt-6.1-sol | Exact-likelihood bounded quadrature posterior median; HSSM choice-only RL/custom likelihood; BayesFlow 2 / sbi posterior estimator |
| [N05](../../literature/specialist-review-2026-11-01/N05.json) | task-baseline (deterministic_correctness) | none | Direct HDF5 extraction with independent unit/timing implementation; PyNWB current validated I/O; NWBInspector |

## Qualitative findings: the current-specialist search changes the next experiment

The review records queries, primary links, dates where verified, endpoint compatibility, negative findings and next comparators for every measured task. It identifies current DREDge presets (older SpikeInterface presets remain in the original pilot), modern latent population models, contemporary calcium/event methods, sleep/EEG foundations and new cell-typing contenders. Examples: [DREDge official code](https://github.com/evarol/dredge), [NLB official challenge and method links](https://neurallatents.github.io/challenge.html), [AIND compression benchmark](https://github.com/AllenNeuralDynamics/ephys-compression). The NLB challenge is closed; its published leaderboard snapshot and now-public test data are not a new blind evaluation.

The search does not yield a single defensible current global winner on any of our 30 custom contracts. Some endpoints have no official leaderboard; others alter inputs, split, metric, runtime or allowed pretraining. A new paper does not automatically outperform an older method. Modern pretrained models with extra channels, video, ISIs, gene identities or test-source exposure belong in explicitly different information tiers. Read the per-task review before choosing a comparator.

This revision contains **137 candidate entries and 166 distinct primary-source URLs** across 30 task reviews. These are source associations and candidate entries, not counts of unique papers/models or proof of exhaustive coverage. All scores in the plots still come from locally executed or explicitly archived matched outputs. No unmatched paper/leaderboard number has been imported as a comparable score. [Full specialist matrix](specialist-matrix.csv), [source ledger](specialist-source-ledger.json), [coverage counts](specialist-coverage.json).

## Repair-assisted sensitivity: usability, not fresh model capability

Four model runtime failures are recovered in a separate track: B08's two whitelist rejections, J08's shape bug and N05's link traversal. Only three meet the original line cap; repaired N05 has 265 lines. B08 changes only the harness; J08 and N05 are human/Codex-debugged programs. Selective post-hoc debugging is not an unbiased comparison of original model generation ability. Original attempts and the old macro panel remain intact.

| Scope | Newer vs older | Better | Worse | Numerical tie | Incomplete |
|---|---|---:|---:|---:|---:|
| all_measured_tasks | gpt-6-sol vs gpt-5.6-sol | 14 | 14 | 2 | 0 |
| all_measured_tasks | gpt-6.1-sol vs gpt-5.6-sol | 20 | 9 | 1 | 0 |
| all_measured_tasks | gpt-6.1-sol vs gpt-6-sol | 18 | 11 | 1 | 0 |
| observed_data_tasks | gpt-6-sol vs gpt-5.6-sol | 11 | 12 | 1 | 0 |
| observed_data_tasks | gpt-6.1-sol vs gpt-5.6-sol | 18 | 6 | 0 | 0 |
| observed_data_tasks | gpt-6.1-sol vs gpt-6-sol | 18 | 6 | 0 | 0 |

Four C05 archived reference outputs genuinely lack finite values on required support. Their official legacy scorer accepts partial coverage, which differs from our complete-output contract. Padding, interpolating, dropping target support or changing the scoring contract would not recover missing author predictions. They remain explicitly unresolved; obtain/rerun complete predictions under a prospective contract if needed. [Repair methods, verification and attempt history](../../experiments/repairs-v1/README.md).

## Every task's original native trajectory

| ID | Metric (direction) | 5.6 | 6 | 6.1 | Version trajectory |
|---|---|---:|---:|---:|---|
| [A09](../../literature/specialist-review-2026-11-01/A09.json) | macro_f1 (higher) | 0.86897195 | 0.87594631 | 0.88069602 | both steps improve |
| [A14](../../literature/specialist-review-2026-11-01/A14.json) | rmse_missing (lower) | 0.44854936 | 0.43612087 | 0.45059489 | peaks at GPT-6 |
| [A15](../../literature/specialist-review-2026-11-01/A15.json) | recording_macro_event_f1_20ms_onset_20ms_or_20pct_offset (higher) | 0.98631183 | 0.98685456 | 0.99207954 | both steps improve |
| [B01](../../literature/specialist-review-2026-11-01/B01.json) | mean_gt_accuracy (higher) | 0.87499051 | 0.94001146 | 0.75045045 | peaks at GPT-6 |
| [B03](../../literature/specialist-review-2026-11-01/B03.json) | recording_mean_motion_rmse_um (lower) | 3.6041552 | 4.4182637 | 5.2750984 | both steps regress |
| [B07](../../literature/specialist-review-2026-11-01/B07.json) | encoded_bits_per_int16_sample (lower) | 7.0198301 | 6.9016978 | 7.2145891 | peaks at GPT-6 |
| [B08](../../literature/specialist-review-2026-11-01/B08.json) | mean_encoded_bits_per_event_50us (lower) | failed/incomplete | failed/incomplete | 8.6368016 | incomplete original attempts |
| [C05](../../literature/specialist-review-2026-11-01/C05.json) | median_pearson_40ms (higher) | 0.45219612 | 0.44330525 | 0.46789571 | dips at GPT-6 |
| [C06](../../literature/specialist-review-2026-11-01/C06.json) | animal_mean_neuron_pearson_smoothed200ms (higher) | 0.85641544 | 0.8465793 | 0.86759199 | dips at GPT-6 |
| [D02](../../literature/specialist-review-2026-11-01/D02.json) | rmse_mV (lower) | 0.21777564 | 0.21770548 | 0.23553334 | peaks at GPT-6 |
| [E01](../../literature/specialist-review-2026-11-01/E01.json) | bits_per_spike (higher) | 0.20350701 | 0.16113406 | 0.20737614 | dips at GPT-6 |
| [E06](../../literature/specialist-review-2026-11-01/E06.json) | mse_dff (lower) | 0.0027376365 | 0.0026275243 | 0.0025069204 | both steps improve |
| [F04](../../literature/specialist-review-2026-11-01/F04.json) | poisson_nll (lower) | 1.5506315 | 1.6247416 | 1.5108014 | dips at GPT-6 |
| [G01](../../literature/specialist-review-2026-11-01/G01.json) | r2_variance_weighted (higher) | 0.091285544 | 0.076163231 | 0.094640888 | dips at GPT-6 |
| [H01](../../literature/specialist-review-2026-11-01/H01.json) | balanced_accuracy (higher) | 0.64888011 | 0.71837945 | 0.69795784 | peaks at GPT-6 |
| [H02](../../literature/specialist-review-2026-11-01/H02.json) | subject_equal_roc_auc (higher) | 0.75719459 | 0.73054819 | 0.78853654 | dips at GPT-6 |
| [H08](../../literature/specialist-review-2026-11-01/H08.json) | macro_f1_sleep (higher) | 0.80271584 | 0.79267485 | 0.79223587 | both steps regress |
| [H16](../../literature/specialist-review-2026-11-01/H16.json) | temporal_rrmse (lower) | 0.46160665 | 0.52647835 | 0.45338359 | dips at GPT-6 |
| [I07](../../literature/specialist-review-2026-11-01/I07.json) | balanced_accuracy (higher) | 0.43611111 | 0.50818713 | 0.5505848 | both steps improve |
| [I10](../../literature/specialist-review-2026-11-01/I10.json) | balanced_accuracy (higher) | 0.63526316 | 0.60719298 | 0.63789474 | dips at GPT-6 |
| [J08](../../literature/specialist-review-2026-11-01/J08.json) | instance_f1_iou50_multirater (higher) | 0.64336833 | 0.49207381 | failed/incomplete | incomplete original attempts |
| [K01](../../literature/specialist-review-2026-11-01/K01.json) | macro_f1 (higher) | 0.94091451 | 0.94091451 | 0.94307424 | tie then improvement |
| [K04](../../literature/specialist-review-2026-11-01/K04.json) | section_equal_macro_f1_7classes (higher) | 0.50507114 | 0.53194204 | 0.55055019 | both steps improve |
| [K05](../../literature/specialist-review-2026-11-01/K05.json) | donor_block_macro_rmse (lower) | 0.067423672 | 0.057937996 | 0.055228746 | both steps improve |
| [K06](../../literature/specialist-review-2026-11-01/K06.json) | class_balanced_mouse_accuracy (higher) | 0.87777778 | 0.86944444 | 0.89027778 | dips at GPT-6 |
| [L04](../../literature/specialist-review-2026-11-01/L04.json) | bits_per_spike_train_mean (higher) | 3.1947435 | 3.2799514 | 3.2638214 | peaks at GPT-6 |
| [L06](../../literature/specialist-review-2026-11-01/L06.json) | c2st_accuracy_2000 (lower) | 0.51250001 | 0.49737501 | 0.5056 | peaks at GPT-6 |
| [M01](../../literature/specialist-review-2026-11-01/M01.json) | mouse_equal_binary_log_loss (lower) | 0.43651524 | 0.43758409 | 0.43663393 | dips at GPT-6 |
| [M04](../../literature/specialist-review-2026-11-01/M04.json) | range_normalized_mae (lower) | 0.058222606 | 0.058219401 | 0.05822149 | peaks at GPT-6 |
| [N05](../../literature/specialist-review-2026-11-01/N05.json) | field_accuracy (higher) | failed/incomplete | 1 | 1 | incomplete original attempts |

Inspect [task-trajectories.csv](task-trajectories.csv) for exact raw deltas/slopes, [all-model-slices.csv](all-model-slices.csv) for every original slice, and [trajectories.json](trajectories.json) for both tracks and source-linked evidence. Native equal-slice means summarize this finite panel only. All new recommendations are exploratory and require prospective validation.
