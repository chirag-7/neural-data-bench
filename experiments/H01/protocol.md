# H01 — Subject-disjoint EEG motor imagery decoding

Protocol version: `physionet-mi-lr-subjects1-8-v1`, frozen before evaluated-model submissions, 2026-10-30.

## Scientific question and scope

Can a general model write a numerical program that learns to classify imagined left-fist versus right-fist movement from multichannel EEG and transfers to previously unseen people? This is the T3 code-generation regime: numerical model fitting happens externally. It is not evidence that a language model directly interprets EEG samples in its context window, and it is not an evaluation of all MOABB motor-imagery datasets.

The data come from Schalk's [EEG Motor Movement/Imagery Dataset, version 1.0.0](https://physionet.org/content/eegmmidb/1.0.0/), [DOI 10.13026/C28G6P](https://doi.org/10.13026/C28G6P), recorded with [BCI2000](https://doi.org/10.1109/TBME.2004.827072). Original acquisition was 64 EEG channels, normally at 160 Hz. Dataset attribution and ODC-By-1.0 terms apply to the data independently of this repository's software license. Raw files and prepared arrays remain in the ignored local cache; exact source URLs and SHA-256 hashes are tracked in [the manifest](../../data/manifests/H01.json).

## Fixed data and target

- Train: participants S001–S005. Test: S006–S008. These are deterministic first identifiers, not a random representative population sample.
- Runs 4, 8 and 12 only: unilateral left/right **imagined** fist movement. Motor execution and bilateral hands/feet runs are excluded.
- EDF annotation T1 maps to 0 (left); T2 maps to 1 (right). T0 rest intervals are not classification targets.
- One nonoverlapping epoch per task event: 1.0 seconds inclusive to 4.0 seconds exclusive after onset, 480 samples at 160 Hz. The 1-second delay reduces immediate cue-evoked responses; sustained visual-attention confounds can remain. The adapter asserts epochs stay inside the annotated task period.
- Inputs: `(n_trials, 64, 480)` float32 microvolts in the original channel order, after a common-average reference at each time sample. No label-derived preprocessing or artifact rejection. Each fitted estimator may apply filters using only its supplied inputs and training labels.
- Every subject appears in exactly one split. Trial IDs, subject/run metadata, and labels are persisted locally with the prepared arrays. No random windows, overlapping augmentation across splits, or train/test mixing is allowed.

The official [MOABB PhysionetMI documentation](https://moabb.neurotechx.com/docs/generated/moabb.datasets.PhysionetMI.html) provides dataset context. Its within-session published score table and the [MNE CSP tutorial](https://mne.tools/stable/auto_examples/decoding/decoding_csp_eeg.html) use different splits/conditions. Their scores are **not** comparable to this new slice and are not imported as current SOTA.

## Scoring and reference

Primary metric: pooled trial balanced accuracy, `sklearn.metrics.balanced_accuracy_score`, higher is better, two-class chance reference 0.5. Also report each held-out participant's balanced accuracy and the participant mean; the three test participants, rather than the 135-ish test trials, are the population-generalization units. A larger study needs participant-resampled intervals and additional held-out participants; trial-wise confidence intervals would overstate independent replication.

The fixed local reference is a transparent, traditional EEG pipeline: fourth-order Butterworth 7–30 Hz filtering within each supplied epoch, per-epoch temporal centering, trace-normalized trial covariance, class-average covariance, generalized-eigenvalue CSP with two components from each eigenvalue extreme, log variance, and shrinkage LDA (`solver='lsqr', shrinkage='auto'`). The CSP covariance receives a fixed `1e-6 * trace / channels` diagonal ridge to handle the rank loss from common-average referencing. It is fitted on training labels only; there is no hyperparameter search or post-score adjustment. This is a reproduced specialist baseline, **not verified current best performance**.

All model submissions receive the same array schema, sample frequency, class meaning and allowed standard numerical libraries. They receive no held-out labels or test-feedback repair. Generation repetitions and compute budgets are controlled by the enclosing release protocol and must be recorded with each run. A valid model output is an integer array of length `n_test` taking only values 0 or 1.

## Reproduction

Run `python experiments/H01/adapter.py` from the repository root to acquire and prepare. Preparation requires `mne==1.10.2`; baseline evaluation uses NumPy, SciPy and scikit-learn. The module's `load()` returns `(train_x, train_y, test_x, test_y)` and `baseline(train_x, train_y, test_x)` returns predictions. Keep test_y in the evaluator process only. See [adapter.py](adapter.py), [requirements-preparation.txt](requirements-preparation.txt) and [worklog.md](worklog.md).

## Limits on interpretation

Only three held-out people are tested, from a single public dataset. Artifact-correlated information, person selection, public-label pretraining contamination and a single generated program per model can affect the results. This slice does not test calibrated within-subject operation, longitudinal transfer, clinical deployment, online latency, or neurophysiological validity of the learned features. There is no verified same-protocol published SOTA; comparisons must remain against the local fixed reference. Further MI datasets belong under H01 as additional dataset slices, not as artificial new task-family counts.
