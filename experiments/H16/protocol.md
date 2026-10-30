# H16 — EEGdenoiseNet ocular artifact repair

Protocol version `eegdenoisenet-eog-disjoint-v1`, frozen 2026-10-30 before evaluated-model submissions.

## Question and evidential meaning

Can a general model generate a numerical estimator that removes an added EOG component from a single-channel EEG segment? This is a T3 code-synthesis experiment with external supervised fitting. Its ground truth is a known source component in a **semisynthetic mixture of real preprocessed recordings**. It does not establish recovery of pristine neural physiology from real simultaneous artifacts.

The original [EEGdenoiseNet repository](https://github.com/ncclabsustech/EEGdenoiseNet), pinned to commit `8d290661146c7189c98cc04812d37371d4b9426c`, and [dataset paper v4](https://arxiv.org/html/2009.11662v4) are the primary sources. The article describes cleaned, expert-inspected EEG and EOG component pools. The original repository carries an [MIT license](https://raw.githubusercontent.com/ncclabsustech/EEGdenoiseNet/8d290661146c7189c98cc04812d37371d4b9426c/LICENSE); the original physiological sources have their own provenance. This release tracks acquisition URLs, hashes, code and statistics; it does not redistribute the component pools or mixtures. See [the data manifest](../../data/manifests/H16.json).

## Frozen construction

Acquire original `data/EEG_all_epochs.npy` (4514 × 512) and `data/EOG_all_epochs.npy` (3400 × 512). These are two-second segments at 256 Hz. Use NumPy `default_rng(20261030)` to independently permute EEG and EOG row indices. Select 2600 unique rows from each pool: 2000 pairs for training, 600 pairs for evaluation. Split components **before** mixing. No component index may cross splits; the adapter also checks exact component-byte duplicates across splits. Participant identities are not provided per row, so this is segment-disjoint, with no claimed participant-disjoint generalization.

Use ten equally represented levels `s = -7,-6,...,2`: 200 training pairs and 60 evaluation pairs at each level, independently shuffled by the same fixed generator. A component appears in only one mixture, so different SNRs are not duplicate independent observations of a reused clean segment.

For clean EEG `e` and EOG `o`, construct `m = e + a o`, with `a = RMS(e)/(RMS(o) * 10**(s/10))`. This follows the **literal original data-preparation code** and its `10 log10(RMS ratio)` convention. It differs from conventional power-SNR dB (`20 log10(RMS ratio)`), which would be twice this numeric label. Do not interpret the reported SNR labels as conventional power-SNR values. The distinction is verified against the pinned [original preparation code](https://raw.githubusercontent.com/ncclabsustech/EEGdenoiseNet/8d290661146c7189c98cc04812d37371d4b9426c/code/benchmark_networks/data_prepare.py).

Inputs and targets are `x = m/std(m)` and `y = e/std(m)`, the paired scaling used by the original code. Arrays have shape `(segments,512)`, float32. This scaling depends on the observed mixture, not hidden test labels. The mixture amplitude is not separately supplied to submissions. Component indices, source hashes, exact SNR labels and unique pair IDs are retained in the ignored cache for audit.

## Score and local reference

Primary score is mean temporal relative root mean squared error, following the paper's temporal RRMSE equation:

`mean_i [sqrt(mean_t((prediction[i,t]-target[i,t])**2)) / sqrt(mean_t(target[i,t]**2))]`.

Lower is better. Aggregate the per-segment ratios, **not** a single global residual norm. `adapter.score(target,prediction)` returns this exact scalar and `per_unit_score` returns each segment's ratio. Predictions must be finite and exactly `(600,512)`. Also report scores by SNR level. Zero prediction gives RRMSE 1; identity prediction is a useful uncorrected reference, whose result depends on the fixed SNR distribution. Neither is a specialist SOTA.

The frozen traditional local reference is stationary Wiener spectral shrinkage. Estimate average clean and noise (`train_x-train_y`) power spectra from training pairs only, smooth both across frequency bins with a fixed Gaussian sigma of 2 bins, use gain `Pclean/(Pclean+Pnoise)`, set the DC gain to zero, and reconstruct test segments with inverse real FFT. There is no test-label tuning or parameter search. This supervised traditional reference has access to exactly the training pairs available to each generated estimator. It is a **local conventional baseline**, not a reproduction of the paper's deep networks and not verified current best performance.

All generated programs receive identical training arrays and test inputs, sampling frequency and shape; no test target, row identity, SNR labels or score feedback is provided. Generation repetition and execution limits must be logged by the enclosing release evaluator. Published paper scores are not transplanted: this is a smaller fixed slice, using one mixture per unique pair and a different split.

## Reproduce and interpret

Run `python experiments/H16/adapter.py` to acquire and prepare; only NumPy and the standard library are needed. `load()` returns the four arrays. `baseline()` additionally uses SciPy. Arrays remain under `data/cache/H16/`; see [adapter.py](adapter.py) and [worklog.md](worklog.md).

This task covers ocular component attenuation under controlled linear addition. It leaves EMG/ECG artifacts, multichannel ICA, real artifacts, physiological downstream-feature preservation and causal online filtering unmeasured. The original EEG clean target itself reflects preprocessing choices. Component disjointness prevents direct row reuse but cannot remove unknown within-person or source-recording dependence. Do not bootstrap individual samples as independent animals or people, and do not count SNR strata as separate task families.
