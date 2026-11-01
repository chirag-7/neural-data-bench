import numpy as np

# ----------------------------- Helpers -----------------------------

def _rfft(x):
    return np.fft.rfft(x, axis=1)

def _irfft(X, n):
    return np.fft.irfft(X, n=n, axis=1)

def _smooth_1d(v, k):
    # Uniform moving average smoothing with reflect padding
    if k is None or k <= 1:
        return v
    if k % 2 == 0:
        k += 1
    pad = k // 2
    vp = np.pad(v, (pad, pad), mode='reflect')
    w = np.ones(k, dtype=v.dtype)
    w /= w.sum()
    return np.convolve(vp, w, mode='valid')

def _estimate_transfer(Xf, Yf, lam_rel=1e-3, smooth=7, gamma=0.05):
    # Xf, Yf: (n_segments, n_freq) complex
    # Compute cross/auto spectra summed across segments
    s_xx = np.sum((np.abs(Xf) ** 2), axis=0)  # real, >=0
    s_xy = np.sum(np.conj(Xf) * Yf, axis=0)   # complex
    # Regularization scaled by mean power to be scale-invariant
    lam = lam_rel * (np.mean(s_xx) + 1e-12)
    Hc = s_xy / (s_xx + lam)                  # complex LS solution
    H = Hc.real                               # enforce zero-phase (real) response
    # Smooth across frequency to reduce variance
    H = _smooth_1d(H, smooth)
    # Clip to [0,1] as a Wiener-like attenuator
    H = np.clip(H, 0.0, 1.0)
    # Shrink slightly toward identity to avoid over-attenuation
    if gamma is not None and gamma > 0:
        H = gamma + (1.0 - gamma) * H
    return H.astype(np.float64)

def _rel_rmse(pred, target):
    # pred, target: (n, t)
    diff = pred - target
    num = np.sqrt(np.sum(diff * diff, axis=1))
    den = np.sqrt(np.sum(target * target, axis=1)) + 1e-12
    return float(np.mean(num / den))

# ----------------------------- Main API -----------------------------

def fit_predict(train_x, train_y, test_x):
    """
    Learn a zero-phase frequency-domain Wiener filter from (train_x -> train_y)
    and apply it to test_x. Returns an array with the same shape as test_x.
    """
    # Cast to float64 for numerical stability in spectral ratios
    X_tr = np.asarray(train_x, dtype=np.float64)
    Y_tr = np.asarray(train_y, dtype=np.float64)
    X_te = np.asarray(test_x, dtype=np.float64)

    n_train, n_samples = X_tr.shape
    n_test = X_te.shape[0]
    n_freq = n_samples // 2 + 1

    # Precompute FFTs
    Xf_all = _rfft(X_tr)
    Yf_all = _rfft(Y_tr)

    # Hold-out split (deterministic)
    rng = np.random.RandomState(0)
    idx = np.arange(n_train)
    rng.shuffle(idx)
    n_val = max(1, int(0.2 * n_train))
    val_idx = idx[:n_val]
    tr_idx = idx[n_val:]

    Xf_tr = Xf_all[tr_idx]
    Yf_tr = Yf_all[tr_idx]
    Xf_val = Xf_all[val_idx]
    Y_val = Y_tr[val_idx]

    # Hyperparameter grid (small, fast)
    lam_list = [1e-4, 3e-4, 1e-3, 3e-3, 1e-2]
    smooth_list = [1, 3, 7, 15, 31]
    gamma_list = [0.0, 0.05, 0.1]

    best = (np.inf, None)

    # Precompute inverse FFT length
    N = n_samples

    for lam_rel in lam_list:
        for sm in smooth_list:
            # Estimate transfer once per (lam, sm) then test gammas cheaply
            H_base = _estimate_transfer(Xf_tr, Yf_tr, lam_rel=lam_rel, smooth=sm, gamma=0.0)
            for gamma in gamma_list:
                if gamma > 0:
                    H = gamma + (1.0 - gamma) * H_base
                else:
                    H = H_base
                # Ensure bounds after shrink
                H = np.clip(H, 0.0, 1.0)
                # Validate
                Yf_pred_val = Xf_val * H[None, :]
                y_pred_val = _irfft(Yf_pred_val, n=N)
                score = _rel_rmse(y_pred_val, Y_val)
                if score < best[0]:
                    best = (score, (lam_rel, sm, gamma))

    # Refit on all training with the best hyperparameters
    lam_rel, sm, gamma = best[1]
    H_all = _estimate_transfer(Xf_all, Yf_all, lam_rel=lam_rel, smooth=sm, gamma=gamma)

    # Apply to test
    Xf_te = _rfft(X_te)
    Yf_te_pred = Xf_te * H_all[None, :]
    y_te_pred = _irfft(Yf_te_pred, n=N)

    return y_te_pred.astype(np.float32)
