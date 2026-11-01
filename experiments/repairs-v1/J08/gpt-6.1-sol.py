import numpy as np
from scipy import ndimage as ndi
from scipy.optimize import linear_sum_assignment
from sklearn.ensemble import ExtraTreesRegressor

_CONN = np.ones((3, 3), dtype=bool)

def _features(a):
    a = np.asarray(a, dtype=np.float32)
    g = [ndi.gaussian_filter(a, s) for s in (0.7, 1.4, 2.8, 5.6, 9.0)]
    sd = np.sqrt(np.maximum(ndi.gaussian_filter(a * a, 2.8) - g[2] ** 2, 0))
    dx = ndi.sobel(g[1], axis=1) * 0.125
    dy = ndi.sobel(g[1], axis=0) * 0.125
    xx = ndi.gaussian_filter(a, 1.1, order=(0, 2))
    yy = ndi.gaussian_filter(a, 1.1, order=(2, 0))
    xy = ndi.gaussian_filter(a, 1.1, order=(1, 1))
    tr = xx + yy
    disc = np.sqrt((xx - yy) ** 2 + 4 * xy ** 2)
    f = [a] + g + [g[0] - g[2], g[1] - g[3], g[2] - g[4],
        a - g[4], (a - g[4]) / (sd + 0.04), sd,
        np.sqrt(dx * dx + dy * dy), tr, (tr - disc) * 0.5,
        (tr + disc) * 0.5,
        ndi.maximum_filter(a, 3) - ndi.minimum_filter(a, 3),
        ndi.maximum_filter(a, 7) - ndi.minimum_filter(a, 7)]
    return np.stack(f, axis=-1).astype(np.float32)

def _objects(y, valid):
    z = np.where(valid & (y > 0), y, 0)
    _, inv = np.unique(z, return_inverse=True)
    lab = inv.reshape(z.shape).astype(np.int32) + 1
    lab[z == 0] = 0
    out = np.zeros(z.shape, np.int32)
    center = np.zeros(z.shape, np.float32)
    radii = []
    count = 0
    for k, sl in enumerate(ndi.find_objects(lab), 1):
        if sl is None:
            continue
        pieces, n = ndi.label(lab[sl] == k, structure=_CONN)
        for j in range(1, n + 1):
            obj = pieces == j
            if np.count_nonzero(obj) < 4:
                continue
            d = ndi.distance_transform_edt(np.pad(obj, 1))[1:-1, 1:-1]
            radius = float(d.max())
            count += 1
            out[sl][obj] = count
            center[sl][obj] = (d[obj] / max(radius, 1)).astype(np.float32)
            radii.append(radius)
    return out, center, radii

def _segment(p, c, valid, threshold, seed_threshold, radius):
    p = ndi.gaussian_filter(p.astype(np.float32), 0.55)
    c = ndi.gaussian_filter(c.astype(np.float32), 0.7)
    mask = (p >= threshold) & valid
    mask = ndi.binary_fill_holes(mask) & valid
    cc, n = ndi.label(mask, structure=_CONN)
    if n == 0:
        return np.zeros(mask.shape, np.int32)
    peaks = mask & (c >= seed_threshold)
    peaks &= c >= ndi.maximum_filter(c, size=2 * radius + 1)
    markers, ns = ndi.label(peaks, structure=_CONN)
    indices = np.arange(1, n + 1)
    present = np.asarray(ndi.maximum(markers, labels=cc, index=indices))
    missing = indices[present == 0]
    if missing.size:
        positions = ndi.maximum_position(c, labels=cc, index=missing)
        for pos in positions:
            ns += 1
            markers[pos] = ns
    surface = np.clip(255 * (1 - 0.75 * c - 0.25 * p), 0, 254).astype(np.uint8)
    surface[~mask] = 255
    markers = markers.astype(np.int32)
    markers[~mask] = -1
    result = ndi.watershed_ift(surface, markers, structure=_CONN)
    result[~mask] = 0
    result[result < 0] = 0
    sizes = np.bincount(result.ravel())
    result[sizes[result] < 4] = 0
    return result.astype(np.int32)

def _counts(gt, pred):
    _, g = np.unique(gt.ravel(), return_inverse=True)
    _, p = np.unique(pred.ravel(), return_inverse=True)
    # Explicit background slots also handle images entirely covered by objects.
    g = g + 1
    p = p + 1
    g[gt.ravel() == 0] = 0
    p[pred.ravel() == 0] = 0
    ng, npred = int(g.max()), int(p.max())
    ag = np.bincount(g, minlength=ng + 1)
    ap = np.bincount(p, minlength=npred + 1)
    inter = np.bincount(g * (npred + 1) + p,
                        minlength=(ng + 1) * (npred + 1)).reshape(ng + 1, npred + 1)
    active_g = np.flatnonzero(ag[1:]) + 1
    active_p = np.flatnonzero(ap[1:]) + 1
    if not active_g.size or not active_p.size:
        return 0, int(active_p.size), int(active_g.size)
    it = inter[np.ix_(active_g, active_p)]
    iou = it / np.maximum(ag[active_g, None] + ap[None, active_p] - it, 1)
    matches = iou >= 0.5
    rows, cols = linear_sum_assignment(-matches.astype(float) - iou * 1e-5)
    return int(matches[rows, cols].sum()), int(active_p.size), int(active_g.size)

def _validation_split(x, rng):
    n = len(x)
    steps = np.full(n, np.nan)
    for i in range(n):
        a = np.asarray(x[i, 0, ::2, ::2]).ravel()
        u = np.unique(a[(a > 0.002) & (a < 0.998)])
        if u.size < 64:
            continue
        gaps = np.diff(u).astype(np.float64)
        d = float(np.quantile(gaps, 0.2))
        if d <= 1e-7:
            continue
        close = gaps[(gaps > 0.8 * d) & (gaps < 1.2 * d)]
        if close.size < 16:
            continue
        d = float(np.median(close))
        delta = u.astype(np.float64) - float(u[0])
        k = np.rint(delta / d)
        d = float(np.dot(k, delta) / max(np.dot(k, k), 1))
        if d > 0 and np.mean(np.abs(delta / d - k) < 0.04) > 0.94:
            steps[i] = d
    groups = np.full(n, -1, dtype=int)
    order = np.flatnonzero(np.isfinite(steps))
    order = order[np.argsort(steps[order])]
    gid, anchor = -1, 0.0
    for i in order:
        if gid < 0 or abs(steps[i] - anchor) > 0.0003 * anchor:
            gid += 1
            anchor = steps[i]
        groups[i] = gid
    candidates = [g for g in range(gid + 1)
                  if 8 <= np.count_nonzero(groups == g) <= max(16, n // 4)]
    if len(order) > 0.7 * n and 5 <= gid + 1 <= 100 and len(candidates) >= 3:
        held = []
        total = 0
        for g in rng.permutation(candidates):
            held.append(g)
            total += np.count_nonzero(groups == g)
            if total >= max(32, int(n * 0.10)):
                break
        excluded = np.isin(groups, held)
    else:
        width = max(1, int(n * 0.14))
        start = max(0, (n - width) // 2)
        excluded = np.zeros(n, bool)
        excluded[max(0, start - 12):min(n, start + width + 12)] = True
        groups[:] = 0
    validation = np.flatnonzero(excluded)
    validation = rng.permutation(validation)[:40]
    training = np.flatnonzero(~excluded)
    if training.size == 0:
        training = np.arange(n)
    return training, validation, groups

def fit_predict(train_x, train_y, test_x):
    rng = np.random.RandomState(314159)
    training, validation, groups = _validation_split(train_x, rng)
    samples, targets, radii = [], [], []
    for i in training:
        a = np.nan_to_num(np.asarray(train_x[i, 0], dtype=np.float32),
                          nan=0.0, posinf=1.0, neginf=0.0)
        valid = (np.asarray(train_x[i, 1]) > 0.5) & (train_y[i] >= 0)
        if not valid.any():
            continue
        gt, center, rr = _objects(train_y[i], valid)
        radii.extend(rr)
        safe = ndi.binary_erosion(valid, iterations=2)
        if safe.sum() < 32:
            safe = valid
        available = np.flatnonzero(safe)
        positive = np.flatnonzero(safe & (gt > 0))
        ix = rng.choice(available, min(128, available.size), replace=False)
        if positive.size:
            ix = np.concatenate((ix, rng.choice(positive, min(64, positive.size), replace=False)))
        f = _features(a).reshape(-1, 18)
        samples.append(f[ix])
        targets.append(np.column_stack(((gt.ravel()[ix] > 0).astype(np.float32),
                                         center.ravel()[ix])))
    output = np.zeros((len(test_x), test_x.shape[2], test_x.shape[3]), np.int32)
    if not samples:
        return output
    model = ExtraTreesRegressor(n_estimators=48, max_depth=18,
        min_samples_leaf=5, max_features=0.75, n_jobs=1, random_state=271828)
    model.fit(np.concatenate(samples), np.concatenate(targets))
    del samples, targets
    radius = int(np.clip(np.rint(np.median(radii) * 0.85), 1, 4)) if radii else 2
    records = []
    for i in validation:
        valid = (np.asarray(train_x[i, 1]) > 0.5) & (train_y[i] >= 0)
        if valid.sum() < 64:
            continue
        a = np.nan_to_num(np.asarray(train_x[i, 0], np.float32),
                          nan=0.0, posinf=1.0, neginf=0.0)
        shape = a.shape
        prediction = model.predict(_features(a).reshape(-1, 18)).reshape(*shape, 2)
        gt, _, _ = _objects(train_y[i], valid)
        records.append((prediction, valid, gt, int(groups[i])))
    best, chosen = -1.0, (0.48, 0.30)
    for threshold in (0.30, 0.40, 0.50, 0.60, 0.70):
        for seed_threshold in (0.18, 0.30, 0.42):
            totals = {}
            for pr, valid, gt, group in records:
                pred = _segment(pr[..., 0], pr[..., 1], valid, threshold, seed_threshold, radius)
                counts = np.asarray(_counts(gt, pred), dtype=float)
                totals[group] = totals.get(group, np.zeros(3)) + counts
            scores = [2 * v[0] / max(v[1] + v[2], 1) for v in totals.values()]
            score = float(np.mean(scores)) if scores else -1.0
            if score > best:
                best, chosen = score, (threshold, seed_threshold)
    for i in range(len(test_x)):
        extent = np.asarray(test_x[i, 1]) > 0.5
        rows, cols = np.where(extent)
        if rows.size == 0:
            continue
        sl = (slice(int(rows.min()), int(rows.max()) + 1),
              slice(int(cols.min()), int(cols.max()) + 1))
        a = np.nan_to_num(np.asarray(test_x[i, 0][sl], np.float32),
                          nan=0.0, posinf=1.0, neginf=0.0)
        pr = model.predict(_features(a).reshape(-1, 18)).reshape(*a.shape, 2)
        output[i][sl] = _segment(pr[..., 0], pr[..., 1], extent[sl],
                                  chosen[0], chosen[1], radius)
    return output
