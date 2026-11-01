import numpy as np
from scipy.optimize import nnls
from scipy.signal import fftconvolve

def _extract_finite_block(arr):
    # arr: (T,)
    finite = np.isfinite(arr)
    if not np.any(finite):
        return np.zeros(0, dtype=arr.dtype), np.zeros(0, dtype=bool)
    i0 = np.searchsorted(finite, True)
    i1 = len(arr) - np.searchsorted(finite[::-1], True)
    return arr[i0:i1], (i0, i1)

def _fit_single_kernel(fluor, spikes, n_lags):
    # fluor, spikes: (N,) arrays, already finite
    N = len(fluor)
    if N < n_lags+1:
        return np.zeros(n_lags)
    # Standardize
    f = (fluor - np.nanmean(fluor)) / (np.nanstd(fluor) + 1e-10)
    y = (spikes - np.nanmean(spikes)) / (np.nanstd(spikes) + 1e-10)
    # Build Toeplitz design for non-causal kernel (past lags predicting now)
    X = np.zeros((N - n_lags + 1, n_lags))
    for k in range(n_lags):
        X[:, k] = f[k:N - n_lags + k + 1]
    y_fit = y[n_lags - 1:]
    # Fit nnls
    k_fit, _ = nnls(X, y_fit)
    return k_fit

def _apply_kernel(ca, k_fit):
    # ca: (T,), k_fit: (n_lags,)
    # Acausal convolution, outputs same shape as ca, unshifted (centered)
    ca0 = np.copy(ca)
    nan_mask = ~np.isfinite(ca0)
    mean = np.nanmean(ca0)
    std = np.nanstd(ca0) + 1e-10
    ca0[nan_mask] = mean
    ca0 = (ca0 - mean) / std
    pred = fftconvolve(ca0, k_fit[::-1], mode='full')[:len(ca0)]
    pred[nan_mask] = np.nan  # Retain NaNs
    return pred

def fit_predict(train_calcium, train_spikes, test_calcium):
    n_lags = 6  # 60 ms, enough for most indicator kernels at 100 Hz
    train_n = train_calcium.shape[1]
    test_n = test_calcium.shape[1]
    # Store per-train weights and their stats
    kernels = []
    train_stats = []  # (mean, std, n_finite)
    for i in range(train_n):
        f_col = train_calcium[:, i]
        s_col = train_spikes[:, i]
        # Extract valid region
        mask = np.isfinite(f_col) & np.isfinite(s_col)
        if np.sum(mask) < n_lags + 2:
            kernels.append(np.zeros(n_lags))
            train_stats.append((0., 1., 0))
            continue
        f_trim = f_col[mask]
        s_trim = s_col[mask]
        k = _fit_single_kernel(f_trim, s_trim, n_lags)
        kernels.append(k)
        train_stats.append((np.nanmean(f_trim), np.nanstd(f_trim) + 1e-10, np.sum(mask)))
    kernels = np.stack(kernels, axis=0)  # shape (train_n, n_lags)
    # For test, predict each test neuron with best-matched train kernel
    preds = np.full_like(test_calcium, np.nan)
    for j in range(test_n):
        ca_col = test_calcium[:, j]
        # Get stat of test: std for matching
        test_std = np.nanstd(ca_col)
        test_finite = np.sum(np.isfinite(ca_col))
        # Choose kernel trained on neuron with most similar std
        train_diffs = [abs(test_std - stat[1]) + abs(test_finite - stat[2]) * 1e-4 for stat in train_stats]
        best_idx = int(np.argmin(train_diffs))
        k_sel = kernels[best_idx]
        pred_j = _apply_kernel(ca_col, k_sel)
        # Remove mean, set negatives to zero
        pred_j = pred_j - np.nanmin(pred_j)
        pred_j = np.where(np.isfinite(pred_j), np.maximum(pred_j, 0), np.nan)
        # Restore original NaNs
        preds[:, j] = pred_j
    # Preserve trailing NaNs exactly
    for j in range(test_n):
        nans_in = np.isnan(test_calcium[:, j])
        preds[nans_in, j] = np.nan
    return preds
