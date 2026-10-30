import numpy as np
from scipy.ndimage import gaussian_filter1d, uniform_filter1d
from scipy.optimize import minimize
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.linear_model import Ridge
from sklearn.ensemble import HistGradientBoostingRegressor


def _bands(x):
    parts = []
    previous = x
    for sigma in (1, 2, 4, 8, 16, 32):
        smooth = gaussian_filter1d(x, sigma, axis=1, mode='reflect')
        parts.append(previous - smooth)
        previous = smooth
    parts.append(previous)
    return np.stack(parts, axis=1).astype(np.float32)


def _cache(x):
    b = _bands(x)
    r = np.sqrt(np.mean(b * b, axis=2) + 1e-10)
    total = np.sqrt(np.mean(x * x, axis=1) + 1e-10)
    peak = np.max(np.abs(x), axis=1) / total
    delta = np.sqrt(np.mean(np.diff(x, axis=1) ** 2, axis=1) + 1e-10)
    kurt = np.mean((x / total[:, None]) ** 4, axis=1)
    g = np.column_stack((np.log(r),
                         np.abs(np.mean(x, axis=1)) / total,
                         np.log(np.maximum(peak, 1e-5)),
                         np.log(delta),
                         np.log(np.maximum(kurt, 1e-5)))).astype(np.float32)
    local1 = np.empty_like(b)
    local2 = np.empty_like(b)
    for k in range(7):
        size = min(x.shape[1], 6 * (2 ** k) + 1)
        local1[:, k] = np.sqrt(np.maximum(uniform_filter1d(
            b[:, k] ** 2, size=size, axis=1, mode='reflect'), 0) + 1e-10)
        local2[:, k] = np.sqrt(np.maximum(uniform_filter1d(
            b[:, k] ** 2, size=min(x.shape[1], 4 * size),
            axis=1, mode='reflect'), 0) + 1e-10)
    return {'b': b, 'r': r, 'g': g, 'l1': local1, 'l2': local2}


def _fit_scales(cache, yb, indices):
    g = cache['g'][indices]
    first = StandardScaler().fit(g)
    poly = PolynomialFeatures(2, include_bias=False)
    z = poly.fit_transform(first.transform(g))
    second = StandardScaler().fit(z)
    signal = np.sqrt(np.mean(yb[indices] ** 2, axis=2) + 1e-10)
    artifact = np.sqrt(np.mean((cache['b'][indices] - yb[indices]) ** 2,
                               axis=2) + 1e-10)
    target = np.log(np.column_stack((signal, artifact)))
    model = Ridge(alpha=80.0).fit(second.transform(z), target)
    return first, poly, second, model


def _scales(model, cache):
    first, poly, second, ridge = model
    z = second.transform(poly.transform(first.transform(cache['g'])))
    amplitudes = np.exp(np.clip(ridge.predict(z), -9, 3)).astype(np.float32)
    s = np.maximum(amplitudes[:, :7], 1e-4)
    a = np.maximum(amplitudes[:, 7:], 1e-4)
    gain = s * s / (s * s + a * a + 1e-12)
    return s, gain


def _features(cache, s, gain, k, rows, positions):
    b = cache['b']
    length = b.shape[2]
    amplitude = s[rows, k]
    value = b[rows, k, positions]
    sign = np.where(value >= 0, 1.0, -1.0).astype(np.float32)
    cols = [np.abs(value) / amplitude]
    step = 2 ** k
    for offset in (-4, -2, -1, 1, 2, 4):
        p = np.clip(positions + offset * step, 0, length - 1)
        cols.append(b[rows, k, p] * sign / amplitude)
    for j in (max(0, k - 1), min(6, k + 1), min(6, k + 2)):
        cols.append(b[rows, j, positions] * sign / s[rows, j])
        cols.append(cache['l1'][rows, j, positions] / s[rows, j])
    cols.extend((cache['l1'][rows, k, positions] / amplitude,
                 cache['l2'][rows, k, positions] / amplitude,
                 cache['r'][rows, k] / amplitude,
                 gain[rows, k], np.log(amplitude),
                 np.minimum(positions, length - 1 - positions) / float(length)))
    for j in range(cache['g'].shape[1]):
        cols.append(cache['g'][rows, j])
    features = np.column_stack(cols).astype(np.float32)
    return np.clip(features, -200, 200), sign


def _fit_and_predict(cache, yb, y_energy, train_indices, destination,
                     destination_indices, seed):
    scale_model = _fit_scales(cache, yb, train_indices)
    s, gain = _scales(scale_model, cache)
    if destination is cache:
        ds, dg = s, gain
    else:
        ds, dg = _scales(scale_model, destination)
    rng = np.random.RandomState(seed)
    length = cache['b'].shape[2]
    rows = np.repeat(train_indices, 24)
    positions = rng.randint(0, length, size=len(rows))
    # Include boundary samples, where reflected smoothing behaves differently.
    positions[::24] = 0
    positions[1::24] = length - 1
    dr = np.repeat(destination_indices, length)
    dp = np.tile(np.arange(length), len(destination_indices))
    components = np.empty((len(destination_indices), 14, length), dtype=np.float32)
    for k in range(7):
        features, sign = _features(cache, s, gain, k, rows, positions)
        baseline = gain[rows, k] * cache['b'][rows, k, positions]
        target = (yb[rows, k, positions] - baseline) * sign / s[rows, k]
        weight = s[rows, k] ** 2 / y_energy[rows]
        weight = np.clip(weight / (np.mean(weight) + 1e-12), 0.025, 30)
        learner = HistGradientBoostingRegressor(
            loss='squared_error', learning_rate=0.075, max_iter=65,
            max_leaf_nodes=15, max_bins=63, min_samples_leaf=90,
            l2_regularization=8.0, early_stopping=False,
            random_state=seed + k)
        learner.fit(features, np.clip(target, -15, 15), sample_weight=weight)
        del features
        # Predict in batches to bound temporary feature memory.
        corrections = np.empty(len(dr), dtype=np.float32)
        for start in range(0, len(dr), 65536):
            stop = min(start + 65536, len(dr))
            f, sg = _features(destination, ds, dg, k,
                              dr[start:stop], dp[start:stop])
            corrections[start:stop] = learner.predict(f) * sg * ds[dr[start:stop], k]
        components[:, k] = (dg[destination_indices, k, None] *
                             destination['b'][destination_indices, k])
        components[:, 7 + k] = corrections.reshape(len(destination_indices), length)
    return components


def _calibrate(components, clean):
    c = components.astype(np.float64)
    y = clean.astype(np.float64)
    energy = np.sum(y * y, axis=1) + 1e-12
    gram = np.einsum('nkt,njt->nkj', c, c, optimize=True) / energy[:, None, None]
    cross = np.einsum('nkt,nt->nk', c, y, optimize=True) / energy[:, None]
    prior = np.r_[np.ones(7), np.full(7, 0.8)]
    def objective(w):
        gw = np.einsum('nij,j->ni', gram, w)
        squared = np.maximum(1 - 2 * cross.dot(w) + np.sum(gw * w, axis=1), 1e-10)
        roots = np.sqrt(squared)
        penalty = 0.0004 * np.sum((w - prior) ** 2)
        gradient = np.mean((gw - cross) / roots[:, None], axis=0)
        gradient += 0.0008 * (w - prior)
        return np.mean(roots) + penalty, gradient
    result = minimize(objective, prior, method='L-BFGS-B', jac=True,
                      bounds=[(0.0, 1.7)] * 7 + [(0.0, 1.3)] * 7,
                      options={'maxiter': 100, 'ftol': 1e-9})
    return result.x if np.all(np.isfinite(result.x)) else prior


def fit_predict(train_x, train_y, test_x):
    x = np.asarray(train_x, dtype=np.float32)
    y = np.asarray(train_y, dtype=np.float32)
    test = np.asarray(test_x, dtype=np.float32)
    if test.shape[0] == 0:
        return np.empty_like(test)
    cache = _cache(x)
    yb = _bands(y)
    energy = np.mean(y * y, axis=1) + 1e-10
    rng = np.random.RandomState(2026)
    order = rng.permutation(len(x))
    nval = max(1, int(round(0.15 * len(x))))
    validation = order[:nval]
    training = order[nval:]
    validation_components = _fit_and_predict(
        cache, yb, energy, training, cache, validation, 107)
    weights = _calibrate(validation_components, y[validation])
    del validation_components
    test_cache = _cache(test)
    components = _fit_and_predict(
        cache, yb, energy, np.arange(len(x)), test_cache,
        np.arange(len(test)), 107)
    prediction = np.einsum('nkt,k->nt', components, weights, optimize=True)
    return prediction.astype(np.float32)
