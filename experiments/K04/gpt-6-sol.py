import numpy as np
from sklearn.feature_selection import f_classif
from sklearn.preprocessing import StandardScaler
from sklearn.kernel_approximation import Nystroem
from sklearn.metrics import f1_score


def _prepare(x_fit, y_fit, x_other):
    scores, _ = f_classif(x_fit, y_fit)
    scores = np.nan_to_num(scores, nan=-1.0, posinf=1e12, neginf=-1.0)
    chosen = np.argsort(scores)[-160:]
    scaler = StandardScaler().fit(x_fit[:, chosen])
    a = np.clip(scaler.transform(x_fit[:, chosen]), -4, 4).astype(np.float32)
    b = np.clip(scaler.transform(x_other[:, chosen]), -4, 4).astype(np.float32)
    return a, b


def _median_distance(x):
    rng = np.random.default_rng(29)
    sample = x[rng.choice(len(x), min(256, len(x)), replace=False)]
    sq = np.sum(sample * sample, axis=1)
    dist = sq[:, None] + sq[None, :] - 2 * (sample @ sample.T)
    values = dist[np.triu_indices(len(sample), 1)]
    return max(float(np.median(np.maximum(values, 0))), 1e-6)


def _design(z_fit, z_other, gamma):
    mapping = Nystroem(gamma=gamma, n_components=min(384, len(z_fit)), random_state=31)
    k_fit = mapping.fit_transform(z_fit).astype(np.float32)
    k_other = mapping.transform(z_other).astype(np.float32)
    return np.concatenate((k_fit, 0.07 * z_fit), axis=1), np.concatenate((k_other, 0.07 * z_other), axis=1)


def _ridge_parts(x, y):
    counts = np.bincount(y, minlength=7)
    present = np.flatnonzero(counts)
    weight = np.minimum((len(y) / (len(present) * counts[y])) ** 0.75, 10).astype(np.float32)
    weight /= weight.mean()
    target = np.eye(7, dtype=np.float32)[y]
    x_mean = np.average(x, axis=0, weights=weight).astype(np.float32)
    y_mean = np.average(target, axis=0, weights=weight).astype(np.float32)
    xc = x - x_mean
    yc = target - y_mean
    gram = xc.T @ (xc * weight[:, None])
    cross = xc.T @ (yc * weight[:, None])
    return gram, cross, x_mean, y_mean, present


def _predict(x, parts, alpha):
    gram, cross, x_mean, y_mean, present = parts
    coef = np.linalg.solve(gram + alpha * np.eye(len(gram), dtype=np.float32), cross)
    scores = (x - x_mean) @ coef + y_mean
    absent = np.setdiff1d(np.arange(7), present)
    scores[:, absent] = -1e9
    return scores.argmax(axis=1).astype(np.int64)


def fit_predict(train_x, train_y, test_x, train_groups):
    x = np.asarray(train_x, dtype=np.float32)
    y = np.asarray(train_y, dtype=np.int64).reshape(-1)
    test = np.asarray(test_x, dtype=np.float32)
    groups = np.asarray(train_groups).reshape(-1)
    widths = (0.7, 2.5)
    penalties = (10.0, 100.0, 1000.0)
    validation = {(width, penalty): [] for width in widths for penalty in penalties}

    for donor in np.unique(groups):
        fit_idx = groups != donor
        val_idx = ~fit_idx
        if np.unique(y[fit_idx]).size < 2 or not np.any(val_idx):
            continue
        z_fit, z_val = _prepare(x[fit_idx], y[fit_idx], x[val_idx])
        distance = _median_distance(z_fit)
        common = np.intersect1d(np.unique(y[fit_idx]), np.unique(y[val_idx]))
        usable = np.isin(y[val_idx], common)
        if not np.any(usable):
            continue
        for width in widths:
            d_fit, d_val = _design(z_fit, z_val, width / distance)
            parts = _ridge_parts(d_fit, y[fit_idx])
            for penalty in penalties:
                pred = _predict(d_val, parts, penalty)
                score = f1_score(y[val_idx][usable], pred[usable], labels=common,
                                 average='macro', zero_division=0)
                validation[(width, penalty)].append(score)

    best = max(validation, key=lambda choice: (np.mean(validation[choice])
                if validation[choice] else -1.0, -choice[1]))
    z_fit, z_test = _prepare(x, y, test)
    d_fit, d_test = _design(z_fit, z_test, best[0] / _median_distance(z_fit))
    return _predict(d_test, _ridge_parts(d_fit, y), best[1])