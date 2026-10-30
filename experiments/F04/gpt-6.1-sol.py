import numpy as np
from scipy.fft import dctn, idctn
from scipy.optimize import minimize
from scipy.special import expit


def _features(D, T, freq, sigma, nonlinear, landmarks, rank):
    filt = np.exp(-0.5 * sigma * sigma * freq)
    Z, V = D * filt, T * filt
    scale = np.sqrt(max(np.mean(np.sum(Z * Z, axis=1)), 1e-20))
    Z, V = Z / scale, V / scale
    A = Z @ Z[landmarks].T
    B = V @ Z[landmarks].T
    if nonlinear:
        qscale = max(np.mean(np.sum(Z * Z, axis=1) ** 2), 1e-12)
        h = int(round(np.sqrt(D.shape[1])))
        band = filt - np.exp(-2.0 * sigma * sigma * freq)
        U = idctn((D * band).reshape(-1, h, h), axes=(1, 2),
                  norm='ortho').reshape(D.shape)
        R = idctn((T * band).reshape(-1, h, h), axes=(1, 2),
                  norm='ortho').reshape(T.shape)
        U, R = U * U, R * R
        center = U.mean(axis=0)
        U, R = U - center, R - center
        es = np.sqrt(max(np.mean(np.sum(U * U, axis=1)), 1e-20))
        U, R = U / es, R / es
        A = (A + 0.5 * A * A / qscale + 0.5 * (U @ U[landmarks].T)) / 2.0
        B = (B + 0.5 * B * B / qscale + 0.5 * (R @ U[landmarks].T)) / 2.0
    K = A[landmarks]
    vals, vecs = np.linalg.eigh((K + K.T) * 0.5)
    keep = np.flatnonzero(vals > max(vals[-1] * 1e-9, 1e-12))[-rank:]
    if len(keep) == 0:
        return np.zeros((len(D), 1)), np.zeros((len(T), 1))
    projection = vecs[:, keep] / np.sqrt(vals[keep])
    F, G = A @ projection, B @ projection
    center = F.mean(axis=0)
    F, G = F - center, G - center
    fs = np.sqrt(max(np.mean(np.sum(F * F, axis=1)), 1e-20))
    return np.ascontiguousarray(F / fs), np.ascontiguousarray(G / fs)


def _fit(F, Y, weights, alpha, link, initial=None, iterations=60):
    n, p = F.shape
    q = Y.shape[1]
    total = weights.sum()
    prior = 0.25 / total
    base = (weights @ Y) / total + prior
    target = (Y + prior) / base
    wn = weights[:, None] / total
    alpha = np.broadcast_to(np.asarray(alpha, dtype=float), (q,))
    if initial is None:
        initial = np.zeros((p + 1, q))
        if link == 'softplus':
            initial[-1] = np.log(np.expm1(1.0))
    else:
        initial = initial.copy()

    def objective(flat):
        W = flat.reshape(p + 1, q)
        eta = F @ W[:-1] + W[-1]
        if link == 'exp':
            e = np.exp(np.minimum(eta, 20.0))
            excess = np.maximum(eta - 20.0, 0.0)
            phi = e * (1.0 + excess + 0.5 * excess * excess)
            loss = phi - target * eta
            residual = e * (1.0 + excess) - target
        else:
            phi = np.logaddexp(0.0, eta)
            safe = np.maximum(phi, 1e-300)
            logphi = np.where(eta < -20.0, eta, np.log(safe))
            sig = expit(eta)
            ratio = np.where(eta < -20.0, 1.0, sig / safe)
            loss = phi - target * logphi
            residual = sig - target * ratio
        residual = residual * wn
        value = np.sum(wn * loss) + 0.5 * np.sum(alpha * W[:-1] ** 2)
        grad = np.empty_like(W)
        grad[:-1] = F.T @ residual + alpha * W[:-1]
        grad[-1] = residual.sum(axis=0)
        return float(value), grad.ravel()

    result = minimize(objective, initial.ravel(), jac=True, method='L-BFGS-B',
                      options={'maxiter': iterations, 'ftol': 2e-8,
                               'gtol': 2e-5, 'maxcor': 8, 'maxls': 20})
    fitted = result.x.reshape(p + 1, q)
    if not np.all(np.isfinite(fitted)):
        fitted = initial
    ceiling = np.maximum(4.0, 3.0 * Y.max(axis=0) + 2.0)
    return fitted, base, ceiling


def _predict(F, fitted, base, ceiling, link):
    eta = F @ fitted[:-1] + fitted[-1]
    if link == 'exp':
        relative = np.exp(np.clip(eta, -30.0, 15.0))
    else:
        relative = np.logaddexp(0.0, eta)
    return np.clip(base * relative, 1e-8, ceiling)


def _ensemble_weights(P, Y, counts, base):
    n, m, q = P.shape
    wn = counts / counts.sum()
    prior = np.full(m, 0.9 / (m - 1))
    prior[0] = 0.1
    regularization = 0.025 * np.sqrt(100.0 / max(n, 20))
    result = np.empty((m, q))
    constraint = {'type': 'eq', 'fun': lambda z: z.sum() - 1.0,
                  'jac': lambda z: np.ones_like(z)}
    for j in range(q):
        A = P[:, :, j] / base[j]
        target = Y[:, j] / base[j]

        def objective(z):
            mu = np.maximum(A @ z, 1e-12)
            delta = z - prior
            value = np.sum(wn * (mu - target * np.log(mu)))
            value += regularization * np.sum(delta * delta)
            grad = A.T @ (wn * (1.0 - target / mu))
            grad += 2.0 * regularization * delta
            return float(value), grad

        opt = minimize(objective, prior.copy(), jac=True, method='SLSQP',
                       bounds=[(0.0, 1.0)] * m, constraints=constraint,
                       options={'maxiter': 65, 'ftol': 1e-8})
        z = np.maximum(opt.x, 0.0) if np.all(np.isfinite(opt.x)) else prior.copy()
        z = z / max(z.sum(), 1e-12)
        result[:, j] = 0.95 * z + 0.05 * prior
    return result


def fit_predict(train_x, train_y, test_x):
    X = np.asarray(train_x, dtype=np.float64)
    raw_y = np.asarray(train_y, dtype=np.float64)
    test = np.asarray(test_x, dtype=np.float64)
    q = raw_y.shape[1]
    if len(test) == 0:
        return np.empty((0, q), dtype=float)
    X, inverse = np.unique(X, axis=0, return_inverse=True)
    n = len(X)
    counts = np.bincount(inverse, minlength=n).astype(float)
    Y = np.zeros((n, q), dtype=float)
    np.add.at(Y, inverse, raw_y)
    Y /= counts[:, None]
    base = (counts @ Y + 0.25) / counts.sum()
    if n < 9:
        return np.tile(base, (len(test), 1))
    test, test_inverse = np.unique(test, axis=0, return_inverse=True)
    center = X.mean(axis=0)
    scale = np.sqrt(max(np.mean((X - center) ** 2), 1e-20))
    h = int(round(np.sqrt(X.shape[1])))
    D = dctn(((X - center) / scale).reshape(-1, h, h),
             axes=(1, 2), norm='ortho').reshape(X.shape)
    T = dctn(((test - center) / scale).reshape(-1, h, h),
             axes=(1, 2), norm='ortho').reshape(test.shape)
    f = np.arange(h, dtype=float) ** 2
    freq = ((np.pi / h) ** 2 * (f[:, None] + f[None, :])).ravel()
    rng = np.random.RandomState(1729)
    landmarks = rng.choice(n, min(n, 256), replace=False)
    rank = min(len(landmarks), 192 if n <= 800 else 160)
    models = []
    for sigma in (0.65, 1.6):
        F, G = _features(D, T, freq, sigma, False, landmarks, rank)
        models.append((F, G, 'exp'))
        models.append((F, G, 'softplus'))
        F, G = _features(D, T, freq, sigma, True, landmarks, rank)
        models.append((F, G, 'exp'))
    kfold = 3 if n <= 600 else 2
    fold_id = np.empty(n, dtype=int)
    fold_id[rng.permutation(n)] = np.arange(n) % kfold
    folds = [(np.flatnonzero(fold_id != k), np.flatnonzero(fold_id == k))
             for k in range(kfold)]
    alphas = np.array([0.3, 0.05, 0.008, 0.0013, 0.0002, 0.00003])
    P = np.empty((n, len(models) + 1, q))
    for tr, va in folds:
        P[va, 0] = (counts[tr] @ Y[tr] + 0.25) / counts[tr].sum()
    chosen = []
    iterations = 60 if n <= 600 else 45
    wn = counts[None, :, None] / counts.sum()
    for model_index, (F, G, link) in enumerate(models):
        cv = np.empty((len(alphas), n, q))
        for tr, va in folds:
            initial = None
            A, B, c = F[tr], Y[tr], counts[tr]
            for a, penalty in enumerate(alphas):
                fitted, b, cap = _fit(A, B, c, penalty, link, initial, iterations)
                cv[a, va] = _predict(F[va], fitted, b, cap, link)
                initial = fitted
        smoothed = np.empty_like(cv)
        for a in range(len(alphas)):
            smoothed[a] = (0.25 * cv[max(a - 1, 0)] + 0.5 * cv[a]
                           + 0.25 * cv[min(a + 1, len(alphas) - 1)])
        scores = np.sum(wn * (smoothed - Y[None] * np.log(smoothed)), axis=1)
        best = np.argmin(scores, axis=0)
        chosen.append(best)
        for j in range(q):
            P[:, model_index + 1, j] = smoothed[best[j], :, j]
    mixing = _ensemble_weights(P, Y, counts, base)
    output = np.broadcast_to(base * mixing[0], (len(test), q)).copy()
    for model_index, (F, G, link) in enumerate(models):
        prediction = np.zeros((len(test), q))
        initial = None
        for offset, weight in ((-1, 0.25), (0, 0.5), (1, 0.25)):
            index = np.clip(chosen[model_index] + offset, 0, len(alphas) - 1)
            penalty = alphas[index] * ((kfold - 1.0) / kfold)
            fitted, b, cap = _fit(F, Y, counts, penalty, link, initial,
                                  80 if n <= 600 else 60)
            prediction += weight * _predict(G, fitted, b, cap, link)
            initial = fitted
        output += prediction * mixing[model_index + 1]
    output = np.where(np.isfinite(output), output, base[None])
    return np.maximum(output, 1e-8)[test_inverse]
