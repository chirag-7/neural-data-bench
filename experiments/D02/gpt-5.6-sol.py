import numpy as np
from scipy.signal import savgol_filter
from scipy.interpolate import PchipInterpolator


def _finite_rows(a):
    a = np.asarray(a, dtype=float).copy()
    for i in range(a.shape[0]):
        r = a[i]
        good = np.isfinite(r)
        if not np.any(good):
            r[:] = 0.0
        elif not np.all(good):
            ind = np.arange(r.size)
            r[~good] = np.interp(ind[~good], ind[good], r[good])
    return a


def _amplitude(row):
    v = row[np.isfinite(row)]
    if v.size == 0:
        return 0.0
    threshold = 0.5 * np.percentile(np.abs(v), 95)
    selected = v[np.abs(v) >= threshold]
    return float(np.median(selected if selected.size else v))


def _smooth(y, window):
    if window <= 1:
        return y.copy()
    w = min(int(window), y.shape[1] if y.shape[1] % 2 else y.shape[1] - 1)
    if w < 5:
        return y.copy()
    return savgol_filter(y, w, min(2, w - 2), axis=1, mode="interp")


def _linear_interp(a, y, q):
    out = np.empty((len(q), y.shape[1]), dtype=float)
    for k, x in enumerate(q):
        j = int(np.searchsorted(a, x))
        j = max(1, min(j, len(a) - 1))
        d = a[j] - a[j - 1]
        f = 0.5 if abs(d) < 1e-15 else (x - a[j - 1]) / d
        out[k] = (1.0 - f) * y[j - 1] + f * y[j]
    return out


def _isotonic_columns(y):
    result = np.empty_like(y)
    n, p = y.shape
    for col in range(p):
        levels = []
        weights = []
        counts = []
        for value in y[:, col]:
            levels.append(float(value))
            weights.append(1.0)
            counts.append(1)
            while len(levels) >= 2 and levels[-2] > levels[-1]:
                w = weights[-2] + weights[-1]
                value = (weights[-2] * levels[-2] +
                         weights[-1] * levels[-1]) / w
                count = counts[-2] + counts[-1]
                levels[-2:] = [value]
                weights[-2:] = [w]
                counts[-2:] = [count]
        pos = 0
        for value, count in zip(levels, counts):
            result[pos:pos + count, col] = value
            pos += count
    return result


def _poly_predict(a, y, q, degree, constrained, ridge):
    scale = max(float(np.max(np.abs(a))), 1.0)
    za = a / scale
    zq = np.asarray(q) / scale
    start = 1 if constrained else 0
    powers = np.arange(start, degree + 1)
    X = np.column_stack([za ** p for p in powers])
    Q = np.column_stack([zq ** p for p in powers])
    gram = X.T @ X
    penalty = np.eye(len(powers)) * float(ridge)
    if not constrained and len(powers):
        penalty[0, 0] = 0.0
    try:
        coef = np.linalg.solve(gram + penalty, X.T @ y)
    except np.linalg.LinAlgError:
        coef = np.linalg.pinv(gram + penalty) @ (X.T @ y)
    return Q @ coef


def _predict_model(spec, a, y, q):
    kind = spec[0]
    q = np.asarray(q, dtype=float)
    if kind == "local_y":
        return _linear_interp(a, y, q)
    if kind == "local_gain":
        denom = np.where(np.abs(a) > 1e-12, a, 1.0)
        return _linear_interp(a, y / denom[:, None], q) * q[:, None]
    if kind == "iso":
        return _linear_interp(a, _isotonic_columns(y), q)
    if kind == "pchip_y":
        return np.asarray(PchipInterpolator(a, y, axis=0)(q))
    if kind == "pchip_gain":
        denom = np.where(np.abs(a) > 1e-12, a, 1.0)
        gain = y / denom[:, None]
        return np.asarray(PchipInterpolator(a, gain, axis=0)(q)) * q[:, None]
    if kind == "poly":
        return _poly_predict(a, y, q, spec[1], spec[2], spec[3])
    raise ValueError("unknown model")


def fit_predict(train_x, train_y, test_x):
    train_x = _finite_rows(np.asarray(train_x, dtype=float))
    train_y = _finite_rows(np.asarray(train_y, dtype=float))
    test_x = _finite_rows(np.asarray(test_x, dtype=float))

    amplitudes = np.array([_amplitude(r) for r in train_x])
    test_amplitudes = np.array([_amplitude(r) for r in test_x])
    order = np.argsort(amplitudes)
    amplitudes = amplitudes[order]
    train_y = train_y[order]

    windows = [1, 5, 9, 15, 25, 41]
    candidates = [
        (("local_y",), "local_y"),
        (("local_gain",), "local_gain"),
        (("iso",), "isotonic"),
        (("pchip_y",), "pchip_y"),
        (("pchip_gain",), "pchip_gain"),
        (("poly", 1, True, 0.0), "constrained_linear"),
        (("poly", 2, True, 0.0), "constrained_quadratic"),
        (("poly", 2, True, 0.001), "constrained_quadratic"),
        (("poly", 2, True, 0.01), "constrained_quadratic"),
        (("poly", 1, False, 0.0), "affine"),
        (("poly", 2, False, 0.001), "quadratic"),
        (("poly", 2, False, 0.01), "quadratic"),
    ]

    records = []
    interior = list(range(1, len(amplitudes) - 1))
    if not interior:
        interior = list(range(len(amplitudes)))

    for window in windows:
        sy = _smooth(train_y, window)
        for spec, family in candidates:
            errors = []
            for held in interior:
                keep = np.arange(len(amplitudes)) != held
                if np.sum(keep) < 2:
                    continue
                try:
                    pred = _predict_model(
                        spec, amplitudes[keep], sy[keep],
                        np.array([amplitudes[held]]))[0]
                    if np.all(np.isfinite(pred)):
                        errors.append(np.mean((pred - train_y[held]) ** 2))
                except Exception:
                    pass
            score = float(np.mean(errors)) if errors else np.inf
            records.append((score, window, spec, family))

    best_by_family = {}
    for rec in records:
        family = rec[3]
        if family not in best_by_family or rec[0] < best_by_family[family][0]:
            best_by_family[family] = rec
    selected = sorted(best_by_family.values(), key=lambda z: z[0])[:5]

    predictions = []
    scores = []
    for score, window, spec, _ in selected:
        try:
            sy = _smooth(train_y, window)
            pred = _predict_model(spec, amplitudes, sy, test_amplitudes)
            if pred.shape == test_x.shape and np.all(np.isfinite(pred)):
                predictions.append(pred)
                scores.append(score)
        except Exception:
            pass

    if not predictions:
        pred = _linear_interp(amplitudes, _smooth(train_y, 9), test_amplitudes)
    else:
        scores = np.asarray(scores, dtype=float)
        best = float(np.min(scores))
        temperature = max(0.05 * max(best, 1e-8), 1e-10)
        weights = np.exp(-np.minimum((scores - best) / temperature, 50.0))
        weights /= np.sum(weights)
        pred = np.sum(np.asarray(predictions) * weights[:, None, None], axis=0)

    reference = _smooth(train_y, 9)
    span = max(float(np.percentile(reference, 99) -
                     np.percentile(reference, 1)), 1e-6)
    lower = np.min(reference, axis=0) - 0.25 * span
    upper = np.max(reference, axis=0) + 0.25 * span
    pred = np.maximum(lower[None, :], np.minimum(upper[None, :], pred))
    pred = np.nan_to_num(pred, nan=0.0, posinf=upper.max(), neginf=lower.min())
    return np.asarray(pred, dtype=float).reshape(test_x.shape)
