import numpy as np
from scipy.ndimage import gaussian_filter1d


def _normalize_rows(a):
    a = a - np.mean(a, axis=1, keepdims=True)
    n = np.sqrt(np.sum(a * a, axis=1, keepdims=True))
    return a / np.maximum(n, 1e-12)


def _pairwise_shifts(raster, overlap, max_lag=12):
    t, n = raster.shape
    full = _normalize_rows(raster)
    cubes = []
    lags = np.arange(-max_lag, max_lag + 1)
    for lag in lags:
        if lag >= 0:
            a = raster[:, lag:]
            b = raster[:, :n - lag]
            af = full[:, lag:]
            bf = full[:, :n - lag]
        else:
            q = -lag
            a = raster[:, :n - q]
            b = raster[:, q:]
            af = full[:, :n - q]
            bf = full[:, q:]
        if overlap:
            aa = _normalize_rows(a)
            bb = _normalize_rows(b)
            c = aa @ bb.T
        else:
            c = af @ bf.T
        cubes.append(np.clip(c, -1.0, 1.0))
    cube = np.asarray(cubes)
    k = np.argmax(cube, axis=0)
    ii = np.arange(t)[:, None]
    jj = np.arange(t)[None, :]
    y0 = cube[k, ii, jj]
    km = np.maximum(k - 1, 0)
    kp = np.minimum(k + 1, len(lags) - 1)
    ym = cube[km, ii, jj]
    yp = cube[kp, ii, jj]
    den = ym - 2.0 * y0 + yp
    delta = np.zeros_like(y0)
    valid = (k > 0) & (k + 1 < len(lags)) & (np.abs(den) > 1e-8)
    delta[valid] = 0.5 * (ym[valid] - yp[valid]) / den[valid]
    delta = np.clip(delta, -0.75, 0.75)
    shift = (lags[k].astype(float) + delta) * 5.0
    shift = 0.5 * (shift - shift.T)
    corr = 0.5 * (y0 + y0.T)
    np.fill_diagonal(shift, 0.0)
    np.fill_diagonal(corr, 1.0)
    return shift, corr


def _linear_solve(weights, shifts, temporal_fraction):
    t = weights.shape[0]
    degree = np.sum(weights, axis=1)
    positive = degree[degree > 1e-10]
    typical = np.median(positive) if positive.size else 1.0
    temporal = temporal_fraction * max(float(typical), 1e-3)
    lap = np.diag(degree) - weights
    rhs = np.sum(weights * shifts, axis=1)
    if t > 1 and temporal > 0.0:
        q = np.arange(t - 1)
        lap[q, q] += temporal
        lap[q + 1, q + 1] += temporal
        lap[q, q + 1] -= temporal
        lap[q + 1, q] -= temporal
    lap += np.ones((t, t), dtype=float) / float(t)
    try:
        p = np.linalg.solve(lap, rhs)
    except np.linalg.LinAlgError:
        p = np.linalg.lstsq(lap, rhs, rcond=1e-10)[0]
    p -= np.mean(p)
    return p


def _synchronize(shifts, corr, threshold, power, temporal_fraction,
                 robust):
    q = np.maximum(corr - threshold, 0.0) / max(1.0 - threshold, 1e-6)
    if power == 0:
        w = (q > 0.0).astype(float)
    else:
        w = q ** power
    w = 0.5 * (w + w.T)
    np.fill_diagonal(w, 0.0)
    p = _linear_solve(w, shifts, temporal_fraction)
    if robust:
        for cutoff in (12.0, 8.0):
            residual = p[:, None] - p[None, :] - shifts
            factor = np.minimum(1.0, cutoff / np.maximum(np.abs(residual), 1e-6))
            wr = w * factor
            p = _linear_solve(wr, shifts, temporal_fraction)
    return p


def _registered_feature(x, config):
    transform, spatial, temporal, overlap, threshold, power, prior, robust = config
    if transform == "sqrt":
        r = np.sqrt(np.maximum(x, 0.0) + 0.25)
    elif transform == "log":
        r = np.log1p(np.maximum(x, 0.0))
    else:
        r = np.maximum(x, 0.0)
    if spatial > 0.0:
        r = gaussian_filter1d(r, spatial, axis=1, mode="nearest")
    if temporal > 0.0:
        r = gaussian_filter1d(r, temporal, axis=0, mode="nearest")
    shifts, corr = _pairwise_shifts(r, overlap)
    return _synchronize(shifts, corr, threshold, power, prior, robust)


def _base_features(recording):
    configs = (
        ("sqrt", 0.9, 0.0, True, 0.08, 2, 0.045, True),
        ("sqrt", 1.4, 0.0, False, 0.10, 0, 0.030, False),
        ("log", 0.7, 0.55, True, 0.10, 2, 0.090, True),
        ("raw", 1.1, 0.0, True, 0.14, 1, 0.140, True),
    )
    base = [_registered_feature(recording, c) for c in configs]
    depth = 5.0 * np.arange(recording.shape[1], dtype=float)
    mass = np.sum(recording, axis=1)
    centroid = np.sum(recording * depth[None, :], axis=1) / np.maximum(mass, 1.0)
    centroid -= np.mean(centroid)
    centroid = gaussian_filter1d(centroid, 0.7, mode="nearest")
    base.append(centroid)
    columns = []
    for p in base:
        p = np.asarray(p, dtype=float)
        p -= np.mean(p)
        columns.append(p)
        columns.append(gaussian_filter1d(p, 0.9, mode="nearest"))
        columns.append(gaussian_filter1d(p, 2.0, mode="nearest"))
    f = np.column_stack(columns)
    f -= np.mean(f, axis=0, keepdims=True)
    return np.nan_to_num(f, nan=0.0, posinf=0.0, neginf=0.0)


def _correction_design(features):
    anchor = features[..., 0]
    return np.concatenate((anchor[..., None],
                           features[..., 1:] - anchor[..., None]), axis=-1)


def _fit_correction(features, targets, rows, alpha):
    z = _correction_design(features[rows]).reshape(-1, features.shape[-1])
    y = targets[rows].reshape(-1) - features[rows, :, 0].reshape(-1)
    scale = np.sqrt(np.mean(z * z, axis=0))
    scale = np.maximum(scale, 1e-5)
    zs = z / scale
    gram = zs.T @ zs
    rhs = zs.T @ y
    beta = np.linalg.solve(gram + float(alpha) * np.eye(gram.shape[0]), rhs)
    return scale, beta


def _apply_correction(features, scale, beta):
    z = _correction_design(features)
    return features[..., 0] + (z / scale) @ beta


def fit_predict(train_x, train_y, test_x, train_groups):
    tx = np.nan_to_num(np.asarray(train_x, dtype=float), nan=0.0,
                       posinf=0.0, neginf=0.0)
    vx = np.nan_to_num(np.asarray(test_x, dtype=float), nan=0.0,
                       posinf=0.0, neginf=0.0)
    y = np.nan_to_num(np.asarray(train_y, dtype=float), nan=0.0,
                      posinf=0.0, neginf=0.0)
    y = y - np.mean(y, axis=1, keepdims=True)
    train_f = np.stack([_base_features(r) for r in tx])
    test_f = np.stack([_base_features(r) for r in vx])
    alphas = (0.3, 1.0, 3.0, 10.0, 30.0, 100.0, 300.0, 1000.0)
    errors = []
    all_rows = np.arange(tx.shape[0])
    for alpha in alphas:
        fold_errors = []
        for held in all_rows:
            rows = all_rows[all_rows != held]
            scale, beta = _fit_correction(train_f, y, rows, alpha)
            pred = _apply_correction(train_f[held:held + 1], scale, beta)[0]
            pred -= np.mean(pred)
            fold_errors.append(np.sqrt(np.mean((pred - y[held]) ** 2)))
        errors.append(float(np.mean(fold_errors)))
    best_error = min(errors)
    eligible = [i for i, e in enumerate(errors) if e <= best_error * 1.01 + 1e-9]
    chosen = alphas[max(eligible)]
    scale, beta = _fit_correction(train_f, y, all_rows, chosen)
    output = _apply_correction(test_f, scale, beta)
    output -= np.mean(output, axis=1, keepdims=True)
    output = np.clip(output, -65.0, 65.0)
    output -= np.mean(output, axis=1, keepdims=True)
    return np.nan_to_num(output, nan=0.0, posinf=65.0, neginf=-65.0)
