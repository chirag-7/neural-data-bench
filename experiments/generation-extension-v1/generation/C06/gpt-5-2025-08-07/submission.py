import numpy as np
from sklearn.linear_model import Ridge
from sklearn.model_selection import GroupKFold

# Deterministic behavior
np.random.seed(1337)

# -------------------- Utilities --------------------
def _safe_mad(x):
    x = np.asarray(x)
    med = np.median(x)
    mad = np.median(np.abs(x - med))
    scale = mad * 1.4826
    if not np.isfinite(scale) or scale < 1e-8:
        std = np.std(x)
        scale = std if std > 1e-8 else 1.0
    return med, scale

def _zscore_robust(x, mask):
    # Robust standardization within a recording using only valid frames
    v = (mask > 0.5)
    xv = x[v]
    if xv.size == 0:
        return np.zeros_like(x)
    med, scale = _safe_mad(xv)
    z = (x - med) / scale
    # Limit extreme outliers to reduce leverage
    z = np.clip(z, -8.0, 12.0)
    return z

def _shift_right_edge(x, k):
    # Past-only shift: y[t] = x[t-k], with left edge replicated
    if k <= 0:
        return x.copy()
    y = np.empty_like(x)
    y[:k] = x[0]
    y[k:] = x[:-k]
    return y

def _build_features_row(f, m, dt):
    # f: (T,), m: (T,), dt: scalar seconds
    T = f.shape[0]
    z = _zscore_robust(f, m)
    # First difference (one-step), split into pos/neg
    d1 = z - _shift_right_edge(z, 1)
    dpos = np.maximum(d1, 0.0)
    dneg = np.maximum(-d1, 0.0)
    # Time lags in seconds -> integer steps per recording
    # Fluorescence lags: broader spacing
    times_f = np.arange(0.0, 1.6000001, 0.2)  # 0..1.6s step 0.2
    # Derivative lags: finer spacing to capture rapid rises
    times_df = np.arange(0.0, 1.6000001, 0.1) # 0..1.6s step 0.1
    # Convert to integer shifts with rounding
    if not np.isfinite(dt) or dt <= 0:
        dt = 0.1333333333  # safe fallback ~7.5 Hz
    k_f = [int(round(t / dt)) for t in times_f]
    k_df = [int(round(t / dt)) for t in times_df]
    # Build columns
    cols = []
    # Constant and dt-dependent scale feature
    cols.append(np.ones(T))
    cols.append(np.ones(T) * (1.0 / dt))
    # Z lag features
    for k in k_f:
        cols.append(_shift_right_edge(z, k))
    # Derivative pos/neg lag features
    for k in k_df:
        cols.append(_shift_right_edge(dpos, k))
    for k in k_df:
        cols.append(_shift_right_edge(dneg, k))
    X = np.vstack(cols).T  # (T, P)
    return X

def _pearsonr_safe(a, b):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    if a.size == 0 or b.size == 0:
        return 0.0
    av = a - a.mean()
    bv = b - b.mean()
    va = np.dot(av, av)
    vb = np.dot(bv, bv)
    if va <= 0 or vb <= 0:
        return 0.0
    r = np.dot(av, bv) / np.sqrt(va * vb)
    if not np.isfinite(r):
        return 0.0
    return float(r)

def _standardize_train(X, idx):
    # Compute mean/std on X[idx]
    Xtr = X[idx]
    mu = Xtr.mean(axis=0)
    sd = Xtr.std(axis=0)
    sd[sd < 1e-8] = 1.0
    return mu, sd

def _apply_standardize(X, mu, sd):
    return (X - mu) / sd

# -------------------- Main API --------------------
def fit_predict(train_x, train_y, test_x, train_groups):
    """
    Args:
      train_x: (21, 3, 900) [fluo, mask, dt]
      train_y: (21, 900) target smoothed spike counts (padding -1)
      test_x:  (24, 3, 900)
      train_groups: length-21 iterable of specimen IDs (for CV/weights only)
    Returns:
      (24, 900) nonnegative predictions, finite, zeros on padded frames.
    """
    train_x = np.asarray(train_x)
    train_y = np.asarray(train_y)
    test_x = np.asarray(test_x)
    groups_row = np.asarray(list(train_groups))

    n_train = train_x.shape[0]
    n_test = test_x.shape[0]
    T = train_x.shape[2]

    # Build training design matrices per recording
    X_list = []
    y_list = []
    g_frame = []
    w_list = []

    # Per-recording frame counts (valid) for weighting
    rec_valid_counts = []

    for i in range(n_train):
        f = train_x[i, 0, :].astype(float)
        m = train_x[i, 1, :].astype(float) > 0.5
        dt_row = train_x[i, 2, :]
        # dt constant over valid frames; derive robustly
        dt_vals = dt_row[m]
        dt = float(np.median(dt_vals[dt_vals > 0])) if dt_vals.size else 0.1333333333
        Xi = _build_features_row(f, m, dt)
        yi = train_y[i, :].astype(float)
        valid = m & np.isfinite(yi) & (yi >= 0)
        n_valid = int(valid.sum())
        if n_valid == 0:
            continue
        Xv = Xi[valid, :]
        yv = yi[valid]
        X_list.append(Xv)
        y_list.append(yv)
        g_frame.append(np.full(n_valid, groups_row[i], dtype=object))
        rec_valid_counts.append(n_valid)
        # Base frame weights so each recording contributes equally (sum to 1 per rec)
        w_list.append(np.full(n_valid, 1.0 / n_valid))

    if not X_list:
        # Degenerate safety: predict zeros
        return np.zeros((n_test, T), dtype=float)

    X = np.vstack(X_list)
    y = np.concatenate(y_list)
    g = np.concatenate(g_frame)
    w = np.concatenate(w_list)

    # Balance animals equally: multiply weights so each group has same total
    unique_groups, counts_per_group = np.unique(groups_row, return_counts=True)
    n_groups = unique_groups.size
    if n_groups > 0:
        total_recs = float(counts_per_group.sum())
        group_to_factor = {ug: (total_recs / (n_groups * cnt)) for ug, cnt in zip(unique_groups, counts_per_group)}
        factors = np.vectorize(group_to_factor.get, otypes=[float])(g)
        w = w * factors

    # Cross-validated alpha selection using GroupKFold on frame-level groups
    # If <2 groups, fall back to fixed alpha
    alpha_grid = np.array([0.01, 0.03, 0.1, 0.3, 1.0, 3.0, 10.0, 30.0])
    if np.unique(g).size >= 2:
        gkf = GroupKFold(n_splits=min(5, np.unique(g).size))
        best_alpha = None
        best_score = -1e9
        for a in alpha_grid:
            rs = []
            # Split by animal, frames inherit their row's group ID
            for tr_idx, va_idx in gkf.split(X, y, groups=g):
                mu, sd = _standardize_train(X, tr_idx)
                Xtr = _apply_standardize(X[tr_idx], mu, sd)
                Xva = _apply_standardize(X[va_idx], mu, sd)
                mdl = Ridge(alpha=float(a), fit_intercept=True)
                mdl.fit(Xtr, y[tr_idx], sample_weight=w[tr_idx])
                yp = mdl.predict(Xva)
                rs.append(_pearsonr_safe(y[va_idx], yp))
            score = float(np.mean(rs)) if rs else -1e9
            if score > best_score:
                best_score = score
                best_alpha = float(a)
        alpha = best_alpha if best_alpha is not None else 1.0
    else:
        alpha = 1.0

    # Fit final model on all training frames
    mu_all = X.mean(axis=0)
    sd_all = X.std(axis=0)
    sd_all[sd_all < 1e-8] = 1.0
    Xs = (X - mu_all) / sd_all
    final = Ridge(alpha=float(alpha), fit_intercept=True)
    final.fit(Xs, y, sample_weight=w)

    # Predict on test set
    out = np.zeros((n_test, T), dtype=float)
    for j in range(n_test):
        f = test_x[j, 0, :].astype(float)
        m = test_x[j, 1, :].astype(float) > 0.5
        dt_row = test_x[j, 2, :]
        dt_vals = dt_row[m]
        dt = float(np.median(dt_vals[dt_vals > 0])) if dt_vals.size else 0.1333333333
        Xj = _build_features_row(f, m, dt)
        if m.any():
            Xjs = (Xj - mu_all) / sd_all
            yp = final.predict(Xjs)
            yp = np.maximum(yp, 0.0)  # nonnegative
            out[j, m] = yp[m]
        # padded frames remain zero

    # Ensure finite, nonnegative
    out = np.nan_to_num(out, nan=0.0, posinf=0.0, neginf=0.0)
    out[out < 0] = 0.0
    return out
