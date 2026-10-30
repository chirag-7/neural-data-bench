import numpy as np
from scipy.ndimage import (gaussian_filter1d, uniform_filter1d,
                           minimum_filter1d, maximum_filter1d)
from sklearn.ensemble import HistGradientBoostingRegressor


def _shift(x, k):
    return x[np.clip(np.arange(len(x)) + k, 0, len(x) - 1)]


def _features(a):
    a = np.asarray(a, dtype=np.float64)
    good = np.flatnonzero(np.isfinite(a))
    x = np.interp(np.arange(len(a)), good, a[good])
    dx = np.diff(x)
    noise = np.median(np.abs(dx - np.median(dx))) / 0.953872 if len(dx) else 0.0
    noise = max(noise, np.std(x) * 1e-4, 1e-12)
    centered = x - uniform_filter1d(x, size=501, mode='nearest')
    scale = max(np.percentile(centered, 95) - np.percentile(centered, 5),
                4.0 * noise, 1e-12)
    x = (x - np.median(x)) / scale
    h = x - uniform_filter1d(x, size=501, mode='nearest')
    snr = min(scale / noise, 100.0)
    cols = []
    for sigma in (1.0, 2.0, 4.0, 8.0, 16.0, 32.0):
        s = gaussian_filter1d(h, sigma)
        d = gaussian_filter1d(h, sigma, order=1)
        dd = gaussian_filter1d(h, sigma, order=2)
        cols.extend((s, d, dd, d * snr))
    p = gaussian_filter1d(x, 1.5)
    d = gaussian_filter1d(x, 1.5, order=1)
    for k in (-8, -4, -2, 2, 4, 8, 16, 24):
        cols.append(_shift(d, k))
    for k in (-32, -16, -8, -4, 4, 8, 16, 32):
        cols.append(_shift(p, k) - p)
    for width in (9, 33, 101):
        cols.append(p - minimum_filter1d(p, size=width, mode='nearest'))
        cols.append(maximum_filter1d(p, size=width, mode='nearest') - p)
    floor = minimum_filter1d(gaussian_filter1d(x, 3.0), size=401,
                             mode='nearest')
    floor = gaussian_filter1d(floor, 16.0)
    level = np.maximum(p - floor, 0.0)
    cols.append(level)
    for tau in (10.0, 30.0, 80.0):
        innovation = np.maximum(d + level / tau - 0.2 * noise / scale, 0.0)
        innovation = gaussian_filter1d(innovation, 1.0)
        for k in (0, 4, 8):
            cols.append(_shift(innovation, k))
    result = np.column_stack(cols).astype(np.float32)
    return np.nan_to_num(result, nan=0.0, posinf=1e6, neginf=-1e6)


def _corr40(pred, truth, valid):
    n = (len(pred) // 4) * 4
    if n < 8:
        return 0.0
    keep = valid[:n].reshape(-1, 4).all(axis=1)
    a = pred[:n].reshape(-1, 4).sum(axis=1)[keep]
    b = np.where(valid[:n], truth[:n], 0.0).reshape(-1, 4).sum(axis=1)[keep]
    if len(a) < 2:
        return 0.0
    a = a - a.mean()
    b = b - b.mean()
    den = np.sqrt(np.dot(a, a) * np.dot(b, b))
    return float(np.dot(a, b) / den) if den > 1e-15 else 0.0


def _sample(records, ids, budget):
    rng = np.random.RandomState(731)
    xs, ys = [], []
    limit = max(1, budget // len(ids))
    for i in ids:
        features, target, truth, valid = records[i]
        idx = np.flatnonzero(valid)
        if len(idx) > limit:
            idx = rng.choice(idx, limit, replace=False)
        xs.append(features[idx])
        ys.append(target[idx])
    return np.concatenate(xs), np.concatenate(ys)


def _model(iterations):
    return HistGradientBoostingRegressor(
        loss='squared_error', learning_rate=0.07, max_iter=iterations,
        max_leaf_nodes=15, max_depth=5, min_samples_leaf=60,
        l2_regularization=20.0, max_bins=127, early_stopping=False,
        random_state=731)


def fit_predict(train_calcium, train_spikes, test_calcium):
    train_calcium = np.asarray(train_calcium, dtype=np.float64)
    train_spikes = np.asarray(train_spikes, dtype=np.float64)
    test_calcium = np.asarray(test_calcium, dtype=np.float64)
    records = []
    for j in range(train_calcium.shape[1]):
        good = np.flatnonzero(np.isfinite(train_calcium[:, j]))
        if not len(good):
            continue
        n = good[-1] + 1
        ca = train_calcium[:n, j]
        truth = train_spikes[:n, j].copy()
        valid = np.isfinite(ca) & np.isfinite(truth)
        if valid.sum() < 32:
            continue
        target = gaussian_filter1d(np.where(valid, np.maximum(truth, 0.0), 0.0), 1.0)
        support = gaussian_filter1d(valid.astype(np.float64), 1.0)
        target /= np.maximum(support, 1e-8)
        target /= max(np.std(target[valid]), 1e-8)
        records.append((_features(ca), target, truth, valid))
    output = np.full(test_calcium.shape, np.nan, dtype=np.float64)
    if not records:
        output[np.isfinite(test_calcium)] = 0.0
        return output
    iterations, smoothing = 160, 1.0
    ids = list(range(len(records)))
    if len(records) >= 3:
        count = min(3, max(1, len(records) // 3))
        held = np.linspace(0, len(records) - 1, count, dtype=int).tolist()
        fitting = [i for i in ids if i not in held]
        xx, yy = _sample(records, fitting, 180000)
        estimator = _model(160).fit(xx, yy)
        vx = np.concatenate([records[i][0] for i in held])
        best = -np.inf
        for stage, prediction in enumerate(estimator.staged_predict(vx), 1):
            if stage not in (60, 110, 160):
                continue
            for sigma in (0.0, 1.0, 2.0, 3.0):
                scores, offset = [], 0
                for i in held:
                    features, target, truth, valid = records[i]
                    n = len(truth)
                    p = np.maximum(prediction[offset:offset + n], 0.0)
                    offset += n
                    if sigma:
                        p = gaussian_filter1d(p, sigma)
                    scores.append(_corr40(p, truth, valid))
                score = 0.5 * (np.mean(scores) + np.median(scores))
                if score > best:
                    best, iterations, smoothing = score, stage, sigma
        del estimator, vx, xx, yy
    xx, yy = _sample(records, ids, 240000)
    estimator = _model(iterations).fit(xx, yy)
    del records, xx, yy
    for j in range(test_calcium.shape[1]):
        good = np.flatnonzero(np.isfinite(test_calcium[:, j]))
        if not len(good):
            continue
        n = good[-1] + 1
        p = np.maximum(estimator.predict(_features(test_calcium[:n, j])), 0.0)
        if smoothing:
            p = gaussian_filter1d(p, smoothing)
        p = np.nan_to_num(p, nan=0.0, posinf=0.0, neginf=0.0)
        output[good, j] = np.maximum(p[good], 0.0)
    return output
