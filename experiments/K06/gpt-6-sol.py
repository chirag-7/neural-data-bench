import numpy as np
from scipy.ndimage import gaussian_filter1d
from scipy.spatial.distance import cdist
from sklearn.svm import SVC


def fit_predict(train_x, train_y, test_x, train_groups):
    x = np.asarray(train_x, dtype=float)
    y = np.asarray(train_y, dtype=int)
    xt = np.asarray(test_x, dtype=float)
    groups = np.asarray(train_groups['group_ids'])
    folds = np.asarray(train_groups['cv_fold'])
    n = len(y)

    def mouse_weights(yy, gg):
        w = np.zeros(len(yy), dtype=float)
        for cls in (0, 1):
            mice = np.unique(gg[yy == cls])
            for mouse in mice:
                mask = (yy == cls) & (gg == mouse)
                w[mask] = 1.0 / (2.0 * len(mice) * mask.sum())
        return w / w.mean()

    def features(a, b, mode):
        parts_a, parts_b = [], []
        if mode in ('width', 'scalar', 'width_wave', 'scalar_wave'):
            cols = [0, 1, 4, 5] if mode.startswith('width') else list(range(6))
            aa = a[:, cols].copy()
            bb = b[:, cols].copy()
            for j in range(len(cols)):
                finite = aa[np.isfinite(aa[:, j]), j]
                med = float(np.median(finite)) if len(finite) else 0.0
                scale = float(np.subtract(*np.percentile(finite, [75, 25])[::-1])) / 1.349 if len(finite) else 1.0
                if scale < 1e-8:
                    scale = float(np.std(finite)) if len(finite) else 1.0
                scale = max(scale, 1e-8)
                aa[:, j] = np.clip((np.where(np.isfinite(aa[:, j]), aa[:, j], med) - med) / scale, -6, 6)
                bb[:, j] = np.clip((np.where(np.isfinite(bb[:, j]), bb[:, j], med) - med) / scale, -6, 6)
            parts_a.append(aa / np.sqrt(len(cols)))
            parts_b.append(bb / np.sqrt(len(cols)))
        if mode in ('wave', 'width_wave', 'scalar_wave'):
            wa = gaussian_filter1d(a[:, 6:], 1.2, axis=1, mode='nearest')[:, ::3]
            wb = gaussian_filter1d(b[:, 6:], 1.2, axis=1, mode='nearest')[:, ::3]
            center = wa.mean(axis=0)
            scale = max(float(np.sqrt(np.mean((wa - center) ** 2))), 1e-8)
            parts_a.append(np.clip((wa - center) / scale, -8, 8) / np.sqrt(wa.shape[1]))
            parts_b.append(np.clip((wb - center) / scale, -8, 8) / np.sqrt(wa.shape[1]))
        if len(parts_a) == 2:
            parts_a = [v / np.sqrt(2) for v in parts_a]
            parts_b = [v / np.sqrt(2) for v in parts_b]
        return np.concatenate(parts_a, axis=1), np.concatenate(parts_b, axis=1)

    def mouse_score(decision):
        pred = (decision >= 0).astype(int)
        class_scores = []
        for cls in (0, 1):
            scores = []
            for mouse in np.unique(groups[y == cls]):
                mask = (groups == mouse) & (y == cls)
                scores.append(np.mean(pred[mask] == y[mask]))
            class_scores.append(np.mean(scores))
        return float(np.mean(class_scores))

    modes = ('width', 'scalar', 'wave', 'width_wave', 'scalar_wave')
    candidates = []
    for mode in modes:
        prepared = []
        for fold in np.unique(folds):
            train = folds != fold
            valid = ~train
            a, b = features(x[train], x[valid], mode)
            dist_train = cdist(a, a, 'sqeuclidean')
            dist_valid = cdist(b, a, 'sqeuclidean')
            upper = dist_train[np.triu_indices(len(a), 1)]
            median_dist = max(float(np.median(upper)), 1e-8)
            prepared.append((valid, y[train], mouse_weights(y[train], groups[train]), a, b, dist_train, dist_valid, median_dist))
        for kind in ('linear', 'rbf'):
            for c in (0.1, 1.0, 10.0, 100.0):
                for gamma_factor in ((1.0,) if kind == 'linear' else (0.25, 1.0, 4.0)):
                    oof = np.zeros(n, dtype=float)
                    for valid, yy, weight, a, b, dtrain, dvalid, median_dist in prepared:
                        if kind == 'linear':
                            model = SVC(C=c, kernel='linear', random_state=20261031)
                            model.fit(a, yy, sample_weight=weight)
                            decision = model.decision_function(b)
                        else:
                            gamma = gamma_factor / median_dist
                            kernel_train = np.exp(-gamma * dtrain)
                            kernel_valid = np.exp(-gamma * dvalid)
                            model = SVC(C=c, kernel='precomputed', random_state=20261031)
                            model.fit(kernel_train, yy, sample_weight=weight)
                            decision = model.decision_function(kernel_valid)
                        oof[valid] = decision
                    score = mouse_score(oof)
                    margin_scale = max(float(np.median(np.abs(oof))), 0.2)
                    candidates.append((score, mode, kind, c, gamma_factor, margin_scale))

    best_per_mode = []
    for mode in modes:
        options = [entry for entry in candidates if entry[1] == mode]
        best_per_mode.append(max(options, key=lambda entry: entry[0]))
    best_per_mode.sort(key=lambda entry: entry[0], reverse=True)
    best_score = best_per_mode[0][0]
    selected = [entry for entry in best_per_mode if entry[0] >= best_score - 0.10][:3]
    ensemble_weights = np.exp(np.array([(entry[0] - best_score) / 0.04 for entry in selected]))
    ensemble_weights /= ensemble_weights.sum()

    result = np.zeros(len(xt), dtype=float)
    full_weight = mouse_weights(y, groups)
    for weight, (_, mode, kind, c, gamma_factor, margin_scale) in zip(ensemble_weights, selected):
        a, b = features(x, xt, mode)
        if kind == 'linear':
            model = SVC(C=c, kernel='linear', random_state=20261031)
            model.fit(a, y, sample_weight=full_weight)
            decision = model.decision_function(b)
        else:
            dtrain = cdist(a, a, 'sqeuclidean')
            dtest = cdist(b, a, 'sqeuclidean')
            upper = dtrain[np.triu_indices(len(a), 1)]
            gamma = gamma_factor / max(float(np.median(upper)), 1e-8)
            model = SVC(C=c, kernel='precomputed', random_state=20261031)
            model.fit(np.exp(-gamma * dtrain), y, sample_weight=full_weight)
            decision = model.decision_function(np.exp(-gamma * dtest))
        result += weight * np.clip(np.nan_to_num(decision / margin_scale), -4, 4)
    return (result >= 0).astype(int)
