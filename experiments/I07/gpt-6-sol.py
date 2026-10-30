import numpy as np
from sklearn.linear_model import Ridge


def _temporal(z):
    mean = z.mean(axis=-1)
    change = z[..., 4:].mean(axis=-1) - z[..., :4].mean(axis=-1)
    return np.stack((mean, 0.7 * change), axis=-1)


def _features(z):
    t = _temporal(z)
    left, right = t[:, :34], t[:, 34:]
    lateral = right - left
    common = 0.5 * (right + left)

    def parts(a):
        detailed = a.reshape(len(a), -1)
        aggregate = np.concatenate(
            (a.mean(axis=1).reshape(len(a), -1),
             np.median(a, axis=1).reshape(len(a), -1)), axis=1
        )
        return detailed, aggregate

    ld, la = parts(lateral)
    cd, ca = parts(common)
    return ld, cd, la, ca


def _scaled(train, test):
    center = np.median(train, axis=0)
    spread = np.std(train, axis=0)
    positive = spread[spread > 0]
    floor = 0.5 * np.median(positive) if len(positive) else 1.0
    spread = np.maximum(spread, max(floor, 1e-12))
    a = np.clip((train - center) / spread, -6.0, 6.0)
    b = np.clip((test - center) / spread, -6.0, 6.0)
    return a, b


def fit_predict(train_x, train_y, test_x):
    train = np.nan_to_num(np.asarray(train_x, dtype=np.float64),
                          nan=0.0, posinf=0.0, neginf=0.0)
    test = np.nan_to_num(np.asarray(test_x, dtype=np.float64),
                         nan=0.0, posinf=0.0, neginf=0.0)
    y = np.asarray(train_y).reshape(-1).astype(int)
    n = len(y)
    if len(test) == 0:
        return np.empty(0, dtype=np.int64)
    if np.unique(y).size == 1:
        return np.full(len(test), y[0], dtype=np.int64)

    train = train.reshape(n, 68, 2, 8)
    test = test.reshape(len(test), 68, 2, 8)
    cap = np.quantile(np.abs(train), 0.995, axis=(0, 1, 3))
    cap = np.maximum(cap, 1e-8).reshape(1, 1, 2, 1)
    train = np.clip(train, -cap, cap)
    test = np.clip(test, -cap, cap)

    amplitude = np.median(np.abs(train), axis=(1, 2, 3))
    reference = max(float(np.median(amplitude)), 1e-12)
    counts = np.bincount(y, minlength=2)
    weights = np.where(y == 0, n / (2.0 * counts[0]),
                       n / (2.0 * counts[1]))
    target = 2.0 * y - 1.0
    score = np.zeros(len(test), dtype=np.float64)

    for normalized, norm_weight in ((False, 0.6), (True, 0.4)):
        if normalized:
            train_gain = np.clip(amplitude / reference, 0.5, 3.0)
            test_amplitude = np.median(np.abs(test), axis=(1, 2, 3))
            test_gain = np.clip(test_amplitude / reference, 0.5, 3.0)
            tr = train / train_gain[:, None, None, None]
            te = test / test_gain[:, None, None, None]
        else:
            tr, te = train, test

        train_parts = _features(tr)
        test_parts = _features(te)
        scaled = [_scaled(a, b) for a, b in zip(train_parts, test_parts)]

        for indices, multipliers, map_weight in (
            ((0, 2), (1.0, 2.0), 0.55),
            ((0, 1, 2, 3), (1.0, 0.7, 2.0, 1.4), 0.45),
        ):
            a = np.concatenate([scaled[i][0] * m
                                for i, m in zip(indices, multipliers)], axis=1)
            b = np.concatenate([scaled[i][1] * m
                                for i, m in zip(indices, multipliers)], axis=1)
            divisor = np.sqrt(a.shape[1])
            a /= divisor
            b /= divisor
            for alpha, alpha_weight in ((3.0, 0.7), (15.0, 0.3)):
                model = Ridge(alpha=alpha, fit_intercept=True)
                model.fit(a, target, sample_weight=weights)
                score += norm_weight * map_weight * alpha_weight * model.predict(b)

    return (score > 0.0).astype(np.int64)
