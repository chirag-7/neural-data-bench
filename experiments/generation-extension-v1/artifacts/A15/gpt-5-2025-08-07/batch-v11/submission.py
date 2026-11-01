import numpy as np
from numpy.lib.stride_tricks import as_strided
from sklearn.ensemble import HistGradientBoostingClassifier
from collections import defaultdict
import math
import gc

FS = 32000
NFFT = 256
HOP = 32
WIN = np.hanning(NFFT).astype(np.float32)
NBINS = NFFT // 2 + 1
FMIN = 250.0
FMAX = 12000.0
NBANDS = 24
EPS = 1e-10
RNG_SEED = 20261031

np.random.seed(RNG_SEED)

def first_nan_index(x):
    idx = np.flatnonzero(~np.isfinite(x))
    return int(idx[0]) if idx.size else x.shape[0]

def make_filterbank(fs=FS, nfft=NFFT, nbands=NBANDS, fmin=FMIN, fmax=FMAX):
    freqs = np.linspace(0.0, fs/2.0, nfft//2 + 1, dtype=np.float64)
    # Triangular filters with log-spaced edges
    edges = np.logspace(np.log10(fmin), np.log10(fmax), nbands + 2)
    W = np.zeros((freqs.shape[0], nbands), dtype=np.float64)
    for b in range(nbands):
        L, C, R = edges[b], edges[b+1], edges[b+2]
        # Rising slope
        left = (freqs >= L) & (freqs <= C)
        W[left, b] = (freqs[left] - L) / max(C - L, 1e-12)
        # Falling slope
        right = (freqs >= C) & (freqs <= R)
        W[right, b] = (R - freqs[right]) / max(R - C, 1e-12)
    # Broadband (250–12000 Hz) rectangular
    bb = ((freqs >= fmin) & (freqs <= fmax)).astype(np.float64)
    return W.astype(np.float32), bb.astype(np.float32)

FB_W, BB_W = make_filterbank()

def frame_view(x_valid, nfft=NFFT, hop=HOP):
    # Append zeros to allow last (N/hop) frames; need pad of (nfft-hop)
    pad = nfft - hop
    x_pad = np.concatenate([x_valid, np.zeros(pad, dtype=x_valid.dtype)], axis=0)
    n_frames = (x_valid.shape[0] // hop)
    item = x_pad.strides[0]
    return as_strided(x_pad, shape=(n_frames, nfft), strides=(hop*item, item))

def rfft_power(frames):
    Z = np.fft.rfft(frames * WIN[None, :], n=NFFT, axis=1)
    P = (Z.real**2 + Z.imag**2).astype(np.float32)
    return P  # shape (T, NBINS)

def moving_average(x, w):
    if w <= 1:
        return x.copy()
    pad_l = w//2
    pad_r = w - 1 - pad_l
    xp = np.pad(x, (pad_l, pad_r), mode='edge')
    k = np.ones(w, dtype=np.float32) / float(w)
    return np.convolve(xp, k, mode='valid').astype(np.float32)

def full_features_for_record(x_row):
    nvalid = first_nan_index(x_row)
    x_valid = x_row[:nvalid].astype(np.float32, copy=False)
    T = nvalid // HOP
    if T <= 0:
        return np.zeros((0, NBANDS + 3), dtype=np.float32), T
    fv = frame_view(x_valid)
    P = rfft_power(fv)  # (T, NBINS)
    # Band powers
    B = P @ FB_W  # (T, NBANDS)
    B = np.maximum(B, EPS)
    L = np.log10(B, dtype=np.float64)
    p20 = np.percentile(L, 20.0, axis=0)
    Lc = (L - p20[None, :]).astype(np.float32)
    # Broadband
    BB = np.maximum(P @ BB_W, EPS)
    Lbb = np.log10(BB, dtype=np.float64)
    p20bb = np.percentile(Lbb, 20.0)
    RBB = (Lbb - p20bb).astype(np.float32)
    R5 = moving_average(RBB, 5)
    R15 = moving_average(RBB, 15)
    feats = np.concatenate([Lc, RBB[:, None], R5[:, None], R15[:, None]], axis=1)
    return feats, T

def approx_norm_params_from_thin(x_row, step=64):
    nvalid = first_nan_index(x_row)
    x_valid = x_row[:nvalid].astype(np.float32, copy=False)
    T = nvalid // HOP
    if T <= 0:
        return np.zeros((NBANDS,), np.float32), 0.0
    fv = frame_view(x_valid)
    thin = fv[::step]
    if thin.shape[0] == 0:
        thin = fv[:1]
    P = rfft_power(thin)
    B = np.maximum(P @ FB_W, EPS)
    L = np.log10(B, dtype=np.float64)
    p20 = np.percentile(L, 20.0, axis=0).astype(np.float32)
    BB = np.maximum(P @ BB_W, EPS)
    Lbb = np.log10(BB, dtype=np.float64)
    p20bb = float(np.percentile(Lbb, 20.0))
    return p20, np.float32(p20bb)

def features_at_indices(x_row, idxs, p20_bands, p20_bb):
    nvalid = first_nan_index(x_row)
    x_valid = x_row[:nvalid].astype(np.float32, copy=False)
    if len(idxs) == 0:
        return np.zeros((0, NBANDS + 3), dtype=np.float32)
    fv = frame_view(x_valid)
    sel = fv[np.asarray(idxs, dtype=np.int64)]
    P = rfft_power(sel)
    B = np.maximum(P @ FB_W, EPS)
    L = np.log10(B)
    Lc = (L - p20_bands[None, :]).astype(np.float32)
    BB = np.maximum(P @ BB_W, EPS)
    RBB = (np.log10(BB) - p20_bb).astype(np.float32)
    R5 = moving_average(RBB, 5)
    R15 = moving_average(RBB, 15)
    return np.concatenate([Lc, RBB[:, None], R5[:, None], R15[:, None]], axis=1)

def runs_from_binary(b):
    # b: 1D bool array
    if b.size == 0:
        return []
    diff = np.diff(b.astype(np.int8))
    starts = np.flatnonzero(diff == 1) + 1
    ends = np.flatnonzero(diff == -1) + 1
    if b[0]:
        starts = np.r_[0, starts]
    if b[-1]:
        ends = np.r_[ends, b.size]
    return [(int(s), int(e)) for s, e in zip(starts, ends)]

def intervals_from_ybins(y):
    yv = y.astype(np.int8)
    valid = yv >= 0
    yb = (yv[valid] == 1)
    runs = runs_from_binary(yb)
    return [(s, e) for s, e in runs]

def postprocess_probs(p, thr, gap_ms, min_ms):
    b = (p >= thr)
    if gap_ms > 0:
        runs = runs_from_binary(b)
        if runs:
            merged = []
            s0, e0 = runs[0]
            for s, e in runs[1:]:
                if s - e0 <= gap_ms:
                    e0 = e
                else:
                    merged.append((s0, e0))
                    s0, e0 = s, e
            merged.append((s0, e0))
        else:
            merged = []
        b = np.zeros_like(b, dtype=bool)
        for s, e in merged:
            b[s:e] = True
    if min_ms > 0:
        runs = runs_from_binary(b)
        b = np.zeros_like(b, dtype=bool)
        for s, e in runs:
            if (e - s) >= min_ms:
                b[s:e] = True
    return b

def match_events(pred, ref):
    # pred/ref: lists of (start_bin, end_bin)
    if not pred and not ref:
        return 1.0, 0, 0, 0
    # Build adjacency: onset/offset tolerances
    tol_on = 0.020
    adj = [[] for _ in range(len(pred))]
    for i, (ps, pe) in enumerate(pred):
        ps_t, pe_t = ps * 0.001, pe * 0.001
        for j, (rs, re) in enumerate(ref):
            rs_t, re_t = rs * 0.001, re * 0.001
            dur_ref = max(re_t - rs_t, 1e-12)
            tol_off = max(0.020, 0.2 * dur_ref)
            if abs(ps_t - rs_t) <= tol_on and abs(pe_t - re_t) <= tol_off:
                adj[i].append(j)
    # Maximum cardinality matching (Kuhn's algorithm)
    match_r = [-1] * len(ref)
    def dfs(u, vis):
        for v in adj[u]:
            if vis[v]:
                continue
            vis[v] = True
            if match_r[v] == -1 or dfs(match_r[v], vis):
                match_r[v] = u
                return True
        return False
    m = 0
    for u in range(len(pred)):
        vis = [False] * len(ref)
        if dfs(u, vis):
            m += 1
    tp = m
    fp = len(pred) - tp
    fn = len(ref) - tp
    denom = (len(pred) + len(ref))
    f1 = (2.0 * tp / denom) if denom > 0 else 1.0
    return f1, tp, len(pred), len(ref)

def select_hyperparams(clf, val_feats, val_labels):
    # val_feats: list of arrays (T, D); val_labels: list of int8 arrays length T_full
    thresholds = [0.3, 0.5, 0.7]
    gaps = [0, 4, 8]  # ms
    mins = [5, 10, 20]  # ms
    best = (-1.0, thresholds[0], gaps[0], mins[0])
    # Precompute probabilities
    val_probs = []
    val_refs = []
    for Xv, yv in zip(val_feats, val_labels):
        if Xv.shape[0] == 0:
            val_probs.append(np.zeros((0,), dtype=np.float32))
            val_refs.append([])
            continue
        p = clf.predict_proba(Xv)[:, 1].astype(np.float32)
        val_probs.append(p)
        val_refs.append(intervals_from_ybins(yv))
    for thr in thresholds:
        for g in gaps:
            for mn in mins:
                f1s = []
                for p, yv in zip(val_probs, val_refs):
                    if len(p) == 0:
                        f1s.append(1.0 if len(yv) == 0 else 0.0)
                        continue
                    b = postprocess_probs(p, thr, g, mn)
                    pred = runs_from_binary(b)
                    f1, _, _, _ = match_events(pred, yv)
                    f1s.append(f1)
                mf1 = float(np.mean(f1s)) if f1s else 1.0
                if mf1 > best[0]:
                    best = (mf1, thr, g, mn)
    return best[1], best[2], best[3]

def fit_predict(train_x, train_y, test_x, train_groups=None):
    # Fixed validation indices: 0,5,10,...,55
    n_train = train_x.shape[0]
    val_idx = [i for i in range(0, n_train, 5)]
    tr_idx = [i for i in range(n_train) if i not in val_idx]

    # Determine per-recording frame counts and valid masks
    y_valid_counts = []
    for i in range(n_train):
        nvalid = first_nan_index(train_x[i])
        T = nvalid // HOP
        yv = train_y[i][:T]
        mask = (yv >= 0)
        y_valid_counts.append(int(mask.sum()))

    # Provisional training set: uniformly sample up to 60k frames from non-validation recordings
    total_valid_tr = sum(y_valid_counts[i] for i in tr_idx)
    target = min(60000, total_valid_tr)
    # Allocate per record sample counts proportional to valid frames
    per_rec_target = {}
    acc = 0
    for k, i in enumerate(tr_idx):
        if total_valid_tr == 0:
            cnt = 0
        else:
            # Last takes remainder to ensure exact sum
            if k == len(tr_idx) - 1:
                cnt = target - acc
            else:
                cnt = int(round(target * (y_valid_counts[i] / total_valid_tr)))
                cnt = min(cnt, y_valid_counts[i])
                acc += cnt
        per_rec_target[i] = cnt
    Xp_list, yp_list = [], []
    # Cache for later refit
    cached_nonval = {}
    for i in tr_idx:
        cnt = per_rec_target[i]
        if cnt <= 0:
            cached_nonval[i] = (np.empty((0, NBANDS+3), np.float32), np.empty((0,), np.int8), np.empty((0,), np.int64))
            continue
        nvalid = first_nan_index(train_x[i])
        T = nvalid // HOP
        yv = train_y[i][:T]
        valid_bins = np.flatnonzero(yv >= 0)
        if valid_bins.size == 0:
            cached_nonval[i] = (np.empty((0, NBANDS+3), np.float32), np.empty((0,), np.int8), np.empty((0,), np.int64))
            continue
        if cnt > valid_bins.size:
            cnt = valid_bins.size
        sel = np.random.choice(valid_bins, size=cnt, replace=False)
        p20b, p20bb = approx_norm_params_from_thin(train_x[i])
        feats = features_at_indices(train_x[i], sel, p20b, p20bb)
        Xp_list.append(feats)
        yp_list.append(yv[sel].astype(np.int8))
        cached_nonval[i] = (feats, yv[sel].astype(np.int8), sel.astype(np.int64))
        gc.collect()

    if Xp_list:
        Xp = np.concatenate(Xp_list, axis=0)
        yp = np.concatenate(yp_list, axis=0)
    else:
        Xp = np.empty((0, NBANDS+3), dtype=np.float32)
        yp = np.empty((0,), dtype=np.int8)

    # Fit provisional classifier
    clf = HistGradientBoostingClassifier(
        max_iter=80,
        max_leaf_nodes=15,
        learning_rate=0.1,
        l2_regularization=10.0,
        max_bins=128,
        random_state=RNG_SEED
    )
    if Xp.shape[0] == 0:
        # Degenerate: no valid training data; predict zeros
        thr_opt, gap_opt, min_opt = 0.5, 0, 10
        final_clf = clf
    else:
        clf.fit(Xp, yp)
        # Build validation features (exact per-recording normalization)
        val_feats, val_labels = [], []
        for i in val_idx:
            feats, T = full_features_for_record(train_x[i])
            yv = train_y[i][:T].astype(np.int8) if T > 0 else np.empty((0,), dtype=np.int8)
            val_feats.append(feats)
            val_labels.append(yv)
            gc.collect()
        thr_opt, gap_opt, min_opt = select_hyperparams(clf, val_feats, val_labels)
        # Refit on all training recordings with up to 60k frames
        total_valid_all = sum(y_valid_counts)
        target2 = min(60000, total_valid_all)
        per_rec2 = {}
        acc2 = 0
        for k, i in enumerate(range(n_train)):
            if total_valid_all == 0:
                cnt2 = 0
            else:
                if k == n_train - 1:
                    cnt2 = target2 - acc2
                else:
                    cnt2 = int(round(target2 * (y_valid_counts[i] / total_valid_all)))
                    cnt2 = min(cnt2, y_valid_counts[i])
                    acc2 += cnt2
            per_rec2[i] = cnt2
        X2_list, y2_list = [], []
        for i in range(n_train):
            cnt2 = per_rec2[i]
            if cnt2 <= 0:
                continue
            nvalid = first_nan_index(train_x[i])
            T = nvalid // HOP
            yv = train_y[i][:T]
            valid_bins = np.flatnonzero(yv >= 0)
            if valid_bins.size == 0:
                continue
            if i in cached_nonval and cached_nonval[i][0].shape[0] > 0:
                # Reuse some/extend if needed
                feats0, y0, sel0 = cached_nonval[i]
                if cnt2 <= feats0.shape[0]:
                    take = np.random.choice(np.arange(feats0.shape[0]), size=cnt2, replace=False)
                    X2_list.append(feats0[take])
                    y2_list.append(y0[take])
                else:
                    extra_needed = cnt2 - feats0.shape[0]
                    remaining = np.setdiff1d(valid_bins, sel0, assume_unique=False)
                    if remaining.size > 0:
                        extra_take = min(extra_needed, remaining.size)
                        sel_extra = np.random.choice(remaining, size=extra_take, replace=False)
                        p20b, p20bb = approx_norm_params_from_thin(train_x[i])
                        feats_extra = features_at_indices(train_x[i], sel_extra, p20b, p20bb)
                        X2_list.append(np.vstack([feats0, feats_extra]))
                        y2_list.append(np.concatenate([y0, yv[sel_extra].astype(np.int8)]))
                    else:
                        X2_list.append(feats0)
                        y2_list.append(y0)
            else:
                # Build from scratch
                take = min(cnt2, valid_bins.size)
                sel = np.random.choice(valid_bins, size=take, replace=False)
                p20b, p20bb = approx_norm_params_from_thin(train_x[i])
                feats = features_at_indices(train_x[i], sel, p20b, p20bb)
                X2_list.append(feats)
                y2_list.append(yv[sel].astype(np.int8))
            gc.collect()
        if X2_list:
            X2 = np.concatenate(X2_list, axis=0)
            y2 = np.concatenate(y2_list, axis=0)
        else:
            X2 = Xp
            y2 = yp
        final_clf = HistGradientBoostingClassifier(
            max_iter=80,
            max_leaf_nodes=15,
            learning_rate=0.1,
            l2_regularization=10.0,
            max_bins=128,
            random_state=RNG_SEED
        )
        final_clf.fit(X2, y2)
        del X2, y2, Xp, yp, Xp_list, yp_list
        gc.collect()

    # Predict on test set
    n_test = test_x.shape[0]
    out_len = test_x.shape[1] // HOP
    Ypred = np.zeros((n_test, out_len), dtype=np.int8)
    for i in range(n_test):
        feats, T = full_features_for_record(test_x[i])
        if T <= 0:
            continue
        p = final_clf.predict_proba(feats)[:, 1].astype(np.float32)
        b = postprocess_probs(p, thr_opt, gap_opt, min_opt)
        # Respect padding: ensure length equals out_len; rest already zeros
        L = min(out_len, b.shape[0])
        Ypred[i, :L] = b[:L].astype(np.int8)
        gc.collect()
    return Ypred
