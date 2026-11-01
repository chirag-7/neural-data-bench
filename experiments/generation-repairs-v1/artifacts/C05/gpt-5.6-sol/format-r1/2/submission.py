import gc
import numpy as np
from scipy.ndimage import gaussian_filter1d
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import Ridge

def _features(trace):
    a = np.asarray(trace, dtype=np.float64)
    finite = np.isfinite(a)
    if not finite.any():
        return (None, 0)
    last = int(np.flatnonzero(finite)[-1]) + 1
    x = a[:last].copy()
    good = np.isfinite(x)
    ind = np.arange(last)
    if not good.all():
        x[~good] = np.interp(ind[~good], ind[good], x[good])
    q10, q20, q90 = np.percentile(x, [10.0, 20.0, 90.0])
    scale = q90 - q10
    if not np.isfinite(scale) or scale < 1e-08:
        scale = np.std(x)
    if not np.isfinite(scale) or scale < 1e-08:
        scale = 1.0
    z = np.clip((x - q20) / scale, -6.0, 20.0)
    base = gaussian_filter1d(z, 200.0, mode='nearest')
    hp = np.clip(z - base, -8.0, 16.0)
    nb = (last + 3) // 4
    starts = 4 * np.arange(nb)
    center = np.minimum(starts + 2, last - 1)
    cols = []
    offsets = [-80, -60, -40, -24, -16, -12, -8, -6, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 8, 10, 12, 16, 24, 32, 40, 60, 80]
    for off in offsets:
        cols.append(z[np.clip(center + off, 0, last - 1)])
    for off in (-24, -12, -8, -4, 0, 4, 8, 12, 24):
        cols.append(hp[np.clip(center + off, 0, last - 1)])
    for sig in (1.0, 2.0, 4.0, 8.0, 16.0, 32.0):
        sm = gaussian_filter1d(z, sig, mode='nearest')
        lo = sm[np.clip(center - 4, 0, last - 1)]
        md = sm[center]
        hi = sm[np.clip(center + 4, 0, last - 1)]
        cols.extend((md, hi - lo, hi + lo - 2.0 * md))
    pos = np.clip(starts[:, None] + np.arange(4)[None, :], 0, last - 1)
    block = z[pos]
    cols.extend((block.mean(1), block.max(1), block.min(1), block[:, -1] - block[:, 0]))
    prev = np.r_[z[0], z[:-1]]
    for alpha in (0.8, 0.88, 0.93, 0.96, 0.98, 0.99):
        d = z - alpha * prev
        db = d[pos]
        dp = np.maximum(db, 0.0)
        cols.extend((db.sum(1), dp.sum(1), dp.max(1)))
    X = np.column_stack(cols).astype(np.float32)
    X = np.nan_to_num(X, nan=0.0, posinf=20.0, neginf=-20.0)
    return (X, last)

def _stack(data, ids):
    xs, ys, ws = ([], [], [])
    total = sum((len(data[i][1]) for i in ids))
    k = max(len(ids), 1)
    for i in ids:
        X, y, _ = data[i]
        xs.append(X)
        ys.append(y)
        ws.append(np.full(len(y), total / (k * len(y)), dtype=np.float32))
    return (np.concatenate(xs), np.concatenate(ys), np.concatenate(ws))

def _fit_ridge(X, y, w):
    mu = X.mean(axis=0, dtype=np.float64).astype(np.float32)
    sd = X.std(axis=0, dtype=np.float64).astype(np.float32)
    sd[sd < 1e-05] = 1.0
    Z = ((X - mu) / sd).astype(np.float32)
    model = Ridge(alpha=12.0, solver='lsqr', tol=0.0002, max_iter=1000)
    model.fit(Z, y, sample_weight=w)
    return (model, mu, sd)

def _ridge_predict(fit, X):
    model, mu, sd = fit
    return model.predict(((X - mu) / sd).astype(np.float32))

def _fit_booster(X, y, w, iterations):
    args = dict(max_iter=iterations, learning_rate=0.055, max_leaf_nodes=31, min_samples_leaf=80, l2_regularization=2.0, max_bins=63, early_stopping=False, random_state=1729)
    try:
        model = HistGradientBoostingRegressor(loss='poisson', **args)
        model.fit(X, y, sample_weight=w)
    except (ValueError, TypeError):
        model = HistGradientBoostingRegressor(loss='squared_error', **args)
        model.fit(X, y, sample_weight=w)
    return model

def _norm_prediction(p):
    p = np.nan_to_num(np.asarray(p, dtype=np.float64), nan=0.0, posinf=0.0, neginf=0.0)
    p -= np.min(p)
    s = np.std(p)
    if s > 1e-10:
        p /= s
    return p

def fit_predict(train_calcium, train_spikes, test_calcium):
    train_calcium = np.asarray(train_calcium, dtype=np.float64)
    train_spikes = np.asarray(train_spikes, dtype=np.float64)
    test_calcium = np.asarray(test_calcium, dtype=np.float64)
    data = []
    for j in range(train_calcium.shape[1]):
        cf = np.flatnonzero(np.isfinite(train_calcium[:, j]))
        sf = np.flatnonzero(np.isfinite(train_spikes[:, j]))
        if cf.size == 0 or sf.size == 0:
            continue
        last = min(int(cf[-1]), int(sf[-1])) + 1
        nb = last // 4
        if nb < 20:
            continue
        X, _ = _features(train_calcium[:last, j])
        cm = np.isfinite(train_calcium[:4 * nb, j]).reshape(nb, 4).all(1)
        sm = np.isfinite(train_spikes[:4 * nb, j]).reshape(nb, 4).all(1)
        valid = cm & sm
        raw = np.maximum(train_spikes[:4 * nb, j], 0.0)
        raw = raw.reshape(nb, 4).sum(1)[valid]
        Xi = X[:nb][valid]
        if len(raw) < 20:
            continue
        sy = np.std(raw)
        if sy < 1e-08:
            sy = max(np.mean(raw), 1.0)
        data.append((Xi, (raw / sy).astype(np.float32), raw))
    ids = list(range(len(data)))
    blend = 0.75
    if len(ids) >= 4:
        order = np.argsort([len(d[1]) for d in data])
        val_ids = list(order[1::4])
        tr_ids = [i for i in ids if i not in set(val_ids)]
        Xvtr, yvtr, wvtr = _stack(data, tr_ids)
        hb = _fit_booster(Xvtr, yvtr, wvtr, 105)
        lr = _fit_ridge(Xvtr, yvtr, wvtr)
        cached = []
        for i in val_ids:
            X, _, yraw = data[i]
            cached.append((_norm_prediction(hb.predict(X)), _norm_prediction(_ridge_predict(lr, X)), yraw))
        best_score = -np.inf
        for b in (0.0, 0.25, 0.5, 0.75, 1.0):
            cors = []
            for ph, pl, y in cached:
                p = b * ph + (1.0 - b) * pl
                if np.std(p) > 1e-10 and np.std(y) > 1e-10:
                    cors.append(np.corrcoef(p, y)[0, 1])
            if cors:
                score = 0.5 * np.mean(cors) + 0.5 * np.median(cors)
                if score > best_score:
                    best_score, blend = (score, b)
        del Xvtr, yvtr, wvtr, hb, lr, cached
        gc.collect()
    Xall, yall, wall = _stack(data, ids)
    booster = _fit_booster(Xall, yall, wall, 140)
    linear = _fit_ridge(Xall, yall, wall)
    del Xall, yall, wall, data
    gc.collect()
    out = np.full(test_calcium.shape, np.nan, dtype=np.float64)
    for j in range(test_calcium.shape[1]):
        X, last = _features(test_calcium[:, j])
        if X is None:
            continue
        ph = _norm_prediction(booster.predict(X))
        pl = _norm_prediction(_ridge_predict(linear, X))
        pb = np.maximum(blend * ph + (1.0 - blend) * pl, 0.0)
        pred = np.repeat(pb / 4.0, 4)[:last]
        original_finite = np.isfinite(test_calcium[:last, j])
        out[:last, j][original_finite] = pred[original_finite]
    return out
