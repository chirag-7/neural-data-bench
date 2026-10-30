import numpy as np
from scipy.interpolate import CubicSpline


def _unit(v):
    n = np.sqrt(np.sum(v * v, axis=-1, keepdims=True))
    return v / np.maximum(n, 1e-12)


def _geometry(a):
    b = a[:, :, 3:6]
    left = a[:, :, 6:9]
    spine = a[:, :, 9:12]
    e1 = _unit(left - b)
    v = spine - b
    v = v - np.sum(v * e1, axis=-1, keepdims=True) * e1
    e2 = _unit(v)
    e3 = _unit(np.cross(e1, e2))
    e2 = _unit(np.cross(e3, e1))
    E = np.stack((e1, e2, e3), axis=-1)
    d = a[:, :, :3] - b
    c = np.einsum("ntji,ntj->nti", E, d)
    return b, E, c


def _bases(a, obs, miss):
    b, E, c = _geometry(a)
    raw = CubicSpline(obs, a[:, obs, :3], axis=1)(miss)
    cloc = CubicSpline(obs, c[:, obs, :], axis=1)(miss)
    geo = b[:, miss] + np.einsum("ntij,ntj->nti", E[:, miss], cloc)

    lo = int(miss[0] - 1)
    hi = int(miss[-1] + 1)
    u = ((miss - lo) / float(hi - lo))[None, :, None]
    linear = a[:, lo:lo + 1, :3] * (1.0 - u) + a[:, hi:hi + 1, :3] * u
    candidates = np.stack((linear, raw, geo), axis=1)
    return candidates, b, E, c


def _fit_stack(candidates, truth, rows):
    m = truth.shape[1]
    w = np.zeros((m, 2), dtype=np.float64)
    delta = candidates[:, 1:] - candidates[:, :1]
    for j in range(m):
        A = delta[rows, :, j, :].transpose(0, 2, 1).reshape(-1, 2)
        z = (truth[rows, j, :] - candidates[rows, 0, j, :]).reshape(-1)
        G = A.T @ A
        reg = 1e-4 * (np.trace(G) / 2.0 + 1e-12)
        w[j] = np.linalg.solve(G + reg * np.eye(2), A.T @ z)
    return np.clip(w, -1.0, 2.0)


def _apply_stack(candidates, w):
    delta = candidates[:, 1:] - candidates[:, :1]
    return candidates[:, 0] + np.einsum("nkmc,mk->nmc", delta, w)


def _features(a, candidates, b, E, c, miss):
    n, T = a.shape[:2]
    s, e = int(miss[0]), int(miss[-1] + 1)
    ctx = np.r_[np.arange(max(0, s - 7), s),
                np.arange(e, min(T, e + 7))]
    parts = [c[:, ctx].reshape(n, -1)]

    fr = np.arange(max(0, s - 3), min(T, e + 3))
    rel = np.concatenate((a[:, :, 12:15] - b,
                          a[:, :, 15:18] - b), axis=-1)
    rel = rel[:, fr].reshape(n, len(fr), 2, 3)
    local_spine = np.einsum("ntji,ntlj->ntli", E[:, fr], rel)
    parts.append(local_spine.reshape(n, -1))

    f0, f1 = fr[:-1], fr[1:]
    R = np.einsum("ntji,ntjk->ntik", E[:, f0], E[:, f1])
    diag = np.diagonal(R, axis1=-2, axis2=-1)
    skew = np.stack((R[..., 2, 1] - R[..., 1, 2],
                     R[..., 0, 2] - R[..., 2, 0],
                     R[..., 1, 0] - R[..., 0, 1]), axis=-1)
    parts.append(np.concatenate((diag, skew), axis=-1).reshape(n, -1))

    db = b[:, f1] - b[:, f0]
    local_db = np.einsum("ntji,ntj->nti", E[:, f0], db)
    parts.append(local_db.reshape(n, -1))

    for k in (1, 2):
        d = candidates[:, k] - candidates[:, 0]
        dl = np.einsum("ntji,ntj->nti", E[:, miss], d)
        parts.append(dl.reshape(n, -1))
    return np.concatenate(parts, axis=1)


def _ridge_state(X, Y):
    mu = X.mean(axis=0)
    sd = X.std(axis=0)
    keep = np.isfinite(sd) & (sd > 1e-10)
    Z = (X[:, keep] - mu[keep]) / sd[keep]
    ym = Y.mean(axis=0)
    Yc = Y - ym
    G = Z.T @ Z
    C = Z.T @ Yc
    vals, vecs = np.linalg.eigh(G)
    vals = np.maximum(vals, 0.0)
    return mu, sd, keep, ym, vals, vecs, C


def _ridge_coef(state, alpha):
    vals, vecs, C = state[4], state[5], state[6]
    return vecs @ ((vecs.T @ C) / (vals[:, None] + alpha))


def _ridge_predict(X, state, coef):
    mu, sd, keep, ym = state[:4]
    Z = (X[:, keep] - mu[keep]) / sd[keep]
    return Z @ coef + ym


def fit_predict(train_x, train_y, test_x):
    tx = np.asarray(train_x, dtype=np.float64)
    ty = np.asarray(train_y, dtype=np.float64)
    qx = np.asarray(test_x, dtype=np.float64)
    T = tx.shape[1]

    miss = np.flatnonzero(np.isnan(qx[:, :, :3]).any(axis=(0, 2)))
    if miss.size == 0:
        return np.array(test_x, copy=True)
    obs = np.setdiff1d(np.arange(T), miss)

    tcand, tb, tE, tc = _bases(tx, obs, miss)
    truth = ty[:, miss, :3]
    n = tx.shape[0]
    cut = max(1, min(n - 1, (4 * n) // 5))
    fit_rows = np.arange(cut)
    val_rows = np.arange(cut, n)

    w_hold = _fit_stack(tcand, truth, fit_rows)
    choices = [tcand[:, 0], tcand[:, 1], tcand[:, 2],
               _apply_stack(tcand, w_hold)]
    errors = [np.mean((p[val_rows] - truth[val_rows]) ** 2)
              for p in choices]
    scheme = int(np.argmin(errors))
    base_hold = choices[scheme]

    X = _features(tx, tcand, tb, tE, tc, miss)
    residual = truth - base_hold
    Y = np.einsum("ntji,ntj->nti", tE[:, miss], residual).reshape(n, -1)

    state_hold = _ridge_state(X[fit_rows], Y[fit_rows])
    best_alpha, best_gamma, best_loss = 100.0, 0.0, np.inf
    for alpha in (0.01, 0.1, 1.0, 10.0, 100.0, 1000.0, 10000.0):
        coef = _ridge_coef(state_hold, alpha)
        p = _ridge_predict(X[val_rows], state_hold, coef)
        yv = Y[val_rows]
        den = float(np.sum(p * p)) + 1e-20
        gamma = float(np.clip(np.sum(yv * p) / den, 0.0, 1.25))
        loss = float(np.mean((yv - gamma * p) ** 2))
        if loss < best_loss:
            best_loss = loss
            best_alpha = alpha
            best_gamma = gamma

    if scheme == 3:
        final_w = _fit_stack(tcand, truth, np.arange(n))
        base_train = _apply_stack(tcand, final_w)
    else:
        final_w = None
        base_train = tcand[:, scheme]

    residual = truth - base_train
    Yall = np.einsum("ntji,ntj->nti", tE[:, miss], residual).reshape(n, -1)
    state = _ridge_state(X, Yall)
    scaled_alpha = best_alpha * n / float(len(fit_rows))
    coef = _ridge_coef(state, scaled_alpha)

    qcand, qb, qE, qc = _bases(qx, obs, miss)
    if scheme == 3:
        base_test = _apply_stack(qcand, final_w)
    else:
        base_test = qcand[:, scheme]
    Xq = _features(qx, qcand, qb, qE, qc, miss)
    corr_local = _ridge_predict(Xq, state, coef).reshape(len(qx), len(miss), 3)
    corr = np.einsum("ntij,ntj->nti", qE[:, miss], corr_local)
    pred = base_test + best_gamma * corr
    pred = np.where(np.isfinite(pred), pred, qcand[:, 0])

    out = np.array(test_x, dtype=np.float64, copy=True)
    block = out[:, miss, :3]
    block = np.where(np.isnan(block), pred, block)
    out[:, miss, :3] = block
    return out
