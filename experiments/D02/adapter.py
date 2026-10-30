"""Measured within-cell passive voltage deflection under held-out current steps."""
from pathlib import Path
import hashlib
import json
import shutil
import urllib.request
import numpy as np

REPO = Path(__file__).resolve().parents[2]
CACHE = REPO / "data/cache/D02"
CELL = 464212183
RAW_URL = "https://api.brain-map.org/api/v2/well_known_file_download/491202878"
SPECIMEN_URL = "https://api.brain-map.org/api/v2/data/query.json?criteria=model%3A%3ASpecimen%2Crma%3A%3Acriteria%2C%5Bid%24eq464212183%5D%2Crma%3A%3Ainclude%2Cephys_result%28well_known_files%28well_known_file_type%5Bname%24eqNWBDownload%5D%29%29"
SWEEPS_URL = "https://api.brain-map.org/api/v2/data/query.json?criteria=model%3A%3AEphysSweep%2Crma%3A%3Acriteria%2C%5Bspecimen_id%24eq464212183%5D%2Crma%3A%3Aoptions%5Bnum_rows%24eqall%5D"
TRAIN = [19, 21, 23, 24]
TEST = [20, 22]
DT = .002

def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def _acquire(url, path):
    if not path.exists():
        with urllib.request.urlopen(url, timeout=120) as r:
            path.write_bytes(r.read())

def prepare():
    import h5py
    CACHE.mkdir(parents=True, exist_ok=True)
    urls = [(RAW_URL, "464212181_ephys.nwb"), (SPECIMEN_URL, "specimen.json"), (SWEEPS_URL, "sweeps.json")]
    for url, name in urls:
        _acquire(url, CACHE / name)
    sweeps = json.loads((CACHE / "sweeps.json").read_text())
    assert sweeps["success"]
    lookup = {r["sweep_number"]: r for r in sweeps["msg"]}
    arrays = {k: [] for k in ["train_x", "train_y", "test_x", "test_y", "train_groups", "test_groups", "train_units", "test_units"]}
    details = []
    with h5py.File(CACHE / "464212181_ephys.nwb") as f:
        for split, ids in [("train", TRAIN), ("test", TEST)]:
            for number in ids:
                row = lookup[number]
                assert row["stimulus_name"] == "Long Square" and row["stimulus_absolute_amplitude"] < 0
                rg = f[f"acquisition/timeseries/Sweep_{number}"]
                sg = f[f"stimulus/presentation/Sweep_{number}"]
                rate = float(rg["starting_time"].attrs["rate"])
                assert rate == float(sg["starting_time"].attrs["rate"]) == 200000
                assert rg["data"].attrs["unit"] == b"Volts" and sg["data"].attrs["unit"] == b"Amps"
                v = np.asarray(rg["data"], dtype=np.float64) * float(rg["data"].attrs["conversion"]) * 1e3
                i = np.asarray(sg["data"], dtype=np.float64) * float(sg["data"].attrs["conversion"]) * 1e12
                start = int(round(row["stimulus_start_time"] * rate))
                assert start == 204000
                pre = int(.05 * rate)
                rest_v, rest_i = float(v[start-pre:start].mean()), float(i[start-pre:start].mean())
                block = int(DT * rate)
                # Exactly 1 second at indices 204000 through 403999 inclusive.
                stop = start + 500 * block
                current = (i[start:stop] - rest_i).reshape(500, block).mean(axis=1)
                deflection = (v[start:stop] - rest_v).reshape(500, block).mean(axis=1)
                assert np.allclose(current, current[0], atol=.001)
                assert np.isfinite(current).all() and np.isfinite(deflection).all()
                arrays[split + "_x"].append(current)
                arrays[split + "_y"].append(deflection)
                arrays[split + "_groups"].append(CELL)
                arrays[split + "_units"].append(number)
                details.append({"sweep": number, "split": split, "specimen_id": CELL, "amplitude_pa": row["stimulus_absolute_amplitude"], "pre_stimulus_voltage_mv": rest_v, "pre_window_seconds": [.97, 1.02], "response_window_seconds": [1.02, 2.02], "input_sampling_rate_hz": rate, "output_sampling_rate_hz": 500})
    arrays = {k: np.array(v) for k, v in arrays.items()}
    assert not set(arrays["train_units"]) & set(arrays["test_units"])
    np.savez_compressed(CACHE / "data.npz", **arrays)
    meta = {"benchmark_id": "D02", "slice_id": "allen464212183-passive-held-amplitudes-v1", "dataset": "Allen Cell Types Database intracellular NWB", "accessed_on": "2026-10-30", "metric": "rmse", "direction": "lower", "metric_aggregation": "RMSE over 2 held-out sweeps x 500 time bins; same length sweeps have equal weight", "task_description": "Predict the passive voltage DEFLECTION in millivolts caused by known 1-second negative current steps in picoamps for one mouse neuron. Inputs have shape (sweeps,500 time bins) at dt=0.002 seconds (500Hz). Targets have the same shape. Each target is relative to the measured mean voltage in the 50ms BEFORE that sweep; this known initial/rest information is allowed. No measured voltage during a held-out step is supplied. Four training amplitudes -110,-70,-30,-10pA; two unseen test amplitudes -90,-50pA. No spikes, resting-potential prediction or cross-cell generalization are scored.", "input": "float64 (sweep,500), current pA relative to pre-step current, block-averaged 500 Hz", "target": "float64 (sweep,500), voltage deflection mV relative to measured pre-stimulus rest", "sampling_rate_hz": 500, "dt_seconds": DT, "time_bin_centers_seconds": (.001 + np.arange(500) * DT).tolist(), "allowed_initial_condition": "Each sweep's measured 50ms PRE-stimulus voltage mean is used to define zero target; no in-pulse test response available", "specimen_id": CELL, "grouping": "cell shared by all sweeps; independent held-out stimulus sweep is prediction unit; no population CI", "train_sweeps": TRAIN, "test_sweeps": TEST, "train_groups": [CELL] * len(TRAIN), "test_groups": [CELL] * len(TEST), "train_unit_ids": TRAIN, "test_unit_ids": TEST, "n_train": len(TRAIN), "n_test": len(TEST), "train_shape": list(arrays["train_x"].shape), "test_shape": list(arrays["test_x"].shape), "split": "within-cell complete held-out hyperpolarizing amplitude sweeps: train19/21/23/24, test20/22; frozen before model evaluation", "baseline": "Train-only leave-one-amplitude-out selection among linear/quadratic through-origin response interpolation and a single-RC step response fit", "baseline_role": "transparent domain-informed conventional reference; not verified current SOTA", "current_best_status": "not verified; custom one-cell subthreshold protocol", "license": "Allen Institute Terms of Use, research/noncommercial use with attribution; no data relicensing under code license", "terms_url": "https://alleninstitute.org/terms-of-use/", "source": RAW_URL, "reader": "h5py 3.15.1 (preparation only)", "data_sha256": sha256(CACHE / "data.npz"), "limitations": ["One cell only; two test sweeps are correlated within a single preparation", "Interpolated negative pulse amplitudes only; no spikes, arbitrary waveforms, held-out stimulus family or cross-cell test", "Measured test pre-stimulus voltage establishes target zero; this is conditional deflection prediction, not absolute voltage prediction", "500Hz block averaging removes fast detail; no spike timing claim", "Only one generated program per model unless central run says otherwise; public data allow possible contamination", "No verified current specialist SOTA and no population confidence interval"]}
    (CACHE / "metadata.json").write_text(json.dumps(meta, indent=2) + "\n")
    (CACHE / "sweep-manifest.json").write_text(json.dumps(details, indent=2) + "\n")
    manifest = {"benchmark_id": "D02", "accessed_on": "2026-10-30", "files": [{"url": url, "path": str((CACHE/name).relative_to(REPO)), "bytes": (CACHE/name).stat().st_size, "sha256": sha256(CACHE/name)} for url, name in urls], "prepared": {"path": "data/cache/D02/data.npz", "sha256": meta["data_sha256"]}, "use_terms": meta["license"], "terms_url": meta["terms_url"], "attribution": "Allen Institute for Brain Science, Allen Cell Types Database (2015); https://celltypes.brain-map.org/", "redistribution": "Raw and prepared data in ignored cache; downloader/manifests tracked"}
    (REPO / "data/manifests/D02.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return meta

def load():
    with np.load(CACHE / "data.npz", allow_pickle=False) as d:
        return tuple(d[k].copy() for k in ["train_x", "train_y", "test_x", "test_y"])

def _predict(kind, train_x, train_y, test_x):
    from scipy.optimize import minimize_scalar
    a = np.mean(train_x, axis=1) / 100.
    b = np.mean(test_x, axis=1) / 100.
    if kind in ("linear", "quadratic"):
        tx = a[:, None] if kind == "linear" else np.column_stack([a, a*a])
        ux = b[:, None] if kind == "linear" else np.column_stack([b, b*b])
        coef = np.linalg.lstsq(tx, train_y, rcond=None)[0]
        return ux @ coef
    t = (np.arange(train_y.shape[1]) + .5) * DT
    def fit(tau):
        basis = a[:, None] * (1 - np.exp(-t[None, :] / tau))
        resistance = np.sum(basis * train_y) / np.sum(basis * basis)
        return resistance, np.mean((basis * resistance - train_y)**2)
    result = minimize_scalar(lambda logtau: fit(np.exp(logtau))[1], bounds=(np.log(.001), np.log(.5)), method="bounded")
    tau = np.exp(result.x)
    resistance, _ = fit(tau)
    return b[:, None] * (1 - np.exp(-t[None, :] / tau)) * resistance

def baseline(train_x, train_y, test_x):
    kinds = ["linear", "quadratic", "single_RC"]
    losses = []
    for kind in kinds:
        error = []
        for j in range(len(train_x)):
            keep = np.arange(len(train_x)) != j
            p = _predict(kind, train_x[keep], train_y[keep], train_x[j:j+1])
            error.extend(((p - train_y[j:j+1])**2).ravel())
        losses.append(float(np.mean(error)))
    return _predict(kinds[int(np.argmin(losses))], train_x, train_y, test_x)

if __name__ == "__main__":
    print(json.dumps(prepare(), indent=2))
