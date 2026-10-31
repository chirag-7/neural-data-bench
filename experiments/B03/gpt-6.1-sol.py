import numpy as np
from scipy.ndimage import gaussian_filter1d
from scipy.sparse import csr_matrix, diags, eye
from scipy.sparse.linalg import spsolve


def _center(a):
    return a - np.mean(a, axis=-1, keepdims=True)


def _scale(z, y):
    z, y = _center(z), _center(y)
    den = float(np.sum(z * z))
    if den < 1e-10:
        return 1.0
    return float(np.clip((np.sum(z * y) / den + 0.04) / 1.04, 0.5, 1.8))


def _graph(f):
    n, m = f.shape
    radius = 12
    cc = np.empty((2 * radius + 1, n, n))
    for lag in range(radius + 1):
        a = f[:, :m-lag] if lag else f
        b = f[:, lag:] if lag else f
        sa, sb = a.sum(axis=1), b.sum(axis=1)
        length = a.shape[1]
        cross = np.einsum('ik,jk->ij', a, b, optimize=False)
        cross -= sa[:, None] * sb[None, :] / length
        va = np.maximum(np.sum(a*a, axis=1) - sa*sa/length, 1e-12)
        vb = np.maximum(np.sum(b*b, axis=1) - sb*sb/length, 1e-12)
        c = cross / np.sqrt(va[:, None] * vb[None, :])
        cc[radius + lag] = c
        cc[radius - lag] = c.T
    ii, jj = np.triu_indices(n, 1)
    curves = cc[:, ii, jj]
    k = np.argmax(curves, axis=0)
    edge = np.arange(len(ii))
    kc = np.clip(k, 1, 2*radius-1)
    left, mid, right = curves[kc-1, edge], curves[kc, edge], curves[kc+1, edge]
    frac = 0.5*(left-right) / np.minimum(left-2*mid+right, -1e-12)
    frac = np.where((k > 0) & (k < 2*radius), np.clip(frac, -0.5, 0.5), 0)
    delta = 5.0 * (k - radius + frac)
    peak = curves[k, edge]
    distant = np.abs(np.arange(2*radius+1)[:, None] - k[None, :]) >= 3
    alternative = np.max(np.where(distant, curves, -1.0), axis=0)
    margin = np.maximum(peak-alternative, 0)
    base = np.maximum(peak-0.1, 0)**2
    base *= 0.3 + 0.7*np.clip(margin/0.12, 0, 1)
    if base.sum() < 1e-10:
        return np.zeros(n)
    weights = base.copy()
    idx = np.arange(n)
    adjacent = np.arange(n-1)
    d = np.zeros(n)
    for iteration in range(8):
        wmat = np.zeros((n, n))
        wmat[ii, jj] = weights
        wmat += wmat.T
        degree = wmat.sum(axis=1)
        strength = max(float(degree.mean()), 1e-8)
        lap = -wmat
        lap[idx, idx] += degree + 1e-6*strength
        prior = 0.003*strength
        lap[adjacent, adjacent] += prior
        lap[adjacent+1, adjacent+1] += prior
        lap[adjacent, adjacent+1] -= prior
        lap[adjacent+1, adjacent] -= prior
        rhs = np.bincount(jj, weights*delta, minlength=n)
        rhs -= np.bincount(ii, weights*delta, minlength=n)
        d = spsolve(csr_matrix(lap), rhs, use_umfpack=False)
        d -= d.mean()
        residual = d[jj]-d[ii]-delta
        spread = max(2.0, 1.4826*np.median(np.abs(residual-np.median(residual))))
        weights = base / (1.0 + (residual/(2.0*spread))**2)
    return d


def _refine(f, initial):
    n, m = f.shape
    f = _center(f)
    f /= np.maximum(np.sqrt(np.sum(f*f, axis=1, keepdims=True)), 1e-10)
    grid = np.arange(m, dtype=float)
    extent = np.arange(-20, m+20, dtype=float)
    d = initial.copy()
    shifts = np.arange(min(-45.0, d.min()-15), max(45.0, d.max()+15)+0.25, 0.5)
    for iteration in range(3):
        total = np.zeros(len(extent))
        coverage = np.zeros(len(extent))
        for t in range(n):
            coordinate = extent+d[t]/5.0
            valid = (coordinate >= 0) & (coordinate <= m-1)
            total += np.interp(coordinate, grid, f[t], left=0, right=0)
            coverage += valid
        template = total / np.maximum(coverage, 1)
        shifted = np.interp(grid[None, :]-shifts[:, None]/5.0, extent, template)
        shifted = _center(shifted)
        shifted /= np.maximum(np.sqrt(np.sum(shifted*shifted, axis=1, keepdims=True)), 1e-10)
        scores = np.einsum('ik,jk->ij', f, shifted, optimize=False)
        scores -= 0.00015*(shifts[None, :]-initial[:, None])**2
        k = np.argmax(scores, axis=1)
        kc = np.clip(k, 1, len(shifts)-2)
        rows = np.arange(n)
        left, mid, right = scores[rows, kc-1], scores[rows, kc], scores[rows, kc+1]
        frac = 0.5*(left-right)/np.minimum(left-2*mid+right, -1e-12)
        frac = np.where((k > 0) & (k < len(shifts)-1), np.clip(frac, -0.5, 0.5), 0)
        new = shifts[k]+0.5*frac
        d = _center(0.25*d+0.75*new)
    return d


def _estimate(x, config):
    sigma, power = config
    f = gaussian_filter1d(x**power, sigma, axis=1, mode='constant')
    f -= gaussian_filter1d(f, 8.0, axis=1, mode='constant')
    d = _graph(f)
    return d, _refine(f, d)


def _smooth(z, setting):
    mode, amount = setting
    if amount == 0:
        return _center(z.copy())
    if mode == 'gaussian':
        return _center(gaussian_filter1d(z, amount, mode='nearest'))
    n = len(z)
    difference = diags([np.ones(n-2), -2*np.ones(n-2), np.ones(n-2)],
                       [0, 1, 2], shape=(n-2, n), format='csr')
    identity = eye(n, format='csr')
    out = z.copy()
    for iteration in range(12):
        curvature = difference @ out
        weights = 1.0/np.sqrt(curvature*curvature+0.5**2)
        system = identity + amount*(difference.T @ diags(weights) @ difference)
        out = spsolve(system.tocsc(), z, use_umfpack=False)
    return _center(out)


def fit_predict(train_x, train_y, test_x, train_groups):
    np.random.seed(0)
    train = np.maximum(np.nan_to_num(np.asarray(train_x, dtype=float),
                                   nan=0.0, posinf=0.0, neginf=0.0), 0)
    test = np.maximum(np.nan_to_num(np.asarray(test_x, dtype=float),
                                  nan=0.0, posinf=0.0, neginf=0.0), 0)
    y = _center(np.asarray(train_y, dtype=float))
    configs = [(s, p) for s in (0.8, 1.4, 2.2, 3.2) for p in (0.5, 1.0)]
    settings = [('gaussian', s) for s in (0, 0.65, 1.2, 2.0)]
    settings += [('trend', s) for s in (2.0, 6.0, 18.0)]
    candidates = []
    recordings = np.arange(len(train))
    for config_id, config in enumerate(configs):
        estimates = [_estimate(row, config) for row in train]
        for kind in (0, 1):
            raw = np.stack([pair[kind] for pair in estimates])
            for setting_id, setting in enumerate(settings):
                z = np.stack([_smooth(row, setting) for row in raw])
                losses = []
                for held in recordings:
                    keep = recordings != held
                    gain = _scale(z[keep], y[keep])
                    losses.append(np.sqrt(np.mean((gain*z[held]-y[held])**2)))
                candidates.append((float(np.mean(losses)), config_id, kind, setting_id, z))
    candidates.sort(key=lambda item: item[0])
    best = candidates[0][0]
    selected = []
    counts = {}
    for candidate in candidates:
        loss, config_id, kind, setting_id, z = candidate
        if loss > best+max(0.3, 0.15*best):
            break
        if counts.get(config_id, 0) >= 2:
            continue
        selected.append(candidate)
        counts[config_id] = counts.get(config_id, 0)+1
        if len(selected) == 6:
            break
    temperature = max(0.08, 0.08*best)
    weights = np.exp(-np.array([c[0]-best for c in selected])/temperature)
    weights /= weights.sum()
    gains = [_scale(c[4], y) for c in selected]
    result = np.zeros(test.shape[:2], dtype=float)
    for recording_id, row in enumerate(test):
        cache = {}
        prediction = np.zeros(row.shape[0], dtype=float)
        for weight, gain, candidate in zip(weights, gains, selected):
            loss, config_id, kind, setting_id, z = candidate
            if config_id not in cache:
                cache[config_id] = _estimate(row, configs[config_id])
            displacement = _smooth(cache[config_id][kind], settings[setting_id])
            prediction += weight*gain*displacement
        result[recording_id] = _center(prediction)
    return np.nan_to_num(result, nan=0.0, posinf=0.0, neginf=0.0)
