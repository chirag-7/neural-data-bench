# E01 / dmfc_rsg: frozen-program source portability

Status: prepared and independently validated before any evaluated program was run on this slice. This is an additional source under **E01**, not a new independent task ID.

## Scientific endpoint and source

Ready-set-go time interval reproduction; dorsomedial frontal cortex. Subject **Haydn**, DANDI **000130**, published release **0.241017.1448**. [Versioned data citation](https://doi.org/10.48324/dandi.000130/0.241017.1448); [NLB datasets](https://neurallatents.github.io/datasets); [official tensor implementation](https://github.com/neurallatents/nlb_tools/blob/42f8410b88e12db136910fa2f888b025ea0aa2ae/nlb_tools/make_tensors.py); [official scorer](https://github.com/neurallatents/nlb_tools/blob/42f8410b88e12db136910fa2f888b025ea0aa2ae/nlb_tools/evaluation.py).

Raw train asset `c90cbccc-31a5-4815-88e6-822d8c5ca68c`, test asset `a2c3ced1-2869-4483-aa19-8815c2d18c91`. Exact URLs, fetched-byte checksums, prepared-array checksums and complete source records accompany this protocol. The versioned metadata explicitly licenses the data **CC BY4.0**; vendored nlb_tools is MIT. Cache is not committed. Both raw NWBs are downloaded in full and SHA256 recorded.

## Preprocessing and split

Use pinned official `NWBDataset`, `resample(20)`, `make_train_input_tensors(...,trial_split=['train','val'],seed=0)` and `make_eval_input_tensors(...,trial_split='test',seed=0)`. Read train and test NWBFiles separately through the officially supported NWBFile constructor. Skip behavioral TimeSeries only; retain all neural spike counts and trial metadata. Behavior is neither a predictor nor target here. This also avoids unrelated behavior availability dropping neural trials. No arbitrary random frame/bin split.

Combined train+validation **1006 trials**, train inputs `[1006, 75, 40]`, targets `[1006, 75, 14]`; official test **283 trials**, inputs `[283, 75, 40]`, targets `[283, 75, 14]`. Training labels are raw held-out-neuron counts, not inferred latents or pseudo-labels. Train/test share the source subject and recording; do not describe this as animal/session generalization. Unit strings retain source trial IDs. Both partitions carry the same true subject/session group label; they are not separate scientific session groups.

Alignment: **packed/jittered go-time from −1500 to0ms;75 consecutive20ms bins**. The official held-out target has a contiguous valid interval per trial and NaNs outside it. This hidden window reflects set→go timing and original random alignment jitter. All75 input bins are finite and retained unchanged. Predictions must be finite for all75 bins, while only finite target entries are scored. The hidden mask and jitter are scoring-only, never model inputs.

Official test truth comes directly from `dmfc_rsg_20/eval_spikes_heldout` in the publisher's `eval_data_test.h5`, SHA256 `f2f434d30193251b58e6a693381fdd185c8fbc0e47d38f8810e65295bc42c865`. No target interpolation, zero-fill, shift or resampling is applied after loading that group.

## Evaluation and comparison limits

Return finite nonnegative expected counts (notHz) with target shape. The wrapper delegates to the **unchanged frozen baseE01 scorer** and has numerical equality with pinned official `bits_per_spike` on fixed positive arrays and the evaluation-mean null, including target NaNs. The null uses the evaluation-set per-neuron mean only as scoring normalization; it must never enter model fitting. Zero rates follow official1e-9 replacement.

This is a **custom supervised population diagnostic**, not an official neural-latents leaderboard submission. Root evaluation may run the original frozen baseE01 generated programs unchanged on these shapes, refitting learned coefficients solely from this slice's training arrays. There is no new prompt, model generation, selected program repair, or hyperparameter tuning after test feedback. Such portability measures whether the original algorithm transfers to different dimensions, brain areas and scientific tasks; it does not measure fresh-generation capability or historical model trend on independent tasks. Report slice results and aggregate at E01 before macro counts.

The available reference is the same frozen Gaussian(sigma1bin)+Ridge(alpha100) positive readout. It is a transparent traditional reference, **not current specialist SOTA**. No specialist leaderboard number is directly comparable without the same supervised regime and exact split.

## Validation and acknowledged limits

`../verify_slices.py` independently bins every raw test spike time with integer1ms truncation and20ms aggregation, then checks exact equality with every prepared held-in count. It verifies neuron/trial order, alignment and count units. It also checks exact official target-array equality including NaNs, integer nonnegative finite counts, and negative-output rejection. Results: `validation.json`.

Public test NWB omits held-out neurons and original set_time; therefore independent raw held-out timing reconstruction is impossible. The exact official archived target is the authoritative mask and count reference. Hidden jitter, behavioral values and mask stay scoring-only; no inferred alignment is supplied to models. An initial preparation assertion incorrectly expected input padding and then prefix-only target padding; source inspection corrected both assumptions before execution of any evaluated program. All official input values remain unchanged.

## Reproduction

With NumPy, SciPy, scikit-learn, h5py, PyNWB2.8.3 and HDMF3.14.6 installed, run `python experiments/E01/slices/dmfc_rsg/adapter.py`; this downloads small missing files and uses cached HTTP ranges for Area2. Requires the shared official test-truth archive already acquired by baseE01 preparation. Run `python experiments/E01/slices/verify_slices.py` to verify both slices. `adapter.load()` returns four arrays; `baseline(train_x,train_y,test_x)` and `score(predictions,test_y)` delegate to unchanged baseE01 code.
