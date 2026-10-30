import numpy as np


def _features(x):
    x = np.maximum(x, 0.0)
    return np.concatenate((x, np.sqrt(x), np.log1p(4.0 * x)), axis=1)


def _standardize(train, other):
    mean = train.mean(axis=0)
    scale = train.std(axis=0)
    scale = np.where(scale > 1e-8, scale, 1.0)
    return (train - mean) / scale, (other - mean) / scale


def _ridge_system(z, y):
    y_mean = y.mean(axis=0)
    centered_y = y - y_mean
    n = len(y)
    gram = (z.T @ z) / n
    cross = (z.T @ centered_y) / n
    return gram, cross, y_mean


def _coefficients(gram, cross, alpha):
    values, vectors = np.linalg.eigh(gram)
    values = np.maximum(values, 0.0)
    return vectors @ ((vectors.T @ cross) / (values[:, None] + alpha))


def fit_predict(train_x, train_y, test_x):
    x = np.asarray(train_x, dtype=np.float64)
    t = np.asarray(test_x, dtype=np.float64)
    y = np.asarray(train_y, dtype=np.float64)

    if not np.isfinite(x).all() or not np.isfinite(t).all():
        finite_x = np.where(np.isfinite(x), x, np.nan)
        med = np.nanmedian(finite_x, axis=0)
        med = np.where(np.isfinite(med), med, 0.0)
        x = np.where(np.isfinite(x), x, med)
        t = np.where(np.isfinite(t), t, med)

    x = _features(x)
    t = _features(t)
    groups = [np.arange(96), np.arange(96, 192),
              np.arange(192), np.arange(288)]
    alphas = (0.003, 0.03, 0.3, 3.0, 30.0)
    scores = np.zeros((len(groups), len(alphas), 2), dtype=np.float64)
    n = len(y)
    cuts = (int(0.50 * n), int(0.75 * n))

    for split, end in enumerate(cuts):
        val_end = cuts[1] if split == 0 else n
        val_start = min(end + 12, val_end)
        z_train, z_val = _standardize(x[:end], x[val_start:val_end])
        y_train = y[:end]
        y_val = y[val_start:val_end]
        gram, cross, y_mean = _ridge_system(z_train, y_train)
        limits = np.quantile(y_train, (0.001, 0.999), axis=0)
        total = np.sum((y_val - y_val.mean(axis=0)) ** 2)
        weight = 0.7 if split == 0 else 0.3

        for gi, cols in enumerate(groups):
            values, vectors = np.linalg.eigh(gram[np.ix_(cols, cols)])
            values = np.maximum(values, 0.0)
            projected = vectors.T @ cross[cols]
            val_features = z_val[:, cols]
            for ai, alpha in enumerate(alphas):
                coef = vectors @ (projected / (values[:, None] + alpha))
                pred = val_features @ coef + y_mean
                plain = np.sum((y_val - pred) ** 2)
                clipped = np.sum((y_val - np.clip(pred, limits[0], limits[1])) ** 2)
                scores[gi, ai, 0] += weight * (1.0 - plain / total)
                scores[gi, ai, 1] += weight * (1.0 - clipped / total)

    gi, ai, use_clip = np.unravel_index(np.argmax(scores), scores.shape)
    cols = groups[gi]
    z_train, z_test = _standardize(x[:, cols], t[:, cols])
    gram, cross, y_mean = _ridge_system(z_train, y)
    coef = _coefficients(gram, cross, alphas[ai])
    pred = z_test @ coef + y_mean
    if use_clip:
        limits = np.quantile(y, (0.001, 0.999), axis=0)
        pred = np.clip(pred, limits[0], limits[1])
    return np.nan_to_num(pred, nan=0.0, posinf=0.0, neginf=0.0)
