"""Allen Cell Types: donor-disjoint spiny/aspiny prediction from ephys only."""
from pathlib import Path
import hashlib
import json
import urllib.request
from urllib.parse import urlencode
import numpy as np

REPO = Path(__file__).resolve().parents[2]
CACHE = REPO / "data/cache/K01"
API = "https://api.brain-map.org/api/v2/data/query.json?" + urlencode({"criteria": "model::ApiCellTypesSpecimenDetail,rma::options[num_rows$eqall]"})
FEATURES = ["ef__adaptation", "ef__avg_firing_rate", "ef__avg_isi", "ef__f_i_curve_slope", "ef__fast_trough_v_long_square", "ef__peak_t_ramp", "ef__ri", "ef__tau", "ef__threshold_i_long_square", "ef__upstroke_downstroke_ratio_long_square", "ef__vrest"]

def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def prepare():
    from sklearn.model_selection import GroupShuffleSplit
    CACHE.mkdir(parents=True, exist_ok=True)
    raw = CACHE / "cells.json"
    if not raw.exists():
        with urllib.request.urlopen(API, timeout=120) as response:
            raw.write_bytes(response.read())
    document = json.loads(raw.read_text())
    assert document["success"] and len(document["msg"]) == document["total_rows"]
    records = sorted([r for r in document["msg"] if r["donor__species"] == "Mus musculus" and r["tag__dendrite_type"] in ("aspiny", "spiny")], key=lambda r: r["specimen__id"])
    x = np.array([[np.nan if r[k] is None else r[k] for k in FEATURES] for r in records], dtype=np.float64)
    y = np.array([int(r["tag__dendrite_type"] == "spiny") for r in records], dtype=np.int64)
    groups = np.array([r["donor__id"] for r in records], dtype=np.int64)
    units = np.array([r["specimen__id"] for r in records], dtype=np.int64)
    assert len(np.unique(units)) == len(units)
    train, test = next(GroupShuffleSplit(n_splits=1, test_size=.25, random_state=20261030).split(x, y, groups))
    assert not set(groups[train]) & set(groups[test])
    assert set(y[train]) == set(y[test]) == {0, 1}
    arrays = {}
    for split, idx in [("train", train), ("test", test)]:
        for key, value in [("x", x), ("y", y), ("groups", groups), ("units", units)]:
            arrays[split + "_" + key] = value[idx]
    np.savez_compressed(CACHE / "data.npz", **arrays)
    meta = {"benchmark_id": "K01", "slice_id": "allen-mouse-ephys-morphology-donorholdout-v1", "dataset": "Allen Cell Types Database", "task_description": "Predict binary mouse dendritic morphology (0=aspiny, 1=spiny) using only the 11 supplied electrophysiological features. Fit on training cells and predict cells from disjoint test mice. Missing features are NaN; fit preprocessing on training data only.", "accessed_on": "2026-10-30", "metric": "macro_f1", "direction": "higher", "n_classes": 2, "metric_aggregation": "pooled held-out cells, with donor-blocked uncertainty if computed", "input": "float64 (cell,11 electrophysiological features); NaN denotes missing feature", "feature_names": FEATURES, "label_encoding": {"0": "aspiny", "1": "spiny"}, "target": "independent dendritic morphology annotation; not a transcriptomic taxonomy or predicted cell class", "species": "Mus musculus only", "grouping": "Allen donor ID (mouse)", "split": "GroupShuffleSplit, test_size=0.25, random_state=20261030; cells sorted by specimen ID", "n_train": len(train), "n_test": len(test), "train_shape": list(x[train].shape), "test_shape": list(x[test].shape), "n_train_donors": len(set(groups[train])), "n_test_donors": len(set(groups[test])), "train_groups": groups[train].tolist(), "test_groups": groups[test].tolist(), "train_unit_ids": units[train].tolist(), "test_unit_ids": units[test].tolist(), "label_counts": {"train": np.bincount(y[train], minlength=2).tolist(), "test": np.bincount(y[test], minlength=2).tolist()}, "missing_feature_fraction": float(np.isnan(x).mean()), "baseline": "RF500 vs ExtraTrees500, balanced classes, train-only median imputation, grouped 3-fold train CV macro-F1 selection", "current_best_status": "not verified; custom donor split, no imported paper scores", "source": API, "license": "Allen Institute Terms of Use: research/noncommercial use and attribution; data are not covered by repository MIT code license", "terms_url": "https://alleninstitute.org/terms-of-use/", "data_sha256": sha256(CACHE / "data.npz"), "limitations": ["Binary morphology endpoint only; not the full multimodal cell taxonomy", "Cre targeting and protocol selection may introduce acquisition/population confounds even though genetic predictors are excluded", "Only mouse donor generalization within one institute/acquisition resource; not cross-lab or cross-species validation", "Morphological annotation may be imperfect; sparsely-spiny cells excluded before splitting", "Public labels permit potential pretraining contamination", "Generic estimator baseline is strong conventional tabular ML, not a verified neuroscience specialist SOTA"]}
    (CACHE / "metadata.json").write_text(json.dumps(meta, indent=2) + "\n")
    manifest = {"benchmark_id": "K01", "accessed_on": "2026-10-30", "files": [{"url": API, "path": "data/cache/K01/cells.json", "bytes": raw.stat().st_size, "sha256": sha256(raw)}], "prepared": {"path": "data/cache/K01/data.npz", "sha256": meta["data_sha256"]}, "use_terms": meta["license"], "terms_url": meta["terms_url"], "attribution": "Allen Institute for Brain Science, Allen Cell Types Database (2015); https://celltypes.brain-map.org/", "raw_count": len(document["msg"]), "eligible_count": len(records), "exclusions": {"human_cells": sum(r["donor__species"] != "Mus musculus" for r in document["msg"]), "mouse_sparsely_spiny": sum(r["donor__species"] == "Mus musculus" and r["tag__dendrite_type"] not in ("spiny", "aspiny") for r in document["msg"])}, "redistribution": "Cache excluded from Git; tracked downloader/manifests retain source and hashes"}
    (REPO / "data/manifests/K01.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return meta

def load():
    with np.load(CACHE / "data.npz", allow_pickle=False) as d:
        return tuple(d[k].copy() for k in ["train_x", "train_y", "test_x", "test_y"])

def baseline(train_x, train_y, test_x):
    """Two preregistered conventional classifiers; selection uses train donors only."""
    from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier
    from sklearn.impute import SimpleImputer
    from sklearn.pipeline import make_pipeline
    from sklearn.model_selection import GroupKFold, cross_val_score
    with np.load(CACHE / "data.npz", allow_pickle=False) as d:
        groups = d["train_groups"]
    assert len(groups) == len(train_x)
    candidates = [make_pipeline(SimpleImputer(strategy="median", add_indicator=True), cls(n_estimators=500, class_weight="balanced", random_state=20261030, n_jobs=1)) for cls in [RandomForestClassifier, ExtraTreesClassifier]]
    scores = [float(np.mean(cross_val_score(m, train_x, train_y, groups=groups, cv=GroupKFold(3), scoring="f1_macro", n_jobs=1))) for m in candidates]
    model = candidates[int(np.argmax(scores))]
    model.fit(train_x, train_y)
    return model.predict(test_x)

if __name__ == "__main__":
    print(json.dumps(prepare(), indent=2))
