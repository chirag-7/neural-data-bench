import numpy as np
from sklearn.cluster import KMeans
from collections import defaultdict

# ----------------- helpers -----------------

def _mad(x):
    med = np.median(x)
    return np.median(np.abs(x - med))

def _robust_sigmas(rec):
    # per-channel robust sigma (assume near zero-mean after CAR)
    sig = np.empty(rec.shape[1], dtype=np.float32)
    for ch in range(rec.shape[1]):
        mad = _mad(rec[:, ch])
        sig[ch] = (mad / 0.67448975) if mad > 1e-12 else 1.0
    sig[sig < 1e-6] = 1.0
    return sig

def _detect_channel_peaks(x, thr_val, refr):
    # negative local minima below thr_val, enforce refractory per channel
    if x.size < 3:
        return np.empty(0, dtype=np.int32)
    xi = x[1:-1]
    under = xi < thr_val
    left = xi <= x[:-2]
    right = xi < x[2:]
    cand = np.where(under & left & right)[0] + 1
    if cand.size == 0:
        return cand.astype(np.int32)
    # greedy max-pooling in refractory windows
    kept = []
    j = 0
    n = cand.size
    while j < n:
        best_idx = cand[j]
        best_val = x[best_idx]
        t_end = cand[j] + refr
        j += 1
        while j < n and cand[j] <= t_end:
            v = x[cand[j]]
            if v < best_val:  # more negative is better
                best_val = v
                best_idx = cand[j]
            j += 1
        kept.append(best_idx)
    return np.asarray(kept, dtype=np.int32)

def _merge_across_channels(times, chans, amps, merge_win):
    # merge events across channels within +/- merge_win samples, keep most negative amp
    if times.size == 0:
        return np.empty(0, dtype=np.int32), np.empty(0, dtype=np.int32), np.empty(0, dtype=np.float32)
    order = np.argsort(times, kind='mergesort')
    t = times[order]
    c = chans[order]
    a = amps[order]
    kept_t = []
    kept_c = []
    kept_a = []
    i = 0
    n = t.size
    while i < n:
        t0 = t[i]
        best_j = i
        best_amp = a[i]
        j = i + 1
        while j < n and (t[j] - t0) <= merge_win:
            if a[j] < best_amp:
                best_amp = a[j]
                best_j = j
            j += 1
        kept_t.append(int(t[best_j]))
        kept_c.append(int(c[best_j]))
        kept_a.append(float(a[best_j]))
        i = j
    return (np.asarray(kept_t, dtype=np.int32),
            np.asarray(kept_c, dtype=np.int32),
            np.asarray(kept_a, dtype=np.float32))

def _nearest_channels(pos, k):
    # pos: (nch, 3) -> neighbor indices sorted by distance (self first)
    nch = pos.shape[0]
    d2 = ((pos[:, None, :] - pos[None, :, :]) ** 2).sum(axis=2)
    nn = np.argsort(d2, axis=1)[:, :min(k, nch)]
    return nn, np.sqrt(d2)

def _fit_pca(X, n_comp):
    # X: (n, d)
    if X.shape[0] == 0:
        mean = np.zeros((X.shape[1],), dtype=np.float32)
        comps = np.eye(X.shape[1], dtype=np.float32)[:n_comp]
        return mean.astype(np.float32), comps.astype(np.float32)
    mean = X.mean(axis=0)
    Xc = X - mean
    # economy SVD
    try:
        U, S, Vt = np.linalg.svd(Xc, full_matrices=False)
        comps = Vt[:n_comp]
    except np.linalg.LinAlgError:
        # fallback to random components if SVD fails
        rng = np.random.RandomState(0)
        Q, _ = np.linalg.qr(rng.randn(X.shape[1], X.shape[1]))
        comps = Q[:n_comp]
    return mean.astype(np.float32), comps.astype(np.float32)

def _robust_scale(F):
    med = np.median(F, axis=0)
    mad = np.median(np.abs(F - med), axis=0)
    scale = 1.4826 * mad + 1e-9
    return (F - med) / scale, med.astype(np.float32), scale.astype(np.float32)

def _choose_k(n):
    if n < 800:
        return 3
    if n < 2000:
        return 5
    if n < 5000:
        return 8
    if n < 10000:
        return 12
    return 16

def _extract_flat(rec, t, ch_idx, pre, post, sigmas):
    # returns flattened whitened snippet (len(ch_idx)*L) or None if edge
    L = pre + post
    if t - pre < 0 or t + post >= rec.shape[0]:
        return None
    wf = rec[t - pre:t + post, ch_idx]  # (L, M)
    wf = wf / sigmas[ch_idx]  # whiten per channel
    return wf.T.reshape(-1).astype(np.float32)

def _build_features(rec, times, pch, nn_idx, pre, post, sig, n_sub=5000, n_comp=8):
    nsp = times.size
    if nsp == 0:
        return np.empty((0, n_comp + 1), dtype=np.float32), None, None
    d = min(nn_idx.shape[1], rec.shape[1]) * (pre + post)
    # training subset indices (evenly spaced)
    m = min(n_sub, nsp)
    if m > 0:
        idx_train = np.linspace(0, nsp - 1, m, dtype=np.int32)
    else:
        idx_train = np.empty(0, dtype=np.int32)
    Xtr = np.zeros((idx_train.size, d), dtype=np.float32)
    ti = 0
    for ii, i in enumerate(idx_train):
        chs = nn_idx[pch[i]]
        flat = _extract_flat(rec, int(times[i]), chs, pre, post, sig)
        if flat is None:
            continue
        Xtr[ti] = flat
        ti += 1
    Xtr = Xtr[:ti]
    mean, comps = _fit_pca(Xtr, n_comp)
    # features for all spikes
    F = np.zeros((nsp, n_comp + 1), dtype=np.float32)
    for i in range(nsp):
        chs = nn_idx[pch[i]]
        flat = _extract_flat(rec, int(times[i]), chs, pre, post, sig)
        if flat is None:
            # mark NaN; will drop later
            F[i, :] = np.nan
            continue
        pc = (flat - mean).dot(comps.T)
        amp_feat = -rec[int(times[i]), int(pch[i])] / (sig[int(pch[i])] + 1e-9)
        F[i, :-1] = pc
        F[i, -1] = amp_feat
    return F, mean, comps

def _compute_templates(rec, times, labels, n_units, pre, post, sig, max_wf=150):
    L = pre + post
    nch = rec.shape[1]
    templ = np.zeros((n_units, nch, L), dtype=np.float32)
    counts = np.zeros(n_units, dtype=np.int32)
    for u in range(n_units):
        idx = np.where(labels == u)[0]
        if idx.size == 0:
            continue
        step = max(1, idx.size // max_wf)
        sel = idx[::step]
        for i in sel:
            t = int(times[i])
            if t - pre < 0 or t + post >= rec.shape[0]:
                continue
            wf = rec[t - pre:t + post, :] / sig[None, :]
            templ[u] += wf.T
            counts[u] += 1
    for u in range(n_units):
        if counts[u] > 0:
            templ[u] /= counts[u]
    return templ, counts

def _primary_channel_of_template(templ):
    # choose channel with most negative trough around center
    L = templ.shape[2]
    center = L // 3  # trough often near early post trigger; be permissive
    search = slice(max(0, center - 6), min(L, center + 10))
    mins = templ[:, :, search].min(axis=2)
    return np.argmin(mins, axis=1)

class _DSU:
    def __init__(self, n):
        self.p = list(range(n))
    def find(self, a):
        while self.p[a] != a:
            self.p[a] = self.p[self.p[a]]
            a = self.p[a]
        return a
    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.p[rb] = ra

# ----------------- main entry -----------------

def sort(recording_uv, fs, channel_positions_um):
    rng = np.random.RandomState(0)
    rec = np.asarray(recording_uv, dtype=np.float32)
    T, nch = rec.shape
    # CAR
    car = np.median(rec, axis=1, keepdims=True)
    rec = rec - car
    # noise
    sig = _robust_sigmas(rec)
    # detect per channel
    thr_factor = 4.5
    refr = int(round(0.000375 * fs))  # 12 @ 32kHz
    if refr < 1:
        refr = 1
    all_t = []
    all_c = []
    all_a = []
    for ch in range(nch):
        thr = -thr_factor * sig[ch]
        peaks = _detect_channel_peaks(rec[:, ch], thr, refr)
        if peaks.size == 0:
            continue
        all_t.append(peaks)
        all_c.append(np.full(peaks.shape, ch, dtype=np.int32))
        all_a.append(rec[peaks, ch].astype(np.float32))
    if len(all_t) == 0:
        return np.zeros((0, 2), dtype=np.int64)
    times = np.concatenate(all_t)
    chans = np.concatenate(all_c)
    amps = np.concatenate(all_a)
    # cross-channel dedup
    merge_win = refr
    times, pch, amps = _merge_across_channels(times, chans, amps, merge_win)
    # edge validity for waveform window
    pre = int(round(0.0005 * fs))  # 0.5 ms
    post = int(round(0.0010 * fs))  # 1.0 ms
    if pre < 1:
        pre = 1
    if post < 2:
        post = 2
    valid = (times >= pre) & (times < (T - post))
    times = times[valid]
    pch = pch[valid]
    amps = amps[valid]
    nsp = times.size
    if nsp == 0:
        return np.zeros((0, 2), dtype=np.int64)
    # geometry neighbors
    nn_idx, dist = _nearest_channels(np.asarray(channel_positions_um, dtype=np.float32), 8)
    # features
    F, mean, comps = _build_features(rec, times, pch, nn_idx, pre, post, sig, n_sub=5000, n_comp=8)
    ok = ~np.any(~np.isfinite(F), axis=1)
    times = times[ok]
    pch = pch[ok]
    amps = amps[ok]
    F = F[ok]
    if F.shape[0] == 0:
        return np.zeros((0, 2), dtype=np.int64)
    Fz, Fmed, Fscale = _robust_scale(F)
    # clustering
    K = _choose_k(Fz.shape[0])
    km = KMeans(n_clusters=K, random_state=0, n_init=10)
    labels = km.fit_predict(Fz)
    # drop tiny clusters
    counts = np.bincount(labels, minlength=K)
    min_size = max(20, int(0.005 * Fz.shape[0]))
    keep_units = np.where(counts >= min_size)[0]
    if keep_units.size == 0:
        return np.zeros((0, 2), dtype=np.int64)
    # remap labels: others -> -1
    mask = np.isin(labels, keep_units)
    labels2 = np.full(labels.shape, -1, dtype=np.int32)
    for new_id, u in enumerate(keep_units):
        labels2[labels == u] = new_id
    labels = labels2
    sel = labels >= 0
    times = times[sel]
    pch = pch[sel]
    amps = amps[sel]
    labels = labels[sel]
    if times.size == 0:
        return np.zeros((0, 2), dtype=np.int64)
    # template merging
    n_units = labels.max() + 1
    templ, tcounts = _compute_templates(rec, times, labels, n_units, pre, post, sig, max_wf=150)
    if n_units > 1:
        prim = _primary_channel_of_template(templ)
        # normalize templates for cosine similarity
        flat = templ.reshape(n_units, -1)
        norms = np.linalg.norm(flat, axis=1) + 1e-9
        flatn = (flat.T / norms).T
        thr_corr = 0.95
        dsu = _DSU(n_units)
        for i in range(n_units):
            if tcounts[i] == 0:
                continue
            for j in range(i + 1, n_units):
                if tcounts[j] == 0:
                    continue
                # primary channel proximity
                if dist[prim[i], prim[j]] > 65.0:
                    continue
                c = float(np.dot(flatn[i], flatn[j]))
                if c > thr_corr:
                    dsu.union(i, j)
        # build mapping
        root_to_new = {}
        new_id = 0
        for u in range(n_units):
            r = dsu.find(u)
            if r not in root_to_new:
                root_to_new[r] = new_id
                new_id += 1
        labels = np.array([root_to_new[dsu.find(int(u))] for u in labels], dtype=np.int32)
        n_units = labels.max() + 1
    # enforce intra-unit refractory
    refr_u = refr
    keep_evt = np.zeros(times.shape[0], dtype=bool)
    for u in range(labels.max() + 1):
        idx = np.where(labels == u)[0]
        if idx.size == 0:
            continue
        order = np.argsort(times[idx], kind='mergesort')
        idx = idx[order]
        i = 0
        n = idx.size
        while i < n:
            base_t = times[idx[i]]
            best = idx[i]
            best_amp = amps[idx[i]]
            j = i + 1
            while j < n and (times[idx[j]] - base_t) <= refr_u:
                if amps[idx[j]] < best_amp:
                    best_amp = amps[idx[j]]
                    best = idx[j]
                j += 1
            keep_evt[best] = True
            i = j
    times_f = times[keep_evt]
    units_f = labels[keep_evt]
    if times_f.size == 0:
        return np.zeros((0, 2), dtype=np.int64)
    # make unit ids contiguous and sort by time then unit
    uniq = np.unique(units_f)
    remap = {u: i for i, u in enumerate(uniq.tolist())}
    units_f = np.array([remap[int(u)] for u in units_f], dtype=np.int32)
    order = np.lexsort((units_f, times_f))
    out = np.column_stack((times_f[order].astype(np.int64), units_f[order].astype(np.int64)))
    return out
