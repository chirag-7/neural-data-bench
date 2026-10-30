import numpy as np
from scipy.ndimage import gaussian_filter1d, uniform_filter1d
from sklearn.ensemble import HistGradientBoostingRegressor


def _shift(a, lag):
    return a[np.clip(np.arange(a.size) + lag, 0, a.size - 1)]


def _features(x):
    n = x.size
    good = np.isfinite(x)
    if not good.all():
        if good.any():
            x = np.interp(np.arange(n), np.flatnonzero(good), x[good])
        else:
            x = np.zeros(n)
    baseline = uniform_filter1d(x, size=1001, mode='nearest')
    h = x - baseline
    q10, q99 = np.percentile(h, [10, 99])
    noise = np.median(np.abs(np.diff(x))) / 0.954 if n > 1 else 0.0
    scale = max(q99 - q10, 4.0 * noise, 1e-8)
    h = h / scale
    g1 = gaussian_filter1d(h, 1.0, mode='nearest')
    g4 = gaussian_filter1d(h, 4.0, mode='nearest')
    g12 = gaussian_filter1d(h, 12.0, mode='nearest')
    g30 = gaussian_filter1d(h, 30.0, mode='nearest')
    f = []
    for lag in (-8, -4, -2, 0, 2, 4, 8, 12, 20, 30):
        f.append(_shift(g1, lag))
    for lag in (-12, -6, 0, 6, 12, 20, 32):
        f.append(_shift(g4, lag))
    for lag in (-24, -12, 0, 12, 24, 40):
        f.append(_shift(g12, lag))
    f.append(g30)
    rise = g1 - 0.98 * _shift(g1, -1)
    for lag in (-4, 0, 4, 8, 12, 20):
        f.append(_shift(rise, lag))
    f.extend((g4 - _shift(g4, -4), _shift(g4, 4) - g4,
              g12 - _shift(g12, -12), _shift(g12, 12) - g12,
              g1 - g12, g4 - g30))
    return np.clip(np.column_stack(f), -10.0, 10.0).astype(np.float32)


def fit_predict(train_calcium, train_spikes, test_calcium):
    rng = np.random.default_rng(2026)
    blocks_x, blocks_y = [], []
    for j in range(train_calcium.shape[1]):
        valid = np.isfinite(train_calcium[:, j]) & np.isfinite(train_spikes[:, j])
        indices = np.flatnonzero(valid)
        if indices.size < 100:
            continue
        end = indices[-1] + 1
        features = _features(train_calcium[:end, j])
        spikes = np.where(np.isfinite(train_spikes[:end, j]),
                          np.maximum(train_spikes[:end, j], 0.0), 0.0)
        positive = spikes[spikes > 0]
        if positive.size:
            spikes = spikes / max(np.median(positive), 1e-8)
        target = gaussian_filter1d(np.clip(spikes, 0.0, 10.0), 1.5,
                                   mode='constant')
        count = min(22000, indices.size)
        chosen = rng.choice(indices, size=count, replace=False)
        blocks_x.append(features[chosen])
        blocks_y.append(target[chosen].astype(np.float32))
    result = np.full(test_calcium.shape, np.nan, dtype=np.float64)
    if not blocks_x:
        result[np.isfinite(test_calcium)] = 0.0
        return result
    X = np.concatenate(blocks_x)
    y = np.concatenate(blocks_y)
    if not np.any(y > 0):
        result[np.isfinite(test_calcium)] = 0.0
        return result
    model = HistGradientBoostingRegressor(
        loss='poisson', max_iter=150, learning_rate=0.07,
        max_leaf_nodes=15, min_samples_leaf=80,
        l2_regularization=2.0, max_bins=128,
        early_stopping=True, validation_fraction=0.12,
        n_iter_no_change=12, random_state=2026)
    model.fit(X, y)
    for j in range(test_calcium.shape[1]):
        finite = np.isfinite(test_calcium[:, j])
        if not finite.any():
            continue
        end = np.flatnonzero(finite)[-1] + 1
        features = _features(test_calcium[:end, j])
        prediction = model.predict(features)
        prediction = np.clip(np.nan_to_num(prediction, nan=0.0,
                                            posinf=1e6, neginf=0.0), 0.0, 1e6)
        result[:end, j][finite[:end]] = prediction[finite[:end]]
    return result