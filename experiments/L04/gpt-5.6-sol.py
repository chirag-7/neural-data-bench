import numpy as np
from scipy.ndimage import gaussian_filter1d
from scipy.special import expit
from sklearn.preprocessing import SplineTransformer
from sklearn.linear_model import PoissonRegressor


def _clean_fit(x):
    x = np.asarray(x, dtype=float)
    med = np.nanmedian(x, axis=0)
    med = np.where(np.isfinite(med), med, 0.0)
    return np.where(np.isfinite(x), x, med), med


def _clean_apply(x, med):
    x = np.asarray(x, dtype=float)
    return np.where(np.isfinite(x), x, med)


def _fit_spline(x, y, cfg):
    x, med = _clean_fit(x)
    kind, npk, nvk, alpha = cfg
    transformers = []
    bases = []
    limits = []
    dims = 1 if kind == "p" else 2
    knots_by_dim = [npk, nvk]
    for j in range(dims):
        z = x[:, j]
        lo, hi = np.quantile(z, [0.002, 0.998])
        if not np.isfinite(lo + hi) or hi <= lo + 1e-10:
            lo = float(np.min(z))
            hi = float(np.max(z))
        if hi <= lo + 1e-10:
            hi = lo + 1.0
        k = np.linspace(lo, hi, int(knots_by_dim[j]))[:, None]
        tr = SplineTransformer(knots=k, degree=3, include_bias=False,
                               extrapolation="constant", order="C")
        b = tr.fit_transform(np.clip(z, lo, hi)[:, None])
        transformers.append(tr)
        bases.append(b)
        limits.append((lo, hi))
    if kind == "p":
        f = bases[0]
    elif kind == "a":
        f = np.column_stack((bases[0], bases[1]))
    else:
        inter = (bases[0][:, :, None] * bases[1][:, None, :]).reshape(len(x), -1)
        f = np.column_stack((bases[0], bases[1], inter))
    model = PoissonRegressor(alpha=float(alpha), fit_intercept=True,
                             max_iter=250, tol=1e-6)
    model.fit(f, y)
    return ("spline", kind, med, transformers, limits, model)


def _predict_spline(obj, x):
    _, kind, med, transformers, limits, model = obj
    x = _clean_apply(x, med)
    bases = []
    for j, tr in enumerate(transformers):
        lo, hi = limits[j]
        bases.append(tr.transform(np.clip(x[:, j], lo, hi)[:, None]))
    if kind == "p":
        f = bases[0]
    elif kind == "a":
        f = np.column_stack((bases[0], bases[1]))
    else:
        inter = (bases[0][:, :, None] * bases[1][:, None, :]).reshape(len(x), -1)
        f = np.column_stack((bases[0], bases[1], inter))
    return model.predict(f)


def _fit_hist(x, y, cfg):
    x, med = _clean_fit(x)
    _, bins, sigma, prior, directional = cfg
    z = x[:, 0]
    lo, hi = np.quantile(z, [0.001, 0.999])
    if hi <= lo + 1e-10:
        lo, hi = float(np.min(z)), float(np.max(z))
    if hi <= lo + 1e-10:
        hi = lo + 1.0
    edges = np.linspace(lo, hi, int(bins) + 1)
    centers = 0.5 * (edges[:-1] + edges[1:])
    mean = max(float(np.mean(y)), 1e-10)
    if directional:
        av = np.abs(x[:, 1])
        scale = float(np.median(av[av > 1e-8])) if np.any(av > 1e-8) else 1.0
        scale = max(scale, float(np.std(x[:, 1])) * 0.2, 1e-6)
        wp = expit(np.clip(x[:, 1] / scale, -30.0, 30.0))
        weights = (wp, 1.0 - wp)
    else:
        scale = 1.0
        weights = (np.ones(len(x)),)
    rates = []
    for w in weights:
        occ = np.histogram(z, edges, weights=w)[0]
        spk = np.histogram(z, edges, weights=w * y)[0]
        occ = gaussian_filter1d(occ.astype(float), sigma, mode="nearest")
        spk = gaussian_filter1d(spk.astype(float), sigma, mode="nearest")
        rates.append((spk + prior * mean) / (occ + prior))
    return ("hist", med, centers, rates, scale, bool(directional))


def _predict_hist(obj, x):
    _, med, centers, rates, scale, directional = obj
    x = _clean_apply(x, med)
    r0 = np.interp(x[:, 0], centers, rates[0])
    if not directional:
        return r0
    w = expit(np.clip(x[:, 1] / scale, -30.0, 30.0))
    r1 = np.interp(x[:, 0], centers, rates[1])
    return w * r0 + (1.0 - w) * r1


def _fit_model(x, y, cfg):
    if cfg[0] == "h":
        return _fit_hist(x, y, cfg)
    return _fit_spline(x, y, cfg)


def _predict_model(obj, x):
    if obj[0] == "hist":
        return _predict_hist(obj, x)
    return _predict_spline(obj, x)


def _safe_prediction(p, mean, ymax):
    p = np.asarray(p, dtype=float).reshape(-1)
    p = np.nan_to_num(p, nan=mean, posinf=ymax, neginf=0.0)
    return np.clip(p, max(1e-10, mean * 1e-5), ymax)


def fit_predict(train_x, train_y, test_x):
    x = np.asarray(train_x, dtype=float)
    y = np.asarray(train_y, dtype=float).reshape(-1)
    tx = np.asarray(test_x, dtype=float)
    ntest = len(tx)
    if len(y) == 0:
        return np.zeros(ntest, dtype=float)
    y = np.nan_to_num(y, nan=0.0, posinf=0.0, neginf=0.0)
    y = np.maximum(y, 0.0)
    full_mean = float(np.mean(y))
    if np.sum(y) < 4 or full_mean <= 0.0:
        return np.full(ntest, max(full_mean, 0.0), dtype=float)

    configs = [
        ("p", 7, 0, .03), ("p", 10, 0, .004), ("p", 10, 0, .04),
        ("p", 15, 0, .004), ("p", 15, 0, .04),
        ("p", 21, 0, .006), ("p", 21, 0, .06), ("p", 28, 0, .012),
        ("a", 10, 5, .015), ("a", 15, 6, .008), ("a", 21, 6, .02),
        ("t", 9, 4, .035), ("t", 12, 5, .012),
        ("t", 12, 5, .06), ("t", 17, 5, .018), ("t", 20, 6, .04),
        ("h", 45, 1.5, 1.0, False), ("h", 65, 2.3, 1.5, False),
        ("h", 90, 3.2, 2.0, False),
        ("h", 45, 1.8, 2.0, True), ("h", 65, 2.7, 3.0, True),
        ("h", 85, 3.6, 4.0, True)
    ]
    shrink = np.array([0.0, 0.55, 0.75, 0.90, 1.0])
    scores = np.zeros((len(configs), len(shrink)), dtype=float)
    n = len(y)
    gap = min(50, max(5, n // 100))
    folds = [(int(.60 * n), int(.60 * n) + gap, int(.80 * n)),
             (int(.80 * n), int(.80 * n) + gap, n)]
    val_spikes = 0.0
    for end_train, start_val, end_val in folds:
        if start_val >= end_val or np.sum(y[:end_train]) < 2:
            continue
        yf = y[:end_train]
        yv = y[start_val:end_val]
        m = max(float(np.mean(yf)), 1e-10)
        cap = max(1.5, 1.5 * float(np.max(yf)), 20.0 * m)
        base = np.full(len(yv), m)
        base_ll = float(np.sum(yv * np.log(base) - base))
        val_spikes += float(np.sum(yv))
        for i, cfg in enumerate(configs):
            try:
                obj = _fit_model(x[:end_train], yf, cfg)
                raw = _safe_prediction(_predict_model(obj, x[start_val:end_val]), m, cap)
                for j, s in enumerate(shrink):
                    pred = (1.0 - s) * m + s * raw
                    scores[i, j] += float(np.sum(yv * np.log(pred) - pred) - base_ll)
            except Exception:
                pass

    best_shrink_idx = np.argmax(scores, axis=1)
    best_scores = scores[np.arange(len(configs)), best_shrink_idx]
    order = np.argsort(-best_scores)[:4]
    predictions = []
    selected_scores = []
    cap = max(1.5, 1.5 * float(np.max(y)), 20.0 * full_mean)
    for i in order:
        s = float(shrink[best_shrink_idx[i]])
        if s == 0.0:
            predictions.append(np.full(ntest, full_mean))
            selected_scores.append(best_scores[i])
            continue
        try:
            obj = _fit_model(x, y, configs[i])
            raw = _safe_prediction(_predict_model(obj, tx), full_mean, cap)
            predictions.append((1.0 - s) * full_mean + s * raw)
            selected_scores.append(best_scores[i])
        except Exception:
            pass
    if not predictions:
        return np.full(ntest, full_mean, dtype=float)
    sc = np.asarray(selected_scores, dtype=float)
    temperature = max(1.0, 0.03 * val_spikes)
    w = np.exp(np.clip((sc - np.max(sc)) / temperature, -30.0, 0.0))
    w /= np.sum(w)
    out = np.sum(np.asarray(predictions) * w[:, None], axis=0)
    return _safe_prediction(out, full_mean, cap)
