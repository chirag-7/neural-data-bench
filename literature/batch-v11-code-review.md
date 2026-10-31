# Batch v11 generated-program static review

Reviewed 21/21 available submissions by reading code and parsing AST only. No submitted code/reference was executed; no result scores were read. This is observational review, not formal proof.

## Cross-cutting findings

- K05 frozen protocol says selected feature IDs supplied equally, but actual4argument numerical interface supplies no source gene IDs to either general model or reference. Interpret as supervised anonymous selected numeric expression features; no marker-identity-informed comparison.
- B08 frozen harness utility whitelist excludes heapq, whereas prompt ordinary/utilities wording does not clearly expose this exact exclusion. Any whitelist failure mixes interface disclosure and code construction compliance, not scientific compression fidelity alone.
- C06 permits acausal context and unsupervised normalization within each whole test recording; this is distinct from forbidden pooled-test fitted transforms in E06/K05/K06.

## Per-submission findings

### B08 / gpt-5.6-sol

177 lines (<240). Assessment: `harness_whitelist_violation_with_prompt_disclosure_ambiguity`. Exact source/prompt hashes, import lines and function anchors retained in JSON.

- Arithmetic-codes quantized time gaps plus exact label sequence, including per-label refractory minimum in charged metadata. Origin, event count, label dictionary and count tables serialized into blob. Decoder rebuilds state from blob only; no encoder mutation read observed.
- Imports heapq (line1), rejected by frozen codec harness allowed imports. Prompt says usual numerical/utilities and protocol ordinary utilities, so exact exclusion is not clearly disclosed; distinguish harness enforcement from unambiguous scientific-fidelity violation.
- The custom Python arithmetic coder loops over events; runtime and round-trip correctness need independent execution evidence.

### B08 / gpt-6-sol

178 lines (<240). Assessment: `harness_whitelist_violation_with_prompt_disclosure_ambiguity`. Exact source/prompt hashes, import lines and function anchors retained in JSON.

- Canonical Huffman gap and label codes; blob contains origin/count/unit dictionary/code lengths and payload sizes. Decoder reconstructs event sequence from blob, with monotone quantized time sums.
- Imports heapq (line1), rejected by frozen codec harness allowed imports; broad prompt ordinary/utilities language makes whitelist disclosure ambiguous.
- 100us nearest-grid timing intent meets stated50us tolerance mathematically; floating-point edges, actual equality and runtime remain empirical.

### B08 / gpt-6.1-sol

191 lines (<240). Assessment: `no_observed_material_contract_violation`. Exact source/prompt hashes, import lines and function anchors retained in JSON.

- Allowed struct/zlib/lzma/math/NumPy imports only. Builds self-contained byte frames containing unit dictionary/counts, origin and adaptive entropy tables; selects global-stream or per-unit interval encoding based only on current input.
- Per-unit decode stably sorts reconstructed quantized times and explicitly restores within-tick label permutation from charged tie metadata. No encoder state or original-array lookup observed; raw float64 fallback exists if quantization check fails.
- 100us nearest-grid timing is intentionally lossy and labels/order are intended exact. Source review does not establish ANS/bitpacking/tie permutation round-trip correctness or runtime; independent saved-blob audit is required.

### C06 / gpt-5.6-sol

224 lines (<240). Assessment: `no_observed_material_contract_violation`. Exact source/prompt hashes, import lines and function anchors retained in JSON.

- Actual training specimen vector is mapped to group integers solely for weights/GroupKFold and training-only blend calibration.
- Per-record baseline/noise/amplitude/shift features include acausal context and test-row unsupervised statistics. These are allowed within each complete recording. Features are constructed per recording before concatenating tabular examples; no filtering across record boundaries observed.
- Training-only scaler/tree/ridge fits and output clipping are visible. Internal blend metric pools within specimen, whereas official scorer averages neurons within specimen; this is a selection surrogate, not a scorer violation.

### C06 / gpt-6-sol

114 lines (<240). Assessment: `no_observed_material_contract_violation`. Exact source/prompt hashes, import lines and function anchors retained in JSON.

- Accepts actual specimen vector; groups affect sample weights only. StandardScaler and all regressors fit on training features only.
- Test recording median/noise/percentiles/acausal smoothing are row-local unsupervised feature computations, allowed by this recording contract. No cross-record temporal smoothing observed.
- Final outputs are zero-padded, finite and nonnegative by explicit clipping/sanitization; return units intended expected counts, no conversion to Hz.

### C06 / gpt-6.1-sol

214 lines (<240). Assessment: `no_observed_material_contract_violation`. Exact source/prompt hashes, import lines and function anchors retained in JSON.

- AR1/OASIS-style event extraction is implemented directly in NumPy, with allowed scipy/sklearn calls; no specialist package or external weights imported.
- Per-record fluorescence percentile baselines, AR1 extraction and acausal Gaussian smoothing stay within each record. Training groups define specimen-held-out predictions and training-only blend/amplitude calibration.
- Training validation uses recording correlations averaged within animal, not exact per-neuron concatenation aggregation of final scorer. This is an internal surrogate; no observed outer-test leakage.

### E06 / gpt-5.6-sol

207 lines (<240). Assessment: `no_observed_material_contract_violation`. Exact source/prompt hashes, import lines and function anchors retained in JSON.

- Shared/neuron-specific temporal ridge, training-fitted latent basis, and training-validation ensemble weights. All fitted means/bases/coefficients/weights derive from training x/y.
- Every test operation reduces over within-row time/features or applies fixed training coefficients. Output allocates len(test), and no cross-test-row fitting, adjacency inference, smoothing or target access observed; taxis12rows supported.
- Chronological75% inner split has no purge although training windows overlap at stride16 with64context and32targets. Inner training/validation physical frames can overlap; optimistic internal model selection is possible, without contamination of outer test.

### E06 / gpt-6-sol

125 lines (<240). Assessment: `no_observed_material_contract_violation`. Exact source/prompt hashes, import lines and function anchors retained in JSON.

- Training-only blocked validation with distance>5 training-row embargo; all scales/means/decays/ensemble weights fitted using training.
- Forecast outputs use each64frame history independently; hardcoded64input/32output lengths match frozen contract, while row count is dynamic and supports taxis.
- No cross-test-row computation or future target access observed. scipy SLSQP and NumPy fits are allowed; finite-output sanitization present.

### E06 / gpt-6.1-sol

218 lines (<240). Assessment: `no_observed_material_contract_violation`. Exact source/prompt hashes, import lines and function anchors retained in JSON.

- Training `_split` infers training-window adjacency from shared observations and purges5rows at its chronological boundary; no such inference is applied to test rows.
- Training-only means/scales/eigenbases, shared/local/global regressors and validation hyperparameters. Test kernel compares each test feature vector to fixed training features, not test-to-test fitting.
- Dynamic row count supports taxis;32horizon/64context constants match contract. Private sklearn threadpool utility imports are within allowed sklearn root but version compatibility remains empirical.

### K05 / gpt-5.6-sol

216 lines (<240). Assessment: `no_observed_material_contract_violation`. Exact source/prompt hashes, import lines and function anchors retained in JSON.

- Correct dictionary contract: group_ids donor and block_ids vectors are used for weighting/leave-one-donor-out validation, never included as predictors.
- Weighted imputation/scaling/supervised numeric-column selection is refitted within each donor fold and on full training; no test-fitted statistics. Numeric features alone are used, no feature-name/marker dictionary access.
- Internal `_grouped_loss` squares mean prediction minus mean truth within block; official scorer averages per-replicate squared errors first. This changes selection risk by ignoring within-block prediction dispersion, but final outputs remain scored by unchanged canonical evaluator.

### K05 / gpt-6-sol

154 lines (<240). Assessment: `no_observed_material_contract_violation`. Exact source/prompt hashes, import lines and function anchors retained in JSON.

- Correct donor/block dictionary contract. Training-block collapsing, weights, variance selection and ridge candidates use training data; query predictions do not fit on test.
- Missing-value fill is computed on complete outer-training x before inner donor CV; this leaks inner-validation feature statistics into imputation if NaNs exist, not outer-test statistics. Prepared expression inputs are intended finite; practical effect requires data verification.
- Internal `_score_predictions` matches order of per-row squared errors→block→donor→per-target sqrt. sklearn threadpool utility optional import has fallback; package compatibility not established by static reading.

### K05 / gpt-6.1-sol

178 lines (<240). Assessment: `no_observed_material_contract_violation`. Exact source/prompt hashes, import lines and function anchors retained in JSON.

- Correct donor/block dictionary contract. Weighted imputation/scaling, variance/correlation screening and ridge bases are fit separately inside donor folds; final transforms fit full training only.
- No external gene names/reference markers or test identifiers used. Model computes each query prediction from fixed training coefficients and explicitly clips fractions[0,1].
- Donor/block-balanced validation weights preserve intended grouping; conservative soft ensemble uses training OOF errors only.

### K06 / gpt-5.6-sol

214 lines (<240). Assessment: `no_observed_material_contract_violation`. Exact source/prompt hashes, import lines and function anchors retained in JSON.

- Correct group_ids/cv_fold dictionary contract. Mouse/class weights and supplied folds only drive validation/weighting; no ID feature column or test IDs.
- Waveform feature engineering is row-local. Missing-value imputation/scaling refitted inside each supplied fold, then full training. Supervised SVC/ExtraTrees candidates never fit on test.
- Dynamic integer output0/1; deterministic seeds and n_jobs1 tree settings visible. Runtime of many candidate fits remains empirical.

### K06 / gpt-6-sol

125 lines (<240). Assessment: `no_observed_material_contract_violation`. Exact source/prompt hashes, import lines and function anchors retained in JSON.

- Correct mouse IDs/fixed-fold dictionary use for training validation/weights only. Scalar imputation/scaling and waveform centering/scaling trained inside each fold and refit full training.
- RBF distance/kernel scale uses train-train distances; test-train distances only apply fixed fitted classifier. No pooled-test scaling or label fitting.
- Scalar robust-scale expression reverses percentile subtraction and is negative for varying columns, triggering standard-deviation fallback. This is an implementation detail/possible method bug, not outer-test leakage or contract violation.

### K06 / gpt-6.1-sol

194 lines (<240). Assessment: `no_observed_material_contract_violation`. Exact source/prompt hashes, import lines and function anchors retained in JSON.

- Correct group_ids/cv_fold use. Row-local waveform engineering followed by training-fold imputation/scaling and class/mouse-balanced SVC/ExtraTrees.
- Training OOF utility selects mixture; final preprocessing/models refit training only. Test rows only transform/predict.
- Finite fallback and int64 thresholded labels present. No forbidden tools/imports or test-fit transforms observed.

## Evidence limits

Output shape/fidelity intent and absence of observed forbidden operations are not empirical validation. Runtime, external package compatibility, codec round-trip fidelity and source-array checks belong to separate execution audits. Static code cannot verify generation-time no-tool events. Preserve submissions and failures; this review makes no repair or score-based exclusion recommendation.

## Extension: B03 and A15

Total reviewed 21/21. Original15reviews above retained unchanged. No submitted/reference programs executed or result scores inspected.

### B03 / gpt-5.6-sol

194 source lines including blanks; frozen limit<240. Assessment: `no_observed_material_contract_violation`.

- No simulator imports, hidden recording seeds/periods, source lookup or target regeneration observed. The constants are generic registration/smoothing/regularization settings;5um depth scaling is public prompt information.
- Pairwise shifts/global synchronization and acausal temporal smoothing are computed independently per recording, then whole-training-recording CV fits a ridge correction/scale. No test-to-test borrowing or test-target fitting observed; train_groups is unused None.
- Cross-correlation lag convention uses positive shift for increased depth. Output temporal centering fixes the allowed additive gauge per recording; no test-target sign/scale/time alignment is performed. Learned signed correction derives only from training labels. Actual physical-sign accuracy remains empirical.

### B03 / gpt-6-sol

109 source lines including blanks; frozen limit<240. Assessment: `no_observed_material_contract_violation`.

- No hidden simulator seeds/periods, template truth, procedural target reconstruction or source-identity lookup observed. Public5um spatial scaling is explicit.
- Per-record iterative spatial alignment updates an unsupervised template using only that complete recording. This is allowed offline context, not shared test-population fitting. Test rows processed independently.
- Whole-record training CV chooses spatial/temporal preprocessing and positive scale; full-training scale is bounded0.5–2.0. Interpolation grid-minus-shift corresponds to increased-depth positive displacement. Mean subtraction gives allowed per-record gauge; scorer-only sign selection is not present.

### B03 / gpt-6.1-sol

192 source lines including blanks; frozen limit<240. Assessment: `no_observed_material_contract_violation`.

- np.random.seed(0) is generic algorithm determinism; no use of hidden simulator seeds/periods, simulator generation API or reconstructed target profiles observed. All imposed-motion knowledge is limited to public5um depth-bin scale and broad registration ranges.
- Pairwise displacement graph, robust weights, template refinement and temporal trend denoising operate independently per recording. Training whole-record CV selects preprocessing/smoothers/ensemble and calibrates positive gain; train_groups is unused None.
- Graph equations solve d[j]-d[i]=positive-depth shift with5um scale. Per-record mean centering fixes additive gauge; no heldout sign/scale/temporal alignment or score access. Realized fidelity/sign and sparse solver behavior require independent execution audit.

### A15 / gpt-5.6-sol

268 source lines including blanks; frozen limit<240. Assessment: `line_limit_violation`.

- Source is268lines including blanks, violating frozen exclusive240line limit. This is observed submission noncompliance; do not trim/repair or retrospectively redefine counting. Empirical validity and any score must be labeled separately.
- NaN-padded audio valid lengths and-1target tails are found via binary search, consistent with contiguous padding contract. Test output dimensions derive from test_x.shape[1]//32, not longer training dimensions; returned array initialized0and only assigned1inside intervals.
- Feature extraction/STFT/smoothing and20th-percentile noise-floor normalization are applied per recording. Such deterministic unsupervised test-record normalization/acausal context is explicitly allowed. No cross-record temporal filtering or jointly fitted test transform observed.
- train_groups deleted (None); no hidden bird IDs/source filenames. Classifier fitting, event-threshold/gap/duration selection and final refit use training recordings only, including exposed fixed row0,5,...validation recipe.

### A15 / gpt-6-sol

142 source lines including blanks; frozen limit<240. Assessment: `no_observed_material_contract_violation`.

- Allowed NumPy/SciPy/sklearn imports. Complete finite audio prefix is used before feature construction; number of output bins is dynamic test length//32 and every assignment is integer0/1with padding0.
- STFT/band energy/20th-percentile normalization and temporal smoothing are recording-local. The model never joins recordings into a continuous signal or estimates a pooled test transform. Analytic per-record normalization and offline/acausal context are allowed.
- train_groups unused(None), no hidden IDs. Classifier sampling uses only training labels; exposed whole-record validation row recipe selects event postprocessing. Expanded threshold grid is a training-only procedure choice, not use of heldout labels.

### A15 / gpt-6.1-sol

195 source lines including blanks; frozen limit<240. Assessment: `no_observed_material_contract_violation`.

- Allowed NumPy/SciPy/sklearn/gc imports only; optional private sklearn threadpool-control utility is allowed by package root, while runtime version compatibility remains empirical. No files, source lookups, bird IDs or external model assets observed.
- Finite sample counts determine each complete32sample bin count. Each recording is separately trimmed before STFT; output shape derives from current test_x length//32 and is initialized0with only interval slices assigned1. Different train/test padding widths do not create hardcoded output mismatch.
- Within-record20th/95th energy percentiles, spectral noise floor, bidirectional lags and smoothing use allowed deterministic analytic/acausal test context. No cross-record temporal borrowing, pooled test fit or test-label access observed.
- Fixed whole-training-record validation controls ensemble, smoothing and event threshold/gap/minimum duration; all classifier fitting/refitting is training-only. train_groups remains unusedNone; source attribution/modification notice is included.

