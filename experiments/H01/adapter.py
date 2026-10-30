"""Fixed subject-disjoint PhysioNet EEGMMI left/right imagery slice.

Acquisition needs mne==1.10.2; evaluation/baseline needs numpy/scipy/sklearn.
Raw arrays are microvolts, common-average referenced, 1.0 <= t < 4.0 s.
"""
from pathlib import Path
import hashlib
import json
import urllib.request
from concurrent.futures import ThreadPoolExecutor
import numpy as np

REPO = Path(__file__).resolve().parents[2]
CACHE = REPO / "data/cache/H01"
SOURCE = "https://physionet.org/files/eegmmidb/1.0.0/"
TRAIN_SUBJECTS = [1, 2, 3, 4, 5]
TEST_SUBJECTS = [6, 7, 8]
RUNS = [4, 8, 12]  # left-versus-right imagined fist movement, never execution


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _download(pair):
    subject, run = pair
    rel = f"S{subject:03d}/S{subject:03d}R{run:02d}.edf"
    target = CACHE / "raw" / Path(rel).name
    if not target.exists():
        temp = target.with_suffix(".partial")
        with urllib.request.urlopen(SOURCE + rel, timeout=90) as response:
            temp.write_bytes(response.read())
        temp.replace(target)
    return {"subject": subject, "run": run, "url": SOURCE + rel,
            "path": str(target.relative_to(REPO)), "bytes": target.stat().st_size,
            "sha256": sha256(target)}


def prepare():
    """Acquire immutable version files, hash each, and prepare the frozen split."""
    import mne
    assert mne.__version__ == "1.10.2", "Use the pinned EDF reader for preparation"
    (CACHE / "raw").mkdir(parents=True, exist_ok=True)
    pairs = [(s, r) for s in TRAIN_SUBJECTS + TEST_SUBJECTS for r in RUNS]
    with ThreadPoolExecutor(max_workers=4) as pool:
        manifest = list(pool.map(_download, pairs))
    arrays = {k: [] for k in ["train_x", "train_y", "test_x", "test_y",
                             "train_groups", "test_groups", "train_units", "test_units"]}
    trial_manifest = []
    channel_names = None
    for item in manifest:
        subject, run = item["subject"], item["run"]
        raw = mne.io.read_raw_edf(REPO / item["path"], preload=True, verbose="ERROR")
        assert float(raw.info["sfreq"]) == 160.0
        assert len(raw.ch_names) == 64
        names = [n.strip('.').upper() for n in raw.ch_names]
        if channel_names is None:
            channel_names = names
        assert names == channel_names
        signal = raw.get_data() * 1e6
        signal -= signal.mean(axis=0, keepdims=True)
        split = "train" if subject in TRAIN_SUBJECTS else "test"
        for trial, annotation in enumerate(raw.annotations):
            desc = annotation["description"]
            if desc not in ("T1", "T2"):
                continue
            onset, duration = float(annotation["onset"]), float(annotation["duration"])
            # Entire 3 s epoch remains inside its 4.1 s task interval.
            assert duration >= 4.0
            start = int(round((onset + 1.0) * 160))
            stop = start + 480
            epoch = signal[:, start:stop].astype(np.float32)
            assert epoch.shape == (64, 480) and np.isfinite(epoch).all()
            label = 0 if desc == "T1" else 1
            unit = f"S{subject:03d}R{run:02d}_event{trial:02d}"
            arrays[split + "_x"].append(epoch)
            arrays[split + "_y"].append(label)
            arrays[split + "_groups"].append(subject)
            arrays[split + "_units"].append(unit)
            trial_manifest.append({"unit_id": unit, "subject": subject, "run": run,
                                   "split": split, "onset_seconds": onset,
                                   "duration_seconds": duration, "label": label})
    arrays = {k: np.array(v) for k, v in arrays.items()}
    assert not set(arrays["train_groups"]) & set(arrays["test_groups"])
    assert set(arrays["train_y"]) == set(arrays["test_y"]) == {0, 1}
    np.savez_compressed(CACHE / "data.npz", **arrays)
    metadata = {
        "benchmark_id": "H01", "slice_id": "physionet-mi-lr-subjects1-8-v1",
        "dataset": "EEG Motor Movement/Imagery Dataset", "version": "1.0.0",
        "dataset_doi": "10.13026/C28G6P", "license": "ODC-By-1.0",
        "metric": "balanced_accuracy", "direction": "higher", "n_classes": 2,
        "chance": 0.5, "metric_aggregation": "pooled trials; report per-subject balanced accuracy separately",
        "input": "float32 (trial,64 channels,480 samples), microvolts, common-average referenced",
        "input_details": {"sampling_rate_hz": 160, "epoch_seconds": [1.0, 4.0],
                          "channels": channel_names, "prefilter": None,
                          "label_encoding": {"0": "imagined left fist", "1": "imagined right fist"}},
        "train_subjects": TRAIN_SUBJECTS, "test_subjects": TEST_SUBJECTS,
        "runs": RUNS, "train_shape": list(arrays["train_x"].shape),
        "test_shape": list(arrays["test_x"].shape),
        "train_groups": arrays["train_groups"].tolist(), "test_groups": arrays["test_groups"].tolist(),
        "train_unit_ids": arrays["train_units"].tolist(), "test_unit_ids": arrays["test_units"].tolist(),
        "n_train": len(arrays["train_y"]), "n_test": len(arrays["test_y"]),
        "grouping": "participant", "split": "fixed subject-disjoint subjects 1–5 train; 6–8 test",
        "label_counts": {k: np.bincount(arrays[k + "_y"], minlength=2).tolist() for k in ["train", "test"]},
        "baseline": "Fixed 7–30 Hz fourth-order Butterworth, regularized 4-component CSP, shrinkage LDA",
        "current_best_status": "not verified; custom small subject split prevents transplanting published within-subject scores",
        "reader": "mne 1.10.2", "data_sha256": sha256(CACHE / "data.npz"),
        "limitations": ["Only three held-out participants; no population-wide significance claim",
                         "Fixed first subjects, no random representative sample",
                         "No artifact rejection; task-correlated ocular/muscle artifacts can affect decoding",
                         "Public labels permit potential training contamination",
                         "This is a new transparent slice, not an official full MOABB benchmark result"]}
    (CACHE / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    (CACHE / "trial-manifest.json").write_text(json.dumps(trial_manifest, indent=2) + "\n")
    output = {"benchmark_id": "H01", "version": "1.0.0", "source": SOURCE,
              "doi": "10.13026/C28G6P", "license": "ODC-By-1.0",
              "accessed_on": "2026-10-30", "files": manifest,
              "prepared": {"path": "data/cache/H01/data.npz", "sha256": metadata["data_sha256"]},
              "redistribution": "Raw data remain ignored cache; acquisition script and attribution are tracked"}
    (REPO / "data/manifests/H01.json").write_text(json.dumps(output, indent=2) + "\n")
    return metadata


def load():
    with np.load(CACHE / "data.npz", allow_pickle=False) as d:
        return tuple(d[k].copy() for k in ["train_x", "train_y", "test_x", "test_y"])


def baseline(train_x, train_y, test_x):
    """Transparent fixed CSP+LDA; no test-label tuning and no specialist imports."""
    from scipy.linalg import eigh
    from scipy.signal import butter, sosfiltfilt
    from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
    sos = butter(4, [7, 30], fs=160, btype="bandpass", output="sos")
    train = sosfiltfilt(sos, np.asarray(train_x, dtype=np.float64), axis=-1)
    test = sosfiltfilt(sos, np.asarray(test_x, dtype=np.float64), axis=-1)
    train -= train.mean(axis=-1, keepdims=True)
    test -= test.mean(axis=-1, keepdims=True)
    cov = train @ train.transpose(0, 2, 1)
    cov /= np.trace(cov, axis1=1, axis2=2)[:, None, None]
    covs = [cov[np.asarray(train_y) == label].mean(axis=0) for label in [0, 1]]
    # Common average reference loses one rank. Fixed ridge prevents singular eigensystem.
    covs = [c + 1e-6 * np.trace(c) / c.shape[0] * np.eye(c.shape[0]) for c in covs]
    values, vectors = eigh(covs[0], covs[0] + covs[1])
    filters = vectors[:, [0, 1, -2, -1]].T
    def feature(x):
        v = np.var(np.einsum("kc,nct->nkt", filters, x), axis=-1)
        return np.log(np.maximum(v, 1e-12))
    model = LinearDiscriminantAnalysis(solver="lsqr", shrinkage="auto")
    model.fit(feature(train), train_y)
    return model.predict(feature(test))


if __name__ == "__main__":
    print(json.dumps(prepare(), indent=2))
