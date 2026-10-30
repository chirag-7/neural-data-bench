import numpy as np


def _best_threshold(y, p):
    """Exact best macro-F1 threshold, considering only realizable tie boundaries."""
    y = np.asarray(y, dtype=np.int8)
    p = np.asarray(p, dtype=float)
    order = np.argsort(-p, kind="mergesort")
    ps = p[order]
    ys = y[order]
    n = y.size
    pos = int(ys.sum())
    neg = n - pos

    tp = np.r_[0, np.cumsum(ys, dtype=np.int64)]
    k = np.arange(n + 1, dtype=np.int64)
    fp = k - tp
    fn = pos - tp
    tn = neg - fp

    den1 = 2 * tp + fp + fn
    den0 = 2 * tn + fp + fn
    f1_pos = np.divide(2.0 * tp, den1, out=np.zeros(n + 1), where=den1 != 0)
    f1_neg = np.divide(2.0 * tn, den0, out=np.zeros(n + 1), where=den0 != 0)
    scores = 0.5 * (f1_pos + f1_neg)

    valid = np.ones(n + 1, dtype=bool)
    if n > 1:
        valid[1:n] = ps[:-1] > ps[1:]
    candidates = np.flatnonzero(valid)
    best_score = float(np.max(scores[candidates]))
    tied = candidates[np.isclose(scores[candidates], best_score, rtol=0.0, atol=1e-12)]

    thresholds = []
    for cut in tied:
        if cut == 0:
            threshold = np.nextafter(ps[0], np.inf)
        elif cut == n:
            threshold = np.nextafter(ps[-1], -np.inf)
        else:
            threshold = ps[cut] + 0.5 * (ps[cut - 1] - ps[cut])
        thresholds.append(threshold)
    thresholds = np.asarray(thresholds)
    threshold = float(thresholds[np.argmin(np.abs(thresholds - 0.5))])
    return best_score, threshold


def _models(seed):
    from sklearn.pipeline import Pipeline
    from sklearn.impute import SimpleImputer
    from sklearn.preprocessing import RobustScaler
    from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier
    from sklearn.ensemble import HistGradientBoostingClassifier
    from sklearn.svm import SVC
    from sklearn.linear_model import LogisticRegression

    def imputer():
        return SimpleImputer(strategy="median", add_indicator=True)

    models = []
    models.append((
        "extra",
        Pipeline([
            ("impute", imputer()),
            ("clf", ExtraTreesClassifier(
                n_estimators=320,
                criterion="entropy",
                max_features=0.8,
                min_samples_leaf=3,
                class_weight="balanced",
                random_state=seed,
                n_jobs=1
            ))
        ]),
        False
    ))
    models.append((
        "forest",
        Pipeline([
            ("impute", imputer()),
            ("clf", RandomForestClassifier(
                n_estimators=280,
                criterion="entropy",
                max_features=0.8,
                min_samples_leaf=3,
                class_weight="balanced_subsample",
                max_samples=0.85,
                random_state=seed + 1,
                n_jobs=1
            ))
        ]),
        False
    ))
    models.append((
        "hist",
        Pipeline([
            ("impute", imputer()),
            ("clf", HistGradientBoostingClassifier(
                learning_rate=0.045,
                max_iter=190,
                max_leaf_nodes=15,
                min_samples_leaf=18,
                l2_regularization=2.0,
                early_stopping=False,
                random_state=seed + 2
            ))
        ]),
        True
    ))
    models.append((
        "rbf",
        Pipeline([
            ("impute", imputer()),
            ("scale", RobustScaler(quantile_range=(15.0, 85.0))),
            ("clf", SVC(
                C=1.5,
                gamma="scale",
                class_weight="balanced",
                probability=True,
                cache_size=512,
                random_state=seed + 3
            ))
        ]),
        False
    ))
    models.append((
        "linear",
        Pipeline([
            ("impute", imputer()),
            ("scale", RobustScaler(quantile_range=(15.0, 85.0))),
            ("clf", LogisticRegression(
                C=0.35,
                class_weight="balanced",
                solver="liblinear",
                max_iter=2000,
                random_state=seed + 4
            ))
        ]),
        False
    ))
    return models


def fit_predict(train_x, train_y, test_x):
    from sklearn.model_selection import RepeatedStratifiedKFold
    from sklearn.utils.class_weight import compute_sample_weight

    x = np.asarray(train_x, dtype=np.float64)
    y = np.asarray(train_y).reshape(-1).astype(np.int8)
    xt = np.asarray(test_x, dtype=np.float64)

    if xt.shape[0] == 0:
        return np.empty(0, dtype=np.int64)
    classes = np.unique(y)
    if classes.size == 1:
        return np.full(xt.shape[0], int(classes[0]), dtype=np.int64)

    n_models = 5
    oof_sum = np.zeros((x.shape[0], n_models), dtype=np.float64)
    oof_count = np.zeros(x.shape[0], dtype=np.int16)
    test_sum = np.zeros((xt.shape[0], n_models), dtype=np.float64)
    folds = RepeatedStratifiedKFold(n_splits=5, n_repeats=2, random_state=1729)
    n_fits = 0

    for fold_id, (fit_idx, val_idx) in enumerate(folds.split(x, y)):
        models = _models(3100 + 37 * fold_id)
        weights = compute_sample_weight(class_weight="balanced", y=y[fit_idx])
        for model_id, (_, model, needs_weight) in enumerate(models):
            if needs_weight:
                model.fit(x[fit_idx], y[fit_idx], clf__sample_weight=weights)
            else:
                model.fit(x[fit_idx], y[fit_idx])
            oof_sum[val_idx, model_id] += model.predict_proba(x[val_idx])[:, 1]
            test_sum[:, model_id] += model.predict_proba(xt)[:, 1]
        oof_count[val_idx] += 1
        n_fits += 1

    oof = oof_sum / oof_count[:, None]
    test_probabilities = test_sum / float(n_fits)

    candidates = []
    for mask in range(1, 1 << n_models):
        indices = [j for j in range(n_models) if mask & (1 << j)]
        blended = np.mean(oof[:, indices], axis=1)
        score, threshold = _best_threshold(y, blended)
        candidates.append((score, len(indices), indices, threshold))

    highest = max(item[0] for item in candidates)
    stable = [item for item in candidates if item[0] >= highest - 0.0015]
    largest = max(item[1] for item in stable)
    stable = [item for item in stable if item[1] == largest]
    chosen = max(stable, key=lambda item: item[0])
    indices = chosen[2]
    threshold = chosen[3]

    final_probability = np.mean(test_probabilities[:, indices], axis=1)
    return (final_probability >= threshold).astype(np.int64)
