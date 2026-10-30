import numpy as np
from scipy.ndimage import gaussian_filter, gaussian_filter1d, map_coordinates


def _prepare(train_x, test_x):
    tr = np.asarray(train_x, dtype=float).reshape(-1, 2).copy()
    te = np.asarray(test_x, dtype=float).reshape(-1, 2).copy()
    for j in range(2):
        good = np.isfinite(tr[:, j])
        median = np.median(tr[good, j]) if np.any(good) else 0.0
        tr[~good, j] = median
        te[~np.isfinite(te[:, j]), j] = median
    return tr, te


def _estimate(tr, y, te, kind, hp, hv):
    p = tr[:, 0]
    mean = max(float(np.mean(y)), 1e-8)
    p0, p1 = np.quantile(p, [0.001, 0.999])
    span = max(float(p1 - p0), 1e-6)
    pedges = np.linspace(p0 - 0.15 * span, p1 + 0.15 * span, 161)
    pc = (pedges[:-1] + pedges[1:]) * 0.5
    dp = pedges[1] - pedges[0]
    sp = max(0.8, hp * span / dp)

    if kind == 1:
        occ = np.histogram(p, bins=pedges)[0].astype(float)
        spikes = np.histogram(p, bins=pedges, weights=y)[0]
        prior = 3.0 / (np.sqrt(2.0 * np.pi) * sp)
        smooth_occ = gaussian_filter1d(occ, sp, mode='constant')
        smooth_spikes = gaussian_filter1d(spikes, sp, mode='constant')
        rate = (smooth_spikes + prior * mean) / (smooth_occ + prior)
        result = np.interp(te[:, 0], pc, rate, left=mean, right=mean)
    else:
        v = tr[:, 1]
        v0, v1 = np.quantile(v, [0.001, 0.999])
        vspan = float(v1 - v0)
        if vspan < 1e-6:
            return _estimate(tr, y, te, 1, hp, 0.0)
        vedges = np.linspace(v0 - 0.15 * vspan, v1 + 0.15 * vspan, 42)
        vc = (vedges[:-1] + vedges[1:]) * 0.5
        dv = vedges[1] - vedges[0]
        sv = max(0.8, hv * vspan / dv)
        occ = np.histogram2d(p, v, bins=(pedges, vedges))[0]
        spikes = np.histogram2d(p, v, bins=(pedges, vedges), weights=y)[0]
        prior = 3.0 / (2.0 * np.pi * sp * sv)
        smooth_occ = gaussian_filter(occ, (sp, sv), mode='constant')
        smooth_spikes = gaussian_filter(spikes, (sp, sv), mode='constant')
        rate = (smooth_spikes + prior * mean) / (smooth_occ + prior)
        coords = np.vstack(((te[:, 0] - pc[0]) / dp,
                            (te[:, 1] - vc[0]) / dv))
        result = map_coordinates(rate, coords, order=1, mode='nearest')
        vdist = np.maximum(np.maximum(v0 - te[:, 1], te[:, 1] - v1), 0.0)
        result = mean + np.exp(-0.5 * (vdist / (hv * vspan)) ** 2) * (result - mean)

    pdist = np.maximum(np.maximum(p0 - te[:, 0], te[:, 0] - p1), 0.0)
    result = mean + np.exp(-0.5 * (pdist / (hp * span)) ** 2) * (result - mean)
    return np.maximum(result, 1e-8)


def _loglik(y, rate):
    return float(np.dot(y, np.log(np.maximum(rate, 1e-8))) - np.sum(rate))


def fit_predict(train_x, train_y, test_x):
    tr, te = _prepare(train_x, test_x)
    y = np.asarray(train_y, dtype=float).reshape(-1).copy()
    y[~np.isfinite(y)] = 0.0
    y = np.maximum(y, 0.0)
    n = len(y)
    if n == 0:
        return np.full(len(te), 1e-8)
    mean = max(float(np.mean(y)), 1e-8)
    if np.sum(y) == 0 or n < 100:
        return np.full(len(te), mean)

    widths = (0.02, 0.04, 0.08, 0.16)
    candidates = [(1, hp, 0.0) for hp in widths]
    candidates += [(2, hp, hv) for hp in widths for hv in (0.08, 0.20, 0.50)]
    folds = ((int(0.55 * n), int(0.75 * n), 0.4),
             (int(0.75 * n), n, 0.6))
    scores = []
    for candidate in candidates:
        score = 0.0
        for stop, end, weight in folds:
            target = y[stop:end]
            pred = _estimate(tr[:stop], y[:stop], tr[stop:end], *candidate)
            baseline = max(float(np.mean(y[:stop])), 1e-8)
            gain = _loglik(target, pred) - _loglik(target, np.full(len(target), baseline))
            score += weight * gain / max(len(target), 1)
        scores.append(score)

    ranking = np.argsort(scores)[::-1]
    selected = [int(i) for i in ranking[:3] if scores[int(i)] > 0.0]
    if not selected:
        return np.full(len(te), mean)
    weights = np.array((0.5, 0.3, 0.2)[:len(selected)], dtype=float)
    weights /= weights.sum()
    result = np.zeros(len(te), dtype=float)
    for weight, index in zip(weights, selected):
        result += weight * _estimate(tr, y, te, *candidates[index])
    return np.clip(result, 1e-8, max(1.0, float(np.max(y))))