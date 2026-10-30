import numpy as np
from sklearn.ensemble import ExtraTreesClassifier, HistGradientBoostingClassifier
from sklearn.metrics import f1_score
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import QuantileTransformer
from sklearn.svm import SVC


def _impute_fit(x):
    med = np.array([
        np.median(x[np.isfinite(x[:, j]), j]) if np.any(np.isfinite(x[:, j])) else 0.0
        for j in range(x.shape[1])
    ])
    missing = ~np.isfinite(x)
    return np.where(missing, med, x), missing, med


def _impute_apply(x, med):
    missing = ~np.isfinite(x)
    return np.where(missing, med, x), missing


def _svm_features_fit(x):
    filled, missing, med = _impute_fit(x)
    qt = QuantileTransformer(
        n_quantiles=min(256, len(x)), output_distribution='normal',
        random_state=41, subsample=1000000000
    )
    z = np.clip(qt.fit_transform(filled), -3.5, 3.5)
    return np.column_stack((z, 0.7 * missing)), med, qt


def _svm_features_apply(x, med, qt):
    filled, missing = _impute_apply(x, med)
    z = np.clip(qt.transform(filled), -3.5, 3.5)
    return np.column_stack((z, 0.7 * missing))


def _predict_models(train_x, train_y, test_x):
    train_filled, train_missing, med = _impute_fit(train_x)
    test_filled, test_missing = _impute_apply(test_x, med)
    et_train = np.column_stack((train_filled, train_missing))
    et_test = np.column_stack((test_filled, test_missing))
    svm_train, svm_med, qt = _svm_features_fit(train_x)
    svm_test = _svm_features_apply(test_x, svm_med, qt)

    booster = HistGradientBoostingClassifier(
        max_iter=200, learning_rate=0.055, max_leaf_nodes=9,
        min_samples_leaf=25, l2_regularization=5.0,
        early_stopping=False, random_state=41
    )
    trees = ExtraTreesClassifier(
        n_estimators=350, min_samples_leaf=3, max_features=0.9,
        n_jobs=1, random_state=41
    )
    svm = SVC(C=2.5, gamma='scale', probability=True, random_state=41)

    booster.fit(train_x, train_y)
    trees.fit(et_train, train_y)
    svm.fit(svm_train, train_y)
    return np.column_stack((
        booster.predict_proba(test_x)[:, 1],
        trees.predict_proba(et_test)[:, 1],
        svm.predict_proba(svm_test)[:, 1]
    ))


def fit_predict(train_x, train_y, test_x):
    x = np.asarray(train_x, dtype=np.float64).copy()
    y = np.asarray(train_y, dtype=np.int64).ravel()
    test = np.asarray(test_x, dtype=np.float64).copy()
    x[~np.isfinite(x)] = np.nan
    test[~np.isfinite(test)] = np.nan
    if len(np.unique(y)) < 2:
        return np.full(len(test), y[0], dtype=np.int64)

    weights = np.array([0.35, 0.25, 0.40])
    oof = np.zeros((len(y), 3), dtype=np.float64)
    cv = StratifiedKFold(n_splits=4, shuffle=True, random_state=41)
    for fit_idx, val_idx in cv.split(x, y):
        oof[val_idx] = _predict_models(x[fit_idx], y[fit_idx], x[val_idx])

    validation_prob = oof @ weights
    thresholds = np.linspace(0.35, 0.65, 61)
    scores = np.array([
        f1_score(y, validation_prob >= t, average='macro', zero_division=0)
        for t in thresholds
    ])
    best = np.flatnonzero(scores >= scores.max() - 0.001)
    threshold = thresholds[best[np.argmin(np.abs(thresholds[best] - 0.5))]]

    test_prob = _predict_models(x, y, test) @ weights
    return (test_prob >= threshold).astype(np.int64)
