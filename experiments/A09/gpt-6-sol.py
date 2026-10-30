import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier


def _features(x):
    x = np.nan_to_num(np.asarray(x, dtype=np.float32), nan=0.0, posinf=0.0, neginf=0.0)
    p = x.reshape(-1, 7, 2, 2, 7).transpose(0, 1, 2, 4, 3)
    out = []

    def length(v):
        return np.sqrt(np.sum(v * v, axis=-1))

    def dot(a, b):
        return np.sum(a * b, axis=-1)

    def add(v, full=True, dynamic=False):
        indices = (0, 1, 2, 3, 4, 5, 6) if full else (2, 3, 4)
        for i in indices:
            out.append(v[:, i])
        if dynamic:
            out.append(v[:, 4] - v[:, 2])
            out.append(v[:, 5] - v[:, 1])
            out.append(v[:, 6] - v[:, 0])
            out.append(np.std(v[:, 2:5], axis=1))

    nose = p[:, :, :, 0, :]
    neck = p[:, :, :, 3, :]
    hips = 0.5 * (p[:, :, :, 4, :] + p[:, :, :, 5, :])
    tail = p[:, :, :, 6, :]
    center = 0.5 * (neck + hips)
    axis = nose - tail
    unit = axis / (length(axis)[..., None] + 1e-3)

    for m in (0, 1):
        add(length(nose[:, :, m] - tail[:, :, m]), full=False)
        add(length(neck[:, :, m] - hips[:, :, m]), full=False)
        add(length(p[:, :, m, 1] - p[:, :, m, 2]), full=False)
        add(length(p[:, :, m, 4] - p[:, :, m, 5]), full=False)
        add(length(nose[:, :, m] - neck[:, :, m]), full=False)
        add(length(tail[:, :, m] - hips[:, :, m]), full=False)
        add(dot(nose[:, :, m] - neck[:, :, m], unit[:, :, m]), full=False)
        add(unit[:, :, m, 0])
        add(unit[:, :, m, 1])
        out.extend((center[:, 3, m, 0], center[:, 3, m, 1]))

    c0, c1 = center[:, :, 0], center[:, :, 1]
    u0, u1 = unit[:, :, 0], unit[:, :, 1]
    delta = c1 - c0
    add(delta[..., 0], dynamic=True)
    add(delta[..., 1], dynamic=True)
    add(length(delta), dynamic=True)
    add(length(nose[:, :, 0] - nose[:, :, 1]), dynamic=True)
    add(length(neck[:, :, 0] - neck[:, :, 1]))
    add(length(tail[:, :, 0] - tail[:, :, 1]))

    for a, b in ((0, 3), (0, 6), (0, 4), (0, 5)):
        add(length(p[:, :, 0, a] - p[:, :, 1, b]), dynamic=(a == 0 and b == 3))
        add(length(p[:, :, 1, a] - p[:, :, 0, b]), dynamic=(a == 0 and b == 3))

    for m in (0, 1):
        other = 1 - m
        rel = nose[:, :, other] - center[:, :, m]
        u = unit[:, :, m]
        add(length(rel), dynamic=True)
        add(dot(rel, u), dynamic=True)
        add(u[..., 0] * rel[..., 1] - u[..., 1] * rel[..., 0], dynamic=True)

    add(dot(u0, u1))
    add(u0[..., 0] * u1[..., 1] - u0[..., 1] * u1[..., 0])

    intervals = ((0, 1, 10.0), (1, 2, 4.0), (2, 3, 1.0),
                 (3, 4, 1.0), (4, 5, 4.0), (5, 6, 10.0))
    for m in (0, 1):
        for points in (center[:, :, m], nose[:, :, m], tail[:, :, m]):
            for a, b, gap in intervals:
                velocity = (points[:, b] - points[:, a]) / gap
                out.append(length(velocity))
                if points is center[:, :, m] and False:
                    pass
        for a, b in ((2, 3), (3, 4)):
            velocity = center[:, b, m] - center[:, a, m]
            out.extend((velocity[:, 0], velocity[:, 1]))

    for a, b, gap in intervals:
        relative_velocity = (delta[:, b] - delta[:, a]) / gap
        out.extend((relative_velocity[:, 0], relative_velocity[:, 1], length(relative_velocity)))

    return np.nan_to_num(np.column_stack(out).astype(np.float32),
                         nan=0.0, posinf=0.0, neginf=0.0)


def fit_predict(train_x, train_y, test_x):
    y = np.asarray(train_y, dtype=np.int64).reshape(-1)
    if np.unique(y).size == 1:
        return np.full(len(test_x), y[0], dtype=np.int64)
    train_features = _features(train_x)
    test_features = _features(test_x)
    counts = np.bincount(y, minlength=4)
    class_weights = (counts.max() / np.maximum(counts, 1)) ** 0.4
    sample_weights = class_weights[y]
    sample_weights = sample_weights / sample_weights.mean()
    model = HistGradientBoostingClassifier(
        max_iter=110, learning_rate=0.09, max_leaf_nodes=31,
        min_samples_leaf=30, max_bins=127, l2_regularization=3.0,
        early_stopping=False, random_state=31
    )
    model.fit(train_features, y, sample_weight=sample_weights)
    return model.predict(test_features).astype(np.int64)
