# D02: within-cell passive voltage deflection, slice v1

## What is evaluated

Predict a measured neuron's voltage deflection during a known 1-second negative current step at two unseen amplitudes. This is a deliberately narrow real-data current-to-voltage task: one mouse cell, subthreshold hyperpolarization, held-out complete sweeps. It does not evaluate spikes, arbitrary current waveforms, resting-potential prediction, mechanistic identification, or transfer to other cells.

The [Allen Cell Types API documentation](https://brain-map.org/support/documentation/cell-types-database-api) describes current-injection sweeps, measured voltage, NWB downloads and long-square protocols. The [AllenSDK data example](https://alleninstitute.github.io/AllenSDK/_static/examples/nb/cell_types.html) supplies specimen 464212183 as an accessible example. The specimen is a mouse Sst-IRES-Cre;Ai14 cell (donor 312883165). No genetic metadata are prediction inputs.

## Source and acquisition

On 2026-10-30 the official specimen API identified NWB file 491202878, `464212181_ephys.nwb`. An HTTP HEAD response established a manageable 61,980,832-byte recording before acquisition. The official EphysSweep API supplied 102 sweep annotations, including 21 Long Square sweeps. File URLs, SHA-256 and byte counts are tracked in `data/manifests/D02.json`; raw files remain in ignored `data/cache/D02`.

The file is old-style NWB HDF5. The adapter reads `acquisition/timeseries/Sweep_N/data` and `stimulus/presentation/Sweep_N/data` with h5py 3.15.1. Their stored units are Volts and Amps, conversions 1.0, and both rates are 200,000 Hz. The stimulus onset is 1.02 seconds relative to each sweep, indices 204000–403999 inclusive for the entire 1-second pulse. The reader checks units, rates, annotations, finiteness and constant pulse amplitude.

## Frozen split and processing

Use the six negative Long Square amplitudes -110,-90,-70,-50,-30,-10 pA. This selection uses stimulus metadata and the passive hyperpolarizing domain; it does not select trials according to predictive performance. Training sweeps 19,21,23,24 have amplitudes -110,-70,-30,-10 pA; test sweeps 20,22 have amplitudes -90,-50 pA. Entire sweeps are split; no fragment from a held-out sweep enters training. All sweeps belong to the same cell. Test amplitudes are interpolated between training amplitudes, not out-of-range challenges.

For each sweep, subtract its measured current and voltage means from the 50 ms before the pulse (0.97–1.02 seconds). The test PRE-stimulus voltage is explicitly allowed initial-condition information and defines zero response. The measured voltage during the test pulse remains the hidden target. The task predicts **deflection relative to pre-stimulus rest**, not absolute voltage without prior state. Root model prompts describe this conditioning.

Average consecutive nonoverlapping blocks of 400 raw samples. At 500 Hz, x has shape `(sweeps,500)` in pA; y has the same shape in mV. Bin centers are 1,3,…,999 ms after pulse onset. The deterministic averaging is performed independently per sweep. It is an explicitly low-pass endpoint and does not preserve fast spike details.

## Metric and baseline

Primary metric is RMSE in mV, pooled over both held-out 500-bin responses. Report each sweep if desired; equal-length sweeps carry equal weight. There are two correlated sweeps from one cell, so a cell/animal population confidence interval is not justified.

The transparent domain-informed conventional reference uses leave-one-amplitude-out training validation to choose among (1) linear-through-origin response interpolation, (2) quadratic-through-origin interpolation and (3) a single passive RC step response with a fitted resistance coefficient and time constant constrained to 1–500 ms. Interpolation candidates fit each output time bin using only the four training responses. RC fits minimize training squared voltage error. The winner is chosen on pooled held-training-amplitude MSE, then refit on all training sweeps. Ties follow the stated order. No test label selects the candidate or parameters. This reference is stronger than selecting a simple RC model after viewing test results, but it is not verified current specialist SOTA. No scores from full spiking/cross-cell papers can be transplanted to this slice.

## Validity limits

A general program can solve this narrow setting through amplitude interpolation. A win here cannot imply successful biophysical modeling, spiking prediction or general laboratory deployment. Whole-sweep drift, imperfect bridge compensation and active hyperpolarizing currents may affect the apparent passive response. The public example may be represented in model training. Between-model differences require repeated independent generations before being interpreted as stable model ability.

## Worklog

- 2026-10-30: Inspected official specimen/sweep metadata and recording size before downloading a single 62 MB NWB file. No large corpus download attempted.
- 2026-10-30: Confirmed HDF5 schema, units/rates, stimulus edges and finite voltage ranges for all six negative sweeps. Response ranges were inspected for data quality, not to score a candidate estimator. No model predictions existed at protocol freeze.
- 2026-10-30: Fixed complete-sweep train/test IDs, response units, known pre-stimulus state, block averaging, primary metric and train-only reference selection before model evaluation. Prepared arrays and source/sweep manifests with split assertions.
- Model outputs, prediction hashes, timings and external test scores are subsequently recorded by the central execution harness.

## Data terms

Attribute Allen Institute for Brain Science, Allen Cell Types Database (2015), [celltypes.brain-map.org](https://celltypes.brain-map.org/). The [Allen Institute Terms of Use](https://alleninstitute.org/terms-of-use/) permit research/noncommercial use with attribution and retain separate data terms; repository code licensing does not relicense these data. Run `python experiments/D02/adapter.py` with the isolated HDF5 reader available to reproduce acquisition and preparation.
