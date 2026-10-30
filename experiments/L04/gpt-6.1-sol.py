import numpy as np
from scipy.interpolate import BSpline
from scipy.sparse import csr_matrix
from scipy.linalg import cho_factor, cho_solve


def _prepare(x):
    x = np.asarray(x, dtype=float).reshape(-1, 2)
    med = np.zeros(2)
    for j in range(2):
        good = x[np.isfinite(x[:, j]), j]
        med[j] = np.median(good) if len(good) else 0.0
    z = np.where(np.isfinite(x), x, med)
    lo, hi = np.quantile(z[:, 0], [0.001, 0.999])
    if hi - lo < 1e-6:
        lo, hi = lo - 0.5, hi + 0.5
    scale = max(2.0, 0.2 * np.quantile(np.abs(z[:, 1]), 0.75))
    velocity = np.arcsinh(z[:, 1] / scale)
    vlo, vhi = np.quantile(velocity, [0.005, 0.995])
    if vhi - vlo < 1e-6:
        vlo, vhi = vlo - 0.5, vhi + 0.5
    return med, lo, hi, scale, vlo, vhi


def _spline(z, lo, hi, size, degree):
    interior = np.linspace(lo, hi, size - degree + 1)[1:-1]
    knots = np.r_[np.repeat(lo, degree + 1), interior,
                  np.repeat(hi, degree + 1)]
    return BSpline(knots, np.eye(size), degree,
                   extrapolate=False)(np.clip(z, lo, hi))


def _design(x, state, kind):
    med, lo, hi, scale, vlo, vhi = state
    x = np.asarray(x, dtype=float).reshape(-1, 2)
    z = np.where(np.isfinite(x), x, med)
    position = _spline(z[:, 0], lo, hi, 24, 3)
    if kind == 'position':
        velocity = np.ones((len(z), 1))
    elif kind == 'direction':
        q = 0.5 * (1.0 + np.tanh(z[:, 1] / scale))
        velocity = np.column_stack((1.0 - q, q))
    else:
        v = np.arcsinh(z[:, 1] / scale)
        velocity = _spline(v, vlo, vhi, 6, 2)
    design = (position[:, :, None] * velocity[:, None, :])
    return csr_matrix(design.reshape(len(z), -1))


def _penalty(kind, lp, lv):
    nv = {'position': 1, 'direction': 2, 'full': 6}[kind]
    dp = np.diff(np.eye(24), n=2, axis=0)
    penalty = lp * np.kron(dp.T @ dp, np.eye(nv))
    if nv > 1:
        order = 1 if nv == 2 else 2
        dv = np.diff(np.eye(nv), n=order, axis=0)
        penalty += lv * np.kron(np.eye(24), dv.T @ dv)
    p = 24 * nv
    penalty += 0.01 * (np.eye(p) - np.ones((p, p)) / p)
    return penalty


def _fit(b, y, penalty):
    p = b.shape[1]
    coef = np.full(p, np.log(max(float(np.mean(y)), 1e-9)))
    if np.sum(y) == 0:
        return coef
    bt = b.T.tocsr()
    eta = np.clip(np.asarray(b @ coef).ravel(), -25.0, 15.0)
    mu = np.exp(eta)
    loss = mu.sum() - y @ eta + 0.5 * coef @ penalty @ coef
    for iteration in range(40):
        gradient = np.asarray(bt @ (mu - y)).ravel() + penalty @ coef
        hessian = (bt @ b.multiply(mu[:, None])).toarray() + penalty
        hessian.flat[::p + 1] += 1e-8
        try:
            step = cho_solve(cho_factor(hessian, lower=True,
                                       check_finite=False), gradient,
                             check_finite=False)
        except np.linalg.LinAlgError:
            step = np.linalg.lstsq(hessian, gradient, rcond=1e-9)[0]
        if np.max(np.abs(step)) < 1e-5:
            break
        amount = 1.0
        accepted = False
        for trial in range(18):
            proposed = coef - amount * step
            new_eta = np.clip(np.asarray(b @ proposed).ravel(), -25.0, 15.0)
            new_mu = np.exp(new_eta)
            new_loss = (new_mu.sum() - y @ new_eta
                        + 0.5 * proposed @ penalty @ proposed)
            if np.isfinite(new_loss) and new_loss <= loss + 1e-10:
                accepted = True
                break
            amount *= 0.5
        if not accepted:
            break
        improvement = loss - new_loss
        coef, eta, mu, loss = proposed, new_eta, new_mu, new_loss
        if improvement < 1e-7 * (1.0 + abs(loss)):
            break
    return coef


def _predict(b, coef):
    return np.exp(np.clip(np.asarray(b @ coef).ravel(), -25.0, 4.0))


def fit_predict(train_x, train_y, test_x):
    x = np.asarray(train_x, dtype=float).reshape(-1, 2)
    y = np.asarray(train_y, dtype=float).reshape(-1)
    test = np.asarray(test_x, dtype=float).reshape(-1, 2)
    n = len(y)
    if len(test) == 0:
        return np.empty(0, dtype=float)
    if n == 0:
        return np.zeros(len(test), dtype=float)
    mean = float(np.mean(y))
    if mean <= 0:
        return np.zeros(len(test), dtype=float)
    if n < 300 or np.sum(y) < 5:
        return np.full(len(test), mean, dtype=float)

    configs = [('position', value, 0.0) for value in (0.03, 0.3, 3.0, 30.0)]
    configs += [('direction', a, b) for a, b in
                ((0.1, 0.03), (1.0, 0.1), (10.0, 0.3), (3.0, 3.0))]
    configs += [('full', a, b) for a, b in
                ((0.1, 0.1), (1.0, 1.0), (10.0, 3.0), (3.0, 30.0))]
    penalties = [_penalty(*config) for config in configs]
    scores = np.zeros(len(configs) + 1)
    validation_spikes = 0.0
    folds = [(int(0.6 * n), int(0.8 * n)), (int(0.8 * n), n)]
    for end_train, end_valid in folds:
        start_valid = end_train + 50
        if start_valid >= end_valid:
            continue
        state = _prepare(x[:end_train])
        yt = y[:end_train]
        yv = y[start_valid:end_valid]
        validation_spikes += float(yv.sum())
        baseline = max(float(np.mean(yt)), 1e-9)
        baseline_score = yv.sum() * np.log(baseline) - len(yv) * baseline
        cache = {}
        for kind in ('position', 'direction', 'full'):
            cache[kind] = (_design(x[:end_train], state, kind),
                           _design(x[start_valid:end_valid], state, kind))
        for j, config in enumerate(configs):
            bt, bv = cache[config[0]]
            coef = _fit(bt, yt, penalties[j])
            pred = _predict(bv, coef)
            scores[j + 1] += float(yv @ np.log(pred) - pred.sum() - baseline_score)

    temperature = max(2.0, min(6.0, 0.015 * validation_spikes))
    weights = np.exp(np.maximum((scores - scores.max()) / temperature, -60.0))
    weights /= weights.sum()
    weights[weights < 0.005] = 0.0
    weights /= weights.sum()
    prediction = np.full(len(test), weights[0] * mean)
    state = _prepare(x)
    cache = {}
    for j, config in enumerate(configs):
        weight = weights[j + 1]
        if weight == 0:
            continue
        kind = config[0]
        if kind not in cache:
            cache[kind] = (_design(x, state, kind), _design(test, state, kind))
        bt, bv = cache[kind]
        coef = _fit(bt, y, penalties[j])
        prediction += weight * _predict(bv, coef)
    return np.maximum(np.nan_to_num(prediction, nan=mean, posinf=mean,
                                    neginf=0.0), 0.0).reshape(-1)
