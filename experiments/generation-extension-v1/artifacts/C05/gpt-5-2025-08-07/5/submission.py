import numpy as np
from scipy.signal import fftconvolve

# ------------------------ Helpers ------------------------

def _first_invalid_index(a):
    idx = np.where(~np.isfinite(a))[0]
    return int(idx[0]) if idx.size else a.size

def _robust_standardize(x):
    # Return standardized copy; keep NaNs in place
    out = x.astype(np.float64, copy=True)
    finite = np.isfinite(out)
    if not np.any(finite):
        return out  # all NaN
    xi = out[finite]
    med = np.median(xi)
    mad = np.median(np.abs(xi - med))
    scale = 1.4826 * mad
    if not np.isfinite(scale) or scale < 1e-8:
        s = np.std(xi)
        scale = s if (np.isfinite(s) and s >= 1e-8) else 1.0
    out[finite] = (xi - med) / scale
    return out

def _accumulate_correlations(train_calcium, train_spikes, Kmax):
    # Accumulate across neurons: r_xx for diffs in [-2Kmax..2Kmax], r_xy for lags in [-Kmax..Kmax]
    r_xx = np.zeros(4 * Kmax + 1, dtype=np.float64)
    r_xy = np.zeros(2 * Kmax + 1, dtype=np.float64)
    ncols = min(train_calcium.shape[1], train_spikes.shape[1])
    for i in range(ncols):
        cx = train_calcium[:, i]
        sy = train_spikes[:, i]
        n_valid = min(_first_invalid_index(cx), _first_invalid_index(sy))
        if n_valid <= 16:
            continue
        x = cx[:n_valid].astype(np.float64, copy=False)
        y = sy[:n_valid].astype(np.float64, copy=False)
        # Robust standardize x, zero-mean y
        xs = _robust_standardize(x)
        # ensure zero-mean for correlation-based Wiener equations
        xs = xs - np.nanmean(xs[np.isfinite(xs)])
        y = np.nan_to_num(y, nan=0.0)
        y = y - np.mean(y)
        # FFT-based correlations
        cxx = fftconvolve(xs, xs[::-1], mode='full')
        cxy = fftconvolve(xs, y[::-1], mode='full')
        center = n_valid - 1
        # r_xx slice for diffs in [-2Kmax..2Kmax]
        s0 = center - 2 * Kmax
        e0 = center + 2 * Kmax + 1
        as0 = max(s0, 0)
        ae0 = min(e0, cxx.size)
        part_xx = cxx[as0:ae0]
        o0 = as0 - s0
        r_xx[o0:o0 + part_xx.size] += part_xx
        # r_xy slice for lags in [-Kmax..Kmax]
        s1 = center - Kmax
        e1 = center + Kmax + 1
        as1 = max(s1, 0)
        ae1 = min(e1, cxy.size)
        part_xy = cxy[as1:ae1]
        o1 = as1 - s1
        r_xy[o1:o1 + part_xy.size] += part_xy
    return r_xx, r_xy

def _solve_filter_from_corr(r_xx_all, r_xy_all, K, ridge_alpha):
    # Build Toeplitz system R h = r using diffs from r_xx_all
    L = 2 * K + 1
    Kmax = (r_xy_all.size - 1) // 2
    center_diff = (r_xx_all.size - 1) // 2  # equals 2*Kmax
    # Toeplitz matrix
    R = np.empty((L, L), dtype=np.float64)
    for i in range(L):
        base = center_diff - i
        R[i, :] = r_xx_all[base:base + L]
    r = r_xy_all[Kmax - K:Kmax + K + 1]
    # Ridge regularization scaled to signal energy
    diag_scale = R[0, 0] / max(L, 1)
    lam = float(ridge_alpha) * (diag_scale if np.isfinite(diag_scale) and diag_scale > 0 else 1.0)
    R.flat[:: L + 1] += lam
    try:
        h = np.linalg.solve(R, r)
    except np.linalg.LinAlgError:
        h = np.linalg.lstsq(R, r, rcond=None)[0]
    return h

def _apply_two_sided_filter(x, h):
    # y[t] = sum_{lag=-K..K} h[lag+K] * x[t + lag]
    n = x.size
    y = np.zeros(n, dtype=np.float64)
    L = h.size
    K = (L - 1) // 2
    for idx, lag in enumerate(range(-K, K + 1)):
        w = h[idx]
        if w == 0.0:
            continue
        if lag < 0:
            y[-lag:] += w * x[:n + lag]
        elif lag > 0:
            y[:n - lag] += w * x[lag:]
        else:
            y += w * x
    return y

# ------------------------ Main API ------------------------

def fit_predict(train_calcium, train_spikes, test_calcium):
    # Parameters (100 Hz sampling): two-sided window ±0.8 s
    fs = 100.0
    K = int(round(0.8 * fs))  # 80 taps each side -> L=161
    ridge_alpha = 1e-2  # relative to R[0,0]/L

    # Train global filter on all training neurons
    r_xx_all, r_xy_all = _accumulate_correlations(train_calcium, train_spikes, K)
    h = _solve_filter_from_corr(r_xx_all, r_xy_all, K, ridge_alpha)

    # Predict for test neurons
    T, M = test_calcium.shape
    preds = np.empty_like(test_calcium, dtype=np.float64)
    for j in range(M):
        x = test_calcium[:, j]
        n_valid = _first_invalid_index(x)
        if n_valid == 0:
            preds[:, j] = np.nan
            continue
        xs = _robust_standardize(x[:n_valid])
        xs = xs - np.nanmean(xs[np.isfinite(xs)])
        yhat = _apply_two_sided_filter(xs, h)
        yhat = np.maximum(yhat, 0.0)  # enforce nonnegativity
        # place back, keep trailing NaNs
        col = np.full(T, np.nan, dtype=np.float64)
        col[:n_valid] = yhat
        preds[:, j] = col
    return preds
