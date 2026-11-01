import numpy as np


def _ensure_finite(a, fill=0.0):
    a = np.asarray(a, dtype=np.float64)
    if not np.isfinite(a).all():
        a = np.where(np.isfinite(a), a, fill)
    return a


def _smooth_hamming(x, win=15):
    # Symmetric 1D smoothing with a Hamming window; odd window size enforced
    x = np.asarray(x, dtype=np.float64)
    if win < 3:
        return x.copy()
    if win % 2 == 0:
        win += 1
    kernel = np.hamming(win)
    kernel = kernel / kernel.sum()
    pad = win // 2
    # Reflect padding preserves edge shapes reasonably well
    xp = np.pad(x, (pad, pad), mode='reflect')
    y = np.convolve(xp, kernel, mode='valid')
    return y


def fit_predict(train_x, train_y, test_x):
    """
    Predict passive voltage deflection for held-out constant-current steps.

    Args:
        train_x: (n_train, T) injected currents (pA), relative to pre-step.
        train_y: (n_train, T) voltage deflections (mV), relative to pre-step.
        test_x:  (n_test,  T) injected currents (pA), relative to pre-step.

    Returns:
        (n_test, T) predicted voltage deflections (mV).
    """
    # Convert and sanitize inputs
    X = _ensure_finite(train_x)
    Y = _ensure_finite(train_y)
    Xt = _ensure_finite(test_x)

    # Basic shape checks
    if X.ndim != 2 or Y.ndim != 2 or Xt.ndim != 2:
        raise ValueError("All inputs must be 2D arrays (sweeps, time)")
    if X.shape != Y.shape:
        raise ValueError("train_x and train_y must have the same shape")
    n_train, T = X.shape
    if Xt.shape[1] != T:
        raise ValueError("test_x must have the same number of time samples as train_x")

    # Zero-intercept OLS per time sample: g(t) = sum_j x*y / (sum_j x^2 + ridge)
    denom = np.sum(X * X, axis=0)
    numer = np.sum(X * Y, axis=0)
    ridge = 1e-12 + 1e-8 * float(np.mean(denom))  # tiny regularization for safety
    g = numer / (denom + ridge)

    # Physical constraints: passive response per unit current is non-negative
    g = np.clip(g, 0.0, None)

    # Smooth to suppress measurement noise while retaining onset dynamics
    g_s = _smooth_hamming(g, win=15)  # ~30 ms at 500 Hz (dt=2 ms)

    # Calibrate steady-state gain using the last 20% of the step to preserve R_in
    tail_start = max(0, int(0.8 * T))
    # Global tail slope across all sweeps and tail time samples
    X_tail = X[:, tail_start:]
    Y_tail = Y[:, tail_start:]
    numer_tail = float(np.sum(X_tail * Y_tail))
    denom_tail = float(np.sum(X_tail * X_tail))
    g_inf = numer_tail / (denom_tail + 1e-12)

    mean_g_tail = float(np.mean(g_s[tail_start:])) if tail_start < T else float(g_s[-1])
    if mean_g_tail > 0 and np.isfinite(g_inf):
        scale = g_inf / (mean_g_tail + 1e-12)
        g_s *= scale

    # Enforce monotonic non-decreasing step shape and g(0)=0
    g_s = np.maximum.accumulate(np.maximum(g_s, 0.0))
    g_s[0] = 0.0

    # Final safety: if tail went off due to accumulation, re-anchor plateau
    if tail_start < T:
        end_mean = float(np.mean(g_s[tail_start:]))
        if end_mean > 0 and np.isfinite(g_inf):
            g_s *= g_inf / (end_mean + 1e-12)

    # Predict: pointwise multiply by test current per time sample
    Y_pred = Xt * g_s[None, :]

    # Ensure finite outputs
    Y_pred = np.where(np.isfinite(Y_pred), Y_pred, 0.0)

    return Y_pred
