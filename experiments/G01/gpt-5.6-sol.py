import numpy as np


def _clean_x(x):
    x = np.asarray(x, dtype=np.float64)
    return np.nan_to_num(x, nan=0.0, posinf=0.0, neginf=0.0)


def _clean_y(y):
    y = np.asarray(y, dtype=np.float64).copy()
    for j in range(y.shape[1]):
        good = np.isfinite(y[:, j])
        fill = np.median(y[good, j]) if np.any(good) else 0.0
        y[~good, j] = fill
    return y


def _base_transform(x, kind):
    if kind == 0:
        return x
    xp = np.maximum(x, 0.0)
    if kind == 1:
        return np.sqrt(xp)
    return np.log1p(xp)


def _fit_preprocessor(x, kind):
    a = _base_transform(x, kind)
    mean1 = np.mean(a, axis=0)
    scale1 = np.std(a, axis=0)
    scale1 = np.where(scale1 > 1e-8, scale1, 1.0)
    z = np.clip((a - mean1) / scale1, -8.0, 8.0)
    mean2 = np.mean(z, axis=0)
    scale2 = np.std(z, axis=0)
    scale2 = np.where(scale2 > 1e-8, scale2, 1.0)
    z = (z - mean2) / scale2
    return z, (kind, mean1, scale1, mean2, scale2)


def _apply_preprocessor(x, state):
    kind, mean1, scale1, mean2, scale2 = state
    a = _base_transform(x, kind)
    z = np.clip((a - mean1) / scale1, -8.0, 8.0)
    return (z - mean2) / scale2


def _ridge_path(x, y, alpha_fractions):
    ymean = np.mean(y, axis=0)
    yc = y - ymean
    gram = x.T @ x
    cross = x.T @ yc
    vals, vecs = np.linalg.eigh(gram)
    vals = np.maximum(vals, 0.0)
    projected = vecs.T @ cross
    weights = []
    n = float(x.shape[0])
    for frac in alpha_fractions:
        denom = vals + max(frac * n, 1e-10)
        weights.append(vecs @ (projected / denom[:, None]))
    return ymean, weights


def _output_bounds(y):
    lo = np.quantile(y, 0.001, axis=0)
    hi = np.quantile(y, 0.999, axis=0)
    span = np.maximum(hi - lo, 1e-8)
    return lo - 0.10 * span, hi + 0.10 * span


def fit_predict(train_x, train_y, test_x):
    x = _clean_x(train_x)
    y = _clean_y(train_y)
    xt = _clean_x(test_x)
    n = x.shape[0]

    alpha_fractions = np.array([
        1e-5, 1e-4, 1e-3, 3e-3, 1e-2,
        3e-2, 1e-1, 3e-1, 1.0, 3.0
    ], dtype=np.float64)
    candidates = [(kind, window) for kind in range(3)
                  for window in (1.0, 0.5)]

    folds = [
        (int(0.48 * n), int(0.52 * n), int(0.70 * n)),
        (int(0.70 * n), int(0.74 * n), n),
    ]
    errors = np.zeros((len(candidates), len(alpha_fractions), 2),
                      dtype=np.float64)

    for ci, (kind, window) in enumerate(candidates):
        for train_end, val_start, val_end in folds:
            used = max(256, int(round(train_end * window)))
            train_start = max(0, train_end - used)
            xfit = x[train_start:train_end]
            yfit = y[train_start:train_end]
            xval = x[val_start:val_end]
            yval = y[val_start:val_end]

            zfit, state = _fit_preprocessor(xfit, kind)
            zval = _apply_preprocessor(xval, state)
            ymean, path = _ridge_path(zfit, yfit, alpha_fractions)
            lo, hi = _output_bounds(yfit)

            for ai, weight in enumerate(path):
                pred = zval @ weight + ymean
                pred = np.clip(pred, lo, hi)
                residual = yval - pred
                errors[ci, ai] += np.sum(residual * residual, axis=0)

    best_alpha_by_candidate = np.argmin(errors, axis=1)
    candidate_scores = np.empty(len(candidates), dtype=np.float64)
    for ci in range(len(candidates)):
        candidate_scores[ci] = sum(
            errors[ci, best_alpha_by_candidate[ci, j], j]
            for j in range(2)
        )
    best_ci = int(np.argmin(candidate_scores))
    kind, window = candidates[best_ci]
    chosen_alpha = best_alpha_by_candidate[best_ci]

    used = max(256, int(round(n * window)))
    start = max(0, n - used)
    xfit = x[start:]
    yfit = y[start:]
    zfit, state = _fit_preprocessor(xfit, kind)
    ztest = _apply_preprocessor(xt, state)
    ymean, path = _ridge_path(zfit, yfit, alpha_fractions)

    pred = np.empty((xt.shape[0], 2), dtype=np.float64)
    for j in range(2):
        weight = path[int(chosen_alpha[j])][:, j]
        pred[:, j] = ztest @ weight + ymean[j]

    lo, hi = _output_bounds(yfit)
    pred = np.clip(pred, lo, hi)
    pred = np.nan_to_num(pred, nan=0.0, posinf=hi, neginf=lo)
    return pred
