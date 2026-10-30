"""Component-disjoint EEGdenoiseNet EOG mixture repair slice, fixed v1."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import urllib.request
import numpy as np

REPO = Path(__file__).resolve().parents[2]
CACHE = REPO / "data/cache/H16"
COMMIT = "8d290661146c7189c98cc04812d37371d4b9426c"
BASE = f"https://raw.githubusercontent.com/ncclabsustech/EEGdenoiseNet/{COMMIT}/"
SEED = 20261030
N_TRAIN, N_TEST = 2000, 600


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _acquire(rel):
    target = CACHE / "raw" / Path(rel).name
    if not target.exists():
        with urllib.request.urlopen(BASE + rel, timeout=90) as response:
            target.write_bytes(response.read())
    return {"url": BASE + rel, "path": str(target.relative_to(REPO)),
            "bytes": target.stat().st_size, "sha256": sha256(target)}


def _row_hashes(x):
    return [hashlib.sha256(np.ascontiguousarray(row).tobytes()).hexdigest() for row in x]


def prepare():
    (CACHE / "raw").mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=4) as pool:
        manifest = list(pool.map(_acquire, ["data/EEG_all_epochs.npy", "data/EOG_all_epochs.npy",
                                            "LICENSE", "code/benchmark_networks/data_prepare.py"]))
    clean = np.load(CACHE / "raw/EEG_all_epochs.npy", allow_pickle=False)
    artifact = np.load(CACHE / "raw/EOG_all_epochs.npy", allow_pickle=False)
    assert clean.shape == (4514, 512) and artifact.shape == (3400, 512)
    assert np.isfinite(clean).all() and np.isfinite(artifact).all()
    rng = np.random.default_rng(SEED)
    # Independent unique component pools, split before synthesizing any mixtures.
    clean_idx = rng.permutation(len(clean))[:N_TRAIN + N_TEST]
    artifact_idx = rng.permutation(len(artifact))[:N_TRAIN + N_TEST]
    train_snr = rng.permutation(np.tile(np.arange(-7, 3), N_TRAIN // 10))
    test_snr = rng.permutation(np.tile(np.arange(-7, 3), N_TEST // 10))
    snr = np.r_[train_snr, test_snr]
    eeg, eog = clean[clean_idx].astype(np.float64), artifact[artifact_idx].astype(np.float64)
    # Use literal ORIGINAL EEGdenoiseNet code convention: 10 log10(RMS ratio).
    # This is not conventional 10 log10(power ratio), which differs by a factor of two.
    rms = lambda a: np.sqrt(np.mean(a * a, axis=-1))
    amplitude = rms(eeg) / (rms(eog) * 10.0 ** (snr / 10.0))
    mixture = eeg + amplitude[:, None] * eog
    scale = mixture.std(axis=-1)
    x, y = mixture / scale[:, None], eeg / scale[:, None]
    assert np.all(scale > 0) and np.isfinite(x).all() and np.isfinite(y).all()
    for idx in [clean_idx, artifact_idx]:
        assert not set(idx[:N_TRAIN]) & set(idx[N_TRAIN:])
    # Detect exact duplicate source rows across the split, not just repeated indices.
    for source in [eeg, eog]:
        assert not set(_row_hashes(source[:N_TRAIN])) & set(_row_hashes(source[N_TRAIN:]))
    arrays = {"train_x": x[:N_TRAIN].astype(np.float32), "train_y": y[:N_TRAIN].astype(np.float32),
              "test_x": x[N_TRAIN:].astype(np.float32), "test_y": y[N_TRAIN:].astype(np.float32),
              "train_snr": train_snr, "test_snr": test_snr,
              "train_clean_indices": clean_idx[:N_TRAIN], "test_clean_indices": clean_idx[N_TRAIN:],
              "train_artifact_indices": artifact_idx[:N_TRAIN], "test_artifact_indices": artifact_idx[N_TRAIN:]}
    np.savez_compressed(CACHE / "data.npz", **arrays)
    unit_ids = [f"eeg{c:04d}_eog{a:04d}_snr{s:+d}" for c, a, s in zip(clean_idx, artifact_idx, snr)]
    metadata = {"benchmark_id": "H16", "slice_id": "eegdenoisenet-eog-disjoint-v1",
                "dataset": "EEGdenoiseNet", "source_commit": COMMIT, "seed": SEED,
                "metric": "rrmse", "direction": "lower", "task_type": "signal_reconstruction",
                "metric_definition": "mean_i sqrt(mean_t((prediction_i-target_i)^2))/sqrt(mean_t(target_i^2))",
                "sampling_rate_hz": 256, "input": "float32 (segments,512 samples),2 seconds,mixture standardized per segment",
                "input_details": {"channels": 1, "sampling_rate_hz": 256, "n_samples": 512,
                                  "snr_levels": list(range(-7, 3)),
                                  "snr_convention": "10 log10(RMS(clean)/RMS(scaled artifact)), literal original code convention",
                                  "normalization": "both mixture and clean target divided by mixture standard deviation"},
                "train_shape": list(arrays["train_x"].shape), "test_shape": list(arrays["test_x"].shape),
                "n_train": N_TRAIN, "n_test": N_TEST,
                "grouping": "unique clean segment and unique EOG segment; source participant IDs unavailable",
                "split": "seeded component-disjoint unique pools, 2000 train pairs and 600 held-out pairs",
                "train_unit_ids": unit_ids[:N_TRAIN], "test_unit_ids": unit_ids[N_TRAIN:],
                "test_groups": unit_ids[N_TRAIN:], "baseline": "Training-derived smoothed stationary Wiener spectral shrinkage",
                "license_evidence": "Original repository MIT LICENSE included; original raw physiological sources have separate provenance; do not redistribute raw pools",
                "data_sha256": sha256(CACHE / "data.npz"),
                "current_best_status": "not verified; custom split/SNR allocation prevents importing paper table values",
                "limitations": ["Semisynthetic sum of real preprocessed components, not real simultaneous contaminated EEG",
                                  "Clean reference was algorithmically cleaned and visually inspected by original authors; not pristine physiology",
                                  "Component IDs disjoint; no participant-level guarantee because original row identities lack participant metadata",
                                  "One mixture per component; no independent claim from repeating same physiological component",
                                  "Only ocular artifact repair; no EMG, ECG, multichannel ICA or downstream-preservation validation"]}
    (CACHE / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    (REPO / "data/manifests/H16.json").write_text(json.dumps({
        "benchmark_id": "H16", "source_commit": COMMIT, "accessed_on": "2026-10-30", "files": manifest,
        "prepared": {"path": "data/cache/H16/data.npz", "sha256": metadata["data_sha256"]},
        "seed": SEED, "redistribution": "Original pools/prepared samples stay in ignored local cache; URLs/hashes/code tracked"}, indent=2) + "\n")
    return metadata


def load():
    with np.load(CACHE / "data.npz", allow_pickle=False) as d:
        return tuple(d[k].copy() for k in ["train_x", "train_y", "test_x", "test_y"])


def baseline(train_x, train_y, test_x):
    """Conventional stationary Wiener gains estimated exclusively from training pairs."""
    from scipy.ndimage import gaussian_filter1d
    train = np.asarray(train_x, np.float64)
    target = np.asarray(train_y, np.float64)
    clean_psd = np.mean(np.abs(np.fft.rfft(target, axis=-1)) ** 2, axis=0)
    noise_psd = np.mean(np.abs(np.fft.rfft(train - target, axis=-1)) ** 2, axis=0)
    clean_psd = gaussian_filter1d(clean_psd, sigma=2.0)
    noise_psd = gaussian_filter1d(noise_psd, sigma=2.0)
    gain = clean_psd / np.maximum(clean_psd + noise_psd, 1e-12)
    gain[0] = 0.0
    return np.fft.irfft(np.fft.rfft(np.asarray(test_x, np.float64), axis=-1) * gain,
                        n=train.shape[-1], axis=-1)


def per_unit_score(target, prediction):
    target, prediction = np.asarray(target, np.float64), np.asarray(prediction, np.float64)
    if target.shape != prediction.shape or not np.isfinite(prediction).all():
        raise ValueError("Require finite predictions with exactly the target shape")
    return np.sqrt(np.mean((target - prediction) ** 2, axis=-1)) / np.maximum(
        np.sqrt(np.mean(target ** 2, axis=-1)), 1e-12)


def score(target, prediction):
    return float(per_unit_score(target, prediction).mean())


if __name__ == "__main__":
    print(json.dumps(prepare(), indent=2))
