# B01: blind unsupervised sorting of a standard MEArec simulation

## Scope

This frozen slice evaluates detection and neuron assignment from a short extracellular voltage recording. The source is the **simulated** 10-second MEArec fixture used in [SpikeInterface's official ground-truth comparison example](https://spikeinterface.readthedocs.io/en/0.96.1/modules/comparison/plot_3_compare_sorter_with_ground_truth.html). It is not paired real recording truth, a drift benchmark, a full SpikeForest run, or independent supervised test-set prediction. The source uses MEArec 1.5.1, known generation seeds and no drift.

The source has 32 channels, 320,000 samples at 32 kHz, amplitudes in microvolts, electrode positions in micrometers, and a 300–6000 Hz source bandpass. All source units and spike times remain in the hidden external scorer. The model receives no true unit count, firing times, neuron IDs, generation templates, locations of simulated cells or clean per-unit traces. Whole-recording unsupervised waveform/template/clustering estimation is permitted, as it normally is in spike sorting.

## Resource and rights

Source: [NeuralEnsemble electrophysiology testing data](https://gin.g-node.org/NeuralEnsemble/ephy_testing_data), file `mearec/mearec_test_10s.h5`, 62,317,832 bytes. Pin repository revision `71e5c5b04e34ab9e69533a4fb092a6ce4d244034`; retain SHA-256 in `data/manifests/B01.json`. The [primary repository README](https://gin.g-node.org/NeuralEnsemble/ephy_testing_data/raw/71e5c5b04e34ab9e69533a4fb092a6ce4d244034/README.md) declares ODbL 1.0 for the database and links CC BY-SA 4.0 for individual contents. Preserve these data terms separately from the repository's code license. Raw/prepared source data remain in ignored cache.

This is an additional standard SpikeInterface/MEArec resource for the registry's B01 spike-sorting task; it does not retroactively establish execution of an official SpikeForest protocol. [SpikeForest's primary repository](https://github.com/flatironinstitute/spikeforest) currently documents a subset release and a kachery-cloud client association with a Google user. Older SHA-1 pointer examples alone were not treated as proof of current credentialless paired-data acquisition. Real paired data remain a high-priority follow-up; simulation is labeled plainly.

## Interface and preparation

`sort(recording_uv, fs, channel_positions_um)` returns a two-column integer event array: `[sample_index, arbitrary_nonnegative_unit_id]`. Sample indices are within the supplied recording, not seconds. Same-unit duplicate sample events are invalid. Output ordering is normalized by time and unit; output cluster labels are arbitrary because the scorer matches them to hidden units.

`inputs.npz` contains only voltage, sampling rate and electrode positions. `truth.npz` separately contains event truth and unit IDs and is never accessible to generated sorting programs. The raw source HDF5, its simulated templates, per-unit clean traces and source annotations must also remain inaccessible to model programs, which would otherwise expose the answer. The root harness isolates permitted arrays and records exact source, model, prompt and runtime constraints.

The recording is already bandpass filtered by the source generator, so no additional bandpass is applied by the adapter. The official Neo/SpikeInterface time-to-sample convention multiplies seconds by sampling frequency then casts to int64 (floor for these nonnegative times); the preparation applies the same conversion. Input timestamps, dimensions, finiteness and no-drift flag are checked. There is one scored recording with hidden labels, not a training recording plus a new test recording.

## Specialist configuration fixed before first score

The sole chosen specialist reference is **MountainSort5 0.5.9 scheme 1**, using **SpikeInterface 0.105.4** preprocessing. It estimates waveform clusters from voltage only; it does not use source templates or truth-derived tuning.

Before any specialist/model test score, fix:

- SpikeInterface global whitening, mean subtraction and regularization through its default GraphicalLassoCV covariance method; seed 20261030; 20 chunks of 10,000 samples each from the unlabeled recording.
- Negative detection threshold 5.5 in whitened units; spatial suppression radius 100 µm; temporal suppression radius 0.5 ms.
- Waveform snippets of 20 samples before and 44 after detection; spatial mask radius 150 µm.
- Three PCA components per channel and ten per clustering subdivision; alignment enabled.
- One numerical thread and NumPy seed 20261030. Exact parameter dictionaries are saved in `adapter.py` and metadata.

These values are preselected practical parameters, not a claim of the best possible MountainSort configuration. Preserve execution failures and runtime evidence. Do not select a new threshold, tolerance, filter, cluster count or alignment offset after inspecting truth comparisons. Package/environment repairs may be documented separately; they do not authorize score-driven parameter changes.

## Official event/unit scorer

Use `spikeinterface.comparison.compare_sorter_to_ground_truth` 0.105.4, count agreement, Hungarian one-to-one unit matching and exhaustive simulated truth. Requested coincident event tolerance is **0.4 ms**; the pinned implementation applies `int(delta_time/1000*fs)`, giving **12 samples or 0.375 ms** at 32 kHz. Matching threshold 0.5, chance threshold 0.1, well-detected threshold 0.8, redundant and overmerged thresholds 0.2 are fixed.

Primary metric is mean ground-truth-unit accuracy: `TP/(TP+FN+FP)` per source unit, averaged over all source units, including zero for unmatched units. This is SpikeInterface's accuracy/Jaccard definition, not raw event classification accuracy. An empty valid predicted sorting receives zero. Ground-truth identity recovers 1 in a scorer integrity test; that oracle test is not a method result.

The mean over ground-truth units does not fully penalize extra unmatched predicted clusters. Therefore preserve and display predicted unit/event counts, false-positive units, redundant units, overmerged units, well-detected units, and per-unit precision/recall with the primary score. No single metric alone establishes useful sorting. No archived tutorial number is transplanted as current SOTA.

## Limits

One public, short, stationary, seeded simulation cannot establish performance on drift, real recording artifacts, new probes, animals or labs. Known synthetic waveforms and noise may favor methods differently from paired real data. Source labels/templates are public and could be present in model pretraining. Units and events within one simulation are not independent biological replications. The task measures one-shot code construction of an unsupervised sorter when paired with the central model harness; it does not directly measure a general model reading raw signals without numerical computation.

## Worklog

- 2026-10-30: Reviewed primary SpikeForest access instructions, SpikeInterface scorer/tutorial documentation and standard test-data repository terms. Inspected the 62.3 MB fixture size before acquisition; selected the smallest clear, credentialless standard synthetic case rather than silently claiming paired real data.
- 2026-10-30: Acquired fixture, recorded repository revision, inspected HDF5 voltage/timestamps/positions/truth fields and generation metadata. Installed isolated SpikeInterface, MountainSort5 and compiled isosplit6 dependencies.
- 2026-10-30: Froze input/truth separation, unsupervised interface, preprocessing, sole specialist configuration, official matching parameters and diagnostics **before** calculating any specialist/model score.
- Later runtime/scorer checks and specialist-only execution are recorded in separate cache logs. Model calls remain the central harness's responsibility.
- First specialist attempt failed before sorting or prediction: SpikeInterface's convenience geometry setter projected the source's planar xyz coordinates onto xy, producing duplicate contacts because every x coordinate is zero. The repair passes the original y/z plane, preserving all inter-contact distances. It changes no sorting parameter or scorer; the original failure, source and log are retained in `infrastructure-attempt-1`. No specialist score existed at repair time.
- The frozen specialist then completed in 2.894 seconds: mean ground-truth-unit accuracy 0.940896, precision 0.995306, recall 0.945451; 11 predicted units and 729 events, with one redundant unit and no false-positive/overmerged units under the pinned category definitions. Exact events, per-unit results, source hash and execution log remain in `data/cache/B01/specialist-*` for central result integration. This single reproduced baseline is not a current-SOTA claim. No general-model generation was performed by this admission worker.
