import numpy as np
from scipy.linalg import eigh
from sklearn.model_selection import StratifiedKFold


def _features(x):
    x = np.asarray(x, dtype=np.float64)
    x = np.nan_to_num(x, nan=0.0, posinf=0.0, neginf=0.0)
    x = x.reshape(len(x), 68, 2, 8)
    t = np.arange(8, dtype=float) + 0.5
    basis = np.cos(np.pi * t[:, None] * np.arange(3)[None, :] / 8.0)
    basis /= np.sqrt(np.sum(basis * basis, axis=0, keepdims=True))
    c = np.einsum('npwt,tk->npwk', x, basis)
    level = c[..., 0].reshape(len(x), -1)
    temporal = c.reshape(len(x), -1)
    counts = [4, 4, 7, 4, 6, 5, 4] * 2
    regional = []
    start = 0
    for count in counts:
        block = c[:, start:start + count]
        regional.append(block.mean(axis=1))
        regional.append(np.median(block, axis=1))
        start += count
    left = c[:, :34].mean(axis=1)
    right = c[:, 34:].mean(axis=1)
    regional.extend([left, right, left - right])
    regional = np.stack(regional, axis=1).reshape(len(x), -1)
    contrast = (c[:, :34] - c[:, 34:]).reshape(len(x), -1)
    return [level, temporal, regional, contrast]


def _scale(a, b, temporal):
    center = np.median(a, axis=0)
    q25, q75 = np.percentile(a, [25, 75], axis=0)
    scale = (q75 - q25) / 1.349
    fallback = a.std(axis=0)
    scale = np.where(scale > 1e-12, scale, fallback)
    scale = np.where(scale > 1e-12, scale, 1.0)
    a = np.clip((a - center) / scale, -6.0, 6.0)
    b = np.clip((b - center) / scale, -6.0, 6.0)
    mean = a.mean(axis=0)
    std = a.std(axis=0)
    std = np.where(std > 1e-10, std, 1.0)
    a = (a - mean) / std
    b = (b - mean) / std
    if temporal:
        weights = np.tile([1.0, 0.7, 0.4], a.shape[1] // 3)
        a = a * weights
        b = b * weights
    return a, b


def _kernel(a, b, kind):
    if kind == 'cosine':
        a = a / np.maximum(np.linalg.norm(a, axis=1, keepdims=True), 1e-12)
        b = b / np.maximum(np.linalg.norm(b, axis=1, keepdims=True), 1e-12)
        return a @ a.T, b @ a.T
    d = float(a.shape[1])
    aa = a @ a.T / d
    ba = b @ a.T / d
    if kind == 'linear':
        return aa, ba
    an = np.sum(a * a, axis=1) / d
    bn = np.sum(b * b, axis=1) / d
    dist_train = np.maximum(an[:, None] + an[None, :] - 2 * aa, 0.0)
    dist_test = np.maximum(bn[:, None] + an[None, :] - 2 * ba, 0.0)
    return np.exp(-0.5 * dist_train), np.exp(-0.5 * dist_test)


def _predict_candidates(train_views, y, test_views, specs, alphas):
    n = len(y)
    npos = np.sum(y == 1)
    nneg = n - npos
    target = np.where(y == 1, n / (2.0 * npos), -n / (2.0 * nneg))
    predictions = []
    scaled = {}
    for view, kind in specs:
        if view not in scaled:
            scaled[view] = _scale(train_views[view], test_views[view], view != 0)
        a, b = scaled[view]
        k, kt = _kernel(a, b, kind)
        colmean = k.mean(axis=0)
        grandmean = colmean.mean()
        k = k - colmean[None, :] - colmean[:, None] + grandmean
        kt = kt - colmean[None, :] - kt.mean(axis=1, keepdims=True) + grandmean
        k = (k + k.T) * 0.5
        eigenvalues, eigenvectors = eigh(k, check_finite=False)
        eigenvalues = np.maximum(eigenvalues, 0.0)
        projected = eigenvectors.T @ target
        coefficients = eigenvectors @ (projected[:, None] /
                                      (eigenvalues[:, None] + alphas[None, :]))
        fitted = k @ coefficients
        normalizer = np.maximum(np.sqrt(np.mean(fitted * fitted, axis=0)), 1e-8)
        predictions.append((kt @ coefficients) / normalizer[None, :])
    return np.concatenate(predictions, axis=1)


def fit_predict(train_x, train_y, test_x):
    y = np.asarray(train_y).reshape(-1).astype(int)
    if len(y) != len(train_x):
        raise ValueError('Training features and labels have different lengths.')
    if len(test_x) == 0:
        return np.empty(0, dtype=int)
    classes, counts = np.unique(y, return_counts=True)
    if len(classes) == 0:
        raise ValueError('At least one training trial is required.')
    if len(classes) == 1:
        return np.full(len(test_x), classes[0], dtype=int)
    if not np.array_equal(classes, [0, 1]):
        raise ValueError('Labels must be 0 or 1.')
    train_views = _features(train_x)
    test_views = _features(test_x)
    specs = [(0, 'linear'), (0, 'rbf'),
             (1, 'linear'), (1, 'cosine'),
             (2, 'linear'), (2, 'rbf'), (3, 'cosine')]
    alphas = np.array([0.1, 1.0, 10.0, 100.0])
    priors = np.repeat([1.0, 0.7, 1.0, 0.8, 1.0, 0.7, 0.7], len(alphas))
    priors *= np.tile([0.75, 1.0, 1.0, 1.0], len(specs))
    weights = priors.copy()
    folds = min(4, int(counts.min()))
    if folds >= 2:
        oof = np.zeros((len(y), len(weights)), dtype=float)
        splitter = StratifiedKFold(n_splits=folds, shuffle=True, random_state=1729)
        for fit_idx, val_idx in splitter.split(np.zeros(len(y)), y):
            fit_views = [v[fit_idx] for v in train_views]
            val_views = [v[val_idx] for v in train_views]
            oof[val_idx] = _predict_candidates(fit_views, y[fit_idx],
                                               val_views, specs, alphas)
        positive = oof >= 0.0
        scores = 0.5 * (positive[y == 1].mean(axis=0) +
                        (~positive[y == 0]).mean(axis=0))
        weights *= np.exp((scores - scores.max()) / 0.035)
    weights /= weights.sum()
    predictions = _predict_candidates(train_views, y, test_views, specs, alphas)
    return ((predictions @ weights) >= 0.0).astype(int)
