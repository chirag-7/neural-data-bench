import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import QuantileTransformer
from sklearn.svm import SVC
from sklearn.ensemble import (
    HistGradientBoostingClassifier, ExtraTreesClassifier,
    RandomForestClassifier
)
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import f1_score, balanced_accuracy_score


class _Features(BaseEstimator, TransformerMixin):
    def __init__(self, mode='tree'):
        self.mode = mode

    def fit(self, X, y=None):
        X = np.asarray(X, dtype=float)
        self.median_ = np.array([
            np.median(X[np.isfinite(X[:, j]), j])
            if np.isfinite(X[:, j]).any() else 0.0
            for j in range(X.shape[1])
        ])
        Z = np.where(np.isfinite(X), X, self.median_)
        if self.mode == 'quantile':
            self.qt_ = QuantileTransformer(
                n_quantiles=min(200, len(Z)),
                output_distribution='normal',
                random_state=731,
                subsample=10000
            )
            self.qt_.fit(Z)
        elif self.mode == 'robust':
            self.center_ = np.median(Z, axis=0)
            lo, hi = np.percentile(Z, [25, 75], axis=0)
            scale = hi - lo
            fallback = np.std(Z, axis=0)
            scale = np.where(scale > 1e-12, scale, fallback)
            self.scale_ = np.where(scale > 1e-12, scale, 1.0)
        return self

    def transform(self, X):
        X = np.asarray(X, dtype=float)
        missing = ~np.isfinite(X)
        Z = np.where(missing, self.median_, X)
        if self.mode == 'quantile':
            Z = self.qt_.transform(Z)
        elif self.mode == 'robust':
            Z = np.clip((Z - self.center_) / self.scale_, -8.0, 8.0)
        return np.hstack((Z, 0.5 * missing.astype(float)))


def _model(k):
    seed = 731 + k
    if k < 2:
        mode = 'robust' if k == 0 else 'quantile'
        estimator = SVC(
            C=5.0 if k == 0 else 6.0,
            gamma=0.08,
            kernel='rbf',
            class_weight='balanced',
            probability=True,
            cache_size=256,
            random_state=seed
        )
        return Pipeline([('features', _Features(mode)), ('model', estimator)])
    if k in (2, 3):
        return HistGradientBoostingClassifier(
            learning_rate=0.045,
            max_iter=280,
            max_leaf_nodes=7 if k == 2 else 15,
            min_samples_leaf=20 if k == 2 else 16,
            l2_regularization=5.0 if k == 2 else 12.0,
            early_stopping=False,
            random_state=seed
        )
    if k == 4:
        estimator = ExtraTreesClassifier(
            n_estimators=320,
            min_samples_leaf=2,
            max_features=0.9,
            class_weight='balanced',
            n_jobs=1,
            random_state=seed
        )
    else:
        estimator = RandomForestClassifier(
            n_estimators=320,
            min_samples_leaf=3,
            max_features=0.9,
            class_weight='balanced_subsample',
            n_jobs=1,
            random_state=seed
        )
    return Pipeline([('features', _Features('tree')), ('model', estimator)])


def _threshold(y, p):
    grid = np.linspace(0.20, 0.80, 121)
    values = np.empty(len(grid))
    for i, t in enumerate(grid):
        pred = (p >= t).astype(int)
        values[i] = (
            f1_score(y, pred, average='macro', zero_division=0)
            + 0.0001 * balanced_accuracy_score(y, pred)
        )
    smooth = np.convolve(np.pad(values, (2, 2), mode='edge'),
                         np.ones(5) / 5.0, mode='valid')
    smooth -= 0.002 * np.abs(grid - 0.5)
    near = smooth >= smooth.max() - 0.001
    t = float(np.mean(grid[near]))
    t = 0.85 * t + 0.15 * 0.5
    score = f1_score(y, p >= t, average='macro', zero_division=0)
    return t, float(score)


def fit_predict(train_x, train_y, test_x):
    X = np.asarray(train_x, dtype=np.float64).copy()
    T = np.asarray(test_x, dtype=np.float64).copy()
    y = np.asarray(train_y, dtype=int).reshape(-1)
    if len(T) == 0:
        return np.empty(0, dtype=int)
    classes, counts = np.unique(y, return_counts=True)
    if len(classes) == 1:
        return np.full(len(T), classes[0], dtype=int)
    X[~np.isfinite(X)] = np.nan
    T[~np.isfinite(T)] = np.nan
    n_splits = min(5, int(counts.min()))
    prior = np.array([0.22, 0.22, 0.20, 0.16, 0.12, 0.08])
    if n_splits < 2:
        model = _model(5)
        model.fit(X, y)
        return model.predict(T).astype(int).reshape(-1)
    folds = list(StratifiedKFold(
        n_splits=n_splits, shuffle=True, random_state=731
    ).split(X, y))
    oof = np.zeros((len(y), 6), dtype=float)
    for k in range(6):
        for fitting, validation in folds:
            model = _model(k)
            model.fit(X[fitting], y[fitting])
            oof[validation, k] = model.predict_proba(X[validation])[:, 1]
    scores = np.array([_threshold(y, oof[:, k])[1] for k in range(6)])
    quality = prior * np.exp(np.clip((scores - scores.max()) / 0.025, -20, 0))
    quality /= quality.sum()
    weights = 0.90 * quality + 0.10 * prior
    threshold, _ = _threshold(y, oof @ weights)
    probability = np.zeros(len(T), dtype=float)
    for k in range(6):
        model = _model(k)
        model.fit(X, y)
        probability += weights[k] * model.predict_proba(T)[:, 1]
    return (probability >= threshold).astype(int).reshape(-1)
