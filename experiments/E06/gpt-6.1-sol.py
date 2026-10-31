import numpy as np
from scipy.linalg import eigh
try:
    from sklearn.utils.parallel import _get_threadpool_controller
    _limits = _get_threadpool_controller().limit
except ImportError:
    from sklearn.utils.fixes import threadpool_limits
    _limits = threadpool_limits


def _moments(x, y):
    count = len(x) * (x.shape[1] + y.shape[1])
    mu = (x.sum(axis=(0, 1)) + y.sum(axis=(0, 1))) / count
    var = ((x*x).sum(axis=(0, 1)) + (y*y).sum(axis=(0, 1))) / count - mu*mu
    floor = max(float(np.median(np.maximum(var, 0))) * .01, 1e-12)
    return mu, np.sqrt(np.maximum(var, floor))


def _shared_features(x, mu):
    anchor = x[:, -4:].mean(axis=1)
    f = np.concatenate(((x-anchor[:, None, :]).transpose(0, 2, 1),
                        (anchor-mu)[:, :, None]), axis=2)
    return f.reshape(-1, f.shape[-1]), anchor


def _shared_state(x, y, mu):
    f, anchor = _shared_features(x, mu)
    r = (y-anchor[:, None, :]).transpose(0, 2, 1).reshape(-1, y.shape[1])
    fm, rm = f.mean(axis=0), r.mean(axis=0)
    f, r = f-fm, r-rm
    gram = f.T @ f / len(f)
    cross = f.T @ r / len(f)
    ev, u = eigh(gram, check_finite=False)
    scale = max(float(np.trace(gram) / gram.shape[0]), 1e-12)
    return fm, rm, np.maximum(ev, 0), u, u.T @ cross, scale


def _shared_predict(x, mu, state, alpha):
    fm, rm, ev, u, cross, scale = state
    beta = u @ (cross / (ev[:, None] + alpha*scale))
    f, anchor = _shared_features(x, mu)
    r = (f-fm) @ beta + rm
    return r.reshape(len(x), x.shape[2], -1).transpose(0, 2, 1) + anchor[:, None, :]


def _local_features(x, mu, sd):
    n, _, d = x.shape
    a = x[:, -4:].mean(axis=1)
    bins = x.reshape(n, 16, 4, d).mean(axis=2)
    f = np.concatenate(((bins-a[:, None, :]).transpose(0, 2, 1),
                        (a-mu)[:, :, None], (x[:, -1]-a)[:, :, None]), axis=2)
    f = f / sd[None, :, None]
    return np.concatenate((f, np.ones((n, d, 1))), axis=2)


def _local_state(f, residual, sd):
    gram = np.einsum('ndp,ndq->dpq', f, f, optimize=True) / len(f)
    cross = np.einsum('ndp,nhd->dph', f, residual/sd[None, None, :],
                      optimize=True) / len(f)
    ev, u = np.linalg.eigh(gram)
    cross = np.einsum('dpq,dph->dqh', u, cross, optimize=True)
    return np.maximum(ev, 0), u, cross


def _local_predict(f, state, alpha, sd):
    ev, u, cross = state
    beta = np.einsum('dpq,dqh->dph', u, cross/(ev+alpha)[:, :, None], optimize=True)
    return np.einsum('ndp,dph->nhd', f, beta, optimize=True) * sd[None, None, :]


def _global_raw(x, mu, scale, basis):
    recent = x[:, -4:].mean(axis=1)
    short = x[:, -16:].mean(axis=1)
    prior = x[:, -32:-16].mean(axis=1)
    early = x[:, :32].mean(axis=1)
    f = np.stack((recent-mu, short-recent, prior-short, early-short), axis=1)
    return ((f/scale) @ basis).reshape(len(x), -1)


def _global_state(x, residual, mu, sd):
    n, _, d = x.shape
    scale = np.sqrt(sd)
    blocks = x.reshape(n, 8, 8, d).mean(axis=2)
    z = ((blocks-mu)/scale).reshape(-1, d)
    z = z-z.mean(axis=0)
    ev, basis = eigh(z.T @ z / len(z), check_finite=False)
    k = min(40, d, max(n-1, 1))
    ev, basis = np.maximum(ev[::-1][:k], 1e-12), basis[:, ::-1][:, :k]
    weights = np.tile((ev/max(float(ev[0]), 1e-12))**.125, 4)
    raw = _global_raw(x, mu, scale, basis)
    fm = raw.mean(axis=0)
    fs = np.maximum(raw.std(axis=0), np.tile(.05*np.sqrt(ev), 4))
    f = (raw-fm)/fs*weights
    params = mu, scale, basis, fm, fs, weights
    targets = residual.reshape(n, 8, 4, d).mean(axis=2).reshape(n, 8*d)
    return params, f, targets


def _global_features(x, params):
    mu, scale, basis, fm, fs, weights = params
    return (_global_raw(x, mu, scale, basis)-fm)/fs*weights


def _kernel(a, b, kind):
    linear = a @ b.T / a.shape[1]
    if kind == 0:
        return linear + 1.
    distance = (np.mean(a*a, axis=1)[:, None] +
                np.mean(b*b, axis=1)[None, :] - 2*linear)
    return .5*linear + .5*np.exp(-.5*np.maximum(distance, 0)) + 1.


def _global_path(f, ft, targets, kind, alphas):
    ev, u = eigh(_kernel(f, f, kind), check_finite=False)
    ev = np.maximum(ev, 0)
    left = _kernel(ft, f, kind) @ u
    right = u.T @ targets
    centers = np.arange(8)*4 + 1.5
    interpolation = np.column_stack([np.interp(np.arange(32), centers,
                                                np.eye(8)[:, j]) for j in range(8)])
    outputs = []
    for alpha in alphas:
        bins = (left/(ev+alpha*len(f))) @ right
        bins = bins.reshape(len(ft), 8, -1)
        outputs.append(np.einsum('hb,nbd->nhd', interpolation, bins, optimize=True))
    return outputs


def _split(x):
    n = len(x)
    linked = np.all(x[1:, :48] == x[:-1, 16:], axis=(1, 2))
    boundaries = np.r_[0, np.flatnonzero(~linked)+1, n]
    train, valid = [], []
    for start, end in zip(boundaries[:-1], boundaries[1:]):
        length = end-start
        if length < 12:
            train.extend(range(start, end))
            continue
        cut = start + int(.8*length)
        train.extend(range(start, max(start+1, cut-5)))
        valid.extend(range(cut, end, 2))
    if len(train) < 70 or len(valid) < 10:
        cut = int(.75*n)
        train = list(range(max(1, cut-5)))
        valid = list(range(cut, n, 2))
    return np.asarray(train, dtype=int), np.asarray(valid, dtype=int)


def _fit_predict(train_x, train_y, test_x):
    x = np.asarray(train_x, dtype=np.float64)
    y = np.asarray(train_y, dtype=np.float64)
    tx = np.asarray(test_x, dtype=np.float64)
    if len(tx) == 0:
        return np.empty((0, 32, x.shape[2]), dtype=np.float64)
    ti, vi = _split(x)
    xt, yt, xv, yv = x[ti], y[ti], x[vi], y[vi]
    mu, sd = _moments(xt, yt)
    shared_grid = (.0001, .001, .01, .1, 1., 10.)
    state = _shared_state(xt, yt, mu)
    losses = [np.mean((_shared_predict(xv, mu, state, a)-yv)**2) for a in shared_grid]
    minimum = min(losses)
    eligible = [j for j, loss in enumerate(losses)
                if loss <= minimum + .001*max(minimum, 1e-12)]
    shared_alpha = shared_grid[eligible[-1]]
    bt = _shared_predict(xt, mu, state, shared_alpha)
    bv = _shared_predict(xv, mu, state, shared_alpha)
    residual, error = yt-bt, yv-bv
    local_grid = (.003, .03, .3, 3., 30.)
    lf = _local_features(xt, mu, sd)
    lv = _local_features(xv, mu, sd)
    local_state = _local_state(lf, residual, sd)
    locals_ = [_local_predict(lv, local_state, a, sd) for a in local_grid]
    params, gf, targets = _global_state(xt, residual, mu, sd)
    gv = _global_features(xv, params)
    global_grid = (.003, .03, .3, 3.)
    globals_, global_specs = [], []
    for kind in (0, 1):
        globals_.extend(_global_path(gf, gv, targets, kind, global_grid))
        global_specs.extend((kind, a) for a in global_grid)
    base_loss = float(np.mean(error*error))
    best, choice = base_loss, (0, 0, 0., 0.)
    global_stats = [(float(np.mean(error*g)), float(np.mean(g*g))) for g in globals_]
    for i, local in enumerate(locals_):
        el, ll = float(np.mean(error*local)), float(np.mean(local*local))
        for j, glob in enumerate(globals_):
            eg, gg = global_stats[j]
            lg = float(np.mean(local*glob))
            for a in (0., .25, .5, .75, 1.):
                for b in (0., .25, .5, .75, 1.):
                    if a+b > 1.25:
                        continue
                    loss = base_loss-2*a*el-2*b*eg+a*a*ll+b*b*gg+2*a*b*lg
                    loss += .002*base_loss*(a*a+b*b)
                    if loss < best:
                        best, choice = loss, (i, j, a, b)
    li, gi, local_weight, global_weight = choice
    mu, sd = _moments(x, y)
    state = _shared_state(x, y, mu)
    prediction = _shared_predict(tx, mu, state, shared_alpha)
    if local_weight or global_weight:
        residual = y-_shared_predict(x, mu, state, shared_alpha)
    if local_weight:
        local_state = _local_state(_local_features(x, mu, sd), residual, sd)
        correction = _local_predict(_local_features(tx, mu, sd), local_state,
                                    local_grid[li], sd)
        prediction += local_weight*correction
    if global_weight:
        params, gf, targets = _global_state(x, residual, mu, sd)
        gt = _global_features(tx, params)
        kind, alpha = global_specs[gi]
        prediction += global_weight*_global_path(gf, gt, targets, kind, (alpha,))[0]
    return np.nan_to_num(prediction, nan=0., posinf=0., neginf=0.)


def fit_predict(train_x, train_y, test_x, train_groups=None):
    with _limits(limits=1):
        np.random.seed(0)
        return _fit_predict(train_x, train_y, test_x)
