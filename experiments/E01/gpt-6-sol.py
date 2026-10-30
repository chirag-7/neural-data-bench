import numpy as np
from scipy.ndimage import gaussian_filter1d


def _features(x):
    x = np.nan_to_num(np.asarray(x, dtype=np.float64), nan=0.0,
                      posinf=0.0, neginf=0.0)
    n, t, _ = x.shape
    sm = {0.0: x}
    for s in (1.2, 2.5, 4.5):
        sm[s] = gaussian_filter1d(x, s, axis=1, mode='reflect')
    centers = np.linspace(0, t - 1, 8)
    basis = np.exp(-0.5 * ((np.arange(t)[:, None] - centers) / 3.5) ** 2)
    basis = np.broadcast_to(basis[None, :, :], (n, t, 8))
    designs = ((1.2,), (2.5,), (4.5,), (0.0, 2.5), (1.2, 4.5))
    return [np.concatenate([sm[s] for s in scales] + [basis], axis=2)
            .reshape(n * t, -1) for scales in designs]


def _decomp(x, y, z):
    xm = x.mean(axis=0)
    xs = np.maximum(x.std(axis=0), 1e-5)
    a = (x - xm) / xs
    b = (z - xm) / xs
    ym = y.mean(axis=0)
    eig, vec = np.linalg.eigh(a.T @ a)
    eig = np.maximum(eig, 0.0)
    q = b @ vec
    r = vec.T @ (a.T @ (y - ym))
    return q, r, eig, ym


def _raw(parts, alpha):
    q, r, eig, ym = parts
    return q @ (r / (eig[:, None] + alpha)) + ym


def _rates(raw, mean, mode):
    m = np.maximum(mean, 1e-4)
    if mode < 3:
        p = np.maximum(raw, (0.03, 0.12, 0.30)[mode] * m)
    else:
        u = np.clip(2.0 * raw / m - 1.0, -30.0, 30.0)
        p = m * np.logaddexp(0.0, u) / np.logaddexp(0.0, 1.0)
    p = np.nan_to_num(p, nan=1e-5, posinf=20.0, neginf=1e-5)
    return np.clip(p, 1e-5, 20.0)


def fit_predict(train_x, train_y, test_x):
    n, t, _ = train_x.shape
    y = np.maximum(np.nan_to_num(np.asarray(train_y, dtype=np.float64),
                                  nan=0.0, posinf=0.0, neginf=0.0), 0.0)
    y = y.reshape(n * t, -1)
    train_features = _features(train_x)
    test_features = _features(test_x)
    alphas = (20.0, 80.0, 320.0, 1280.0)
    scores = np.zeros((len(train_features), len(alphas), 4))
    rng = np.random.RandomState(2026)
    trials = rng.permutation(n)
    for held in np.array_split(trials, 3):
        keep = np.ones(n, dtype=bool)
        keep[held] = False
        tr = np.flatnonzero(np.repeat(keep, t))
        va = np.flatnonzero(np.repeat(~keep, t))
        ytr, yva = y[tr], y[va]
        for d, x in enumerate(train_features):
            parts = _decomp(x[tr], ytr, x[va])
            for ai, alpha in enumerate(alphas):
                raw = _raw(parts, alpha)
                for mode in range(4):
                    p = _rates(raw, parts[3], mode)
                    scores[d, ai, mode] += np.sum(yva * np.log(p) - p)
    best = scores.reshape(len(train_features), -1).max(axis=1)
    chosen = np.argsort(best)[-2:][::-1]
    predictions = []
    for d in chosen:
        ai, mode = np.unravel_index(np.argmax(scores[d]), scores[d].shape)
        parts = _decomp(train_features[d], y, test_features[d])
        predictions.append(_rates(_raw(parts, alphas[ai]), parts[3], mode))
    gap = max(0.0, best[chosen[0]] - best[chosen[1]])
    second_weight = 0.4 * np.exp(-gap / (0.01 * y.sum() + 1.0))
    result = ((1.0 - second_weight) * predictions[0]
              + second_weight * predictions[1])
    return result.reshape(test_x.shape[0], t, train_y.shape[2])