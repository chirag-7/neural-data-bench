# I07 — FRESH fNIRS motor-condition decoding

Protocol `fresh-2s-lr-subject-disjoint-v1`, frozen 2026-10-30 before evaluated-model submissions.

## Purpose and provenance

This diagnostic asks whether a general model can write an estimator to classify left versus right two-second finger-tapping trials from fNIRS optical-density responses in previously unseen participants. It is a T3 code-generation experiment with external numerical fitting. It is a new task slice, not the original FRESH scientific hypothesis test and not a verified published decoding benchmark.

The original [FRESH organizer description](https://openfnirs.org/community/fresh/welcome-to-the-fnirs-fresh-project/) identifies ten participants and four sessions: left/right finger tapping, each at two/three seconds, interleaved with rest. The [FRESH publication](https://doi.org/10.1038/s42003-025-08412-1) concerns variation between researchers' processing and scientific conclusions. Lab-consensus cortical activation decisions are **not** ground-truth labels here. The target is the known task condition. The dataset author's [validation notebook](https://data.nemar.org/on005963/v1.0.0/code/validation.ipynb), BIDS session names and original organizer description jointly establish label meanings; the generic `motor` annotation alone would not identify hand side.

Data are from the versioned [NEMAR on005963 v1.0.0 mirror](https://www.nemar.org/dataset/on005963) of [OpenNeuro ds005963 v1.0.0](https://doi.org/10.18112/openneuro.ds005963.v1.0.0), CC0 as declared in the downloaded `dataset_description.json`. All 20 selected SNIRF files and BIDS sidecars are acquired from stable versioned URLs; [the manifest](../../data/manifests/I07.json) records original byte sizes and SHA-256. Raw and prepared arrays remain in ignored local cache. Source dates of acquisition and later mirror publication are distinct.

## Frozen split and input preparation

Use all participants: sub-01–sub-07 for training, sub-08–sub-10 for evaluation. Only `ses-left2s` and `ses-right2s`; no three-second session. Assign left=0, right=1 from the verified session mapping. Every subject and every recording appears in exactly one split; there is no random trial/window split. Event dependence within recordings remains and must be respected statistically.

The source has continuous-wave optical amplitudes in **V**, sampled every 0.112 seconds (8.928571 Hz), at wavelengths 760 and 850 nm. There are 136 wavelength-specific measurements: 68 source-detector pairs, including short channels. The adapter checks every SNIRF measurement's source/detector/wavelength against the corresponding BIDS channel table, positive finite intensities, constant time spacing, and BIDS-vs-SNIRF event onset/duration agreement.

Convert voltage amplitude `I` to natural-log optical density `OD=-ln(I/mean_time(I))`, separately per measurement. For each annotated two-second motor event, subtract the mean OD in the three seconds immediately preceding onset. This subtraction cancels the arbitrary recording reference intensity. Then compute eight separate one-second means for **3 ≤ t < 11 seconds** after onset, yielding an array `(trial,136 channels,8 bins)` of dimensionless OD change. Baseline correction and binning are fixed without labels, feature selection or test-score tuning. No unknown differential pathlength factor is invented: these arrays are **not HbO/HbR concentrations** and are not passed through modified Beer–Lambert conversion. No motion repair, short-channel regression or channel-quality optimization is claimed.

The delayed interval targets the slower hemodynamic response. One vector is made for each event; it does not multiply the sample count by sliding windows. Baseline intervals and physiological tails may share information between events inside a recording, but all such related samples remain in the same participant split. Trial-level resampling therefore does not give independent participant uncertainty.

## Score and local reference

Primary metric: pooled trial balanced accuracy, higher is better, chance 0.5. Report held-out-participant balanced accuracy separately. Participants, rather than trials or channels, are the generalization units. Only three are held out; this supports a diagnostic comparison, not a precise population estimate or broad significance claim.

The frozen conventional reference averages each channel's eight delayed bins, fits feature standardization on training trials only, then fits shrinkage LDA (`solver='lsqr', shrinkage='auto'`). It receives the same preprocessed inputs and labels as each generated estimator. There is no feature/hyperparameter search or adjustment after a held-out score is inspected. This is a local traditional decoder; **current best performance is unverified**. FRESH lab-concordance percentages and scientific-hypothesis outcomes are different endpoints and cannot be charted as classifier accuracy.

Each model gets identical training arrays, test inputs, wavelength/time-bin schema and label meaning, with no held-out labels or score-feedback repair. Generation/execution budgets and prompt repetitions must be recorded by the enclosing release evaluator. Output must be finite integer labels of length `n_test`, taking only 0 or 1.

## Limits that matter

The hand condition is blocked by separate recording sessions, so order, systemic physiology, session drift and instrument differences can contribute to classification. Subject holdout prevents direct person reuse but does not resolve these confounds or prove motor-cortical decoding. A stronger experiment would interleave left/right within recordings and evaluate new sites or sessions. The original demographic table contains placeholders; it cannot support age/demographic analyses. The OD representation evaluates a constrained signal-analysis task and leaves physiological concentration estimation, activation inference and complete fNIRS analysis workflows unmeasured.

## Reproduction

Run `python experiments/I07/adapter.py` to acquire/prepare; SNIRF reading requires `h5py==3.15.1` plus NumPy. `load()` returns `(train_x,train_y,test_x,test_y)`; `baseline()` additionally requires scikit-learn. See [adapter.py](adapter.py) and [worklog.md](worklog.md). Keep test labels in the evaluator, never in evaluated-model prompts.
