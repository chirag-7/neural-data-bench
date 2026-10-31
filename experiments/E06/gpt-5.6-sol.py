import numpy as np


def _solve(a, b):
    try:
        return np.linalg.solve(a, b)
    except np.linalg.LinAlgError:
        return np.linalg.pinv(a, rcond=1e-10) @ b


def _fit_shared(x, y):
    n, t, q = x.shape
    h = y.shape[1]
    last = x[:, -1, :]
    xx = (x - last[:, None, :]).transpose(0, 2, 1).reshape(n * q, t)
    yy = (y - last[:, None, :]).transpose(0, 2, 1).reshape(n * q, h)
    xm = xx.mean(axis=0)
    ym = yy.mean(axis=0)
    xc = xx - xm
    gram = xc.T @ xc
    gram.flat[::t + 1] += 1.0
    coef = _solve(gram, xc.T @ (yy - ym))
    return xm, ym, coef


def _predict_shared(model, x, h):
    xm, ym, coef = model
    n, t, q = x.shape
    last = x[:, -1, :]
    xx = (x - last[:, None, :]).transpose(0, 2, 1).reshape(n * q, t)
    out = (xx - xm) @ coef + ym
    out = out.reshape(n, q, h).transpose(0, 2, 1)
    return out + last[:, None, :]


def _fit_neuron(x, y):
    n, t, q = x.shape
    h = y.shape[1]
    xm = np.empty((q, t), dtype=np.float64)
    ym = np.empty((q, h), dtype=np.float64)
    coef = np.empty((q, t, h), dtype=np.float64)
    last = x[:, -1, :]
    for j in range(q):
        xx = x[:, :, j] - last[:, j, None]
        yy = y[:, :, j] - last[:, j, None]
        xm[j] = xx.mean(axis=0)
        ym[j] = yy.mean(axis=0)
        xc = xx - xm[j]
        scale = max(float(np.sum(xc * xc) / t), 1e-8)
        gram = xc.T @ xc
        gram.flat[::t + 1] += 0.20 * scale
        coef[j] = _solve(gram, xc.T @ (yy - ym[j]))
    return xm, ym, coef


def _predict_neuron(model, x, h):
    xm, ym, coef = model
    n, _, q = x.shape
    last = x[:, -1, :]
    out = np.empty((n, h, q), dtype=np.float64)
    for j in range(q):
        xx = x[:, :, j] - last[:, j, None]
        out[:, :, j] = (xx - xm[j]) @ coef[j] + ym[j] + last[:, j, None]
    return out


def _latent_features(x, mean, vectors):
    z = np.einsum('ntq,qk->ntk', x - mean, vectors, optimize=True)
    pieces = [z[:, -1, :]]
    for width in (4, 8, 16, 32, 64):
        width = min(width, z.shape[1])
        pieces.append(z[:, -width:, :].mean(axis=1))
    w4 = min(4, z.shape[1] // 2)
    w8 = min(8, z.shape[1] // 2)
    pieces.append(z[:, -w4:, :].mean(axis=1) -
                  z[:, -2 * w4:-w4, :].mean(axis=1))
    pieces.append(z[:, -w8:, :].mean(axis=1) -
                  z[:, -2 * w8:-w8, :].mean(axis=1))
    return np.concatenate(pieces, axis=1)


def _fit_latent(x, y):
    n, _, q = x.shape
    h = y.shape[1]
    frames = np.concatenate((x.reshape(-1, q), y.reshape(-1, q)), axis=0)
    mean = frames.mean(axis=0)
    centered = frames - mean
    covariance = centered.T @ centered / max(len(frames), 1)
    values, vectors = np.linalg.eigh(covariance)
    k = min(20, q, max(1, n - 2))
    vectors = vectors[:, np.argsort(values)[-k:]]
    features = _latent_features(x, mean, vectors)
    fm = features.mean(axis=0)
    fs = features.std(axis=0)
    fs = np.where(fs > 1e-8, fs, 1.0)
    design = (features - fm) / fs
    last = x[:, -1, :]
    target = np.einsum('nhq,qk->nhk', y - last[:, None, :],
                       vectors, optimize=True).reshape(n, h * k)
    tm = target.mean(axis=0)
    dc = design - design.mean(axis=0)
    p = design.shape[1]
    gram = dc.T @ dc
    gram.flat[::p + 1] += 25.0
    coef = _solve(gram, dc.T @ (target - tm))
    return mean, vectors, fm, fs, design.mean(axis=0), tm, coef, h


def _predict_latent(model, x, h):
    mean, vectors, fm, fs, dm, tm, coef, fitted_h = model
    features = (_latent_features(x, mean, vectors) - fm) / fs
    delta = (features - dm) @ coef + tm
    k = vectors.shape[1]
    delta = delta.reshape(len(x), fitted_h, k)
    out = np.einsum('nhk,qk->nhq', delta, vectors, optimize=True)
    return out[:, :h, :] + x[:, -1:, :]


def _baselines(x, h):
    last = x[:, -1:, :]
    persistence = np.repeat(last, h, axis=1)
    history_mean = np.repeat(x.mean(axis=1)[:, None, :], h, axis=1)
    width = min(12, x.shape[1])
    times = np.arange(width, dtype=np.float64)
    times -= times.mean()
    slope = np.einsum('t,ntq->nq', times, x[:, -width:, :])
    slope /= max(float(times @ times), 1.0)
    step = np.arange(1, h + 1, dtype=np.float64)
    gain = 6.0 * (1.0 - np.exp(-step / 6.0))
    trend = last + gain[None, :, None] * slope[:, None, :]
    return persistence, history_mean, trend


def _candidates(models, x, h):
    shared, neuron, latent = models
    base = _baselines(x, h)
    return [_predict_shared(shared, x, h),
            _predict_neuron(neuron, x, h),
            _predict_latent(latent, x, h),
            base[0], base[1], base[2]]


def _fit_models(x, y):
    return (_fit_shared(x, y), _fit_neuron(x, y), _fit_latent(x, y))


def _simplex_weights(predictions, truth):
    m = len(predictions)
    h = truth.shape[1]
    weights = np.zeros((h, m), dtype=np.float64)
    for horizon in range(h):
        errors = np.stack([(p[:, horizon, :] - truth[:, horizon, :]).ravel()
                           for p in predictions])
        gram = errors @ errors.T / errors.shape[1]
        jitter = max(float(np.trace(gram) / m), 1.0) * 1e-12
        gram.flat[::m + 1] += jitter
        best_loss = np.inf
        best = None
        for mask in range(1, 1 << m):
            ids = [j for j in range(m) if mask & (1 << j)]
            size = len(ids)
            sub = gram[np.ix_(ids, ids)]
            system = np.empty((size + 1, size + 1), dtype=np.float64)
            system[:size, :size] = sub
            system[:size, size] = 1.0
            system[size, :size] = 1.0
            system[size, size] = 0.0
            rhs = np.zeros(size + 1, dtype=np.float64)
            rhs[size] = 1.0
            solution = _solve(system, rhs)[:size]
            if np.min(solution) >= -1e-9:
                solution = np.maximum(solution, 0.0)
                solution /= solution.sum()
                loss = float(solution @ sub @ solution)
                if loss < best_loss:
                    best_loss = loss
                    best = np.zeros(m, dtype=np.float64)
                    best[ids] = solution
        weights[horizon] = best if best is not None else np.eye(1, m, 0)[0]
    smooth = np.empty_like(weights)
    for horizon in range(h):
        lo = max(0, horizon - 2)
        hi = min(h, horizon + 3)
        smooth[horizon] = weights[lo:hi].mean(axis=0)
    smooth *= 0.90
    smooth[:, 0] += 0.10
    smooth /= smooth.sum(axis=1, keepdims=True)
    return smooth


def fit_predict(train_x, train_y, test_x, train_groups):
    x = np.asarray(train_x, dtype=np.float64)
    y = np.asarray(train_y, dtype=np.float64)
    test = np.asarray(test_x, dtype=np.float64)
    n = len(x)
    h = y.shape[1]
    cut = max(2, min(n - 1, int(0.75 * n)))
    validation_models = _fit_models(x[:cut], y[:cut])
    validation_predictions = _candidates(validation_models, x[cut:], h)
    weights = _simplex_weights(validation_predictions, y[cut:])
    full_models = _fit_models(x, y)
    predictions = _candidates(full_models, test, h)
    output = np.zeros((len(test), h, y.shape[2]), dtype=np.float64)
    for j, prediction in enumerate(predictions):
        output += weights[:, j][None, :, None] * prediction
    fallback = np.repeat(test[:, -1:, :], h, axis=1)
    return np.where(np.isfinite(output), output, fallback)
