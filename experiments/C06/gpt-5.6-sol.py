import numpy as np
from scipy.ndimage import gaussian_filter1d
from sklearn.ensemble import ExtraTreesRegressor, HistGradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.model_selection import GroupKFold


def _shift(a, k):
    n = len(a)
    if n < 2 or k == 0:
        return a.copy()
    k = int(max(-n + 1, min(n - 1, k)))
    m = abs(k)
    z = np.pad(a, (m, m), mode="reflect")
    return z[m + k:m + k + n]


def _row_features(x, dt):
    x = np.asarray(x, dtype=np.float64)
    n = len(x)
    if n == 0:
        return np.empty((0, 1), dtype=np.float32)
    good = np.isfinite(x)
    if not np.all(good):
        ii = np.arange(n)
        if np.any(good):
            x = np.interp(ii, ii[good], x[good])
        else:
            x = np.zeros(n)
    dt = float(dt) if np.isfinite(dt) and dt > 0 else 0.13
    center = np.median(x)
    a = x - center
    if n > 1:
        d = np.diff(a)
        dm = np.median(d)
        noise = np.median(np.abs(d - dm)) / 0.67448975 / np.sqrt(2.0)
    else:
        noise = 1.0
    amp = np.percentile(a, 90) - np.percentile(a, 10)
    floor = max(1e-6, 1e-4 * (np.max(np.abs(a)) + 1.0))
    noise = max(float(noise), floor)
    amp = max(float(amp), 2.0 * noise, floor)

    times = (0.06, 0.12, 0.24, 0.48, 0.96, 1.92, 3.84)
    smooth = [gaussian_filter1d(a, max(0.35, t / dt), mode="reflect")
              for t in times]
    f = []
    for s in smooth:
        f.append(s / noise)
        f.append(s / amp)
        f.append((_shift(s, 1) - _shift(s, -1)) / (2.0 * noise))
    for i in range(len(smooth) - 1):
        f.append((smooth[i] - smooth[i + 1]) / noise)

    delays = (-1.50, -1.00, -0.65, -0.40, -0.25, -0.13, 0.0,
              0.13, 0.25, 0.40, 0.65, 1.00, 1.50, 2.00, 3.00)
    base = smooth[0]
    for delay in delays:
        f.append(_shift(base, int(round(delay / dt))) / noise)

    for tau in (0.28, 0.45, 0.70, 1.05, 1.60):
        g = np.exp(-dt / tau)
        for delay in (-0.25, 0.0, 0.13, 0.30, 0.55):
            k = int(round(delay / dt))
            innovation = (_shift(base, k) - g * _shift(base, k - 1)) / noise
            f.append(innovation)
            f.append(np.maximum(innovation, 0.0))
    f.append(np.full(n, np.log1p(amp / noise)))
    f.append(np.full(n, dt))
    return np.column_stack(f).astype(np.float32)


def _base_weights(groups):
    groups = np.asarray(groups, dtype=np.int64)
    w = np.zeros(len(groups), dtype=np.float64)
    for g in np.unique(groups):
        q = groups == g
        w[q] = 1.0 / max(1, np.sum(q))
    return w * (len(w) / max(np.sum(w), 1e-12))


def _fit_models(X, y, groups, seed):
    bw = _base_weights(groups)
    pos = y[y > 0]
    q = np.percentile(pos, 70) if len(pos) else 1.0
    q = max(float(q), 1e-6)
    ew = bw * (1.0 + 2.0 * np.minimum(y / q, 4.0))
    ew *= len(ew) / np.sum(ew)

    sw = np.sum(ew)
    mean = np.sum(X * ew[:, None], axis=0) / sw
    var = np.sum((X - mean) ** 2 * ew[:, None], axis=0) / sw
    scale = np.sqrt(np.maximum(var, 1e-8))
    ridge = Ridge(alpha=45.0, fit_intercept=True)
    ridge.fit((X - mean) / scale, y, sample_weight=ew)

    extra = ExtraTreesRegressor(
        n_estimators=140, min_samples_leaf=7, max_features=0.72,
        random_state=seed, n_jobs=1, bootstrap=False
    )
    extra.fit(X, y, sample_weight=ew)

    hist = HistGradientBoostingRegressor(
        loss="poisson", learning_rate=0.055, max_iter=170,
        max_leaf_nodes=15, min_samples_leaf=28,
        l2_regularization=2.0, early_stopping=False,
        random_state=seed
    )
    hist.fit(X, y, sample_weight=bw)
    cap = max(1e-5, 2.0 * float(np.max(y)),
              3.0 * float(np.percentile(y, 99.9)))
    return ((ridge, mean, scale), extra, hist, cap)


def _predict_models(models, X):
    ridge_info, extra, hist, cap = models
    ridge, mean, scale = ridge_info
    p0 = ridge.predict((X - mean) / scale)
    p1 = extra.predict(X)
    p2 = hist.predict(X)
    P = np.column_stack((p0, p1, p2))
    return np.clip(np.nan_to_num(P, nan=0.0, posinf=cap, neginf=0.0), 0.0, cap)


def _group_correlation(y, p, groups):
    vals = []
    for g in np.unique(groups):
        q = groups == g
        a = y[q] - np.mean(y[q])
        b = p[q] - np.mean(p[q])
        den = np.sqrt(np.dot(a, a) * np.dot(b, b))
        vals.append(float(np.dot(a, b) / den) if den > 1e-15 else 0.0)
    return float(np.mean(vals)) if vals else 0.0


def _choose_blend(y, P, groups):
    bw = _base_weights(groups)
    scales = np.ones(P.shape[1])
    target_total = np.dot(bw, y)
    for j in range(P.shape[1]):
        predicted_total = np.dot(bw, P[:, j])
        if predicted_total > 1e-12:
            scales[j] = np.clip(target_total / predicted_total, 0.1, 10.0)
    Q = P * scales
    best_w = np.array([0.3, 0.4, 0.3])
    best = _group_correlation(y, Q @ best_w, groups)
    for i in range(11):
        for j in range(11 - i):
            w = np.array([i, j, 10 - i - j], dtype=np.float64) / 10.0
            score = _group_correlation(y, Q @ w, groups)
            if score > best + 1e-12:
                best, best_w = score, w
    return scales, best_w


def fit_predict(train_x, train_y, test_x, train_groups):
    train_x = np.asarray(train_x)
    train_y = np.asarray(train_y, dtype=np.float64)
    test_x = np.asarray(test_x)
    n_train = train_x.shape[0]
    raw_groups = np.asarray(train_groups).reshape(-1)
    if len(raw_groups) != n_train:
        raise ValueError("train_groups must contain one entry per training recording")
    group_map = {}
    row_groups = np.empty(n_train, dtype=np.int64)
    for i, value in enumerate(raw_groups.tolist()):
        key = repr(value)
        if key not in group_map:
            group_map[key] = len(group_map)
        row_groups[i] = group_map[key]

    xparts, yparts, gparts = [], [], []
    for i in range(n_train):
        mask = np.asarray(train_x[i, 1] > 0.5)
        n = int(np.sum(mask))
        if n == 0:
            continue
        dtv = train_x[i, 2, :n]
        dtv = dtv[np.isfinite(dtv) & (dtv > 0)]
        dt = np.median(dtv) if len(dtv) else 0.13
        F = _row_features(train_x[i, 0, :n], dt)
        y = train_y[i, :n]
        keep = np.isfinite(y) & (y >= 0)
        xparts.append(F[keep])
        yparts.append(y[keep])
        gparts.append(np.full(np.sum(keep), row_groups[i], dtype=np.int64))
    X = np.concatenate(xparts, axis=0)
    y = np.concatenate(yparts).astype(np.float64)
    groups = np.concatenate(gparts)

    test_parts, lengths = [], []
    for i in range(test_x.shape[0]):
        n = int(np.sum(test_x[i, 1] > 0.5))
        lengths.append(n)
        if n:
            dtv = test_x[i, 2, :n]
            dtv = dtv[np.isfinite(dtv) & (dtv > 0)]
            dt = np.median(dtv) if len(dtv) else 0.13
            test_parts.append(_row_features(test_x[i, 0, :n], dt))
    XT = np.concatenate(test_parts, axis=0) if test_parts else np.empty((0, X.shape[1]))

    unique_groups = np.unique(groups)
    if len(unique_groups) >= 2:
        oof = np.zeros((len(y), 3), dtype=np.float64)
        splitter = GroupKFold(n_splits=min(4, len(unique_groups)))
        for fold, (tr, va) in enumerate(splitter.split(X, y, groups)):
            models = _fit_models(X[tr], y[tr], groups[tr], 1729 + fold)
            oof[va] = _predict_models(models, X[va])
        scales, blend = _choose_blend(y, oof, groups)
    else:
        scales = np.ones(3)
        blend = np.array([0.3, 0.4, 0.3])

    final_models = _fit_models(X, y, groups, 2718)
    pred = (_predict_models(final_models, XT) * scales) @ blend if len(XT) else np.empty(0)
    cap = final_models[3] * max(1.0, float(np.max(scales)))
    pred = np.clip(np.nan_to_num(pred, nan=0.0, posinf=cap, neginf=0.0), 0.0, cap)
    out = np.zeros((test_x.shape[0], test_x.shape[2]), dtype=np.float64)
    at = 0
    for i, n in enumerate(lengths):
        if n:
            out[i, :n] = pred[at:at + n]
            at += n
    return out
