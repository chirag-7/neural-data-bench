import numpy as np
from scipy.interpolate import CubicSpline
from scipy.optimize import minimize
from scipy.spatial.distance import cdist
from scipy.linalg import eigh, cho_factor, cho_solve

_OBS = np.r_[0:12, 19:31]
_GAP = np.arange(12, 19)
_NEAR = np.r_[8:12, 19:23]

def _unit(a):
    return a / np.maximum(np.linalg.norm(a, axis=-1, keepdims=True), 1e-10)

def _fill(x):
    z = np.array(x, dtype=np.float64, copy=True)
    t = np.arange(z.shape[1])[None, :]
    for j in range(z.shape[2]):
        a = z[:, :, j]
        ok = np.isfinite(a)
        if ok.all():
            continue
        left = np.maximum.accumulate(np.where(ok, t, -1), axis=1)
        right = np.minimum.accumulate(np.where(ok, t, z.shape[1])[:, ::-1], axis=1)[:, ::-1]
        left = np.where(left < 0, np.minimum(right, z.shape[1] - 1), left)
        right = np.where(right == z.shape[1], left, right)
        lo = np.take_along_axis(a, left, axis=1)
        hi = np.take_along_axis(a, right, axis=1)
        f = (t - left) / np.maximum(right - left, 1)
        a[:] = np.where(ok, a, lo + f * (hi - lo))
    return np.nan_to_num(z, nan=0.0, posinf=0.0, neginf=0.0)

def _bridge(a, k):
    tl = np.arange(1 - k, 1, dtype=float)
    tr = np.arange(k, dtype=float)
    pl = np.linalg.pinv(np.column_stack((np.ones(k), tl, tl * tl)))
    pr = np.linalg.pinv(np.column_stack((np.ones(k), tr, tr * tr)))
    vl = np.einsum('ik,nkd->nid', pl, a[:, 12-k:12])
    vr = np.einsum('ik,nkd->nid', pr, a[:, 19:19+k])
    h = (np.arange(1, 8) / 8.0)[None, :, None]
    return ((2*h**3-3*h**2+1)*vl[:, 0:1] +
            (h**3-2*h**2+h)*8*vl[:, 1:2] +
            (-2*h**3+3*h**2)*vr[:, 0:1] +
            (h**3-h**2)*8*vr[:, 1:2])

def _local(v, frame, scale):
    return np.einsum('ntj,ntjk->ntk', v, frame) / scale[:, None, None]

def _world(q, frame, scale):
    return np.einsum('ntk,ntjk->ntj', q, frame) * scale[:, None, None]

def _prepare(raw):
    x = _fill(raw)
    n = len(x)
    f, b, l = x[:, :, :3], x[:, :, 3:6], x[:, :, 6:9]
    u = _unit(l - b)
    bad = np.linalg.norm(u, axis=2) < 0.5
    u[bad] = np.array([1.0, 0.0, 0.0])
    neck = x[:, :, 9:12] - b
    v = neck - np.sum(neck*u, axis=2, keepdims=True)*u
    fallback = np.zeros_like(v)
    fallback[:, :, 2] = 1
    switch = np.abs(u[:, :, 2]) > 0.9
    fallback[switch] = np.array([0.0, 1.0, 0.0])
    fallback -= np.sum(fallback*u, axis=2, keepdims=True)*u
    v = _unit(np.where(np.linalg.norm(v, axis=2, keepdims=True) < 1e-7, fallback, v))
    body = np.stack((u, v, np.cross(u, v)), axis=-1)
    transported = np.empty_like(v)
    transported[:, 15] = v[:, 15]
    for sequence in (range(16, 31), range(14, -1, -1)):
        for t in sequence:
            p = t - 1 if t > 15 else t + 1
            a, c = u[:, p], u[:, t]
            old = transported[:, p]
            den = np.maximum(1 + np.sum(a*c, axis=1), 1e-6)
            new = old - (np.sum(old*c, axis=1)/den)[:, None]*(a+c)
            new -= np.sum(new*c, axis=1, keepdims=True)*c
            transported[:, t] = _unit(np.where(np.linalg.norm(new, axis=1, keepdims=True) < 1e-7, v[:, t], new))
    frame = np.stack((u, transported, np.cross(u, transported)), axis=-1)
    scale = np.maximum(np.median(np.linalg.norm(l-b, axis=2), axis=1), 1e-3)
    fg = frame[:, _GAP]
    bg = b[:, _GAP]
    candidates = []
    for k in (4, 6):
        candidates.append(_local(_bridge(f, k)-bg, fg, scale))
        candidates.append(_local(_bridge(f-b, k), fg, scale))
    q = _local(f-b, frame, scale)
    qb = _local(f-b, body, scale)
    for axes, coordinates in ((frame, q), (body, qb)):
        def convert(z):
            return _local(_world(z, axes[:, _GAP], scale), fg, scale)
        for k in (4, 6):
            candidates.append(convert(_bridge(coordinates, k)))
        angle = np.zeros((n, 31, 1))
        angle[:, _OBS, 0] = np.unwrap(np.arctan2(coordinates[:, _OBS, 2], coordinates[:, _OBS, 1]), axis=1)
        axial = coordinates[:, _NEAR, 0].mean(axis=1)[:, None]
        radius = np.linalg.norm(coordinates[:, _NEAR, 1:3], axis=2).mean(axis=1)[:, None]
        for method in (4, 6, 0, -1):
            if method > 0:
                theta = _bridge(angle, method)[:, :, 0]
            elif method == 0:
                theta = CubicSpline(_OBS, angle[:, _OBS, 0], axis=1)(_GAP)
            else:
                h = np.arange(1, 8)[None, :] / 8.0
                theta = (1-h)*angle[:, 11, 0:1] + h*angle[:, 19, 0:1]
            z = np.stack((np.broadcast_to(axial, theta.shape), radius*np.cos(theta), radius*np.sin(theta)), axis=2)
            candidates.append(convert(z))
    times = np.array([5, 8, 10, 11, 12, 14, 16, 18, 19, 20, 22, 25])
    points = x[:, times, 3:].reshape(n, len(times), 5, 3) - b[:, 15, None, None, :]
    static = np.einsum('ntlj,njk->ntlk', points, frame[:, 15]) / scale[:, None, None, None]
    features = np.concatenate((static.reshape(n, -1), q[:, _OBS].reshape(n, -1), qb[:, _NEAR].reshape(n, -1)), axis=1)
    return x, frame, scale, np.stack(candidates, axis=1), features

def _weights(c, target, scale):
    d = (c-target[:, None]) * (scale/np.median(scale))[:, None, None, None]
    d = d.transpose(0, 2, 3, 1).reshape(-1, c.shape[1])
    gram = d.T @ d / max(len(d), 1)
    gram /= max(np.trace(gram)/len(gram), 1e-12)
    gram += np.eye(len(gram))*1e-5
    initial = np.full(len(gram), 1.0/len(gram))
    result = minimize(lambda w: 0.5*w@gram@w, initial, jac=lambda w: gram@w,
                      bounds=[(0, 1)]*len(gram), constraints={'type': 'eq', 'fun': lambda w: w.sum()-1, 'jac': lambda w: np.ones_like(w)},
                      method='SLSQP', options={'maxiter': 150, 'ftol': 1e-10})
    w = np.maximum(result.x, 0)
    return w/max(w.sum(), 1e-12)

def _kernel(z, centers, bandwidth):
    d = cdist(z, centers, metric='sqeuclidean') / bandwidth
    return np.concatenate((np.exp(-d/0.35), np.exp(-d/1.2)), axis=1)

def _design(raw, parameters):
    mean, sd, projection, centers, bandwidth, km, ks = parameters
    a = np.clip((raw-mean)/sd, -8, 8)
    k = _kernel(a@projection, centers, bandwidth)
    return np.concatenate((a, np.clip((k-km)/ks, -10, 10)), axis=1)

def fit_predict(train_x, train_y, test_x):
    rng = np.random.RandomState(1729)
    tx, tf, ts, tc, features = _prepare(train_x)
    labels = np.asarray(train_y, dtype=float)[:, _GAP, :3]
    keep = np.isfinite(labels).all(axis=(1, 2))
    target = _local(labels[keep]-tx[keep][:, _GAP, 3:6], tf[keep][:, _GAP], ts[keep])
    tc, features, ts = tc[keep], features[keep], ts[keep]
    del tx, tf
    n = len(target)
    model = None
    weights = np.full(tc.shape[1], 1.0/tc.shape[1])
    if n >= 128:
        order = rng.permutation(n)
        nv = max(32, n//5)
        va, tr = order[:nv], order[nv:]
        weights = _weights(tc[tr], target[tr], ts[tr])
        base = np.einsum('nkij,k->nij', tc, weights)
        raw = np.concatenate((features, base.reshape(n, -1)), axis=1)
        mean = raw[tr].mean(axis=0)
        sd = np.maximum(raw[tr].std(axis=0), 0.03)
        a = np.clip((raw-mean)/sd, -8, 8)
        covariance = a[tr].T@a[tr]/len(tr)
        values, vectors = eigh(covariance, check_finite=False)
        rank = min(40, len(values))
        projection = vectors[:, -rank:] / np.maximum(values[-rank:], 1e-6)[None, :]**0.25
        z = a@projection
        centers = z[rng.choice(tr, min(256, len(tr)), replace=False)].copy()
        distances = cdist(centers, centers, metric='sqeuclidean')
        bandwidth = max(float(np.median(distances)), 1e-6)
        k = _kernel(z, centers, bandwidth)
        km = k[tr].mean(axis=0)
        ks = np.maximum(k[tr].std(axis=0), 0.005)
        parameters = (mean, sd, projection, centers, bandwidth, km, ks)
        p = np.concatenate((a, np.clip((k-km)/ks, -10, 10)), axis=1)
        y = (target-base).reshape(n, -1)
        ym = y[tr].mean(axis=0)
        bound = np.maximum(4*y[tr].std(axis=0)+np.abs(ym), 0.04)
        gram = p[tr].T@p[tr]
        values, vectors = eigh(gram, check_finite=False)
        cross = vectors.T@(p[tr].T@(y[tr]-ym))
        pv = p[va]@vectors
        sw = (ts[va]/np.median(ts[tr]))[:, None]
        best = float(np.mean((y[va]*sw)**2))
        chosen, strength = 100.0, 0.0
        for penalty in (1.0, 10.0, 100.0, 1000.0, 10000.0):
            correction = np.clip(ym + pv@(cross/(np.maximum(values, 0)+penalty)[:, None]), -bound, bound)
            weighted = correction*sw
            shrink = np.clip(np.sum(weighted*(y[va]*sw))/max(np.sum(weighted**2), 1e-15), 0, 1)
            loss = float(np.mean(((y[va]-shrink*correction)*sw)**2))
            if loss < best:
                best, chosen, strength = loss, penalty, float(shrink)
        if strength > 0:
            ym = y.mean(axis=0)
            gram = p.T@p
            gram.flat[::len(gram)+1] += chosen*n/len(tr)
            beta = cho_solve(cho_factor(gram, lower=True, check_finite=False), p.T@(y-ym), check_finite=False)
            model = (parameters, beta, ym, bound, strength)
    sx, sf, ss, sc, sftr = _prepare(test_x)
    prediction = np.einsum('nkij,k->nij', sc, weights)
    if model is not None:
        parameters, beta, ym, bound, strength = model
        raw = np.concatenate((sftr, prediction.reshape(len(sx), -1)), axis=1)
        correction = np.clip(_design(raw, parameters)@beta+ym, -bound, bound)
        prediction += strength*correction.reshape(-1, 7, 3)
    world = _world(prediction, sf[:, _GAP], ss) + sx[:, _GAP, 3:6]
    original = np.asarray(test_x)
    result = np.array(original, dtype=float, copy=True)
    missing = ~np.isfinite(result)
    result[missing] = sx[missing]
    result[:, 12:19, :3] = np.where(np.isfinite(original[:, 12:19, :3]), original[:, 12:19, :3], world)
    return result
