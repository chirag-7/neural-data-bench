import numpy as np
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold


# Fixed positions of acquisition dimensions/spacings and tissue voxel counts.
_DROP = np.array([18, 19, 20, 29, 30, 31, 36, 44, 52, 60], dtype=int)


def _learn_transform(x):
    x = np.asarray(x, dtype=np.float64)
    finite = np.isfinite(x)
    p = x.shape[1]
    med = np.zeros(p, dtype=np.float64)
    scale = np.ones(p, dtype=np.float64)
    for j in range(p):
        v = x[finite[:, j], j]
        if v.size:
            med[j] = np.median(v)
            q25, q75 = np.percentile(v, [25.0, 75.0])
            s = q75 - q25
            if not np.isfinite(s) or s < 1e-12:
                s = np.median(np.abs(v - med[j])) * 1.4826
            if not np.isfinite(s) or s < 1e-12:
                s = np.std(v)
            if np.isfinite(s) and s >= 1e-12:
                scale[j] = s
    return med, scale


def _transform(x, med, scale):
    x = np.asarray(x, dtype=np.float64)
    missing = ~np.isfinite(x)
    z = np.where(missing, med[None, :], x)
    z = (z - med[None, :]) / scale[None, :]
    z = np.clip(z, -12.0, 12.0)
    tree_x = np.hstack((z, missing.astype(np.float64)))
    # The compressed copy improves linear modeling of highly skewed IQMs.
    signed_log = np.sign(z) * np.log1p(np.abs(z))
    linear_x = np.hstack((z, signed_log, missing.astype(np.float64)))
    return tree_x, linear_x


def _models(seed, trees):
    extra = ExtraTreesClassifier(
        n_estimators=trees,
        max_features=0.65,
        min_samples_leaf=3,
        class_weight="balanced",
        random_state=seed,
        n_jobs=1
    )
    forest = RandomForestClassifier(
        n_estimators=trees,
        max_features="sqrt",
        min_samples_leaf=3,
        class_weight="balanced_subsample",
        random_state=seed + 1009,
        n_jobs=1
    )
    linear = LogisticRegression(
        C=0.25,
        class_weight="balanced",
        solver="liblinear",
        max_iter=2000,
        random_state=seed + 2017
    )
    return extra, forest, linear


def _p1(model, x):
    pos = np.flatnonzero(model.classes_ == 1)
    if pos.size:
        return model.predict_proba(x)[:, pos[0]]
    return np.full(x.shape[0], float(model.classes_[0] == 1))


def _fit_probability(train_x, train_y, pred_x, seed, trees):
    med, scale = _learn_transform(train_x)
    tr_tree, tr_linear = _transform(train_x, med, scale)
    pr_tree, pr_linear = _transform(pred_x, med, scale)
    extra, forest, linear = _models(seed, trees)
    extra.fit(tr_tree, train_y)
    forest.fit(tr_tree, train_y)
    linear.fit(tr_linear, train_y)
    return (0.40 * _p1(extra, pr_tree) +
            0.40 * _p1(forest, pr_tree) +
            0.20 * _p1(linear, pr_linear))


def _balanced_accuracy(y, pred):
    a = pred[y == 0]
    b = pred[y == 1]
    return 0.5 * (np.mean(a == 0) + np.mean(b == 1))


def _choose_threshold(y, probability):
    candidates = np.unique(np.r_[0.5, np.linspace(0.15, 0.85, 281),
                                 probability])
    best_score = -1.0
    best_threshold = 0.5
    for threshold in candidates:
        score = _balanced_accuracy(y, probability >= threshold)
        if (score > best_score + 1e-12 or
                (abs(score - best_score) <= 1e-12 and
                 abs(threshold - 0.5) < abs(best_threshold - 0.5))):
            best_score = score
            best_threshold = float(threshold)
    return best_threshold


def fit_predict(train_x, train_y, test_x):
    x = np.asarray(train_x, dtype=np.float64)
    y = np.asarray(train_y).reshape(-1).astype(np.int64)
    test = np.asarray(test_x, dtype=np.float64)

    keep = np.ones(x.shape[1], dtype=bool)
    keep[_DROP[_DROP < x.shape[1]]] = False
    x = x[:, keep]
    test = test[:, keep]

    labels, counts = np.unique(y, return_counts=True)
    if labels.size < 2:
        return np.full(test.shape[0], int(labels[0]), dtype=np.int64)

    n_splits = int(min(5, counts.min()))
    if n_splits >= 2:
        oof = np.zeros(y.size, dtype=np.float64)
        cv = StratifiedKFold(n_splits=n_splits, shuffle=True,
                            random_state=314159)
        for fold, (fit_idx, val_idx) in enumerate(cv.split(x, y)):
            oof[val_idx] = _fit_probability(
                x[fit_idx], y[fit_idx], x[val_idx],
                seed=7001 + 97 * fold, trees=260
            )
        threshold = _choose_threshold(y, oof)
    else:
        threshold = 0.5

    probability = _fit_probability(x, y, test, seed=17011, trees=520)
    return (probability >= threshold).astype(np.int64)
