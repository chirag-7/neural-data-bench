import numpy as np
from sklearn.svm import SVC
from sklearn.ensemble import ExtraTreesClassifier


SEED = 20261031


def _weights(y, groups):
    w = np.zeros(len(y), dtype=float)
    for c in (0, 1):
        mask = y == c
        mice = np.unique(groups[mask])
        for mouse in mice:
            rows = mask & (groups == mouse)
            w[rows] = 1.0 / (2.0 * len(mice) * np.sum(rows))
    return w / np.sum(w)


def _engineer(wave):
    result = []
    for raw in wave:
        v = raw - np.median(raw[:8])
        trough = int(np.argmin(v))
        peak = trough + int(np.argmax(v[trough:]))
        depth = max(-v[trough], 1e-6)
        widths = []
        for fraction in (0.25, 0.5, 0.75):
            level = -depth * fraction
            left = trough
            right = trough
            while left > 0 and v[left - 1] <= level:
                left -= 1
            while right < len(v) - 1 and v[right + 1] <= level:
                right += 1
            lo = float(left)
            hi = float(right)
            if left > 0:
                den = v[left] - v[left - 1]
                if abs(den) > 1e-12:
                    lo = left - 1 + np.clip((level - v[left - 1]) / den, 0, 1)
            if right < len(v) - 1:
                den = v[right + 1] - v[right]
                if abs(den) > 1e-12:
                    hi = right + np.clip((level - v[right]) / den, 0, 1)
            widths.append(max(hi - lo, 0.0) * 0.025)
        derivative = np.diff(v)
        curvature = 0.0
        if 0 < trough < len(v) - 1:
            curvature = v[trough - 1] + v[trough + 1] - 2 * v[trough]
        row = [trough * 0.025, (peak - trough) * 0.025,
               v[peak] / depth, np.max(v[:trough + 1]) / depth]
        row.extend(widths)
        row.extend([np.sum(np.maximum(v, 0)) * 0.025,
                    np.sum(np.maximum(-v, 0)) * 0.025,
                    np.mean(v * v), np.max(derivative),
                    np.min(derivative), curvature])
        row.extend([np.mean(v[a:b]) for a, b in
                    ((0, 20), (20, 40), (40, 60), (60, 81))])
        result.append(row)
    return np.asarray(result, dtype=float)


class _Features:
    def fit(self, x):
        self.median = np.array([
            np.median(col[np.isfinite(col)]) if np.any(np.isfinite(col)) else 0.0
            for col in x.T])
        x = self.fill(x)
        blocks = [x[:, :6], x[:, 6:], np.diff(x[:, 6:], axis=1),
                  _engineer(x[:, 6:])]
        self.centers = []
        self.scales = []
        for i, block in enumerate(blocks):
            center = np.mean(block, axis=0)
            scale = np.std(block, axis=0)
            floor = max(0.2 * np.max(scale), 1e-8) if i in (1, 2) else 1e-8
            self.centers.append(center)
            self.scales.append(np.maximum(scale, floor))
        return self

    def fill(self, x):
        return np.where(np.isfinite(x), x, self.median)

    def transform(self, x):
        x = self.fill(x)
        engineered = _engineer(x[:, 6:])
        blocks = [x[:, :6], x[:, 6:], np.diff(x[:, 6:], axis=1), engineered]
        z = [np.clip((b - m) / s, -8, 8)
             for b, m, s in zip(blocks, self.centers, self.scales)]
        scalar = z[0] / np.sqrt(6.0)
        wave = z[1] / np.sqrt(81.0)
        derivative = z[2] / np.sqrt(80.0)
        extra = z[3] / np.sqrt(z[3].shape[1])
        return {
            'scalar': scalar,
            'mixed': np.concatenate((scalar, wave, 0.25 * extra), axis=1),
            'wave': np.concatenate((wave, 0.35 * derivative, 0.25 * extra), axis=1),
            'tree': np.concatenate((x, engineered), axis=1)
        }


def _make_model(config, x, index):
    family, kernel, c, gamma = config
    if family == 'tree':
        return ExtraTreesClassifier(
            n_estimators=320, max_features=kernel, min_samples_leaf=int(c),
            bootstrap=False, n_jobs=1, random_state=SEED + index)
    if kernel == 'rbf':
        gamma = gamma / max(float(np.sum(np.var(x, axis=0))), 1e-8)
        return SVC(C=c, kernel='rbf', gamma=gamma, cache_size=128,
                   shrinking=True, tol=1e-3, random_state=SEED)
    return SVC(C=c, kernel='linear', cache_size=128, tol=1e-3,
               random_state=SEED)


def _margin(model, x, family):
    if family == 'tree':
        columns = np.flatnonzero(model.classes_ == 1)
        if len(columns) == 0:
            return -np.ones(len(x))
        return 2.0 * model.predict_proba(x)[:, columns[0]] - 1.0
    return np.tanh(model.decision_function(x))


def _utility(pred, y, weights):
    accuracy = np.sum(weights * ((pred >= 0) == y))
    error = np.sum(weights * (pred - (2.0 * y - 1.0)) ** 2)
    return float(accuracy - 0.025 * error)


def fit_predict(train_x, train_y, test_x, train_groups):
    x = np.asarray(train_x, dtype=float)
    y = np.asarray(train_y, dtype=int).reshape(-1)
    test = np.asarray(test_x, dtype=float)
    groups = np.asarray(train_groups['group_ids']).reshape(-1)
    folds = np.asarray(train_groups['cv_fold']).reshape(-1)
    weights = _weights(y, groups)
    configs = []
    families = ('scalar', 'mixed', 'wave', 'tree')
    for family in families[:3]:
        for c in (0.1, 1.0, 10.0, 100.0):
            for gamma in (0.25, 1.0, 4.0):
                configs.append((family, 'rbf', c, gamma))
    for family in ('scalar', 'mixed'):
        for c in (0.1, 1.0, 10.0):
            configs.append((family, 'linear', c, 0.0))
    for features in ('sqrt', 1.0):
        for leaf in (1, 3):
            configs.append(('tree', features, leaf, 0.0))
    oof = np.zeros((len(y), len(configs)), dtype=float)
    for fold in np.unique(folds):
        valid = folds == fold
        training = ~valid
        prep = _Features().fit(x[training])
        a = prep.transform(x[training])
        b = prep.transform(x[valid])
        fit_weights = _weights(y[training], groups[training]) * np.sum(training)
        for j, config in enumerate(configs):
            family = config[0]
            model = _make_model(config, a[family], j)
            model.fit(a[family], y[training], sample_weight=fit_weights)
            oof[valid, j] = _margin(model, b[family], family)
    utilities = np.array([_utility(oof[:, j], y, weights)
                          for j in range(len(configs))])
    selections = []
    within_weights = []
    family_predictions = []
    for family in families:
        indices = np.array([j for j, c in enumerate(configs) if c[0] == family])
        order = indices[np.argsort(-utilities[indices], kind='stable')]
        selected = order[:5]
        selected = selected[utilities[selected] >= utilities[order[0]] - 0.05]
        blend = np.exp((utilities[selected] - utilities[selected].max()) / 0.03)
        blend /= blend.sum()
        selections.append(selected)
        within_weights.append(blend)
        family_predictions.append(np.sum(oof[:, selected] * blend, axis=1))
    family_scores = np.array([_utility(p, y, weights) for p in family_predictions])
    prior = np.array([0.22, 0.38, 0.18, 0.22])
    ensemble_weights = prior * np.exp((family_scores - family_scores.max()) / 0.05)
    ensemble_weights /= ensemble_weights.sum()
    prep = _Features().fit(x)
    a = prep.transform(x)
    b = prep.transform(test)
    prediction = np.zeros(len(test), dtype=float)
    for k, family in enumerate(families):
        family_prediction = np.zeros(len(test), dtype=float)
        for j, blend in zip(selections[k], within_weights[k]):
            model = _make_model(configs[j], a[family], int(j))
            model.fit(a[family], y, sample_weight=weights * len(y))
            family_prediction += blend * _margin(model, b[family], family)
        prediction += ensemble_weights[k] * family_prediction
    return (np.nan_to_num(prediction, nan=0.0) >= 0.0).astype(np.int64)
