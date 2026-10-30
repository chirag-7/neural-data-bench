"""FALCON M2 custom chronological cross-day neural-to-finger-velocity slice.

Only small spike/kinematic HDF5 datasets are HTTP range-read; raw fullband voltage
is neither downloaded nor used. This is NOT the official FALCON held-out score.
"""
from pathlib import Path
import hashlib
import json
import urllib.request
import numpy as np

REPO = Path(__file__).resolve().parents[2]
CACHE = REPO / "data/cache/G01"
HERE = Path(__file__).resolve().parent


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha256(path):
    return sha256_bytes(Path(path).read_bytes())


def _extract(spec):
    import h5py
    import fsspec
    name = Path(spec["path"]).stem
    path = CACHE / "extracted" / (name + ".npz")
    receipt = path.with_suffix(".json")
    if path.exists() and receipt.exists():
        record = json.loads(receipt.read_text())
        assert sha256(path) == record["extracted_npz_sha256"]
        return path, record
    # Resolve public data redirect only in memory: do not persist transient URLs.
    meta_url = f"https://api.dandiarchive.org/api/assets/{spec['asset_id']}/"
    asset_meta = json.load(urllib.request.urlopen(meta_url, timeout=90))
    assert asset_meta["contentSize"] == spec["bytes"]
    with urllib.request.urlopen(spec["download_url"], timeout=90) as response:
        resolved = response.geturl()
    buffers = {}
    component_hashes = {}
    with fsspec.open(resolved, mode="rb", block_size=1024*1024, cache_type="blockcache") as remote:
        with h5py.File(remote, "r") as h:
            mapping = {"unit_ids": "units/id", "spike_times": "units/spike_times",
                       "spike_times_index": "units/spike_times_index",
                       "index_velocity": "acquisition/finger_vel/index/data",
                       "mrs_velocity": "acquisition/finger_vel/mrs/data",
                       "timestamps": "acquisition/finger_vel/index/timestamps",
                       "mrs_timestamps": "acquisition/finger_vel/mrs/timestamps",
                       "eval_mask": "acquisition/eval_mask/data",
                       "trial_ids": "intervals/trials/trial_num",
                       "trial_start": "intervals/trials/start_time",
                       "trial_stop": "intervals/trials/stop_time"}
            for key, dataset_path in mapping.items():
                value = h[dataset_path][()]
                buffers[key] = value
                component_hashes[key] = {"dataset_path": dataset_path,
                    "shape": list(value.shape), "dtype": str(value.dtype),
                    "sha256_contiguous_bytes": sha256_bytes(np.ascontiguousarray(value).tobytes())}
            units = [str(h[f"acquisition/finger_vel/{axis}/data"].attrs["unit"])
                     for axis in ["index", "mrs"]]
            assert units == ["AU", "AU"]
            assert np.array_equal(buffers["unit_ids"], np.arange(96))
    np.savez_compressed(path, **buffers)
    record = dict(spec, source_metadata_url=meta_url,
                  source_reported_digest=asset_meta["digest"],
                  acquisition="partial HTTP range extraction of named HDF5 datasets",
                  full_file_sha256_independently_verified=False,
                  target_source_units=units, components=component_hashes,
                  extracted_npz_path=str(path.relative_to(REPO)),
                  extracted_npz_sha256=sha256(path))
    receipt.write_text(json.dumps(record, indent=2) + "\n")
    return path, record


def _features(d):
    """96 causal spike-count features; no future observation or target statistics."""
    times = d["timestamps"]
    assert np.array_equal(times, d["mrs_timestamps"])
    assert np.isfinite(times).all() and (np.diff(times) > 0).all()
    y = np.column_stack([d["index_velocity"], d["mrs_velocity"]])
    count = np.zeros((len(times), 96), dtype=np.float64)
    # M2 official loader treats behavior timestamps as bin STARTS, 20 ms bins.
    # Match the official edge semantics on discontinuous series, too.
    ends = times + 0.02
    starts = np.r_[ends[0] - 0.02, ends[:-1]]
    gap = np.r_[False, np.diff(ends) > 0.02 + 1e-8]
    starts[gap] = ends[gap] - 0.02
    last = 0
    for channel, stop in enumerate(d["spike_times_index"]):
        spikes = d["spike_times"][last:int(stop)]
        last = int(stop)
        assert (np.diff(spikes) >= 0).all()
        # Histogram bins are [start,end), except the globally final edge inclusive.
        a = np.searchsorted(spikes, starts, side="left")
        b = np.searchsorted(spikes, ends, side="left")
        if len(ends):
            b[-1] = np.searchsorted(spikes, ends[-1], side="right")
        count[:, channel] = b - a
    assert last == len(d["spike_times"])
    trial_index = np.searchsorted(d["trial_start"], times, side="right") - 1
    valid_index = np.maximum(trial_index, 0)
    in_trial = (trial_index >= 0) & (times < d["trial_stop"][valid_index])
    trial_id = d["trial_ids"][valid_index]
    # Fixed official-reference causal exponential kernel: 12 taps over 0..220ms.
    kernel = np.exp(-np.arange(0, 240, 20) / 240.0)
    kernel /= kernel.sum()
    from scipy.signal import lfilter
    filtered = lfilter(kernel, [1.0], count, axis=0)
    good = d["eval_mask"].astype(bool) & in_trial & np.isfinite(y).all(axis=1)
    # Same-file trial boundaries remain inside one split; filtering uses only
    # observed past spikes, never past/future velocity labels. Do not reset on labels.
    assert good.any() and np.isfinite(filtered).all()
    return filtered[good].astype(np.float32), y[good].astype(np.float32), trial_id[good], times[good]


def prepare():
    spec = json.loads((HERE / "source-assets.json").read_text())
    (CACHE / "extracted").mkdir(parents=True, exist_ok=True)
    result = {k: [] for k in ["train_x", "train_y", "test_x", "test_y", "train_groups", "test_groups",
                              "train_trial_ids", "test_trial_ids", "train_times", "test_times"]}
    receipts, checks = [], []
    for file in spec["files"]:
        path, receipt = _extract(file)
        receipts.append(receipt)
        session = Path(file["path"]).stem.split("_ses-")[1]
        day = session[:10]
        split = "train" if day in spec["train_days"] else "test"
        assert day in spec["train_days"] + spec["test_days"]
        with np.load(path, allow_pickle=False) as d:
            x, y, trials, time = _features(d)
            checks.append({"session": session, "day": day, "split": split,
                           "n_source_trials": len(d["trial_ids"]),
                           "n_scored_trials": len(np.unique(trials)), "n_scored_bins": len(x),
                           "velocity_variance": np.var(y, axis=0).tolist()})
        result[split + "_x"].append(x)
        result[split + "_y"].append(y)
        result[split + "_groups"].append(np.repeat(day, len(x)))
        result[split + "_trial_ids"].append(np.array([session + "_trial" + str(t) for t in trials]))
        result[split + "_times"].append(time)
    result = {k: np.concatenate(v, axis=0) for k, v in result.items()}
    assert not set(result["train_groups"]) & set(result["test_groups"])
    assert not set(result["train_trial_ids"]) & set(result["test_trial_ids"])
    assert len(np.unique(result["train_trial_ids"])) >= 100
    assert len(np.unique(result["test_trial_ids"])) >= 100
    np.savez_compressed(CACHE / "data.npz", **result)
    metadata = {"benchmark_id": "G01", "slice_id": "falcon-m2-calib-chronological-v1",
                "dataset": "FALCON M2 monkey finger-movement data", "dataset_id": "DANDI:000953",
                "dataset_version": "draft snapshot; exact asset UUID/blob IDs pinned", "license": "CC-BY-4.0",
                "metric": "r2_variance_weighted", "direction": "higher",
                "metric_definition": "sklearn r2_score(test_y,prediction,multioutput='variance_weighted') over source eval_mask bins",
                "input": "float32 (time_bins,96) causal exponential-filtered 20ms multiunit spike counts",
                "input_details": {"bin_width_seconds": 0.02, "causal_smoothing": "12-tap exponential tau240ms,source-reference convention",
                                  "target_order": ["index", "mrs"], "target_units": "AU, as stored in original finger_vel; no conversion to physical SI or AU/s",
                                  "acquisition_latency": "20ms spike bin must complete; smoothing uses current and previous bins only",
                                  "no_future_data": True},
                "train_shape": list(result["train_x"].shape), "test_shape": list(result["test_x"].shape),
                "n_train": len(result["train_y"]), "n_test": len(result["test_y"]),
                "train_days": spec["train_days"], "test_days": spec["test_days"],
                "train_group_counts": {day: int((result["train_groups"] == day).sum()) for day in spec["train_days"]},
                "test_group_counts": {day: int((result["test_groups"] == day).sum()) for day in spec["test_days"]},
                "grouping": "one monkey; held-out days; samples nested in trials/runs/days",
                "split": "official held-in-calib files only, custom trainOct19/20; testOct27/28; no minival or official held-out evaluation",
                "n_train_trials": len(np.unique(result["train_trial_ids"])),
                "n_test_trials": len(np.unique(result["test_trial_ids"])),
                "baseline": "FALCON-style causal count filtering and train-only standardized cross-validated ridge regression",
                "current_best_status": "not verified; custom within-dataset day split, not official FALCON leaderboard protocol",
                "data_sha256": sha256(CACHE / "data.npz"),
                "limitations": ["One monkey and two held-out days; no participant-generalization claim",
                                  "Custom split of public calibration data; not official few-shot FALCON or final held-out score",
                                  "Offline code receives fixed causal features; no closed-loop control, online budget or full sequence-agent claim",
                                  "Native velocity units retained; do not assume AU/s",
                                  "Partial source extraction; source full-file SHA-256 reported but not independently verified"]}
    (CACHE / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    (CACHE / "record-checks.json").write_text(json.dumps(checks, indent=2) + "\n")
    (REPO / "data/manifests/G01.json").write_text(json.dumps({"benchmark_id": "G01", "checked_on": "2026-10-30",
        "dataset_id": "000953", "license": "CC-BY-4.0", "files": receipts,
        "prepared": {"path": "data/cache/G01/data.npz", "sha256": metadata["data_sha256"]}}, indent=2) + "\n")
    return metadata


def load():
    with np.load(CACHE / "data.npz", allow_pickle=False) as d:
        return tuple(d[k].copy() for k in ["train_x", "train_y", "test_x", "test_y"])


def baseline(train_x, train_y, test_x):
    from sklearn.linear_model import RidgeCV
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import make_scorer, r2_score
    # FALCON reference searches these20alphas. This explicit pipeline confines
    # standardization/model selection to training input/targets only.
    scorer = make_scorer(r2_score, multioutput="variance_weighted")
    model = make_pipeline(StandardScaler(), RidgeCV(alphas=np.logspace(-5, 5, 20), cv=5, scoring=scorer))
    model.fit(train_x, train_y)
    return model.predict(test_x)


def score(target, prediction):
    from sklearn.metrics import r2_score
    return float(r2_score(target, prediction, multioutput="variance_weighted"))


if __name__ == "__main__":
    print(json.dumps(prepare(), indent=2))
