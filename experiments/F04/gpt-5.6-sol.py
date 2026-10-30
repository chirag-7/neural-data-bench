import numpy as np
from scipy.optimize import minimize


def _aggregate(x, y=None):
    ux, inv = np.unique(np.asarray(x, dtype=np.float64), axis=0,
                        return_inverse=True)
    if y is None:
        return ux, inv
    y = np.asarray(y, dtype=np.float64)
    sy = np.zeros((len(ux), y.shape[1]), dtype=np.float64)
    counts = np.bincount(inv, minlength=len(ux)).astype(np.float64)
    np.add.at(sy, inv, y)
    return ux, sy / counts[:, None], inv


def _dct_matrix(n):
    j = np.arange(n, dtype=np.float64)[None, :]
    k = np.arange(n, dtype=np.float64)[:, None]
    c = np.sqrt(2.0 / n) * np.cos(np.pi * (j + 0.5) * k / n)
    c[0] = 1.0 / np.sqrt(n)
    return c


def _dct_images(x, c, scale):
    a = np.asarray(x, dtype=np.float64).reshape(-1, 18, 18) / scale
    return np.matmul(np.matmul(c, a), c.T).reshape(len(a), -1)


def _representation(zfit, zeval, smooth):
    nside = 18
    q = np.arange(nside, dtype=np.float64)
    f2 = (q[:, None] ** 2 + q[None, :] ** 2) / ((nside - 1.0) ** 2)
    weight = 1.0 / np.sqrt(1.0 + smooth * f2)
    weight = weight.reshape(-1)

    a = zfit * weight
    b = zeval * weight
    center = a.mean(axis=0)
    a = a - center
    b = b - center

    _, s, vt = np.linalg.svd(a, full_matrices=False)
    if len(s) == 0 or s[0] <= 0:
        return np.zeros((len(a), 0)), np.zeros((len(b), 0))
    rank = int(np.sum(s > s[0] * 1e-9))
    rank = min(rank, 72)
    basis = vt[:rank].T
    return a @ basis, b @ basis


def _poisson_fit(x, y, alpha, initial=None):
    n, p = x.shape
    m = y.shape[1]
    if initial is None or initial.size != p * m + m:
        intercept = np.log(np.maximum(y.mean(axis=0), 1e-4))
        initial = np.r_[np.zeros(p * m, dtype=np.float64), intercept]

    def objective(theta):
        beta = theta[:p * m].reshape(p, m)
        bias = theta[p * m:]
        eta = x @ beta + bias
        safe_eta = np.clip(eta, -30.0, 30.0)
        rate = np.exp(safe_eta)
        loss = (rate.sum() - np.sum(y * safe_eta)) / n
        loss += 0.5 * alpha * np.sum(beta * beta)
        residual = rate - y
        active = ((eta > -30.0) & (eta < 30.0)).astype(np.float64)
        residual *= active
        gb = x.T @ residual / n + alpha * beta
        ga = residual.sum(axis=0) / n
        return float(loss), np.r_[gb.ravel(), ga]

    result = minimize(objective, initial, method="L-BFGS-B", jac=True,
                      options={"maxiter": 90, "maxls": 25,
                               "ftol": 1e-10, "gtol": 2e-5})
    theta = result.x
    if not np.all(np.isfinite(theta)):
        theta = initial
    return theta


def _predict(theta, x, m):
    p = x.shape[1]
    beta = theta[:p * m].reshape(p, m)
    bias = theta[p * m:]
    eta = np.clip(x @ beta + bias, -20.0, 12.0)
    return np.exp(eta)


def fit_predict(train_x, train_y, test_x):
    train_x = np.asarray(train_x, dtype=np.float64)
    train_y = np.asarray(train_y, dtype=np.float64)
    test_x = np.asarray(test_x, dtype=np.float64)

    ux, uy, _ = _aggregate(train_x, train_y)
    tx, test_inverse = _aggregate(test_x)
    n, m = uy.shape

    c = _dct_matrix(18)
    global_scale = float(np.std(ux))
    if not np.isfinite(global_scale) or global_scale < 1e-8:
        global_scale = 1.0

    smoothness = (0.0, 4.0, 16.0)
    alphas = (0.002, 0.008, 0.03, 0.12, 0.5, 2.0, 8.0)
    candidates = [(None, None)]
    candidates += [(s, a) for s in smoothness for a in alphas]
    candidate_index = {v: i for i, v in enumerate(candidates)}
    oof = np.empty((len(candidates), n, m), dtype=np.float64)

    rng = np.random.RandomState(1729)
    order = rng.permutation(n)
    folds = np.array_split(order, min(5, n))

    for valid in folds:
        mask = np.ones(n, dtype=bool)
        mask[valid] = False
        fit_idx = np.nonzero(mask)[0]
        fold_scale = float(np.std(ux[fit_idx]))
        if not np.isfinite(fold_scale) or fold_scale < 1e-8:
            fold_scale = global_scale
        zfit = _dct_images(ux[fit_idx], c, fold_scale)
        zvalid = _dct_images(ux[valid], c, fold_scale)

        null_rate = np.maximum(uy[fit_idx].mean(axis=0), 1e-6)
        oof[0, valid] = null_rate

        for smooth in smoothness:
            xf, xv = _representation(zfit, zvalid, smooth)
            theta = None
            for alpha in reversed(alphas):
                theta = _poisson_fit(xf, uy[fit_idx], alpha, theta)
                ci = candidate_index[(smooth, alpha)]
                oof[ci, valid] = _predict(theta, xv, m)

    oof = np.clip(oof, 1e-8, 1e6)
    point_loss = oof - uy[None, :, :] * np.log(oof)
    scores = point_loss.mean(axis=1)
    selected = np.empty(m, dtype=int)

    simplicity = np.empty(len(candidates), dtype=np.float64)
    simplicity[0] = 100.0
    for i, (smooth, alpha) in enumerate(candidates[1:], start=1):
        simplicity[i] = np.log(alpha) + 0.035 * smooth

    for neuron in range(m):
        best = int(np.argmin(scores[:, neuron]))
        best_losses = point_loss[best, :, neuron]
        eligible = []
        for ci in range(len(candidates)):
            difference = point_loss[ci, :, neuron] - best_losses
            if n > 1:
                se = np.std(difference, ddof=1) / np.sqrt(n)
            else:
                se = 0.0
            if scores[ci, neuron] <= scores[best, neuron] + 0.25 * se + 1e-8:
                eligible.append(ci)
        selected[neuron] = max(eligible, key=lambda q: simplicity[q])

    zall = _dct_images(ux, c, global_scale)
    ztest = _dct_images(tx, c, global_scale)
    unique_prediction = np.tile(np.maximum(uy.mean(axis=0), 1e-6),
                                (len(tx), 1))

    for smooth in smoothness:
        needed = {candidates[selected[j]][1]
                  for j in range(m)
                  if candidates[selected[j]][0] == smooth}
        if not needed:
            continue
        xf, xt = _representation(zall, ztest, smooth)
        theta = None
        for alpha in sorted(needed, reverse=True):
            theta = _poisson_fit(xf, uy, alpha, theta)
            pred = _predict(theta, xt, m)
            for neuron in range(m):
                if candidates[selected[neuron]] == (smooth, alpha):
                    unique_prediction[:, neuron] = pred[:, neuron]

    maximum = np.maximum(0.25, 1.5 * np.max(uy, axis=0) + 0.5)
    unique_prediction = np.minimum(unique_prediction, maximum[None, :])
    unique_prediction = np.nan_to_num(unique_prediction, nan=1e-4,
                                      posinf=maximum[None, :], neginf=1e-4)
    unique_prediction = np.clip(unique_prediction, 1e-5, None)
    return unique_prediction[test_inverse]
