# G01 — FALCON M2 custom chronological decoding diagnostic

Version: `falcon-m2-calib-chronological-v1`, frozen 2026-10-30 before evaluated-model submissions.

**This is a new split of public FALCON calibration data, not the official FALCON held-out evaluation or leaderboard score.** It tests zero-shot transfer between recording days from one monkey; it does not test new animals, clinical efficacy or closed-loop BCI control.

## Source and target

The [FALCON project](https://snel-repo.github.io/falcon/), [official code](https://github.com/snel-repo/falcon-challenge), and [DANDI 000953 M2 record](https://dandiarchive.org/dandiset/000953/draft) provide intracortical multiunit spiking and finger-movement measurements. Original dataset metadata explicitly declares CC-BY-4.0 and explains that apparent DANDI “subjects” are split partitions of **one monkey**. Cite the FALCON paper and original source as listed in the DANDI record; CC-BY attribution applies independently of repository software licensing.

Original M2 target fields are `acquisition/finger_vel/index/data` and `.../mrs/data`. Their ordering is retained as `[index,mrs]`. The native source `unit` is **AU**. These are the actual distributed finger-velocity values; this release neither invents a behavioral target nor silently converts them to physical degrees/s or AU/s. The per-file target variance is recorded and checked. Neural observations use the corresponding 96 multiunit spike-time streams, not the 30 kHz raw-voltage recordings.

## Frozen split

- Training days: **2020-10-19 and2020-10-20**, both available runs on each day: four original `held-in-calib` NWBs.
- Evaluation days: **2020-10-27 and2020-10-28**, two runs on Oct 27 and one run on Oct 28: three original `held-in-calib` NWBs.
- All trials of a recording stay together. Every recording day is in exactly one split. No event/window from a test-day trial appears in training. Official minival is not mixed with calibration: original documentation states minival is a small subset, so combining them could duplicate trials.
- No evaluation-day velocity labels are supplied for fitting, recalibration or model selection. Only the evaluator sees test targets. This is therefore an explicitly **zero-shot** day-transfer slice; it differs from FALCON's standard few-shot calibration/evaluation design and uses public early-day calibration releases as a new held-out-day partition.

The final prepared arrays have70,989 training bins from1,169 trials, and44,633 evaluation bins from754 trials. The evaluation set contains two days, not44,633 independent replications. Trial/run/day identifiers remain in the ignored local cache for grouped analysis.

## Acquisition and integrity

[source-assets.json](source-assets.json) pins the exact seven asset UUIDs, blob IDs, original sizes and stable DANDI API download endpoints. The dataset currently exposes a **draft** snapshot; no immutable published-version claim is made. FALCON reference code is pinned at commit `770c9b9597b8f58bf67b5a9ec6401ef705a2cb0f`.

Original files are roughly1.5–2.4 GB each because they contain raw fullband voltage. Preparation uses `h5py==3.15.1` and `fsspec==2025.10.0` HTTP range reads to extract only spike times/indexes, native finger velocities/timestamps, source evaluation masks and trial intervals/IDs. This retains hundreds of trials per recording without downloading unused fullband arrays. Transient public download redirects are resolved in memory and not persisted.

For each source, [the manifest](../../data/manifests/G01.json) retains the provider-reported full-file SHA-256 and DANDI ETag, labels the acquisition as partial extraction, and hashes every extracted contiguous dataset buffer with its shape/dtype and every saved extracted/prepared NPZ. **The provider's whole-file SHA-256 is not independently verified by partial acquisition.** Component hashes verify exact extracted inputs/labels and allow another reader to reproduce the selected content. Source data remain ignored local cache; code, provenance, verification receipts and aggregate results are tracked.

## Input conversion and causal scope

Behavior timestamps are interpreted as **starts** of20 ms spike-count bins, exactly as the official M2 loader. Spikes are binned with the official histogram edge semantics, including discontinuities, and filtered with the reference causal exponential kernel: `exp(-t/240 ms)`, normalized across12 taps at `t=0,20,...,220 ms`. Filtering resets per original file and otherwise uses only current/past spike observations. It never uses a velocity target or future spike bin. The source `eval_mask`, finite target check and valid trial interval determine which rows are scored. Filtering occurs before masking so available past neural observations can contribute.

Each submission receives `(n_samples,96)` float32 filtered spike-count features and `(n_samples,2)` native target arrays for training, plus test inputs. There is no target standardization or test-day normalization supplied by preparation. Standardization, regularization and nonlinear fitting performed by a generated program must be fitted from training data alone. Generation/execution limits and repetitions are controlled by the enclosing release protocol.

The causal feature construction requires completion of the current20 ms spike bin; it does not establish the latency of the downstream generated estimator. An offline `fit_predict` interface can still implement acausal operations across its test array. Such a submission may be scored as offline decoding but must not be described as an online/causal controller without separate code audit and streaming evaluation.

## Score and reproduced traditional reference

Primary metric is pooled variance-weighted coefficient of determination:

`r2_score(test_y,prediction,multioutput='variance_weighted')`.

Higher is better; negative values are valid and must not be clipped. Also report this metric separately for each held-out day. A corresponding training-mean prediction provides a simple reference; no constant universal “chance accuracy” applies to this regression task. Do not average raw R² with unrelated classification/F1/correlation metrics or treat time bins as independent subjects.

The local traditional reference follows the official FALCON linear-decoder design: causal exponential count filtering, training-only feature standardization, and ridge regression with20 alphas from `logspace(-5,5,20)`. This adapter uses five-fold training-only RidgeCV with the explicitly stated variance-weighted scoring objective; it is an **adapted reproduced traditional reference**, not a byte-identical official challenge submission or verified current best specialist. The coefficient model receives the same prepared training inputs/targets as each generated estimator. No test-day calibration is applied.

Pinned reference source files and their [MIT license](UPSTREAM_LICENSE.txt) are included. The adapter's spike binning and causal filtering were numerically checked against the actual upstream functions on **all seven** extracted recordings; [verification.json](verification.json) records maximum float32 discrepancies below 1.7e-7. No reference parameter was changed after its test score was inspected.

## Boundaries and reproduction

There is one monkey, two training days and two held-out days. Cross-day neural distribution shift is part of the target problem; a poor frozen reference score is reported honestly, not repaired using evaluation feedback. Modern neural foundation/sequence specialist decoders have not been reproduced on this custom protocol. A general model exceeding this local reference would not establish superiority over specialist SOTA.

Run `python experiments/G01/adapter.py` to reproduce partial extraction and preparation. [adapter.py](adapter.py) provides `load()`, `baseline(train_x,train_y,test_x)` and `score(target,prediction)`. [requirements-preparation.txt](requirements-preparation.txt) lists extra reader dependencies; numerical evaluation uses NumPy/SciPy/scikit-learn. See [worklog.md](worklog.md) for the source choices and excluded alternatives.
