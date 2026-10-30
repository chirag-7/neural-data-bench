"""Post-hoc offline subject-aligned pyRiemann reference; see amendment/config.

The prediction runner never loads test_y. Subject IDs are extra metadata compared
with the generated models' three-array interface. No current-SOTA claim.
"""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import time

import numpy as np
import pyriemann
import scipy
from scipy.signal import butter, sosfiltfilt
import sklearn
from sklearn.metrics import balanced_accuracy_score
from sklearn.model_selection import LeaveOneGroupOut
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from pyriemann.estimation import Covariances
from pyriemann.tangentspace import TangentSpace
from pyriemann.transfer import TLCenter, encode_domains

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
CACHE = ROOT / "data/cache/H01"
CONFIG_FILE = HERE / "specialist-aligned-config.json"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def covariances(x, band, sampling_rate):
    sos = butter(4, band, fs=sampling_rate, btype="bandpass", output="sos")
    filtered = sosfiltfilt(sos, np.asarray(x, dtype=np.float64), axis=-1)
    filtered -= filtered.mean(axis=-1, keepdims=True)
    cov = Covariances(estimator="oas").transform(filtered)
    return cov / np.trace(cov, axis1=1, axis2=2)[:, None, None]


def align_subjects(cov, groups):
    """Fit each domain from its own unlabeled epochs, independently.

    Dummy encoded labels only communicate domain IDs to TLCenter. No class
    labels, proportions or data from other subjects enter each domain center.
    """
    domains = np.asarray(groups).astype(str)
    _, encoded = encode_domains(cov, np.zeros(len(cov), dtype=int), domains)
    return TLCenter(target_domain="", metric="riemann").fit_transform(
        cov, encoded
    )


def tangent_features(source_cov, target_cov):
    ts = TangentSpace(metric="riemann", tsupdate=False)
    source = ts.fit_transform(source_cov)
    target = ts.transform(target_cov)
    scaler = StandardScaler()
    return scaler.fit_transform(source), scaler.transform(target)


def classify(train_features, y, eval_features, cost):
    return SVC(C=cost, kernel="linear", class_weight="balanced").fit(
        train_features, y
    ).predict(eval_features)


def fit_predict(train_x, train_y, test_x, train_groups, test_groups, config):
    """Select from training groups, then adapt chosen band to unlabeled test.

    Full participant batches are available offline; do not interpret as causal.
    Test targets are deliberately absent from this function's signature.
    """
    y = np.asarray(train_y, dtype=int)
    groups = np.asarray(train_groups)
    assert set(np.unique(groups)).isdisjoint(set(np.unique(test_groups)))
    assert set(np.unique(y)) == {0, 1}
    folds = list(LeaveOneGroupOut().split(train_x, y, groups))
    candidates, out_of_fold = [], []
    aligned_training = {}
    for band in config["band_grid_hz"]:
        band_key = tuple(band)
        raw = covariances(train_x, band, config["sampling_rate_hz"])
        # Each source subject's center is independent of all other subjects.
        # Reuse is mathematically identical to re-estimating within every fold.
        centered = align_subjects(raw, groups)
        aligned_training[band_key] = centered
        predictions = {cost: np.empty(len(y), dtype=int)
                       for cost in config["C_grid"]}
        fold_scores = {cost: [] for cost in config["C_grid"]}
        for tr, va in folds:
            # Held-out subject center uses only its unlabeled epochs. No
            # held-out subject influences tangent reference or standardization.
            a, b = tangent_features(centered[tr], centered[va])
            for cost in config["C_grid"]:
                p = classify(a, y[tr], b, cost)
                predictions[cost][va] = p
                fold_scores[cost].append({
                    "held_out_training_subject": int(groups[va][0]),
                    "n_source_trials": int(len(tr)),
                    "n_validation_trials": int(len(va)),
                    "balanced_accuracy": float(balanced_accuracy_score(y[va], p)),
                })
        for cost in config["C_grid"]:
            records = fold_scores[cost]
            candidates.append({
                "band": list(band), "C": cost,
                "validation_mean_subject_balanced_accuracy": float(np.mean(
                    [r["balanced_accuracy"] for r in records])),
                "validation_pooled_balanced_accuracy": float(
                    balanced_accuracy_score(y, predictions[cost])),
                "folds": records,
            })
            out_of_fold.append(predictions[cost])
    # max() retains the first candidate on an exact tie, as frozen in config.
    selected_index = max(range(len(candidates)), key=lambda i: candidates[i][
        "validation_mean_subject_balanced_accuracy"])
    best = candidates[selected_index]
    # No test preprocessing or covariances were computed during selection.
    source_cov = aligned_training[tuple(best["band"])]
    target_cov = align_subjects(covariances(
        test_x, best["band"], config["sampling_rate_hz"]), test_groups)
    a, b = tangent_features(source_cov, target_cov)
    prediction = classify(a, y, b, best["C"])
    assert prediction.shape == (len(test_x),)
    assert np.isin(prediction, [0, 1]).all()
    selection = {
        "selected": best,
        "selected_candidate_index": selected_index,
        "training_only_candidates": candidates,
        "test_labels_used": False,
        "unlabeled_test_adaptation": True,
        "explicit_subject_group_ids": True,
        "causal_or_online": False,
        "test_score_computed_by_this_runner": False,
        "posthoc_after_prior_H01_scores": True,
    }
    return prediction, selection, np.stack(out_of_fold)


if __name__ == "__main__":
    config = json.loads(CONFIG_FILE.read_text())
    assert pyriemann.__version__ == config["pyriemann_version"]
    data_file = CACHE / "data.npz"
    data_hash_before = sha256(data_file)
    assert data_hash_before == config["dataset_sha256"]
    # Named loads deliberately omit test_y; NPZ entries are loaded lazily.
    with np.load(data_file, allow_pickle=False) as z:
        x, y, xt, groups, test_groups = [z[k] for k in (
            "train_x", "train_y", "test_x", "train_groups", "test_groups")]
    started = datetime.now(timezone.utc).isoformat()
    start = time.perf_counter()
    pred, selection, validation_predictions = fit_predict(
        x, y, xt, groups, test_groups, config)
    elapsed = time.perf_counter() - start
    dest = ROOT / "results/predictions/H01/specialist--pyriemann-aligned.npz"
    dest.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(dest, predictions=pred,
                        validation_predictions=validation_predictions,
                        validation_groups=groups)
    (HERE / "specialist-aligned-selection.json").write_text(
        json.dumps(selection, indent=2) + "\n")
    data_hash_after = sha256(data_file)
    assert data_hash_before == data_hash_after
    runtime = {
        "reference_id": "pyriemann-aligned",
        "started_at_utc": started,
        "seconds": elapsed,
        "time_budget_seconds": config["time_budget_seconds"],
        "within_time_budget": elapsed <= config["time_budget_seconds"],
        "prediction_file": str(dest.relative_to(ROOT)),
        "prediction_sha256": sha256(dest),
        "config_sha256": sha256(CONFIG_FILE),
        "code_sha256": sha256(Path(__file__)),
        "selection_sha256": sha256(HERE / "specialist-aligned-selection.json"),
        "data_sha256_before": data_hash_before,
        "data_sha256_after": data_hash_after,
        "data_unchanged": data_hash_before == data_hash_after,
        "test_score_computed": False,
        "packages": {"python": platform.python_version(), "numpy": np.__version__,
                     "scipy": scipy.__version__, "sklearn": sklearn.__version__,
                     "pyriemann": pyriemann.__version__},
    }
    (HERE / "specialist-aligned-runtime.json").write_text(
        json.dumps(runtime, indent=2) + "\n")
    print(json.dumps({"seconds": elapsed, "selected": selection["selected"],
                      "prediction_file": str(dest.relative_to(ROOT))}, indent=2))
