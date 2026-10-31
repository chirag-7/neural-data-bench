import numpy as np


def _weights(group_ids, block_ids):
    g = np.asarray(group_ids).reshape(-1)
    b = np.asarray(block_ids).reshape(-1)
    w = np.zeros(g.size, dtype=float)
    donors = np.unique(g)
    nd = max(1, donors.size)
    for donor in donors:
        dm = (g == donor)
        blocks = np.unique(b[dm])
        nb = max(1, blocks.size)
        for block in blocks:
            m = dm & (b == block)
            nr = int(np.sum(m))
            if nr:
                w[m] = 1.0 / (nd * nb * nr)
    s = np.sum(w)
    if s <= 0 and g.size:
        w[:] = 1.0 / g.size
    elif s > 0:
        w /= s
    return w


def _weighted_standardize(X, w):
    finite = np.isfinite(X)
    wf = w[:, None] * finite
    den = np.sum(wf, axis=0)
    num = np.sum(w[:, None] * np.where(finite, X, 0.0), axis=0)
    mu = np.divide(num, den, out=np.zeros(X.shape[1]), where=den > 0)
    filled = np.where(finite, X, mu)
    var_num = np.sum(w[:, None] * finite * (filled - mu) ** 2, axis=0)
    var = np.divide(var_num, den, out=np.zeros(X.shape[1]), where=den > 0)
    sd = np.sqrt(np.maximum(var, 0.0))
    sd = np.where(sd > 1e-10, sd, 1.0)
    return (filled - mu) / sd, mu, sd


def _transform_y(y, transform):
    if transform == 1:
        z = np.clip(y, 1e-4, 1.0 - 1e-4)
        return np.log(z / (1.0 - z))
    return y


def _inverse_y(z, transform):
    if transform == 1:
        z = np.clip(z, -30.0, 30.0)
        return 1.0 / (1.0 + np.exp(-z))
    return z


def _fit_model(X, y, g, b, candidate):
    good_y = np.isfinite(y)
    X = X[good_y]
    y = y[good_y]
    g = g[good_y]
    b = b[good_y]
    if y.size == 0:
        return ("c", 0.0)

    w = _weights(g, b)
    if candidate[0] == "c":
        return ("c", float(np.sum(w * y)))

    transform = candidate[1]
    yt = _transform_y(y, transform)
    Z, mu, sd = _weighted_standardize(X, w)
    ym = float(np.sum(w * yt))
    yc = yt - ym
    cov = np.sum(w[:, None] * Z * yc[:, None], axis=0)
    k = min(int(candidate[2]), Z.shape[1])
    order = np.lexsort((np.arange(Z.shape[1]), -np.abs(cov)))
    selected = order[:k]
    A = Z[:, selected]

    if candidate[0] == "r":
        alpha = float(candidate[3]) * max(1, k)
        sw = np.sqrt(w)
        Aw = A * sw[:, None]
        rhs = sw * yc
        gram = Aw @ Aw.T
        gram.flat[::gram.shape[0] + 1] += alpha
        dual = np.linalg.solve(gram, rhs)
        beta = Aw.T @ dual
    else:
        style = int(candidate[3])
        shrink = float(candidate[4])
        direction = cov[selected].copy()
        if style == 1:
            direction = np.sign(direction)
        norm = float(np.sqrt(np.sum(direction * direction)))
        if norm <= 1e-14:
            beta = np.zeros(k, dtype=float)
        else:
            direction /= norm
            score = A @ direction
            sm = float(np.sum(w * score))
            sc = score - sm
            denom = float(np.sum(w * sc * sc))
            slope = float(np.sum(w * sc * yc)) / (denom * (1.0 + shrink) + 1e-12)
            beta = direction * slope
            ym -= slope * sm

    return ("l", selected, mu[selected], sd[selected], beta, ym, transform)


def _predict_model(model, X):
    if model[0] == "c":
        return np.full(X.shape[0], np.clip(model[1], 0.0, 1.0), dtype=float)
    _, selected, mu, sd, beta, intercept, transform = model
    A = X[:, selected]
    A = np.where(np.isfinite(A), A, mu)
    z = ((A - mu) / sd) @ beta + intercept
    return np.clip(_inverse_y(z, transform), 0.0, 1.0)


def _grouped_loss(y, pred, g, b):
    donor_losses = []
    for donor in np.unique(g):
        dm = (g == donor)
        block_losses = []
        for block in np.unique(b[dm]):
            m = dm & (b == block) & np.isfinite(y) & np.isfinite(pred)
            if np.any(m):
                error = float(np.mean(pred[m]) - np.mean(y[m]))
                block_losses.append(error * error)
        if block_losses:
            donor_losses.append(float(np.mean(block_losses)))
    if not donor_losses:
        return np.inf
    return float(np.sqrt(np.mean(donor_losses)))


def _candidates(n_features):
    base_k = (12, 30, 75, 150, 300, 700, 1400, 2000)
    ks = sorted(set(min(n_features, k) for k in base_k if n_features > 0))
    result = [("c",)]
    for transform in (0, 1):
        for k in ks:
            for lam in (0.003, 0.03, 0.3, 3.0):
                result.append(("r", transform, k, lam))
            for style in (0, 1):
                for shrink in (0.0, 0.75):
                    result.append(("s", transform, k, style, shrink))
    return result


def _fit_one_target(X, y, test_x, g, b, candidates):
    n = X.shape[0]
    oof = np.zeros((len(candidates), n), dtype=float)
    donors = np.unique(g)

    for donor in donors:
        valid = (g == donor)
        train = ~valid
        for j, candidate in enumerate(candidates):
            model = _fit_model(X[train], y[train], g[train], b[train], candidate)
            oof[j, valid] = _predict_model(model, X[valid])

    losses = np.array([
        _grouped_loss(y, oof[j], g, b) for j in range(len(candidates))
    ])
    losses = np.where(np.isfinite(losses), losses, np.inf)
    order = np.lexsort((np.arange(len(candidates)), losses))
    best = float(losses[order[0]])
    yrange = float(np.ptp(y[np.isfinite(y)])) if np.any(np.isfinite(y)) else 0.0
    tolerance = max(0.08 * best, 0.002 * yrange, 1e-5)
    chosen = [int(j) for j in order if losses[j] <= best + tolerance][:8]
    for j in order:
        if len(chosen) >= 3:
            break
        if int(j) not in chosen:
            chosen.append(int(j))

    relative = np.array([losses[j] - best for j in chosen])
    blend_w = np.exp(-relative / (tolerance + 1e-12))
    blend_w /= np.sum(blend_w)
    prediction = np.zeros(test_x.shape[0], dtype=float)
    for weight, j in zip(blend_w, chosen):
        model = _fit_model(X, y, g, b, candidates[j])
        prediction += weight * _predict_model(model, test_x)

    good_y = np.isfinite(y)
    if np.any(good_y):
        fallback_w = _weights(g[good_y], b[good_y])
        fallback = float(np.sum(fallback_w * y[good_y]))
    else:
        fallback = 0.0
    prediction = np.nan_to_num(prediction, nan=fallback, posinf=1.0, neginf=0.0)
    return np.clip(prediction, 0.0, 1.0)


def fit_predict(train_x, train_y, test_x, train_groups):
    X = np.asarray(train_x, dtype=float)
    Y = np.asarray(train_y, dtype=float)
    T = np.asarray(test_x, dtype=float)
    g = np.asarray(train_groups["group_ids"]).reshape(-1)
    b = np.asarray(train_groups["block_ids"]).reshape(-1)

    if X.ndim != 2 or T.ndim != 2 or Y.ndim != 2:
        raise ValueError("Feature and target inputs must be two-dimensional")
    if X.shape[0] != Y.shape[0] or X.shape[0] != g.size or g.size != b.size:
        raise ValueError("Training rows and group vectors must have equal length")
    if X.shape[1] != T.shape[1] or Y.shape[1] != 3:
        raise ValueError("Incompatible feature count or target count")

    candidates = _candidates(X.shape[1])
    output = np.empty((T.shape[0], 3), dtype=float)
    for target in range(3):
        output[:, target] = _fit_one_target(
            X, Y[:, target], T, g, b, candidates
        )
    return np.clip(np.nan_to_num(output, nan=0.0, posinf=1.0, neginf=0.0), 0.0, 1.0)
