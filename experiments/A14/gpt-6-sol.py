import numpy as np
from sklearn.linear_model import Ridge
from sklearn.ensemble import ExtraTreesRegressor


def _geom(x):
    p = np.asarray(x, dtype=np.float64).reshape(-1, 31, 6, 3)
    hb, hl, sf = p[:, :, 1], p[:, :, 2], p[:, :, 3]
    e1 = hl - hb
    e1 = e1 / np.maximum(np.linalg.norm(e1, axis=2, keepdims=True), 1e-8)
    v = hb - sf
    e2 = v - np.sum(v * e1, axis=2, keepdims=True) * e1
    e2 = e2 / np.maximum(np.linalg.norm(e2, axis=2, keepdims=True), 1e-8)
    frame = np.stack((e1, e2, np.cross(e1, e2)), axis=-1)
    c = np.einsum('ntij,nti->ntj', frame, p[:, :, 0] - hb)
    w = ((np.arange(12, 19) - 11) / 8.0)[None, :, None]
    u = ((np.arange(12, 19) - 10) / 10.0)[None, :, None]
    cl = (1 - w) * c[:, 11:12] + w * c[:, 19:20]
    left = np.mean(c[:, 9:12], axis=1, keepdims=True)
    right = np.mean(c[:, 19:22], axis=1, keepdims=True)
    cs = (1 - u) * left + u * right
    cc = np.broadcast_to((left + right) / 2, cl.shape)

    def place(z):
        return hb[:, 12:19] + np.einsum('ntij,ntj->nti', frame[:, 12:19], z)

    world = (1 - w) * p[:, 11:12, 0] + w * p[:, 19:20, 0]
    rel = hb[:, 12:19] + (1 - w) * (p[:, 11:12, 0] - hb[:, 11:12]) + w * (p[:, 19:20, 0] - hb[:, 19:20])
    bases = [world, rel, place(cl), place(cs), place(cc)]
    idx = [9, 11, 13, 15, 17, 19, 21]
    body = np.einsum('ntij,ntki->ntkj', frame, p[:, :, 1:] - hb[:, :, None])
    travel = np.einsum('nij,nti->ntj', frame[:, 15], hb[:, idx] - hb[:, 11:12])
    orient = np.einsum('nij,ntik->ntjk', frame[:, 15], frame[:, idx, :, :2])
    feat = np.concatenate((c[:, [7, 9, 10, 11, 19, 20, 21, 23]].reshape(len(p), -1),
                           body[:, idx, 1:].reshape(len(p), -1),
                           travel.reshape(len(p), -1),
                           orient.reshape(len(p), -1)), axis=1)
    feat = np.clip(np.nan_to_num(feat, nan=0.0, posinf=0.0, neginf=0.0), -1e6, 1e6)
    return hb, frame, cl, bases, feat


def _global(hb, frame, cl, residual):
    c = cl + residual.reshape(-1, 7, 3)
    return hb[:, 12:19] + np.einsum('ntij,ntj->nti', frame[:, 12:19], c)


def _score(pred, truth):
    mask = np.isfinite(truth)
    if not np.any(mask):
        return np.inf
    d = pred[mask] - truth[mask]
    return float(np.sqrt(np.mean(d * d))) if np.all(np.isfinite(d)) else np.inf


def _tree():
    return ExtraTreesRegressor(n_estimators=48, max_depth=14,
                               min_samples_leaf=8, max_features=0.65,
                               n_jobs=1, random_state=19)


def fit_predict(train_x, train_y, test_x):
    hb, frame, cl, bases, feat = _geom(train_x)
    truth = np.asarray(train_y, dtype=np.float64)[:, 12:19, :3]
    residual = np.einsum('ntij,nti->ntj', frame[:, 12:19],
                         truth - hb[:, 12:19]) - cl
    target = residual.reshape(len(feat), -1)
    eligible = np.all(np.isfinite(target), axis=1)
    cut = max(1, min(len(feat) - 1, int(0.8 * len(feat))))
    val_truth = truth[cut:]
    errors = [_score(b[cut:], val_truth) for b in bases]
    base_id = int(np.argmin(errors))
    best_error = errors[base_id]
    choice = ('base', None, 0.0)
    fit_rows = eligible[:cut]

    if np.sum(fit_rows) >= 100 and len(val_truth):
        mu = np.mean(feat[:cut][fit_rows], axis=0)
        sd = np.std(feat[:cut][fit_rows], axis=0)
        sd = np.where(sd > 1e-8, sd, 1.0)
        z = np.clip((feat - mu) / sd, -8, 8)
        models = [('ridge', a, Ridge(alpha=a)) for a in (30.0, 300.0, 3000.0)]
        models.append(('tree', None, _tree()))
        for name, param, model in models:
            model.fit(z[:cut][fit_rows], target[:cut][fit_rows])
            corrected = _global(hb[cut:], frame[cut:], cl[cut:],
                                model.predict(z[cut:]))
            for weight in (0.25, 0.5, 0.75, 1.0):
                pred = (1 - weight) * bases[base_id][cut:] + weight * corrected
                err = _score(pred, val_truth)
                if err < best_error:
                    best_error = err
                    choice = (name, param, weight)

    test_hb, test_frame, test_cl, test_bases, test_feat = _geom(test_x)
    pred = test_bases[base_id]
    name, param, weight = choice
    if name != 'base' and np.sum(eligible) >= 100:
        mu = np.mean(feat[eligible], axis=0)
        sd = np.std(feat[eligible], axis=0)
        sd = np.where(sd > 1e-8, sd, 1.0)
        z_train = np.clip((feat[eligible] - mu) / sd, -8, 8)
        z_test = np.clip((test_feat - mu) / sd, -8, 8)
        model = Ridge(alpha=param) if name == 'ridge' else _tree()
        model.fit(z_train, target[eligible])
        corrected = _global(test_hb, test_frame, test_cl,
                            model.predict(z_test))
        pred = (1 - weight) * pred + weight * corrected

    fallback = np.nan_to_num(test_bases[0], nan=0.0, posinf=0.0, neginf=0.0)
    pred = np.where(np.isfinite(pred), pred, fallback)
    out = np.array(test_x, copy=True)
    out[:, 12:19, :3] = pred
    return out