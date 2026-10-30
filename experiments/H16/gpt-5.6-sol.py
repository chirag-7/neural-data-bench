import gc
import numpy as np
from scipy.ndimage import gaussian_filter1d
from scipy.fft import dct, idct
from sklearn.ensemble import HistGradientBoostingRegressor


def _segment_weights(y):
    e = np.sum(np.asarray(y, dtype=np.float64) ** 2, axis=1)
    w = y.shape[1] / np.maximum(e, 1e-8)
    w /= np.mean(w)
    return np.clip(w, 0.08, 12.0).astype(np.float32)


def _sample_indices(n, t, k, rng):
    k = min(k, t)
    return np.concatenate([
        i * t + rng.choice(t, size=k, replace=False) for i in range(n)
    ]).astype(np.int64)


def _global_features(z, fs=256.0):
    z = np.asarray(z, dtype=np.float32)
    n, t = z.shape
    sp = np.fft.rfft(z, axis=1)
    fr = np.fft.rfftfreq(t, 1.0 / fs)
    bands = [(0, 2), (2, 4), (4, 8), (8, 16),
             (16, 32), (32, 64), (64, fs / 2 + 1)]
    cols = []
    power = sp.real * sp.real + sp.imag * sp.imag
    for lo, hi in bands:
        m = (fr >= lo) & (fr < hi)
        cols.append(np.log1p(np.mean(power[:, m], axis=1)))
    az = np.abs(z)
    for q in (0.50, 0.80, 0.95, 0.99):
        cols.append(np.quantile(az, q, axis=1))
    mu = np.mean(z, axis=1)
    centered = z - mu[:, None]
    var = np.mean(centered * centered, axis=1)
    kurt = np.mean(centered ** 4, axis=1) / np.maximum(var * var, 1e-8)
    cols.extend([mu, np.log1p(kurt)])
    return np.column_stack(cols).astype(np.float32)


def _features(z, ids=None):
    z = np.asarray(z, dtype=np.float32)
    n, t = z.shape
    if ids is None:
        ids = np.arange(n * t, dtype=np.int64)
    else:
        ids = np.asarray(ids, dtype=np.int64)
    gfeat = _global_features(z)
    out = np.empty((len(ids), 28 + gfeat.shape[1]), dtype=np.float32)
    col = 0

    def put(a):
        nonlocal col
        out[:, col] = np.asarray(a).reshape(-1)[ids]
        col += 1

    put(z)
    sigmas = (1, 2, 4, 8, 16, 32, 64)
    sm = [gaussian_filter1d(z, s, axis=1, mode='reflect') for s in sigmas]
    for a in sm:
        put(a)
    put(z - sm[0])
    for i in range(1, len(sm)):
        put(sm[i - 1] - sm[i])
    zz = z * z
    for s in (2, 4, 8, 16, 32):
        r = gaussian_filter1d(zz, s, axis=1, mode='reflect')
        put(np.sqrt(np.maximum(r, 0.0)))
    put(np.gradient(sm[2], axis=1))
    put(np.gradient(sm[4], axis=1))
    for i in (2, 3, 4, 5):
        put(np.abs(sm[i]))
    pos = (ids % t).astype(np.float32)
    out[:, col] = 2.0 * pos / max(t - 1, 1) - 1.0
    col += 1
    out[:, col] = np.minimum(pos, t - 1 - pos) / max(t / 2.0, 1.0)
    col += 1
    rows = ids // t
    for j in range(gfeat.shape[1]):
        out[:, col] = gfeat[rows, j]
        col += 1
    return out


def _make_model(iterations):
    return HistGradientBoostingRegressor(
        loss='squared_error', learning_rate=0.07,
        max_iter=iterations, max_leaf_nodes=31,
        min_samples_leaf=70, l2_regularization=0.01,
        max_bins=127, early_stopping=False, random_state=1729
    )


def _fit_dct_filter(x, y, weights):
    X = dct(np.asarray(x, dtype=np.float64), type=2, norm='ortho', axis=1)
    Y = dct(np.asarray(y, dtype=np.float64), type=2, norm='ortho', axis=1)
    w = np.asarray(weights, dtype=np.float64)[:, None]
    den = np.sum(w * X * X, axis=0)
    num = np.sum(w * X * Y, axis=0)
    positive = den[den > 0]
    scale = np.median(positive) if positive.size else 1.0
    gain = num / (den + 1e-6 * scale)
    gain = gaussian_filter1d(gain, 1.2, mode='nearest')
    return np.clip(gain, 0.0, 1.15)


def _apply_dct_filter(x, gain):
    X = dct(np.asarray(x, dtype=np.float64), type=2, norm='ortho', axis=1)
    return idct(X * gain[None, :], type=2, norm='ortho', axis=1).astype(np.float32)


def _relative_rmse(pred, target):
    d = np.asarray(pred, dtype=np.float64) - target
    num = np.sqrt(np.sum(d * d, axis=1))
    den = np.sqrt(np.sum(np.asarray(target, dtype=np.float64) ** 2, axis=1))
    return float(np.mean(num / np.maximum(den, 1e-8)))


def fit_predict(train_x, train_y, test_x):
    x = np.asarray(train_x, dtype=np.float32)
    y = np.asarray(train_y, dtype=np.float32)
    tx = np.asarray(test_x, dtype=np.float32)
    if x.ndim != 2 or y.shape != x.shape or tx.ndim != 2 or tx.shape[1] != x.shape[1]:
        raise ValueError('Expected matching 2-D segment arrays')

    n, t = x.shape
    rng = np.random.RandomState(1907)
    order = rng.permutation(n)
    nv = max(1, min(n // 5, 400))
    va = order[:nv]
    tr = order[nv:]
    if len(tr) == 0:
        tr = order
        va = order

    xf, yf = x[tr], y[tr]
    xv, yv = x[va], y[va]
    wf = _segment_weights(yf)
    pilot_ids = _sample_indices(len(tr), t, 160, rng)
    F = _features(xf, pilot_ids)
    target = (xf - yf).reshape(-1)[pilot_ids]
    pilot = _make_model(70)
    pilot.fit(F, target, sample_weight=wf[pilot_ids // t])
    del F, target

    FV = _features(xv)
    artifact_v = pilot.predict(FV).reshape(xv.shape).astype(np.float32)
    gain_v = _fit_dct_filter(xf, yf, wf)
    linear_v = _apply_dct_filter(xv, gain_v)

    best = (float('inf'), 1.0, 0.0, 1.0)
    for sigma in (0.0, 0.5, 1.0, 1.7, 2.7):
        if sigma == 0.0:
            av = artifact_v
        else:
            av = gaussian_filter1d(artifact_v, sigma, axis=1, mode='reflect')
        for wh in (0.0, 0.5, 0.75, 1.0, 1.25, 1.5):
            for wd in (0.0, 0.25, 0.5, 0.75, 1.0):
                if wh + wd > 1.75:
                    continue
                pred = xv - wh * av + wd * (linear_v - xv)
                score = _relative_rmse(pred, yv)
                if score < best[0]:
                    best = (score, wh, wd, sigma)
    _, wh, wd, sigma = best
    del pilot, FV, artifact_v, linear_v, xf, yf, xv, yv
    gc.collect()

    wall = _segment_weights(y)
    final_ids = _sample_indices(n, t, 180, rng)
    FT = _features(x, final_ids)
    residual = (x - y).reshape(-1)[final_ids]
    model = _make_model(100)
    model.fit(FT, residual, sample_weight=wall[final_ids // t])
    del FT, residual
    gc.collect()

    Ftest = _features(tx)
    artifact = model.predict(Ftest).reshape(tx.shape).astype(np.float32)
    if sigma > 0.0:
        artifact = gaussian_filter1d(artifact, sigma, axis=1, mode='reflect')
    gain = _fit_dct_filter(x, y, wall)
    linear = _apply_dct_filter(tx, gain)
    pred = tx - wh * artifact + wd * (linear - tx)
    pred = np.nan_to_num(pred, nan=0.0, posinf=20.0, neginf=-20.0)
    return pred.astype(np.float32, copy=False)
