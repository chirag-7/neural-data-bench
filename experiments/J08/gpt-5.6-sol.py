import numpy as np
from scipy import ndimage
from sklearn.ensemble import HistGradientBoostingClassifier


def _features(a):
    a = np.asarray(a, dtype=np.float32)
    g1 = ndimage.gaussian_filter(a, 0.8, mode='nearest')
    g2 = ndimage.gaussian_filter(a, 1.6, mode='nearest')
    g4 = ndimage.gaussian_filter(a, 3.2, mode='nearest')
    lap = -ndimage.gaussian_laplace(a, 1.2, mode='nearest')
    gx = ndimage.sobel(g1, axis=1, mode='nearest') * 0.125
    gy = ndimage.sobel(g1, axis=0, mode='nearest') * 0.125
    grad = np.sqrt(gx * gx + gy * gy)
    z = np.stack((a, g1, g2, g4, a - g2, g1 - g4, lap, grad), axis=-1)
    return z.reshape(-1, z.shape[-1])


def _truth_instances(y, valid):
    out = np.zeros(y.shape, np.int32)
    nxt = 1
    vals = np.unique(y[(y > 0) & valid])
    for v in vals:
        lab, n = ndimage.label((y == v) & valid)
        if n:
            sizes = np.bincount(lab.ravel())
            for k in range(1, n + 1):
                if sizes[k] >= 4:
                    out[lab == k] = nxt
                    nxt += 1
    return out


def _remove_tiny_and_renumber(a):
    if not np.any(a):
        return np.zeros(a.shape, np.int32)
    counts = np.bincount(a.ravel())
    keep = counts >= 4
    keep[0] = False
    table = np.zeros(len(counts), np.int32)
    table[keep] = np.arange(1, np.count_nonzero(keep) + 1)
    return table[a]


def _segment(prob, extent, threshold, peak_size, split_min):
    mask = (prob >= threshold) & extent
    if not np.any(mask):
        return np.zeros(mask.shape, np.int32)
    mask = ndimage.binary_fill_holes(mask) & extent
    comp, nc = ndimage.label(mask)
    sizes = np.bincount(comp.ravel())
    mask &= sizes[comp] >= 4
    comp, nc = ndimage.label(mask)
    if nc == 0:
        return np.zeros(mask.shape, np.int32)

    dist = ndimage.distance_transform_edt(mask)
    smooth = ndimage.gaussian_filter(dist, 0.6)
    maxima = ndimage.maximum_filter(smooth, size=peak_size, mode='constant')
    peaks = mask & (smooth >= maxima - 1e-6) & (dist >= 1.0)

    sizes = np.bincount(comp.ravel())
    boxes = ndimage.find_objects(comp)
    for k, sl in enumerate(boxes, 1):
        if sl is None or sizes[k] >= split_min:
            continue
        local = comp[sl] == k
        p = peaks[sl].copy()
        p[local] = False
        score = np.where(local, smooth[sl], -1.0)
        p.flat[int(np.argmax(score))] = True
        peaks[sl] = p

    seed, ns = ndimage.label(peaks)
    if ns == 0:
        return np.zeros(mask.shape, np.int32)
    _, nearest = ndimage.distance_transform_edt(~peaks, return_indices=True)
    near_seed = seed[nearest[0], nearest[1]]
    key = comp.astype(np.int64) * (ns + 1) + near_seed
    out = np.zeros(mask.shape, np.int32)
    _, inv = np.unique(key[mask], return_inverse=True)
    out[mask] = inv.astype(np.int32) + 1
    return _remove_tiny_and_renumber(out)


def _match_counts(pred, truth):
    npred = int(pred.max())
    ntrue = int(truth.max())
    if npred == 0 or ntrue == 0:
        return 0, npred, ntrue
    pa = np.bincount(pred.ravel(), minlength=npred + 1)
    ta = np.bincount(truth.ravel(), minlength=ntrue + 1)
    use = (pred > 0) & (truth > 0)
    if not np.any(use):
        return 0, npred, ntrue
    base = ntrue + 1
    keys, inter = np.unique(pred[use].astype(np.int64) * base + truth[use],
                            return_counts=True)
    pi = keys // base
    ti = keys % base
    iou = inter / (pa[pi] + ta[ti] - inter)
    good = np.flatnonzero(iou >= 0.5)
    if good.size == 0:
        return 0, npred, ntrue
    good = good[np.argsort(iou[good])[::-1]]
    used_p = np.zeros(npred + 1, bool)
    used_t = np.zeros(ntrue + 1, bool)
    hits = 0
    for q in good:
        p, t = int(pi[q]), int(ti[q])
        if not used_p[p] and not used_t[t]:
            used_p[p] = True
            used_t[t] = True
            hits += 1
    return hits, npred, ntrue


def _odd_size(x):
    x = max(3, int(round(x)))
    return x if x % 2 else x + 1


def fit_predict(train_x, train_y, test_x):
    rng = np.random.RandomState(17041)
    n = train_x.shape[0]

    nominal_group = max(32, int(round(n / 27.0)))
    group = np.arange(n) // nominal_group
    held_groups = np.arange(2, int(group.max()) + 1, 6)
    is_val = np.isin(group, held_groups)
    fit_pool = np.flatnonzero(~is_val)
    val_pool = np.flatnonzero(is_val)
    fit_idx = rng.choice(fit_pool, min(500, fit_pool.size), replace=False)
    val_idx = rng.choice(val_pool, min(84, val_pool.size), replace=False)

    xs = []
    ys = []
    object_areas = []
    for j in fit_idx:
        im = np.asarray(train_x[j, 0], dtype=np.float32)
        yy = np.asarray(train_y[j])
        valid = (train_x[j, 1] > 0.5) & (yy >= 0)
        pos = np.flatnonzero(valid & (yy > 0))
        neg = np.flatnonzero(valid & (yy == 0))
        if pos.size:
            take = rng.choice(pos, min(140, pos.size), replace=False)
            xs.append(_features(im)[take])
            ys.append(np.ones(take.size, np.uint8))
            _, cnt = np.unique(yy.ravel()[pos], return_counts=True)
            object_areas.extend(cnt[cnt >= 4].tolist())
        if neg.size:
            nr = min(90, neg.size)
            random_neg = rng.choice(neg, nr, replace=False)
            nh = min(90, neg.size)
            vals = im.ravel()[neg]
            if nh < neg.size:
                hard_neg = neg[np.argpartition(vals, -nh)[-nh:]]
            else:
                hard_neg = neg
            take = np.concatenate((random_neg, hard_neg))
            f = _features(im) if not pos.size else None
            if f is None:
                f = _features(im)
            xs.append(f[take])
            ys.append(np.zeros(take.size, np.uint8))

    X = np.concatenate(xs, axis=0)
    Y = np.concatenate(ys, axis=0)
    order = rng.permutation(Y.size)
    X = X[order]
    Y = Y[order]
    model = HistGradientBoostingClassifier(
        learning_rate=0.08, max_iter=75, max_leaf_nodes=15,
        min_samples_leaf=24, l2_regularization=0.15,
        early_stopping=True, validation_fraction=0.1,
        n_iter_no_change=8, random_state=17041)
    model.fit(X, Y)
    del X, Y, xs, ys

    median_area = float(np.median(object_areas)) if object_areas else 30.0
    diameter = 2.0 * np.sqrt(median_area / np.pi)
    psmall = _odd_size(0.70 * diameter)
    plarge = _odd_size(1.00 * diameter)
    split_a = max(8, int(round(1.35 * median_area)))
    split_b = max(8, int(round(1.75 * median_area)))
    modes = ((plarge, 10 ** 9), (psmall, split_a), (plarge, split_b))
    thresholds = (0.72, 0.62, 0.52, 0.42, 0.32, 0.24)

    cache = []
    for j in val_idx:
        im = np.asarray(train_x[j, 0], dtype=np.float32)
        yy = np.asarray(train_y[j])
        extent = (train_x[j, 1] > 0.5) & (yy >= 0)
        prob = model.predict_proba(_features(im))[:, 1].reshape(im.shape)
        truth = _truth_instances(yy, extent)
        cache.append((prob.astype(np.float32), extent, truth))

    best_score = -1.0
    best = (0.52, plarge, 10 ** 9)
    for threshold in thresholds:
        for peak_size, split_min in modes:
            hits = preds = truths = 0
            for prob, extent, truth in cache:
                pred = _segment(prob, extent, threshold, peak_size, split_min)
                h, p, t = _match_counts(pred, truth)
                hits += h
                preds += p
                truths += t
            score = 2.0 * hits / max(1, preds + truths)
            if score > best_score:
                best_score = score
                best = (threshold, peak_size, split_min)

    threshold, peak_size, split_min = best
    result = np.zeros((test_x.shape[0], test_x.shape[2], test_x.shape[3]),
                      dtype=np.int32)
    for j in range(test_x.shape[0]):
        im = np.asarray(test_x[j, 0], dtype=np.float32)
        extent = np.asarray(test_x[j, 1]) > 0.5
        prob = model.predict_proba(_features(im))[:, 1].reshape(im.shape)
        result[j] = _segment(prob, extent, threshold, peak_size, split_min)
        result[j, ~extent] = 0
    return result
