import numpy as np

# Constants for window layout
_T = 31
_HF_SLICE = slice(0, 3)       # HeadF x,y,z within feature axis
_OTHERS_SLICE = slice(3, 18)   # other 5 landmarks (15 dims)
_GAP_START = 12
_GAP_END = 18                  # inclusive
_LEFT_ANCHOR = 11
_RIGHT_ANCHOR = 19
_GAP_IDXS = list(range(_GAP_START, _GAP_END + 1))  # [12..18]


def _baseline_at_t(v0, v1, t):
    # Linear interpolation between frames 11 and 19
    r = (t - _LEFT_ANCHOR) / float(_RIGHT_ANCHOR - _LEFT_ANCHOR)
    return v0 + r * (v1 - v0)


def _feature_vector(win, t, v0, v1):
    # Build features for a single (window, t) sample.
    # 1) Other landmarks at t-2..t+2 (clamped) -> 75 dims
    feats = []
    for off in (-2, -1, 0, 1, 2):
        idx = t + off
        if idx < 0:
            idx = 0
        elif idx >= _T:
            idx = _T - 1
        seg = win[idx, _OTHERS_SLICE]
        # Guard against unexpected NaNs (should be fully observed per spec)
        if np.any(~np.isfinite(seg)):
            seg = np.where(np.isfinite(seg), seg, 0.0)
        feats.append(seg)

    # 2) Baseline HeadF at t (3 dims)
    base = _baseline_at_t(v0, v1, t)
    if np.any(~np.isfinite(base)):
        base = np.where(np.isfinite(base), base, 0.0)
    feats.append(base)

    # 3) Endpoints (6 dims)
    v0s = np.where(np.isfinite(v0), v0, 0.0)
    v1s = np.where(np.isfinite(v1), v1, 0.0)
    feats.append(v0s)
    feats.append(v1s)

    # 4) Timing (2 dims): normalized position in gap and absolute frame index
    s_in_gap = (t - _GAP_START) / float(_GAP_END - _GAP_START)  # 0..1
    t_norm = t / float(_T - 1)
    feats.append(np.array([s_in_gap, t_norm], dtype=float))

    return np.concatenate(feats, axis=0)


def _prepare_training(train_x, train_y):
    # Assemble design matrix X and residual targets Y (HeadF only) for frames in the gap.
    n = train_x.shape[0]
    n_gap = len(_GAP_IDXS)
    # Feature dimension: 5*15 (context) + 3 (baseline) + 6 (endpoints) + 2 (timing) = 86
    n_feat = 5 * 15 + 3 + 6 + 2
    X = np.empty((n * n_gap, n_feat), dtype=np.float64)
    Y = np.empty((n * n_gap, 3), dtype=np.float64)

    r = 0
    for i in range(n):
        win_x = train_x[i]
        # Anchors for baseline (expected finite by spec)
        v0 = win_x[_LEFT_ANCHOR, _HF_SLICE].astype(np.float64)
        v1 = win_x[_RIGHT_ANCHOR, _HF_SLICE].astype(np.float64)
        # Safety fallback in case of unexpected NaNs
        if np.any(~np.isfinite(v0)):
            v0 = np.where(np.isfinite(v0), v0, 0.0)
        if np.any(~np.isfinite(v1)):
            v1 = np.where(np.isfinite(v1), v1, 0.0)

        for t in _GAP_IDXS:
            X[r] = _feature_vector(win_x, t, v0, v1)
            base = _baseline_at_t(v0, v1, t)
            truth = train_y[i, t, _HF_SLICE].astype(np.float64)
            Y[r] = truth - base  # residual target (x,y,z)
            r += 1

    # Standardize features
    mean = X.mean(axis=0)
    std = X.std(axis=0)
    std[std < 1e-8] = 1.0
    Xn = (X - mean) / std
    return Xn, Y, mean, std


def _fit_ridge_closed_form(Xn, Y, alpha=1.0):
    # Add intercept column (not penalized)
    n_samples, n_feat = Xn.shape
    ones = np.ones((n_samples, 1), dtype=Xn.dtype)
    Xa = np.concatenate([Xn, ones], axis=1)
    # Normal equations with ridge penalty on weights only (not on intercept)
    A = Xa.T @ Xa  # (n_feat+1, n_feat+1)
    # Apply ridge (alpha) to all but the last diagonal element (intercept)
    diag = np.arange(n_feat + 1)
    A.flat[(diag * (n_feat + 1) + diag)] += np.concatenate([np.full(n_feat, alpha), np.array([0.0])])
    B = Xa.T @ Y  # (n_feat+1, 3)
    W = np.linalg.solve(A, B)  # (n_feat+1, 3)
    return W  # includes intercept as last row


def _predict_residuals(W, x_raw, mean, std):
    # x_raw: (n_feat,)
    z = (x_raw - mean) / std
    # Append intercept term
    y = z @ W[:-1, :] + W[-1, :]
    return y  # (3,)


def fit_predict(train_x, train_y, test_x):
    # Ensure float64 for stable linear algebra
    train_x = np.asarray(train_x, dtype=np.float64)
    train_y = np.asarray(train_y, dtype=np.float64)
    test_x = np.asarray(test_x, dtype=np.float64)

    # Prepare training design matrix and train ridge
    Xn, Y, f_mean, f_std = _prepare_training(train_x, train_y)
    W = _fit_ridge_closed_form(Xn, Y, alpha=1.0)

    # Predict on test windows
    pred = np.array(test_x, copy=True)
    n_test = test_x.shape[0]
    for i in range(n_test):
        win = pred[i]
        v0 = win[_LEFT_ANCHOR, _HF_SLICE]
        v1 = win[_RIGHT_ANCHOR, _HF_SLICE]
        # Fallback in case of unexpected NaNs
        if np.any(~np.isfinite(v0)):
            v0 = np.where(np.isfinite(v0), v0, 0.0)
        if np.any(~np.isfinite(v1)):
            v1 = np.where(np.isfinite(v1), v1, 0.0)

        for t in _GAP_IDXS:
            feats = _feature_vector(win, t, v0, v1)
            resid = _predict_residuals(W, feats, f_mean, f_std)
            base = _baseline_at_t(v0, v1, t)
            est = base + resid
            # Write back only the masked HeadF frames
            win[t, _HF_SLICE] = est

    # Guarantee finite outputs at missing positions
    # (outside of the intended gap we leave the input values untouched)
    return pred
