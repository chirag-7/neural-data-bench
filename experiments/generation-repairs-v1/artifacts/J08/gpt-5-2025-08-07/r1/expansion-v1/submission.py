import numpy as np
from scipy import ndimage

# Helper: evenly spaced subset of indices (deterministic)
def _even_indices(n, k):
    if k >= n:
        return np.arange(n, dtype=int)
    return np.linspace(0, n - 1, k, dtype=int)

# Choose global pixel-wise threshold maximizing F1 within ROI
def _choose_threshold(train_x, train_y, idx, thr_grid=None):
    if thr_grid is None:
        thr_grid = np.linspace(0.05, 0.9, 18)
    tp = np.zeros_like(thr_grid, dtype=np.float64)
    fp = np.zeros_like(thr_grid, dtype=np.float64)
    fn = np.zeros_like(thr_grid, dtype=np.float64)
    for i in idx:
        I = train_x[i, 0].astype(np.float32)
        roi = (train_x[i, 1] > 0.5)
        y = train_y[i]
        known = (y >= 0) & roi
        if not np.any(known):
            continue
        gt = (y > 0) & known
        xk = I[known]
        gk = gt[known]
        # Evaluate grid
        for j, t in enumerate(thr_grid):
            pred = xk >= t
            tp[j] += np.sum(pred & gk)
            fp[j] += np.sum(pred & (~gk))
            fn[j] += np.sum((~pred) & gk)
    denom = (2*tp + fp + fn) + 1e-9
    f1 = (2*tp) / denom
    best_idx = int(np.argmax(f1))
    return float(thr_grid[best_idx])

# Estimate object scale (median area) from GT within ROI
def _estimate_scale(train_x, train_y, idx):
    areas = []
    for i in idx:
        y = train_y[i]
        roi = (train_x[i, 1] > 0.5)
        known = (y >= 0) & roi
        if not np.any(known):
            continue
        y2 = y.copy()
        y2[~known] = 0
        if y2.max() <= 0:
            continue
        counts = np.bincount(y2.ravel())
        if counts.size > 1:
            a = counts[1:]
            if a.size:
                areas.extend(a.tolist())
    if not areas:
        med_area = 9.0
    else:
        med_area = float(np.median(np.asarray(areas)))
        med_area = max(1.0, med_area)
    # Derive seed separation and smoothing
    radius = float(np.sqrt(med_area / np.pi))
    seed_min_dist = int(max(1, min(6, round(radius))))
    sigma = float(max(0.6, min(1.2, 0.5 * radius)))
    return med_area, seed_min_dist, sigma

def _relabel_consecutive(lbl):
    if lbl.size == 0:
        return lbl
    u = np.unique(lbl)
    u = u[u > 0]
    if u.size == 0:
        return lbl
    m = np.zeros(int(u.max()) + 1, dtype=np.int32)
    m[u] = np.arange(1, u.size + 1, dtype=np.int32)
    out = m[lbl]
    return out

def _remove_small(lbl, min_size=4):
    if lbl.max() == 0:
        return lbl
    counts = np.bincount(lbl.ravel())
    keep = np.ones_like(counts, dtype=bool)
    keep[0] = True
    idxs = np.arange(counts.size)
    small = (idxs > 0) & (counts < min_size)
    keep[small] = False
    mapping = np.zeros_like(counts, dtype=np.int32)
    kept_ids = idxs[keep]
    # keep 0 as 0, others compacted to 1..K
    mapping[0] = 0
    if kept_ids.size > 1:
        mapping[kept_ids[1:]] = np.arange(1, kept_ids.size, dtype=np.int32)
    out = mapping[lbl]
    return out

def _find_seeds(I, fg, sigma, min_dist, peak_rel):
    if sigma > 0:
        S = ndimage.gaussian_filter(I, sigma=sigma)
    else:
        S = I
    win = int(max(1, 2 * min_dist + 1))
    local_max = (S == ndimage.maximum_filter(S, size=win, mode='nearest'))
    seeds0 = local_max & (S >= peak_rel) & fg
    # Reduce plateaus to single point
    lab, nlab = ndimage.label(seeds0, structure=np.ones((3, 3), dtype=bool))
    seeds = np.zeros_like(seeds0, dtype=bool)
    if nlab > 0:
        slices = ndimage.find_objects(lab)
        for k, sl in enumerate(slices, start=1):
            if sl is None:
                continue
            patch_lab = lab[sl]
            mask = (patch_lab == k)
            if not mask.any():
                continue
            patch_S = S[sl]
            coords = np.argwhere(mask)
            vals = patch_S[mask]
            m = int(np.argmax(vals))
            r, c = coords[m]
            rr = sl[0].start + r
            cc = sl[1].start + c
            seeds[rr, cc] = True
    return seeds, S

def _ensure_seed_per_component(fg, seeds, strength):
    # strength is the smoothed intensity image S
    cc, ncc = ndimage.label(fg, structure=np.ones((3, 3), dtype=bool))
    if ncc == 0:
        return seeds
    counts = ndimage.sum(seeds, cc, index=np.arange(1, ncc + 1))
    slices = ndimage.find_objects(cc)
    seeds_out = seeds.copy()
    for i in range(1, ncc + 1):
        if counts[i - 1] > 0:
            continue
        sl = slices[i - 1]
        if sl is None:
            continue
        mask = (cc[sl] == i)
        if not np.any(mask):
            continue
        patch_S = strength[sl]
        vals = patch_S[mask]
        m = int(np.argmax(vals))
        coords = np.argwhere(mask)
        r, c = coords[m]
        rr = sl[0].start + r
        cc0 = sl[1].start + c
        seeds_out[rr, cc0] = True
    return seeds_out

def _voronoi_label_from_seeds(fg, seeds):
    if not np.any(fg):
        return np.zeros_like(fg, dtype=np.int32)
    if not np.any(seeds):
        # Single object per FG component
        cc, _ = ndimage.label(fg, structure=np.ones((3, 3), dtype=bool))
        return cc.astype(np.int32)
    # Assign each pixel to nearest seed using EDT indices
    seed_labels = np.zeros(fg.shape, dtype=np.int32)
    coords = np.argwhere(seeds)
    for k, (r, c) in enumerate(coords, start=1):
        seed_labels[r, c] = k
    inv = (seed_labels == 0)
    inds = ndimage.distance_transform_edt(inv, return_distances=False, return_indices=True)
    nearest = seed_labels[inds[0], inds[1]]
    lbl = (nearest * fg.astype(np.int32))
    return lbl

def _segment_image(I, extent_mask, thr, sigma, peak_rel, seed_min_dist, min_keep=4):
    I = np.asarray(I, dtype=np.float32)
    extent = extent_mask.astype(bool)
    if sigma > 0:
        S = ndimage.gaussian_filter(I, sigma=sigma)
    else:
        S = I
    fg = (I >= thr) & extent
    # Remove tiny FG islands before seeding (<=2 px)
    cc0, n0 = ndimage.label(fg, structure=np.ones((3, 3), dtype=bool))
    if n0 > 0:
        cnts = np.bincount(cc0.ravel())
        tiny = (np.arange(cnts.size) > 0) & (cnts < 3)
        if tiny.any():
            rm = tiny[cc0]
            fg[rm] = False
    seeds0, S2 = _find_seeds(I, fg, sigma, seed_min_dist, peak_rel)
    seeds = _ensure_seed_per_component(fg, seeds0, S2)
    lbl = _voronoi_label_from_seeds(fg, seeds)
    lbl = _remove_small(lbl, min_size=min_keep)
    lbl[~extent] = 0
    lbl = _relabel_consecutive(lbl)
    return lbl.astype(np.int32)

def fit_predict(train_x, train_y, test_x):
    # Expect shapes: train_x(N,2,128,128), train_y(N,128,128), test_x(2,2,H,W)
    train_x = np.asarray(train_x)
    train_y = np.asarray(train_y)
    test_x = np.asarray(test_x)
    n = train_x.shape[0]
    # Subsample patches for speed and de-correlation
    idx = _even_indices(n, min(400, n))
    thr = _choose_threshold(train_x, train_y, idx)
    med_area, seed_min_dist, sigma = _estimate_scale(train_x, train_y, idx)
    peak_rel = float(min(0.95, max(thr + 0.10, thr * 1.15)))
    min_keep = 4
    # Segment each test image separately
    T = test_x.shape[0]
    H, W = test_x.shape[2], test_x.shape[3]
    out = np.zeros((T, H, W), dtype=np.int32)
    for i in range(T):
        I = test_x[i, 0].astype(np.float32)
        extent = (test_x[i, 1] > 0.5)
        lab = _segment_image(I, extent, thr, sigma, peak_rel, seed_min_dist, min_keep=min_keep)
        out[i] = lab
    return out
