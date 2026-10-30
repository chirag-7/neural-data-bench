import numpy as np
from scipy.signal import find_peaks
from sklearn.decomposition import PCA
from sklearn.mixture import GaussianMixture


def _cos(a, b):
    a = np.asarray(a).ravel().astype(np.float64, copy=False)
    b = np.asarray(b).ravel().astype(np.float64, copy=False)
    d = np.sqrt(np.dot(a, a) * np.dot(b, b))
    return float(np.dot(a, b) / d) if d > 0 else 0.0


def _dedup(indices, times, strengths, refractory=20):
    if len(indices) < 2:
        return np.asarray(indices, dtype=np.int64)
    ii = np.asarray(indices, dtype=np.int64)
    ii = ii[np.argsort(times[ii], kind="mergesort")]
    keep = [int(ii[0])]
    for q in ii[1:]:
        q = int(q)
        p = keep[-1]
        if times[q] - times[p] < refractory:
            if strengths[q] > strengths[p]:
                keep[-1] = q
        else:
            keep.append(q)
    return np.asarray(keep, dtype=np.int64)


def _coincidence(a, b, tol=8):
    a = np.sort(np.asarray(a, dtype=np.int64))
    b = np.sort(np.asarray(b, dtype=np.int64))
    i = j = hit = 0
    while i < len(a) and j < len(b):
        d = int(a[i]) - int(b[j])
        if abs(d) <= tol:
            hit += 1
            i += 1
            j += 1
        elif d < 0:
            i += 1
        else:
            j += 1
    return hit / max(1, min(len(a), len(b)))


def sort(recording_uv, fs, channel_positions_um):
    x = np.asarray(recording_uv, dtype=np.float32)
    if x.ndim != 2 or x.shape[0] < 80 or x.shape[1] < 1:
        return np.empty((0, 2), dtype=np.int64)
    n, nc = x.shape
    x = np.nan_to_num(x, copy=True, nan=0.0, posinf=0.0, neginf=0.0)

    x -= np.median(x[::8], axis=0).astype(np.float32)
    if nc >= 4:
        x -= np.median(x, axis=1).astype(np.float32)[:, None]
    probe = x[::5]
    med = np.median(probe, axis=0)
    noise = np.median(np.abs(probe - med), axis=0) / 0.67448975
    good = noise[np.isfinite(noise) & (noise > 1e-4)]
    fallback = float(np.median(good)) if good.size else 1.0
    noise = np.where(np.isfinite(noise) & (noise > fallback * 0.08), noise, fallback)
    x /= noise.astype(np.float32)[None, :]

    pos = np.asarray(channel_positions_um, dtype=np.float64)
    if pos.shape != (nc, 3) or not np.all(np.isfinite(pos)):
        pos = np.zeros((nc, 3), dtype=np.float64)
        pos[:, 0] = np.arange(nc, dtype=np.float64)
    if nc > 1:
        dist = np.sqrt(np.sum((pos[:, None, :] - pos[None, :, :]) ** 2, axis=2))
        dd = dist + np.eye(nc) * 1e30
        spacing = float(np.median(np.min(dd, axis=1)))
        radius = min(150.0, max(55.0, 3.2 * spacing))
        neighbors = dist <= radius
    else:
        neighbors = np.ones((1, 1), dtype=bool)

    cand_t = []
    cand_c = []
    cand_s = []
    threshold = 3.8
    for c in range(nc):
        p, prop = find_peaks(-x[:, c], height=threshold, distance=7)
        if p.size:
            h = prop["peak_heights"]
            ok = (p >= 28) & (p < n - 36) & (h < 80.0)
            cand_t.append(p[ok])
            cand_c.append(np.full(np.sum(ok), c, dtype=np.int32))
            cand_s.append(h[ok].astype(np.float32))
    if not cand_t:
        return np.empty((0, 2), dtype=np.int64)
    ct = np.concatenate(cand_t).astype(np.int64)
    cc = np.concatenate(cand_c).astype(np.int32)
    cs = np.concatenate(cand_s).astype(np.float32)
    order = np.argsort(-cs, kind="mergesort")
    blocked = np.zeros((n, nc), dtype=bool)
    accepted = []
    for q in order:
        t = int(ct[q])
        c = int(cc[q])
        if not blocked[t, c]:
            accepted.append(int(q))
            a = max(0, t - 11)
            b = min(n, t + 12)
            blocked[a:b, neighbors[c]] = True
    del blocked
    if not accepted:
        return np.empty((0, 2), dtype=np.int64)
    accepted = np.asarray(accepted, dtype=np.int64)
    if accepted.size > 30000:
        z = np.argpartition(cs[accepted], -30000)[-30000:]
        accepted = accepted[z]
    ev = ct[accepted]
    anchor = cc[accepted]
    strength = cs[accepted]
    oo = np.argsort(ev, kind="mergesort")
    ev, anchor, strength = ev[oo], anchor[oo], strength[oo]
    m = len(ev)
    if m < 6:
        return np.empty((0, 2), dtype=np.int64)

    pre, post = 24, 36
    offsets = np.arange(-pre, post + 1, dtype=np.int64)
    wave = x[ev[:, None] + offsets[None, :], :].astype(np.float32, copy=False)
    center = pre
    ampvec = np.maximum(-np.min(wave[:, center-3:center+4, :], axis=1), 0.0)
    weights = ampvec * ampvec + 1e-5
    loc = (weights @ pos) / np.sum(weights, axis=1, keepdims=True)
    logamp = np.log1p(np.max(ampvec, axis=1))[:, None]

    flat = wave[:, 4:-4:2, :].reshape(m, -1)
    rng = np.random.RandomState(173)
    fit_idx = (rng.choice(m, min(m, 12000), replace=False)
               if m > 12000 else np.arange(m))
    npc = max(1, min(16, flat.shape[1], len(fit_idx) - 1))
    try:
        pca = PCA(n_components=npc, svd_solver="randomized", random_state=173)
        pca.fit(flat[fit_idx])
        feat = np.column_stack((pca.transform(flat), loc, logamp))
    except Exception:
        feat = np.column_stack((ampvec, loc, logamp))
    fm = np.median(feat[fit_idx], axis=0)
    fscl = 1.4826 * np.median(np.abs(feat[fit_idx] - fm), axis=0)
    fscl = np.where(fscl > 1e-5, fscl, 1.0)
    feat = np.clip((feat - fm) / fscl, -9.0, 9.0)
    train = feat[fit_idx]

    maxk = max(1, min(24, len(train) // 12))
    trial = [1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 18, 21, 24]
    trial = sorted(set(k for k in trial if k <= maxk))
    best_model = None
    best_bic = np.inf
    try:
        for k in trial:
            gm = GaussianMixture(
                n_components=k, covariance_type="diag", reg_covar=0.035,
                max_iter=120, n_init=1, random_state=173 + k,
                init_params="kmeans"
            )
            gm.fit(train)
            bic = gm.bic(train)
            if np.isfinite(bic) and bic < best_bic:
                best_bic = bic
                best_model = gm
        labels = best_model.predict(feat) if best_model is not None else anchor.copy()
    except Exception:
        labels = anchor.copy()

    groups = []
    for lab in np.unique(labels):
        idx = np.flatnonzero(labels == lab)
        idx = _dedup(idx, ev, strength, 20)
        if len(idx) >= 6:
            groups.append({"idx": idx, "tpl": np.mean(wave[idx], axis=0)})
    if not groups:
        return np.empty((0, 2), dtype=np.int64)

    parent = list(range(len(groups)))
    def root(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a
    for i in range(len(groups)):
        for j in range(i):
            corr = _cos(groups[i]["tpl"], groups[j]["tpl"])
            coin = _coincidence(ev[groups[i]["idx"]], ev[groups[j]["idx"]])
            if corr > 0.985 or (corr > 0.90 and coin > 0.15) or coin > 0.35:
                ri, rj = root(i), root(j)
                if ri != rj:
                    parent[ri] = rj

    combined = {}
    for i, g in enumerate(groups):
        r = root(i)
        combined.setdefault(r, []).append(g["idx"])
    valid = []
    min_support = 10
    for parts in combined.values():
        idx = _dedup(np.concatenate(parts), ev, strength, 20)
        if len(idx) < min_support:
            continue
        tpl = np.mean(wave[idx], axis=0)
        pt, ch = np.unravel_index(np.argmin(tpl), tpl.shape)
        peak = float(-tpl[pt, ch])
        edge = float(max(np.max(np.abs(tpl[:6])), np.max(np.abs(tpl[-6:]))))
        if abs(pt - center) > 6 or peak < 3.15 or peak < 1.20 * edge:
            continue
        if len(idx) >= 24:
            ta = np.mean(wave[idx[::2]], axis=0)
            tb = np.mean(wave[idx[1::2]], axis=0)
            if _cos(ta, tb) < 0.32:
                continue
        valid.append(idx)
    if not valid:
        return np.empty((0, 2), dtype=np.int64)

    valid.sort(key=lambda q: int(np.min(ev[q])))
    rows = []
    for uid, idx in enumerate(valid):
        tt = np.unique(ev[idx].astype(np.int64))
        rows.append(np.column_stack((tt, np.full(len(tt), uid, dtype=np.int64))))
    out = np.vstack(rows).astype(np.int64, copy=False)
    return out[np.lexsort((out[:, 1], out[:, 0]))]
