# E01 / area2_bump: frozen-program source portability

Status: prepared and independently validated before any evaluated program was run on this slice. This is an additional source under **E01**, not a new independent task ID.

## Scientific endpoint and source

Center-out reaching with externally applied arm perturbations; area2 somatosensory cortex. Subject **Han**, DANDI **000127**, published release **0.220113.0359**. [Versioned data citation](https://doi.org/10.48324/dandi.000127/0.220113.0359); [NLB datasets](https://neurallatents.github.io/datasets); [official tensor implementation](https://github.com/neurallatents/nlb_tools/blob/42f8410b88e12db136910fa2f888b025ea0aa2ae/nlb_tools/make_tensors.py); [official scorer](https://github.com/neurallatents/nlb_tools/blob/42f8410b88e12db136910fa2f888b025ea0aa2ae/nlb_tools/evaluation.py).

Raw train asset `ded26b6c-418d-43f5-8a37-dfd072c2dbd4`, test asset `f907b288-a9b4-4c6e-9d66-6812f306e253`. Exact URLs, fetched-byte checksums, prepared-array checksums and complete source records accompany this protocol. The versioned metadata explicitly licenses the data **CC BY4.0**; vendored nlb_tools is MIT. Cache is not committed. The training NWB is1,822,876,234 bytes; only necessary HDF5 blocks were fetched through immutable-asset HTTP Range requests. The manifest does NOT claim full-file SHA verification.

## Preprocessing and split

Use pinned official `NWBDataset`, `resample(20)`, `make_train_input_tensors(...,trial_split=['train','val'],seed=0)` and `make_eval_input_tensors(...,trial_split='test',seed=0)`. Read train and test NWBFiles separately through the officially supported NWBFile constructor. Skip behavioral TimeSeries only; retain all neural spike counts and trial metadata. Behavior is neither a predictor nor target here. This also avoids unrelated behavior availability dropping neural trials. No arbitrary random frame/bin split.

Combined train+validation **364 trials**, train inputs `[364, 30, 49]`, targets `[364, 30, 16]`; official test **98 trials**, inputs `[98, 30, 49]`, targets `[98, 30, 16]`. Training labels are raw held-out-neuron counts, not inferred latents or pseudo-labels. Train/test share the source subject and recording; do not describe this as animal/session generalization. Unit strings retain source trial IDs. Both partitions carry the same true subject/session group label; they are not separate scientific session groups.

Alignment: **movement onset from −100 to +500ms;30 consecutive20ms bins**. All30 bins scored.

Official test truth comes directly from `area2_bump_20/eval_spikes_heldout` in the publisher's `eval_data_test.h5`, SHA256 `f2f434d30193251b58e6a693381fdd185c8fbc0e47d38f8810e65295bc42c865`. No target interpolation, zero-fill, shift or resampling is applied after loading that group.

## Evaluation and comparison limits

Return finite nonnegative expected counts (notHz) with target shape. The wrapper delegates to the **unchanged frozen baseE01 scorer** and has numerical equality with pinned official `bits_per_spike` on fixed positive arrays and the evaluation-mean null, including target NaNs. The null uses the evaluation-set per-neuron mean only as scoring normalization; it must never enter model fitting. Zero rates follow official1e-9 replacement.

This is a **custom supervised population diagnostic**, not an official neural-latents leaderboard submission. Root evaluation may run the original frozen baseE01 generated programs unchanged on these shapes, refitting learned coefficients solely from this slice's training arrays. There is no new prompt, model generation, selected program repair, or hyperparameter tuning after test feedback. Such portability measures whether the original algorithm transfers to different dimensions, brain areas and scientific tasks; it does not measure fresh-generation capability or historical model trend on independent tasks. Report slice results and aggregate at E01 before macro counts.

The available reference is the same frozen Gaussian(sigma1bin)+Ridge(alpha100) positive readout. It is a transparent traditional reference, **not current specialist SOTA**. No specialist leaderboard number is directly comparable without the same supervised regime and exact split.

## Validation and acknowledged limits

`../verify_slices.py` independently bins every raw test spike time with integer1ms truncation and20ms aggregation, then checks exact equality with every prepared held-in count. It verifies neuron/trial order, alignment and count units. It also checks exact official target-array equality including NaNs, integer nonnegative finite counts, and negative-output rejection. Results: `validation.json`.

All test targets are finite.

## Reproduction

With NumPy, SciPy, scikit-learn, h5py, PyNWB2.8.3 and HDMF3.14.6 installed, run `python experiments/E01/slices/area2_bump/adapter.py`; this downloads small missing files and uses cached HTTP ranges for Area2. Requires the shared official test-truth archive already acquired by baseE01 preparation. Run `python experiments/E01/slices/verify_slices.py` to verify both slices. `adapter.load()` returns four arrays; `baseline(train_x,train_y,test_x)` and `score(predictions,test_y)` delegate to unchanged baseE01 code.
