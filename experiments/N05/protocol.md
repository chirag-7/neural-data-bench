# N05: deterministic real-NWB loading and physical-unit audit

## Purpose and scope

This task tests whether a model-generated parser correctly reads a real laboratory neurophysiology file, converts physical units, locates stimulus timing and computes defined voltage summaries. It is a foundational laboratory workflow task, not scientific discovery, a neural predictor, an autonomous analysis study, or a full NWB standards-conformance test.

Use the same [Allen Cell Types](https://brain-map.org/support/documentation/cell-types-database-api) intracellular NWB file already acquired for D02: specimen 464212183, official file 491202878. This adds a transparent Allen NWB fixture to N05's broader NWB-loading task beyond the originally mapped DANDI/IBL candidate archives. Do not describe it as a DANDI benchmark result or count the fixture as an independent dataset from D02. K01 also uses the same Allen collection, although it predicts a different endpoint from many cells.

## Fixture and interface

`extract(nwb_path) -> JSON-serializable dict` receives exactly one real file. At runtime the program may read that file and use Python standard library, NumPy and h5py 3.15.1. No auxiliary answer, reference code, metadata sidecar, internet or hardcoded extracted numbers are allowed. Models generate the program without exploratory tool access; execution is external. The root harness records exact prompts, returned source, permissions and scoring.

The ignored cache path `data/cache/N05/fixture.nwb` is a relative symlink to `../D02/464212181_ephys.nwb`, preserving the source hash and avoiding a duplicate 62 MB download. `prepare.py` requires D02 acquisition first and regenerates the alias and audited answers. It does not modify the underlying file. Raw data remain under the [Allen Institute research/noncommercial terms](https://alleninstitute.org/terms-of-use/) with attribution; repository code licensing does not relicense the source data.

The model-facing specification is [task.json](task.json), containing only calculation definitions, required keys and types. It does not expose the expected version string or measured answers.

## Required calculations

Return the recorded NWB version and ten fields for each of six sweeps numbered 19–24:

- Recorded sampling rate, total sample count and reciprocal sample interval.
- Stored response and stimulus unit strings, decoded from bytes.
- Main negative-current-pulse onset relative to the sweep start and sample-count duration.
- Main current amplitude in pA relative to the immediately preceding 50 ms current mean.
- Mean response voltage in that preceding 50 ms, in mV.
- Mean response voltage during the main pulse minus the preceding voltage mean, in mV.

The main pulse is the longest contiguous run at least 1e-6 pA below the median holding current. This distinguishes the sustained experimental current from an initial short test pulse. Physical current/voltage calculations must use data conversion attributes and stored units. Absolute acquisition clock values do not replace time relative to the sweep. The complete response length includes all initial/test-pulse portions.

## Reference and independent crosschecks

`reference.py` reads HDF5 directly and produces deterministic answers in ignored `expected.json`. It computes the longest pulse from current data, rather than copying the official annotated times. `prepare.py` crosschecks pulse amplitude and onset against the separate official EphysSweep API response acquired for D02. Official pulse duration uses last-minus-first sample timestamps and is one sample shorter than sample-count duration; the crosscheck tolerates exactly that convention difference. The scoring definition explicitly uses sample-count duration.

Prestimulus means are independently crosschecked against D02's recorded sweep manifest, and mean voltage deflections against D02's independently prepared block-averaged target arrays. These checks establish agreement of two implementations and source metadata; they are not independent biological ground truth or verification of the source laboratory's hardware calibration. The full source hash, reference-answer hash and crosscheck paths are in `data/manifests/N05.json`; six check records are in ignored `validation.json`.

## Scoring fixed before model outputs

There are 61 scored leaf fields: one version string plus six sweeps × eight numeric fields and two unit strings. Primary score is mean field accuracy; secondary score is whether every required field is correct. No model judge or interpretive rubric is involved.

Strings must match exactly after decoding. Sample counts must match exactly. Numeric tolerances use `abs(actual-expected) <= atol + rtol*abs(expected)`:

| Field | Absolute tolerance | Relative tolerance |
|---|---:|---:|
| sampling rate, Hz | 1e-6 | 0 |
| sample interval, seconds | 1e-12 | 0 |
| pulse onset and duration, seconds | 1e-9 | 0 |
| current amplitude, pA | 1e-5 | 1e-8 |
| voltage mean and deflection, mV | 1e-5 | 1e-8 |

Missing, nonfinite, wrong-type or failed-extraction fields receive zero. Additional irrelevant keys cannot substitute for required fields. The correct reference obtains 1.0 by construction; it is an audited deterministic reference, not a measured specialist or verified state-of-the-art performance estimate.

## Limits and dependency accounting

The six sweeps and 61 fields share one neuron/file and several calculations. They are correlated checks, not 61 independent experiments, and field-wise significance tests would be misleading. There is no held-out file format, lab, acquisition system or animal. A clean result demonstrates success on this legacy fixture with explicit instructions, not robust deployment across arbitrary NWB files or identification of injected corruptions. N06 remains a separate, unexecuted fault-detection construction.

When summarizing macro trends, report this operational score separately from prediction accuracy and record its shared source dependency on D02. Do not inflate independent biological dataset breadth when adding workflow-family coverage.

## Worklog

- 2026-10-30: Reused the acquired D02 real NWB source with a relative alias and identical SHA-256; no additional raw dataset download.
- 2026-10-30: Fixed model-facing schema, physical calculations and per-field scoring tolerances before any parser-model output.
- 2026-10-30: Built reference answers; official sweep amplitude/onset, one-sample duration convention, D02 prestimulus means and independently block-averaged deflections all passed crosschecks for all six sweeps.
- 2026-10-30: Screened all six existing N-family entries against primary source descriptions and recorded why additional agentic/rubric-based cases require separate execution conditions. Found EEGAgentBench as an additional related primary resource and reported it for central registry review.
- Root harness subsequently records actual model generations, parser results and scores.
