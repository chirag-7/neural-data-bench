import numpy as np
from scipy.special import expit
from sklearn.model_selection import StratifiedKFold
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier
from sklearn.metrics import roc_auc_score, balanced_accuracy_score


def _features(x):
    x = np.asarray(x, dtype=np.float64)
    x = np.where(np.isfinite(x), x, np.nan)
    if x.shape[1] != 68:
        return x.copy()
    # Remove acquisition dimensions, voxel spacing, and absolute tissue counts.
    omit = {18, 19, 20, 29, 30, 31, 36, 44, 52, 60}
    parts = [x[:, [j for j in range(68) if j not in omit]]]
    wm = np.abs(x[:, 59])
    denominator = np.where(wm > 1e-8, wm, np.nan)
    relative = []
    for start in (32, 40, 48, 56):
        for offset in (1, 2, 3, 5, 6, 7):
            relative.append(x[:, start + offset] / denominator)
        median = np.abs(x[:, start + 3])
        tissue_denominator = np.where(median > 1e-8, median, np.nan)
        relative.append(x[:, start + 7] / tissue_denominator)
        relative.append((x[:, start + 6] - x[:, start + 5]) /
                        tissue_denominator)
    counts = x[:, [36, 44, 52, 60]]
    total = np.sum(counts, axis=1)
    total = np.where(total > 1e-8, total, np.nan)
    parts.append(counts / total[:, None])
    parts.append(np.column_stack(relative))
    result = np.column_stack(parts)
    return np.where(np.isfinite(result), result, np.nan)


class _Preprocessor:
    def fit(self, x):
        z = _features(x)
        self.columns = np.flatnonzero(np.sum(np.isfinite(z), axis=0) >= 2)
        if self.columns.size == 0:
            self.columns = np.array([], dtype=int)
            self.median = np.empty(0)
            self.scale = np.empty(0)
            self.spread = np.empty(0)
            self.indicators = np.empty(0, dtype=int)
            return self
        z = z[:, self.columns]
        self.median = np.nanmedian(z, axis=0)
        missing_rate = np.mean(~np.isfinite(z), axis=0)
        self.indicators = np.flatnonzero((missing_rate > 0.01) &
                                        (missing_rate < 0.99))
        z = np.where(np.isfinite(z), z, self.median)
        quantiles = np.percentile(z, [10, 25, 75, 90], axis=0)
        scale = quantiles[2] - quantiles[1]
        scale = np.where(scale > 1e-10, scale,
                         (quantiles[3] - quantiles[0]) / 2.0)
        scale = np.where(scale > 1e-10, scale, np.std(z, axis=0))
        self.scale = np.where(scale > 1e-10, scale, 1.0)
        transformed = np.arcsinh(np.clip(
            (z - self.median) / self.scale, -1e8, 1e8))
        self.spread = np.maximum(np.std(transformed, axis=0), 0.25)
        return self

    def transform(self, x):
        z = _features(x)[:, self.columns]
        if z.shape[1] == 0:
            return np.zeros((z.shape[0], 1), dtype=np.float64)
        missing = ~np.isfinite(z)
        z = np.where(missing, self.median, z)
        z = np.arcsinh(np.clip((z - self.median) / self.scale, -1e8, 1e8))
        z = np.clip(z / self.spread, -8.0, 8.0)
        if self.indicators.size:
            z = np.column_stack((z, missing[:, self.indicators].astype(float)))
        return z


def _make_model(spec, dimension):
    family, first, second = spec
    if family == 'linear':
        return LogisticRegression(C=first, class_weight='balanced',
                                  solver='liblinear', max_iter=1500,
                                  random_state=173)
    if family == 'svm':
        return SVC(C=first, gamma=second / max(dimension, 1),
                   kernel='rbf', class_weight='balanced',
                   cache_size=256, random_state=173)
    common = dict(n_estimators=300, min_samples_leaf=3,
                  max_features=0.7, class_weight='balanced',
                  n_jobs=1, random_state=173)
    if family == 'extra':
        return ExtraTreesClassifier(**common)
    return RandomForestClassifier(max_depth=14, **common)


def _probability(model, x):
    if isinstance(model, SVC):
        return expit(model.decision_function(x))
    return model.predict_proba(x)[:, 1]


def fit_predict(train_x, train_y, test_x):
    x = np.asarray(train_x, dtype=np.float64)
    test = np.asarray(test_x, dtype=np.float64)
    y = np.asarray(train_y).reshape(-1).astype(np.int64)
    if x.ndim != 2 or test.ndim != 2 or x.shape[1] != test.shape[1]:
        raise ValueError('Training and test inputs must have matching feature columns.')
    if len(x) != len(y) or len(y) == 0:
        raise ValueError('Training inputs and labels must have matching nonzero lengths.')
    if not np.all(np.isin(y, [0, 1])):
        raise ValueError('Labels must use the supplied 0/1 encoding.')
    if len(test) == 0:
        return np.empty(0, dtype=np.int64)
    classes, counts = np.unique(y, return_counts=True)
    if len(classes) == 1:
        return np.full(len(test), classes[0], dtype=np.int64)

    specs = [('linear', 0.03, 0), ('linear', 0.3, 0),
             ('svm', 0.5, 0.5), ('svm', 2.0, 0.5),
             ('svm', 8.0, 0.5), ('svm', 2.0, 1.5),
             ('extra', 0, 0), ('forest', 0, 0)]
    base_weight = {'linear': 0.15, 'svm': 0.40,
                   'extra': 0.20, 'forest': 0.25}
    n_splits = min(4, int(np.min(counts)))
    threshold = 0.5
    if n_splits >= 2:
        oof = np.zeros((len(y), len(specs)), dtype=float)
        splitter = StratifiedKFold(n_splits=n_splits, shuffle=True,
                                  random_state=173)
        for fit_indices, valid_indices in splitter.split(x, y):
            prep = _Preprocessor().fit(x[fit_indices])
            fit_data = prep.transform(x[fit_indices])
            valid_data = prep.transform(x[valid_indices])
            for j, spec in enumerate(specs):
                model = _make_model(spec, fit_data.shape[1])
                model.fit(fit_data, y[fit_indices])
                oof[valid_indices, j] = _probability(model, valid_data)
        quality = np.array([
            0.7 * roc_auc_score(y, oof[:, j]) +
            0.3 * balanced_accuracy_score(y, oof[:, j] >= 0.5)
            for j in range(len(specs))])
        selected, weights = [], []
        for family in ('linear', 'svm', 'extra', 'forest'):
            indices = [j for j, spec in enumerate(specs) if spec[0] == family]
            indices.sort(key=lambda j: quality[j], reverse=True)
            chosen = indices[:2] if family == 'svm' else indices[:1]
            internal = np.exp(12.0 * (quality[chosen] - np.max(quality[chosen])))
            internal /= np.sum(internal)
            family_adjustment = np.exp(8.0 *
                                       (quality[indices[0]] - np.max(quality)))
            for j, fraction in zip(chosen, internal):
                selected.append(j)
                weights.append(base_weight[family] * family_adjustment * fraction)
        weights = np.asarray(weights)
        weights /= weights.sum()
        ensemble = oof[:, selected].dot(weights)
        thresholds = np.linspace(0.30, 0.70, 41)
        objectives = []
        for value in thresholds:
            score = np.mean([
                balanced_accuracy_score(y, ensemble >= value + offset)
                for offset in (-0.025, 0.0, 0.025)])
            objectives.append(score - 0.025 * abs(value - 0.5))
        best = int(np.argmax(objectives))
        threshold = 0.5 + 0.75 * (thresholds[best] - 0.5)
    else:
        selected = [0, 3, 6, 7]
        weights = np.array([0.15, 0.40, 0.20, 0.25])

    prep = _Preprocessor().fit(x)
    fit_data = prep.transform(x)
    test_data = prep.transform(test)
    prediction = np.zeros(len(test), dtype=float)
    for j, weight in zip(selected, weights):
        model = _make_model(specs[j], fit_data.shape[1])
        model.fit(fit_data, y)
        prediction += weight * _probability(model, test_data)
    return (prediction >= threshold).astype(np.int64)
