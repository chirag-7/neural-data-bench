import numpy as np
from scipy.ndimage import gaussian_filter1d
from scipy.optimize import minimize


def _smooth(a, sigma, order=0):
    return gaussian_filter1d(a, sigma=sigma, axis=1, order=order,
                             mode="reflect", truncate=3.0)


def _sample_features(x):
    s0 = _smooth(x, 0.55)
    s1 = _smooth(x, 1.25)
    s2 = _smooth(x, 2.5)
    d1 = _smooth(x, 1.3, order=1)
    sq = np.sqrt(np.maximum(s1, 0.0) + 0.01)
    n, t, _ = x.shape
    ti = np.broadcast_to(np.eye(t, dtype=np.float64)[None, :, :],
                         (n, t, t))
    return np.concatenate((s0, s1, s2, d1, sq, ti), axis=2)


def _trial_features(x):
    s1 = _smooth(x, 0.9)
    s2 = _smooth(x, 2.2)
    z1 = np.sqrt(np.maximum(s1, 0.0) + 0.01)
    return np.concatenate((z1.reshape(len(x), -1),
                           s2.reshape(len(x), -1)), axis=1)


def _standardize(a, b, floor=0.04):
    mu = a.mean(axis=0)
    sd = a.std(axis=0)
    sd = np.maximum(sd, floor)
    p = float(a.shape[1])
    scale = np.sqrt(p)
    return (a - mu) / sd / scale, (b - mu) / sd / scale


def _ridge_many(a, y, b, alphas):
    g = a.T @ a
    vals, vecs = np.linalg.eigh(g)
    vals = np.maximum(vals, 0.0)
    rhs = vecs.T @ (a.T @ y)
    out = []
    for alpha in alphas:
        coef = vecs @ (rhs / (vals[:, None] + alpha))
        out.append(b @ coef)
    return out


def _kernel_ridge_many(a, y, b, alphas):
    g = a @ a.T
    vals, vecs = np.linalg.eigh(g)
    vals = np.maximum(vals, 0.0)
    rhs = vecs.T @ y
    kb = b @ a.T
    out = []
    for alpha in alphas:
        dual = vecs @ (rhs / (vals[:, None] + alpha))
        out.append(kb @ dual)
    return out


def _caps(y):
    q = np.percentile(y, 99.7, axis=(0, 1))
    return np.maximum(0.5, 2.0 * q + 0.05)


def _clean(p, cap):
    p = np.nan_to_num(p, nan=0.0, posinf=0.0, neginf=0.0)
    return np.minimum(np.maximum(p, 1e-5), cap[None, None, :])


def _fit_candidates(x, ys, z, sample_alphas, trial_alphas):
    n, t, no = ys.shape
    base = ys.mean(axis=0)
    cap = _caps(ys)
    candidates = [_clean(np.broadcast_to(base, (len(z), t, no)).copy(), cap)]

    fx = _sample_features(x).reshape(n * t, -1)
    fz = _sample_features(z).reshape(len(z) * t, -1)
    ax, az = _standardize(fx, fz)
    target = ys.reshape(n * t, no) - np.tile(base, (n, 1))
    preds = _ridge_many(ax, target, az, sample_alphas)
    base_rows = np.tile(base, (len(z), 1))
    for p in preds:
        p = (p + base_rows).reshape(len(z), t, no)
        candidates.append(_clean(p, cap))

    tx = _trial_features(x)
    tz = _trial_features(z)
    ax, az = _standardize(tx, tz, floor=0.06)
    flat_base = base.reshape(1, -1)
    target = ys.reshape(n, -1) - flat_base
    preds = _kernel_ridge_many(ax, target, az, trial_alphas)
    for p in preds:
        p = (p + flat_base).reshape(len(z), t, no)
        candidates.append(_clean(p, cap))
    return np.stack(candidates, axis=3)


def _blend_weights(oof, y):
    k = oof.shape[3]
    losses = []
    for j in range(k):
        p = np.maximum(oof[:, :, :, j], 1e-7)
        losses.append(np.mean(p - y * np.log(p)))
    best = int(np.argmin(losses))
    start = np.full(k, 0.5 / k)
    start[best] += 0.5
    start /= start.sum()

    def objective(w):
        p = np.tensordot(oof, w, axes=([3], [0]))
        p = np.maximum(p, 1e-7)
        return float(np.mean(p - y * np.log(p)))

    result = minimize(objective, start, method="SLSQP",
                      bounds=[(0.0, 1.0)] * k,
                      constraints={"type": "eq",
                                   "fun": lambda w: np.sum(w) - 1.0},
                      options={"maxiter": 150, "ftol": 1e-10,
                               "disp": False})
    if result.success and np.all(np.isfinite(result.x)):
        w = np.maximum(result.x, 0.0)
        if w.sum() > 0:
            return w / w.sum()
    w = np.zeros(k)
    w[best] = 1.0
    return w


def fit_predict(train_x, train_y, test_x):
    x = np.asarray(train_x, dtype=np.float64)
    y = np.asarray(train_y, dtype=np.float64)
    z = np.asarray(test_x, dtype=np.float64)
    if x.ndim != 3 or y.ndim != 3 or z.ndim != 3:
        raise ValueError("Inputs must be three-dimensional arrays")
    if x.shape[:2] != y.shape[:2] or x.shape[1:] != z.shape[1:]:
        raise ValueError("Incompatible input shapes")

    ys = _smooth(y, 0.85)
    sample_alphas = (0.03, 0.10, 0.30, 1.0, 3.0)
    trial_alphas = (0.01, 0.03, 0.10, 0.30, 1.0)
    k = 1 + len(sample_alphas) + len(trial_alphas)
    oof = np.empty(y.shape + (k,), dtype=np.float64)

    rng = np.random.RandomState(1701)
    order = rng.permutation(len(x))
    folds = np.array_split(order, 5)
    all_idx = np.arange(len(x))
    for val in folds:
        keep = np.ones(len(x), dtype=bool)
        keep[val] = False
        tr = all_idx[keep]
        oof[val] = _fit_candidates(x[tr], ys[tr], x[val],
                                    sample_alphas, trial_alphas)

    weights = _blend_weights(oof, y)
    oof_blend = np.tensordot(oof, weights, axes=([3], [0]))
    observed = y.sum(axis=(0, 1))
    expected = oof_blend.sum(axis=(0, 1))
    calibration = (observed + 20.0) / (expected + 20.0)
    calibration = np.clip(calibration, 0.65, 1.5)

    test_candidates = _fit_candidates(x, ys, z,
                                      sample_alphas, trial_alphas)
    pred = np.tensordot(test_candidates, weights, axes=([3], [0]))
    pred *= calibration[None, None, :]
    pred = _clean(pred, _caps(ys))
    return pred.astype(np.float64, copy=False)
