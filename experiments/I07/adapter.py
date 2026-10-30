"""FRESH 2-second left/right finger-tapping decoding, subject-disjoint v1.

SNIRF acquisition preparation uses h5py==3.15.1. No hemodynamic concentration
conversion: model inputs are delayed baseline-relative optical-density changes.
"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import csv
import hashlib
import io
import json
import urllib.request
import numpy as np

REPO = Path(__file__).resolve().parents[2]
CACHE = REPO / "data/cache/I07"
BASE = "https://data.nemar.org/on005963/v1.0.0/"
TRAIN_SUBJECTS = list(range(1, 8))
TEST_SUBJECTS = [8, 9, 10]
SESSIONS = ["left2s", "right2s"]


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _acquire(rel):
    target = CACHE / "raw" / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        with urllib.request.urlopen(BASE + rel, timeout=120) as response:
            target.write_bytes(response.read())
    return {"url": BASE + rel, "path": str(target.relative_to(REPO)),
            "bytes": target.stat().st_size, "sha256": sha256(target)}


def _tsv(path):
    return list(csv.DictReader(Path(path).read_text(encoding="utf-8-sig").splitlines(), delimiter="\t"))


def prepare():
    import h5py
    assert h5py.__version__ == "3.15.1"
    subjects = TRAIN_SUBJECTS + TEST_SUBJECTS
    paths = ["README.md", "dataset_description.json", "participants.tsv"]
    for subject in subjects:
        for session in SESSIONS:
            prefix = f"sub-{subject:02d}/ses-{session}/nirs/sub-{subject:02d}_ses-{session}_task-FRESHMOTOR"
            paths += [prefix + suffix for suffix in ["_nirs.snirf", "_nirs.json", "_events.tsv", "_channels.tsv"]]
    with ThreadPoolExecutor(max_workers=4) as pool:
        manifest = list(pool.map(_acquire, paths))
    description = json.loads((CACHE / "raw/dataset_description.json").read_text())
    assert description["License"] == "CC0"
    result = {k: [] for k in ["train_x", "train_y", "test_x", "test_y", "train_groups", "test_groups"]}
    units, records = [], []
    common_names = None
    for subject in subjects:
        for session in SESSIONS:
            prefix = CACHE / "raw" / f"sub-{subject:02d}/ses-{session}/nirs/sub-{subject:02d}_ses-{session}_task-FRESHMOTOR"
            channels = _tsv(str(prefix) + "_channels.tsv")
            events = _tsv(str(prefix) + "_events.tsv")
            details = json.loads(Path(str(prefix) + "_nirs.json").read_text())
            names = [c["name"] for c in channels]
            assert all(c["type"] == "NIRSCWAMPLITUDE" and c["units"] == "V" for c in channels)
            assert all(c["status"] == "good" for c in channels)
            if common_names is None:
                common_names = names
            assert names == common_names and len(names) == 136
            with h5py.File(str(prefix) + "_nirs.snirf", "r") as h:
                values = h["nirs/data1/dataTimeSeries"][()].astype(np.float64)
                time = h["nirs/data1/time"][()]
                wavelengths = h["nirs/probe/wavelengths"][()]
                assert h["nirs/metaDataTags/TimeUnit"][()] == b"s"
                assert np.array_equal(wavelengths, [760, 850])
                assert values.shape == (len(time), 136)
                assert np.isfinite(values).all() and (values > 0).all()
                assert np.allclose(np.diff(time), 0.112, atol=1e-7)
                # Verify BIDS channel order against each actual SNIRF measurement.
                for ci, channel in enumerate(channels):
                    m = h[f"nirs/data1/measurementList{ci+1}"]
                    assert int(m["dataType"][()]) == 1
                    actual = f"S{int(m['sourceIndex'][()])}_D{int(m['detectorIndex'][()])} {int(wavelengths[int(m['wavelengthIndex'][()])-1])}"
                    assert channel["name"] == actual
                snirf_events = h["nirs/stim1/data"][()]
                assert len(snirf_events) == len(events)
                assert np.allclose(snirf_events[:, 0], [float(e["onset"]) for e in events], atol=1e-4)
                assert np.allclose(snirf_events[:, 1], 2.0)
            assert np.isclose(details["SamplingFrequency"], 1 / 0.112)
            # Conversion is dimensionless optical density; no DPF/MBLL assumptions.
            optical_density = -np.log(values / values.mean(axis=0, keepdims=True))
            split = "train" if subject in TRAIN_SUBJECTS else "test"
            label = 0 if session == "left2s" else 1
            for ei, event in enumerate(events):
                onset = float(event["onset"])
                assert event["trial_type"] == "motor" and float(event["duration"]) == 2.0
                assert onset >= 3 and onset + 11 <= time[-1]
                pre = (time >= onset - 3) & (time < onset)
                baseline = optical_density[pre].mean(axis=0)
                # Eight 1-second bins cover the delayed 3 <= t < 11 second interval.
                epoch = np.stack([optical_density[(time >= onset + k) & (time < onset + k + 1)].mean(axis=0)
                                  - baseline for k in range(3, 11)], axis=-1).astype(np.float32)
                assert epoch.shape == (136, 8) and np.isfinite(epoch).all()
                result[split + "_x"].append(epoch)
                result[split + "_y"].append(label)
                result[split + "_groups"].append(subject)
                units.append({"id": f"sub-{subject:02d}_ses-{session}_event-{ei:02d}",
                              "subject": subject, "session": session, "split": split,
                              "onset": onset, "label": label})
            records.append({"subject": subject, "session": session, "n_events": len(events),
                            "shape": list(values.shape), "minimum_intensity_volts": float(values.min())})
    result = {k: np.asarray(v) for k, v in result.items()}
    assert not set(result["train_groups"]) & set(result["test_groups"])
    np.savez_compressed(CACHE / "data.npz", **result)
    metadata = {"benchmark_id": "I07", "slice_id": "fresh-2s-lr-subject-disjoint-v1",
                "dataset": "FRESH Motor Dataset", "dataset_doi": "10.18112/openneuro.ds005963.v1.0.0",
                "mirror_doi": "10.82901/nemar.on005963", "mirror_version": "v1.0.0", "license": "CC0",
                "metric": "balanced_accuracy", "direction": "higher", "n_classes": 2, "chance": 0.5,
                "input": "float32 (trial,136 optical measurement channels,8 one-second bins), baseline-relative dimensionless optical density",
                "input_details": {"raw_units": "V", "raw_sampling_rate_hz": 1 / .112,
                                  "output_units": "dimensionless natural-log optical density change",
                                  "conversion": "-ln(I/mean(I)), subtract mean optical density from -3<=t<0 seconds per event",
                                  "time_bins_seconds": [[k, k + 1] for k in range(3, 11)],
                                  "wavelengths_nm": [760, 850], "channel_names": common_names,
                                  "label_encoding": {"0": "left-hand 2-second finger tapping", "1": "right-hand 2-second finger tapping"}},
                "train_shape": list(result["train_x"].shape), "test_shape": list(result["test_x"].shape),
                "n_train": len(result["train_y"]), "n_test": len(result["test_y"]),
                "train_subjects": TRAIN_SUBJECTS, "test_subjects": TEST_SUBJECTS,
                "train_groups": result["train_groups"].tolist(), "test_groups": result["test_groups"].tolist(),
                "train_unit_ids": [u["id"] for u in units if u["split"] == "train"],
                "test_unit_ids": [u["id"] for u in units if u["split"] == "test"],
                "grouping": "participant; events nested within condition-specific recording",
                "split": "fixed subject1–7 training;8–10 held out; only left2s/right2s sessions",
                "metric_aggregation": "pooled trial balanced accuracy; participant scores secondary",
                "baseline": "Mean delayed optical-density response per channel, train-only standardization and shrinkage LDA",
                "current_best_status": "not verified; novel slice, no comparable published decoder score",
                "reader": "h5py3.15.1", "data_sha256": sha256(CACHE / "data.npz"),
                "limitations": ["Condition is blocked by recording; session/order/instrument confounding can aid classification",
                                  "Only three held-out participants; trial scores are not independent participant replications",
                                  "Optical density input is not HbO/HbR concentration; no DPF or short-channel correction",
                                  "Known task condition is ground truth, not a gold standard for cortical activation or physiology",
                                  "Demographic table has placeholder fields; no age-specific analysis",
                                  "Single dataset and predetermined participant IDs, no representative cohort claim"]}
    (CACHE / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    (CACHE / "trial-manifest.json").write_text(json.dumps(units, indent=2) + "\n")
    (CACHE / "record-checks.json").write_text(json.dumps(records, indent=2) + "\n")
    (REPO / "data/manifests/I07.json").write_text(json.dumps({"benchmark_id": "I07", "accessed_on": "2026-10-30",
        "source": BASE, "license": "CC0", "files": manifest,
        "prepared": {"path": "data/cache/I07/data.npz", "sha256": metadata["data_sha256"]}}, indent=2) + "\n")
    return metadata


def load():
    with np.load(CACHE / "data.npz", allow_pickle=False) as d:
        return tuple(d[k].copy() for k in ["train_x", "train_y", "test_x", "test_y"])


def baseline(train_x, train_y, test_x):
    from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
    from sklearn.preprocessing import StandardScaler
    train = np.asarray(train_x, np.float64).mean(axis=-1)
    test = np.asarray(test_x, np.float64).mean(axis=-1)
    scaler = StandardScaler().fit(train)
    model = LinearDiscriminantAnalysis(solver="lsqr", shrinkage="auto")
    model.fit(scaler.transform(train), train_y)
    return model.predict(scaler.transform(test))


if __name__ == "__main__":
    print(json.dumps(prepare(), indent=2))
