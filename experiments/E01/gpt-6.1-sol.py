import numpy as np
from scipy.ndimage import gaussian_filter1d
from scipy.optimize import minimize


def _baseline(y):
    mean = y.mean(axis=0)
    smooth = gaussian_filter1d(mean, 1.25, axis=0, mode='nearest')
    return np.maximum(0.97 * smooth + 0.03 * mean.mean(axis=0), 1e-6)


def _features(x, z, sigma):
    a = np.sqrt(gaussian_filter1d(x, sigma, axis=1, mode='nearest') + 0.05)
    b = np.sqrt(gaussian_filter1d(z, sigma, axis=1, mode='nearest') + 0.05)
    template = a.mean(axis=0, keepdims=True)
    a = a - template
    b = b - template
    scale = np.sqrt(np.mean(a * a, axis=(0, 1)) + 0.015)
    a = a / scale
    b = b / scale
    flat = a.reshape(-1, a.shape[-1])
    cov = flat.T @ flat / flat.shape[0]
    values, vectors = np.linalg.eigh(cov)
    rank = min(24, vectors.shape[1])
    order = np.argsort(values)[::-1][:rank]
    projection = vectors[:, order] / np.sqrt(np.maximum(values[order], 0) + 0.5)
    a = a @ projection
    b = b @ projection
    t = np.arange(a.shape[1])

    def expand(v):
        parts = [v,
                 v[:, np.clip(t - 2, 0, len(t) - 1)],
                 v[:, np.clip(t + 2, 0, len(t) - 1)]]
        global_state = v[:, :, :min(12, rank)].mean(axis=1, keepdims=True)
        parts.append(np.broadcast_to(global_state,
                                     (v.shape[0], v.shape[1], global_state.shape[2])))
        q = min(4, rank)
        products = [v[:, :, i:i+1] * v[:, :, j:j+1]
                    for i in range(q) for j in range(i, q)]
        if products:
            parts.append(np.concatenate(products, axis=2))
        return np.concatenate(parts, axis=2)

    a, b = expand(a), expand(b)
    center = a.mean(axis=(0, 1))
    # Only normalize the quadratic terms; preserve PCA reliability scaling.
    normalizer = np.ones(a.shape[-1])
    q = min(4, rank)
    nq = q * (q + 1) // 2
    if nq:
        normalizer[-nq:] = np.maximum(a[:, :, -nq:].std(axis=(0, 1)), 0.5)
    a = ((a - center) / normalizer).reshape(-1, a.shape[-1])
    b = ((b - center) / normalizer).reshape(-1, b.shape[-1])
    a = np.column_stack((a, np.ones(a.shape[0])))
    b = np.column_stack((b, np.ones(b.shape[0])))
    return np.ascontiguousarray(a), np.ascontiguousarray(b)


def _fit_poisson(f, y, offset, strength, initial=None):
    d, outputs = f.shape[1], y.shape[1]
    if initial is None:
        initial = np.zeros((d, outputs), dtype=np.float64)
    penalty = np.full(d, strength)
    penalty[-1] = strength * 0.01
    inv_n = 1.0 / f.shape[0]

    def objective(vector):
        w = vector.reshape(d, outputs)
        raw = offset + f @ w
        eta = np.clip(raw, -18.0, 8.0)
        rate = np.exp(eta)
        loss = np.sum(rate - y * eta) * inv_n
        loss += 0.5 * np.sum(penalty[:, None] * w * w)
        residual = (rate - y) * ((raw > -18.0) & (raw < 8.0))
        gradient = (f.T @ residual) * inv_n + penalty[:, None] * w
        return float(loss), gradient.ravel()

    result = minimize(objective, initial.ravel(), jac=True, method='L-BFGS-B',
                      options={'maxiter': 55, 'maxls': 15,
                               'ftol': 2e-7, 'gtol': 2e-5, 'maxcor': 8})
    w = result.x.reshape(d, outputs)
    if not np.all(np.isfinite(w)):
        w = initial.copy()
    return w


def _predict(f, w, baseline, trials, bins):
    offset = np.tile(np.log(baseline), (trials, 1))
    prediction = np.exp(np.clip(offset + f @ w, -18.0, 8.0))
    return prediction.reshape(trials, bins, baseline.shape[-1])


def fit_predict(train_x, train_y, test_x):
    x = np.asarray(train_x, dtype=np.float64)
    y = np.asarray(train_y, dtype=np.float64)
    z = np.asarray(test_x, dtype=np.float64)
    x = np.maximum(np.nan_to_num(x, nan=0.0, posinf=0.0, neginf=0.0), 0)
    y = np.maximum(np.nan_to_num(y, nan=0.0, posinf=0.0, neginf=0.0), 0)
    z = np.maximum(np.nan_to_num(z, nan=0.0, posinf=0.0, neginf=0.0), 0)
    n, bins, outputs = y.shape
    widths = (1.0, 2.0, 3.5)
    strengths = (0.4, 0.07, 0.01)
    configurations = [(s, r) for s in widths for r in strengths]
    oof = np.empty((len(configurations), n, bins, outputs), dtype=np.float64)
    oof_base = np.empty_like(y)
    permutation = np.random.RandomState(1729).permutation(n)
    folds = np.array_split(permutation, 3)

    for valid in folds:
        mask = np.ones(n, dtype=bool)
        mask[valid] = False
        fit_ids = np.flatnonzero(mask)
        base = _baseline(y[fit_ids])
        oof_base[valid] = base
        targets = y[fit_ids].reshape(-1, outputs)
        offset = np.tile(np.log(base), (len(fit_ids), 1))
        for si, sigma in enumerate(widths):
            f, v = _features(x[fit_ids], x[valid], sigma)
            warm = None
            for ri, strength in enumerate(strengths):
                warm = _fit_poisson(f, targets, offset, strength, warm)
                oof[si * len(strengths) + ri, valid] = _predict(
                    v, warm, base, len(valid), bins)

    scores = np.sum(y[None] * np.log(np.maximum(oof, 1e-12)) - oof,
                    axis=(1, 2))
    baseline_score = np.sum(y * np.log(np.maximum(oof_base, 1e-12)) - oof_base,
                            axis=(0, 1))
    selected = np.argsort(scores.sum(axis=1))[::-1][:3]
    blend_scores = np.vstack((scores[selected], baseline_score[None]))
    logits = (blend_scores - blend_scores.max(axis=0, keepdims=True)) / 8.0
    logits[-1] += np.log(0.5)
    weights = np.exp(np.clip(logits, -60.0, 0.0))
    weights /= weights.sum(axis=0, keepdims=True)

    base = _baseline(y)
    targets = y.reshape(-1, outputs)
    offset = np.tile(np.log(base), (n, 1))
    prediction = np.broadcast_to(base, (len(z), bins, outputs)).copy()
    prediction *= weights[-1][None, None, :]
    selected_positions = {int(c): i for i, c in enumerate(selected)}
    for si, sigma in enumerate(widths):
        chosen = [ri for ri in range(len(strengths))
                  if si * len(strengths) + ri in selected_positions]
        if not chosen:
            continue
        f, v = _features(x, z, sigma)
        warm = None
        for ri in chosen:
            warm = _fit_poisson(f, targets, offset, strengths[ri], warm)
            p = _predict(v, warm, base, len(z), bins)
            position = selected_positions[si * len(strengths) + ri]
            prediction += p * weights[position][None, None, :]
    return np.maximum(np.nan_to_num(prediction, nan=1e-6,
                                    posinf=1000.0, neginf=1e-6), 1e-8)
