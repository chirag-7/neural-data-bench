import numpy as np
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import QuantileTransformer
from sklearn.svm import SVC


def _prepare(train, other, columns, for_svm=False):
    a = np.asarray(train[:, columns], dtype=float).copy()
    b = np.asarray(other[:, columns], dtype=float).copy()
    a[~np.isfinite(a)] = np.nan
    b[~np.isfinite(b)] = np.nan

    med = np.empty(a.shape[1], dtype=float)
    for j in range(a.shape[1]):
        finite = a[np.isfinite(a[:, j]), j]
        med[j] = np.median(finite) if finite.size else 0.0
    a = np.where(np.isfinite(a), a, med)
    b = np.where(np.isfinite(b), b, med)

    lo = np.quantile(a, 0.005, axis=0)
    hi = np.quantile(a, 0.995, axis=0)
    a = np.clip(a, lo, hi)
    b = np.clip(b, lo, hi)

    if for_svm:
        transform = QuantileTransformer(
            n_quantiles=min(200, len(a)),
            output_distribution="normal",
            random_state=17,
        )
        a = transform.fit_transform(a)
        b = transform.transform(b)
    return a, b


def _classifier(kind):
    if kind == "rf_core":
        return RandomForestClassifier(
            n_estimators=400, min_samples_leaf=3, max_features=0.6,
            class_weight="balanced_subsample", n_jobs=1, random_state=17,
        )
    if kind == "rf_full":
        return RandomForestClassifier(
            n_estimators=350, min_samples_leaf=4, max_features=0.5,
            class_weight="balanced_subsample", n_jobs=1, random_state=29,
        )
    if kind == "extra_core":
        return ExtraTreesClassifier(
            n_estimators=400, min_samples_leaf=3, max_features=0.7,
            class_weight="balanced", n_jobs=1, random_state=41,
        )
    return SVC(
        C=1.5, gamma="scale", class_weight="balanced",
        probability=True, random_state=53,
    )


def _score(train_x, train_y, other_x, specifications):
    combined = np.zeros(len(other_x), dtype=float)
    for kind, columns, weight in specifications:
        a, b = _prepare(train_x, other_x, columns, kind == "svm_core")
        model = _classifier(kind)
        model.fit(a, train_y)
        combined += weight * model.predict_proba(b)[:, 1]
    return combined


def fit_predict(train_x, train_y, test_x):
    train_x = np.asarray(train_x, dtype=float)
    test_x = np.asarray(test_x, dtype=float)
    train_y = np.asarray(train_y, dtype=int).ravel()
    if len(test_x) == 0:
        return np.empty(0, dtype=int)
    counts = np.bincount(train_y, minlength=2)
    if np.count_nonzero(counts) < 2:
        return np.full(len(test_x), int(np.argmax(counts)), dtype=int)

    # IQMs other than image dimensions, voxel spacing, and raw tissue summaries.
    core = np.array(list(range(18)) + list(range(21, 29)) + list(range(65, 68)))
    full = np.arange(train_x.shape[1])
    specifications = [
        ("rf_core", core, 0.45),
        ("extra_core", core, 0.25),
        ("svm_core", core, 0.15),
        ("rf_full", full, 0.15),
    ]

    threshold = 0.5
    n_splits = min(4, int(counts.min()))
    if n_splits >= 2:
        oof = np.empty(len(train_y), dtype=float)
        folds = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=71)
        for fit_idx, val_idx in folds.split(train_x, train_y):
            oof[val_idx] = _score(
                train_x[fit_idx], train_y[fit_idx], train_x[val_idx],
                specifications,
            )
        grid = np.linspace(0.3, 0.7, 81)
        sensitivity = (oof[train_y == 1, None] >= grid).mean(axis=0)
        specificity = (oof[train_y == 0, None] < grid).mean(axis=0)
        balanced = (sensitivity + specificity) / 2
        near_best = np.flatnonzero(balanced >= balanced.max() - 0.005)
        selected = near_best[np.argmin(np.abs(grid[near_best] - 0.5))]
        threshold = 0.5 + 0.8 * (grid[selected] - 0.5)

    probabilities = _score(train_x, train_y, test_x, specifications)
    return (probabilities >= threshold).astype(int)
