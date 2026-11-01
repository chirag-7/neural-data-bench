import numpy as np
import math

# B03: rigid-motion from depth-time peak-count rasters
# Implements pairwise normalized cross-correlation over depth bins and a
# global least-squares solve with a first-difference temporal prior.

BIN_UM = 5.0
MAX_SHIFT_UM = 60.0
MAX_SHIFT_BINS = int(round(MAX_SHIFT_UM / BIN_UM))  # 12
CORR_THR = 0.10
MIN_OVERLAP_BINS = 40  # stabilize NCC
ANCHOR_EPS = 1e-3


def _zscore_profiles(R):
    # R: (T, L) float counts -> zero-mean, unit-std per time across depth
    R = np.asarray(R, dtype=np.float64)
    m = R.mean(axis=1, keepdims=True)
    s = R.std(axis=1, ddof=0, keepdims=True)
    Z = (R - m) / np.maximum(s, 1e-12)
    return Z


def _cumsum_squares(Z):
    # prefix sums for fast segment-norm queries; cs[t,k]=sum_{0..k-1} Z[t]^2
    return np.concatenate([np.zeros((Z.shape[0], 1), dtype=Z.dtype), np.cumsum(Z * Z, axis=1)], axis=1)


def _best_shift(a, b, sa, sb, max_shift=MAX_SHIFT_BINS, min_overlap=MIN_OVERLAP_BINS):
    # a,b: 1D arrays length L; sa,sb: prefix sums of squares (length L+1)
    L = a.size
    best_c = -1e9
    best_s = 0
    for s in range(-max_shift, max_shift + 1):
        if s >= 0:
            n = L - s
            if n < min_overlap:
                continue
            num = float(np.dot(a[:n], b[s:]))
            den = math.sqrt((sa[n] - sa[0]) * (sb[L] - sb[s])) + 1e-12
        else:
            n = L + s  # s negative
            if n < min_overlap:
                continue
            k = -s
            num = float(np.dot(a[k:], b[:n]))
            den = math.sqrt((sa[L] - sa[k]) * (sb[n] - sb[0])) + 1e-12
        c = num / den
        if c > best_c:
            best_c = c
            best_s = s
    return best_s, best_c


def _build_edges(R):
    # R: (T,L) -> list of (i, j, d_um, corr, dt)
    Z = _zscore_profiles(R)
    cs = _cumsum_squares(Z)
    T, _ = Z.shape
    edges = []
    for i in range(T - 1):
        ai = Z[i]
        sai = cs[i]
        for j in range(i + 1, T):
            aj = Z[j]
            saj = cs[j]
            s, c = _best_shift(ai, aj, sai, saj)
            if c >= CORR_THR:
                # mild penalty if we hit the hard shift boundary
                if abs(s) >= MAX_SHIFT_BINS:
                    c = max(CORR_THR, c - 0.02)
                d_um = s * BIN_UM
                edges.append((i, j, d_um, c, j - i))
    return edges


def _chain_laplacian(T):
    L = np.zeros((T, T), dtype=np.float64)
    for t in range(T):
        if t > 0:
            L[t, t] += 1.0
            L[t, t - 1] -= 1.0
        if t < T - 1:
            L[t, t] += 1.0
            L[t, t + 1] -= 1.0
    return L


def _solve_from_edges(T, edges, lam, tau):
    if len(edges) == 0:
        return np.zeros(T, dtype=np.float64)
    M = np.zeros((T, T), dtype=np.float64)
    b = np.zeros(T, dtype=np.float64)
    for (i, j, d_um, c, dt) in edges:
        w = max(0.0, c - CORR_THR)
        if tau is not None and tau > 0:
            w *= math.exp(-float(dt) / float(tau))
        w2 = w * w
        if w2 <= 0.0:
            continue
        M[i, i] += w2
        M[j, j] += w2
        M[i, j] -= w2
        M[j, i] -= w2
        b[i] -= w2 * d_um
        b[j] += w2 * d_um
    # Temporal smoothness prior
    Lreg = _chain_laplacian(T)
    trM = float(np.trace(M)) + 1e-12
    trL = float(np.trace(Lreg)) + 1e-12
    lam_scaled = float(lam) * (trM / trL)
    P = M + lam_scaled * Lreg
    # Anchor x[0]=0 to remove gauge (scorer subtracts mean anyway)
    P[0, 0] += ANCHOR_EPS * (trM / T + 1.0)
    try:
        x = np.linalg.solve(P, b)
    except np.linalg.LinAlgError:
        x, *_ = np.linalg.lstsq(P, b, rcond=None)
    # Numerical safety
    x = np.clip(x.astype(np.float64, copy=False), -120.0, 120.0)
    return x


def fit_predict(train_x, train_y, test_x, train_groups=None):
    """Estimate per-second rigid displacement (μm) for each test recording.

    Args:
        train_x: (4, 90, 132) peak-count rasters
        train_y: (4, 90) displacement targets (μm)
        test_x:  (4, 90, 132) rasters for inference
        train_groups: unused (None)
    Returns:
        (len(test_x), 90) array of predicted displacements in μm
    """
    np.random.seed(0)
    train_x = np.asarray(train_x, dtype=np.float64)
    train_y = np.asarray(train_y, dtype=np.float64)
    test_x = np.asarray(test_x, dtype=np.float64)
    n_train, T, L = train_x.shape
    _ = L  # silence linters

    # Center training targets per recording (custom target definition)
    y_centered = train_y - train_y.mean(axis=1, keepdims=True)

    # Build training edges once (no label leakage)
    train_edges = [ _build_edges(train_x[r]) for r in range(n_train) ]

    # Hyperparameter search (coarse, deterministic)
    tau_grid = [8.0, 12.0, 18.0, 30.0, 45.0, 60.0]
    lam_grid = [0.001, 0.003, 0.01, 0.03, 0.1, 0.3, 1.0, 3.0]
    best_tau, best_lam, best_err = 30.0, 0.1, float('inf')
    for tau in tau_grid:
        for lam in lam_grid:
            errs = []
            for r in range(n_train):
                x_hat = _solve_from_edges(T, train_edges[r], lam=lam, tau=tau)
                x_hat = x_hat - x_hat.mean()
                diff = x_hat - y_centered[r]
                rmse = math.sqrt(float((diff * diff).mean()))
                errs.append(rmse)
            avg = float(np.mean(errs)) if errs else 1e9
            if avg < best_err:
                best_err, best_tau, best_lam = avg, tau, lam

    # Predict test set
    n_test = test_x.shape[0]
    preds = np.zeros((n_test, T), dtype=np.float64)
    for r in range(n_test):
        edges = _build_edges(test_x[r])
        x_hat = _solve_from_edges(T, edges, lam=best_lam, tau=best_tau)
        preds[r] = x_hat  # scorer mean-centers later

    # Ensure finite output
    preds = np.nan_to_num(preds, copy=False, nan=0.0, posinf=0.0, neginf=0.0)
    return preds
