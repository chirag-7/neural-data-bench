import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
import gc

_OFFSETS = np.array([-15, -5, -1, 0, 1, 5, 15], dtype=np.float32)
_CROSS = ([(0, j) for j in range(7)] +
          [(i, 0) for i in range(1, 7)] +
          [(3, 3), (3, 6), (6, 3), (6, 6),
           (4, 4), (4, 5), (5, 4), (5, 5)])
_WITHIN = [(0, 3), (1, 2), (3, 6), (4, 5)]


def _norm(a):
    return np.sqrt(np.sum(a * a, axis=-1))


def _pose(x):
    return np.asarray(x, dtype=np.float32).reshape(
        -1, 7, 2, 2, 7).transpose(0, 1, 2, 4, 3).copy()


def _features(x, median, scale):
    p = _pose(x)
    np.copyto(p, np.broadcast_to(median, p.shape), where=~np.isfinite(p))
    p /= scale
    n = len(p)
    parts = []

    def add(a):
        parts.append(np.asarray(a, dtype=np.float32).reshape(n, -1))

    ia = [a for a, b in _CROSS]
    ib = [b for a, b in _CROSS]
    distances = _norm(p[:, :, 0, ia, :] - p[:, :, 1, ib, :])
    add(distances)
    wa = [a for a, b in _WITHIN]
    wb = [b for a, b in _WITHIN]
    add(_norm(p[:, :, :, wa, :] - p[:, :, :, wb, :]))

    centers = p[:, :, :, [3, 4, 5, 6], :].mean(axis=3)
    heading = p[:, :, :, 3, :] - p[:, :, :, 6, :]
    lengths = _norm(heading)
    unit = heading / np.maximum(lengths[..., None], 0.05)
    r = centers[:, :, 1, :] - centers[:, :, 0, :]
    separation = _norm(r)
    f0 = np.sum(r * unit[:, :, 0, :], axis=-1)
    f1 = np.sum(-r * unit[:, :, 1, :], axis=-1)
    s0 = np.abs(r[..., 0] * unit[:, :, 0, 1] -
                r[..., 1] * unit[:, :, 0, 0])
    s1 = np.abs(r[..., 0] * unit[:, :, 1, 1] -
                r[..., 1] * unit[:, :, 1, 0])
    alignment = np.sum(unit[:, :, 0, :] * unit[:, :, 1, :], axis=-1)
    crossing = np.abs(unit[:, :, 0, 0] * unit[:, :, 1, 1] -
                      unit[:, :, 0, 1] * unit[:, :, 1, 0])
    add(np.stack([separation, lengths[:, :, 0], lengths[:, :, 1],
                  alignment, crossing, f0, f1, s0, s1,
                  f0 / np.maximum(separation, 0.05),
                  f1 / np.maximum(separation, 0.05)], axis=-1))

    remaining = [(i, j) for i in range(7) for j in range(7)
                 if (i, j) not in _CROSS]
    a, b = zip(*remaining)
    add(_norm(p[:, 3, 0, list(a), :] - p[:, 3, 1, list(b), :]))
    remaining = [(i, j) for i in range(7) for j in range(i + 1, 7)
                 if (i, j) not in _WITHIN]
    a, b = zip(*remaining)
    add(_norm(p[:, 3, :, list(a), :] - p[:, 3, :, list(b), :]))
    add(distances.mean(axis=1))
    add(distances.min(axis=1))
    add(distances.std(axis=1))
    nearest0 = distances[:, :, :7].min(axis=2)
    nearest1 = distances[:, :, [0, 7, 8, 9, 10, 11, 12]].min(axis=2)
    add(np.minimum(nearest0, nearest1))

    dt = np.diff(_OFFSETS) / 30.0
    moving = p[:, :, :, [0, 3, 6], :]
    velocity = np.diff(moving, axis=1) / dt[None, :, None, None, None]
    add(_norm(velocity))
    velocity = np.diff(centers, axis=1) / dt[None, :, None, None]
    direction = unit[:, 1:] + unit[:, :-1]
    direction /= np.maximum(_norm(direction)[..., None], 0.05)
    add(np.sum(velocity * direction, axis=-1))
    add(np.abs(velocity[..., 0] * direction[..., 1] -
               velocity[..., 1] * direction[..., 0]))
    add(np.sum(unit[:, 1:] * unit[:, :-1], axis=-1))
    chosen = [_CROSS.index(pair) for pair in
              [(0, 0), (0, 3), (0, 6), (3, 0), (6, 0), (6, 6)]]
    relational = np.concatenate([distances[:, :, chosen],
                                 separation[..., None]], axis=2)
    for left, right in [(2, 4), (1, 5), (0, 6)]:
        elapsed = (_OFFSETS[right] - _OFFSETS[left]) / 30.0
        add((relational[:, right] - relational[:, left]) / elapsed)
    result = np.concatenate(parts, axis=1)
    np.nan_to_num(result, copy=False, nan=0.0, posinf=100.0, neginf=-100.0)
    np.clip(result, -100.0, 100.0, out=result)
    return result


def _model(iterations):
    return HistGradientBoostingClassifier(
        learning_rate=0.085, max_iter=iterations, max_leaf_nodes=23,
        max_depth=None, min_samples_leaf=30, l2_regularization=3.0,
        max_bins=63, early_stopping=False, random_state=371)


def _probabilities(model, x):
    p = np.zeros((len(x), 4), dtype=np.float32)
    p[:, model.classes_.astype(int)] = model.predict_proba(x)
    return p


def _calibrate(probabilities, y):
    counts = np.bincount(y, minlength=4)
    supported = counts > 0

    def score(weights):
        pred = np.argmax(probabilities * weights[None, :], axis=1)
        matrix = np.bincount(4 * y + pred, minlength=16).reshape(4, 4)
        denominator = matrix.sum(axis=0) + matrix.sum(axis=1)
        f1 = 2.0 * np.diag(matrix) / np.maximum(denominator, 1)
        return float(f1[supported].mean())

    weights = np.ones(4, dtype=np.float64)
    best = score(weights)
    for step in [0.45, 0.22, 0.10]:
        for c in [2, 0, 1, 3]:
            if counts[c] < 20:
                continue
            selected = weights.copy()
            for shift in [-2, -1, 1, 2]:
                candidate = weights.copy()
                candidate[c] = np.clip(candidate[c] * np.exp(step * shift),
                                       0.35, 3.0)
                value = score(candidate)
                if value > best + 1e-6:
                    best = value
                    selected = candidate
            weights = selected
    return weights ** 0.75


def fit_predict(train_x, train_y, test_x):
    y = np.asarray(train_y, dtype=np.int64).reshape(-1)
    n = len(y)
    if len(np.unique(y)) == 1:
        return np.full(len(test_x), y[0], dtype=np.int64)
    sample = _pose(train_x[::max(1, n // 4000)])
    sample[~np.isfinite(sample)] = np.nan
    median = np.nanmedian(sample, axis=(0, 1), keepdims=True)
    median = np.nan_to_num(median, nan=0.0)
    np.copyto(sample, np.broadcast_to(median, sample.shape),
              where=~np.isfinite(sample))
    scale = float(np.median(_norm(sample[:, 3, :, 3, :] -
                                  sample[:, 3, :, 6, :])))
    scale = max(scale, 1.0)
    del sample
    features = _features(train_x, median, scale)
    validation = np.zeros(n, dtype=bool)
    excluded = np.zeros(n, dtype=bool)
    if n >= 1000:
        width = max(1, int(n * 0.04))
        for fraction in [0.16, 0.40, 0.64, 0.88]:
            start = int(n * fraction)
            end = min(start + width, n)
            validation[start:end] = True
            excluded[max(0, start - 30):min(n, end + 30)] = True
    fitting = ~excluded
    counts = np.bincount(y[fitting], minlength=4)
    class_weights = np.clip(
        (fitting.sum() / (4.0 * np.maximum(counts, 1))) ** 0.5, 0.5, 4.0)
    adjustment = np.ones(4, dtype=np.float64)
    if validation.any() and np.unique(y[fitting]).size == np.unique(y).size:
        probe = _model(110)
        probe.fit(features[fitting], y[fitting],
                  sample_weight=class_weights[y[fitting]])
        adjustment = _calibrate(_probabilities(probe, features[validation]),
                                y[validation])
        del probe
        gc.collect()
    model = _model(180)
    model.fit(features, y, sample_weight=class_weights[y])
    del features
    gc.collect()
    if len(test_x) == 0:
        return np.empty(0, dtype=np.int64)
    test_features = _features(test_x, median, scale)
    probabilities = _probabilities(model, test_features)
    return np.argmax(probabilities * adjustment[None, :], axis=1).astype(np.int64)
