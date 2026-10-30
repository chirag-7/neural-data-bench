"""Goldin2022: real mouse retinal image-to-spike-count encoding, all 41 neurons."""
from pathlib import Path
import hashlib
import json
import urllib.request
import numpy as np

REPO = Path(__file__).resolve().parents[2]
CACHE = REPO / "data/cache/F04"
REVISION = "fc7b91e93c9bd4e76d4e3205fcbcc6a31601985a"
RELATIVE = "marre_lab/goldin_2022/mouse-session-1_structured_data.h5"
URL = f"https://huggingface.co/datasets/open-retina/open-retina/resolve/{REVISION}/{RELATIVE}?download=true"

def sha256(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def image_hashes(images):
    return [hashlib.sha256(np.asarray(i, dtype=np.float32).tobytes()).hexdigest() for i in images]

def features(images):
    # Fixed response-independent 6x6 pixel block averaging: 108x108 -> 18x18.
    return images.reshape(len(images), 18, 6, 18, 6).mean(axis=(2, 4)).reshape(len(images), 324).astype(np.float64)

def prepare():
    import h5py
    CACHE.mkdir(parents=True, exist_ok=True)
    raw = CACHE / "mouse-session-1_structured_data.h5"
    if not raw.exists():
        with urllib.request.urlopen(URL, timeout=180) as r:
            raw.write_bytes(r.read())
    with h5py.File(raw) as f:
        train_image = np.asarray(f["train/stimulus"], dtype=np.float32)
        test_image = np.asarray(f["test/stimulus"], dtype=np.float32)
        train_count = np.asarray(f["train/response/binned"], dtype=np.float64).T
        test_mean = np.asarray(f["test/response/binned"], dtype=np.float64).T
        cell_keys = sorted(f["test/repeats"].keys(), key=lambda k: int(k.removeprefix("cell")))
        assert cell_keys == ["cell" + str(k) for k in range(41)]
        repeated = np.stack([np.asarray(f["test/repeats"][k]) for k in cell_keys], axis=-1)
    assert train_image.shape == (3160, 108, 108) and test_image.shape == (30, 108, 108)
    assert train_count.shape == (3160, 41) and repeated.shape == (30, 30, 41)
    assert np.allclose(repeated.mean(axis=0), test_mean)
    assert np.all(train_count == np.round(train_count)) and np.all(repeated == np.round(repeated))
    assert np.all(train_count >= 0) and np.all(repeated >= 0)
    train_hash, test_hash = image_hashes(train_image), image_hashes(test_image)
    assert len(set(train_hash)) == 3160 and len(set(test_hash)) == 30
    assert not set(train_hash) & set(test_hash)
    train_x, test_unique = features(train_image), features(test_image)
    # Trial/repeat major, image minor: all measured counts are retained.
    test_x = np.tile(test_unique, (30, 1))
    test_y = repeated.reshape(900, 41)
    arrays = {"train_x": train_x, "train_y": train_count, "test_x": test_x, "test_y": test_y,
              "train_groups": np.arange(3160), "test_groups": np.tile(np.arange(3160, 3190), 30),
              "train_units": np.array([f"train_image{i:04d}" for i in range(3160)]),
              "test_units": np.array([f"repeat{r:02d}_image{i:02d}" for r in range(30) for i in range(30)])}
    assert np.isfinite(train_x).all() and np.isfinite(test_x).all()
    np.savez_compressed(CACHE / "data.npz", **arrays)
    meta = {"benchmark_id": "F04", "slice_id": "goldin2022-mouse1-static-retinal-encoding-v1", "dataset": "Goldin et al.2022 mouse retinal ganglion cells, OpenRetina processed mouse-session-1", "dataset_doi": "10.5281/zenodo.6868362", "paper_doi": "10.1038/s41467-022-33242-8", "accessed_on": "2026-10-30", "resource_relationship": "Additional openly reusable real retinal encoding resource for F04; not a claim to have executed an official CRCNS benchmark", "metric": "poisson_nll", "direction": "lower", "metric_aggregation": "mean [mu - y*log(mu) + logGamma(y+1)] over 900 held-out repeated image presentations and all41 neurons", "task_description": "Predict expected spike COUNTS per300ms image flash for all41 real mouse retinal ganglion cells. Inputs are fixed6x6 block-averaged natural-image pixels: original108x108->18x18, flattened row-major to324 features. Training x(3160,324), training integer y(3160,41). Test x(900,324) repeats30 held-out unique images30 times; each row's target is a separate measured integer count vector, not a trial average. Return positive finite expected counts, shape(900,41), NOT spikes/second, labels, or sampled spike realizations. Primary mean Poisson negative log-likelihood lower. No response-derived feature allowed; fit preprocessing only on training images. Images are flashed300ms then gray300ms; input contains current image only and no previous spikes/history. The dataset's train and test image hashes are disjoint.", "input": "float64 (image presentation,324) fixed block-averaged intensity pixels, row-major18x18", "pixel_range_original": [-2.401252, 2.478047], "count_source_fields": ["train/response/binned", "test/repeats/cell0..cell40"], "count_integrality_validated": True, "simple_anchor": "Per-neuron training-mean counts, tiled across test images; never estimate null from test", "target": "integer spike counts per300ms response window for41 neurons; model predicts expected counts", "count_window_seconds": .3, "gray_interstimulus_seconds": .3, "n_neurons": 41, "neuron_ids": cell_keys, "n_train": 3160, "n_test": 900, "n_unique_test_images": 30, "n_test_repeats": 30, "train_shape": list(train_x.shape), "test_shape": list(test_x.shape), "target_train_shape": list(train_count.shape), "target_test_shape": list(test_y.shape), "grouping": "held-out image identity (30), not900 independent images; all41 neurons from one retinal session", "train_groups": arrays["train_groups"].tolist(), "test_groups": arrays["test_groups"].tolist(), "train_unit_ids": arrays["train_units"].tolist(), "test_unit_ids": arrays["test_units"].tolist(), "split": "preserve OpenRetina source train/test partition;3160 unique training images and30 disjoint unique test images with30 measured repeats each", "baseline": "train-only pixel scaling/PCA48 plus per-neuron PoissonGLM; alpha selected among0.001/0.1/1 on final20% training images, refit all3160", "baseline_role": "regularized linear-nonlinear-Poisson reference; not verified current specialistSOTA", "current_best_status": "not verified; custom downsampled image-conditioned count endpoint", "source": URL, "source_revision": REVISION, "original_data_license": "CC-BY-4.0 (original Zenodo metadata)", "license": "CC-BY-SA-4.0 processed OpenRetina mirror; distinct from repository code license", "license_url": "https://huggingface.co/datasets/open-retina/open-retina/blob/" + REVISION + "/README.md", "reader": "h5py3.15.1 preparation only", "data_sha256": sha256(CACHE/"data.npz"), "limitations": ["One mouse retinal recording and30 unique test images; repeated presentations and neurons are not independent animals", "Fixed18x18 image reduction can remove fine spatial details; this is not full108x108 CNN or native VLM inference", "Current-image encoding only; no temporal flicker/stimulus-history or spike-history prediction", "Source pixels are already processed/normalized upstream; our scaler/PCA fit on training images only, but cannot undo unknown upstream global normalization", "Original cell identifiers/retina mapping beyond source session index unavailable in processed mirror", "Public widely studied data may be present in model pretraining", "Observed counts may be overdispersed relative to Poisson; predictive log loss is an evaluation rule, not proof of a true Poisson process"]}
    (CACHE / "metadata.json").write_text(json.dumps(meta, indent=2) + "\n")
    (CACHE / "image-manifest.json").write_text(json.dumps({"train_hashes": train_hash, "test_hashes": test_hash, "hash_overlap": 0, "repeat_order": "repeat-major,image-minor"}, indent=2) + "\n")
    manifest = {"benchmark_id": "F04", "accessed_on": "2026-10-30", "source_revision": REVISION, "files": [{"url": URL, "path": "data/cache/F04/" + raw.name, "bytes": raw.stat().st_size, "sha256": sha256(raw)}], "prepared": {"path": "data/cache/F04/data.npz", "sha256": meta["data_sha256"]}, "original_doi": meta["dataset_doi"], "paper_doi": meta["paper_doi"], "data_license": meta["license"], "original_data_license": meta["original_data_license"], "attribution": "Goldin MA et al.(2022), Context-dependent selectivity to natural images in the retina, NatCommun13:5556; OpenRetina processed release", "redistribution": "Raw/prepared images and counts remain ignored cache; acquisition script and manifest tracked. Preserve upstream CC-BY-SA terms for data derivatives, not code-MIT relicensing."}
    (REPO / "data/manifests/F04.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return meta

def load():
    with np.load(CACHE / "data.npz", allow_pickle=False) as d:
        return tuple(d[k].copy() for k in ["train_x", "train_y", "test_x", "test_y"])

def _fit_predict(x, y, t, alpha):
    from sklearn.preprocessing import StandardScaler
    from sklearn.decomposition import PCA
    from sklearn.linear_model import PoissonRegressor
    scaler = StandardScaler().fit(x)
    pca = PCA(n_components=48, whiten=True, svd_solver="full").fit(scaler.transform(x))
    x = pca.transform(scaler.transform(x)); t = pca.transform(scaler.transform(t))
    result = []
    for j in range(y.shape[1]):
        if y[:,j].sum() == 0:
            result.append(np.full(len(t),1e-9))
        else:
            m = PoissonRegressor(alpha=alpha, max_iter=300, tol=1e-6).fit(x,y[:,j])
            result.append(m.predict(t))
    return np.maximum(np.column_stack(result),1e-9)

def mean_anchor(train_x, train_y, test_x):
    return np.tile(np.maximum(train_y.mean(axis=0),1e-9), (len(test_x),1))

def baseline(train_x, train_y, test_x):
    from scipy.special import gammaln
    split = int(len(train_x)*.8)
    losses = []
    for alpha in [.001,.1,1.]:
        p = _fit_predict(train_x[:split], train_y[:split], train_x[split:], alpha)
        y = train_y[split:]
        losses.append(float(np.mean(p-y*np.log(p)+gammaln(y+1))))
    return _fit_predict(train_x, train_y, test_x, [.001,.1,1.][int(np.argmin(losses))])

if __name__ == "__main__":
    print(json.dumps(prepare(), indent=2))
