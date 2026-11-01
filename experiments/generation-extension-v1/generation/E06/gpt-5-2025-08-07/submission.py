import numpy as np
import gc

# E06 — ZAPBench causal 32-frame calcium forecasting
# Implementation notes:
# - Shared linear temporal map 64->32, trained on deltas relative to last frame
# - Ridge penalty on weights (alpha=1.0), unpenalized bias via centering
# - Per-horizon shrinkage toward the last-frame baseline using closed-form LS
# - Deterministic, training-only fitting; vectorized across neurons and windows


def _prepare_training_matrices(train_x, train_y):
    X = np.asarray(train_x, dtype=np.float64)
    Y = np.asarray(train_y, dtype=np.float64)
    n_win, Lx, C = X.shape
    ny, Ly, Cy = Y.shape
    if C != Cy or Lx != 64 or Ly != 32:
        raise ValueError("Unexpected shapes for train_x/train_y")

    last = X[:, -1, :].reshape(-1)  # (n_win*C,)
    # Deltas relative to last observed frame
    Xdiff = (X - last.reshape(n_win, 1, C)).reshape(-1, Lx)  # (n_win*C, 64)
    Ydiff = (Y - last.reshape(n_win, 1, C)).reshape(-1, Ly)  # (n_win*C, 32)

    # Keep rows that are fully finite
    mask = np.isfinite(last)
    mask &= np.isfinite(Xdiff).all(axis=1)
    mask &= np.isfinite(Ydiff).all(axis=1)

    Xd = Xdiff[mask]
    Yd = Ydiff[mask]
    lastv = last[mask]
    return Xd, Yd, lastv


def _fit_affine_ridge(Xd, Yd, alpha=1.0):
    # Fit Y = X W + b, ridge on W only, via centering
    if Xd.size == 0 or Yd.size == 0:
        # Degenerate case: return zeros
        Lx = Xd.shape[1] if Xd.ndim == 2 else 64
        Ly = Yd.shape[1] if Yd.ndim == 2 else 32
        return np.zeros((Lx, Ly), dtype=np.float64), np.zeros(Ly, dtype=np.float64)

    x_mean = Xd.mean(axis=0, dtype=np.float64)
    y_mean = Yd.mean(axis=0, dtype=np.float64)
    Xc = Xd - x_mean
    Yc = Yd - y_mean

    XtX = Xc.T @ Xc
    XtY = Xc.T @ Yc

    # Ridge regularization
    Lx = XtX.shape[0]
    reg = alpha * np.eye(Lx, dtype=np.float64)

    # Solve (XtX + alpha I) W = XtY
    W = np.linalg.solve(XtX + reg, XtY)
    b = y_mean - x_mean @ W
    return W, b


def _fit_shrinkage_gamma(Xd, Yd, W, b, eps=1e-12):
    # Compute per-horizon gamma to shrink model deltas toward zero (baseline deltas)
    # pred_d = Xd @ W + b; target_d = Yd; gamma_j = <pred_d_j, target_d_j> / <pred_d_j, pred_d_j>
    if Xd.size == 0 or Yd.size == 0:
        return np.zeros(32, dtype=np.float64)
    pred_d = Xd @ W + b  # (N, 32)
    num = np.sum(pred_d * Yd, axis=0)
    den = np.sum(pred_d * pred_d, axis=0) + eps
    gamma = num / den
    # Clip to [0,1] for stability
    gamma = np.clip(gamma, 0.0, 1.0)
    return gamma


def _predict_with_model(test_x, W, b, gamma):
    X = np.asarray(test_x, dtype=np.float64)
    n_test, Lx, C = X.shape
    if Lx != 64:
        raise ValueError("Unexpected test_x length")

    last = X[:, -1, :]  # (n_test, C)
    Xdiff = X - last[:, None, :]  # (n_test, 64, C)

    # Matrix multiply across all neurons and windows at once
    Xmat = Xdiff.reshape(-1, Lx)  # (n_test*C, 64)
    pred_d = Xmat @ W + b  # (n_test*C, 32)
    # Apply per-horizon shrinkage of deltas
    pred_d *= gamma[None, :]

    Yhat = pred_d.reshape(n_test, C, 32).transpose(0, 2, 1)  # (n_test, 32, C)
    Yhat += last[:, None, :]  # restore absolute level

    # Ensure finiteness; fallback to last-frame baseline where needed
    bad = ~np.isfinite(Yhat)
    if bad.any():
        baseline = np.broadcast_to(last[:, None, :], Yhat.shape)
        Yhat = np.where(bad, baseline, Yhat)
    return Yhat


def fit_predict(train_x, train_y, test_x, train_groups=None):
    """Fit a shared 64->32 temporal affine map on training-only data and predict.

    Args:
        train_x: (n_train, 64, 256) past frames
        train_y: (n_train, 32, 256) future frames
        test_x:  (n_test, 64, 256) past frames
        train_groups: unused (None per protocol)

    Returns:
        np.ndarray of shape (len(test_x), 32, 256)
    """
    # Prepare training matrices (deltas relative to last frame)
    Xd, Yd, _ = _prepare_training_matrices(train_x, train_y)

    # Fit ridge-regularized affine map with unpenalized bias
    alpha = 1.0
    try:
        W, b = _fit_affine_ridge(Xd, Yd, alpha=alpha)
    except np.linalg.LinAlgError:
        # Stronger regularization fallback if needed
        W, b = _fit_affine_ridge(Xd, Yd, alpha=max(alpha * 10.0, 1.0))

    # Calibrate per-horizon shrinkage toward the last-frame baseline
    try:
        gamma = _fit_shrinkage_gamma(Xd, Yd, W, b)
    except Exception:
        gamma = np.zeros(32, dtype=np.float64)

    # Predict on test contexts
    Yhat = _predict_with_model(test_x, W, b, gamma)

    # Conform dtype to input (native units, finite)
    out_dtype = np.asarray(test_x).dtype
    Yhat = np.asarray(Yhat, dtype=out_dtype)

    # Cleanup large temporaries
    del Xd, Yd
    gc.collect()

    return Yhat
