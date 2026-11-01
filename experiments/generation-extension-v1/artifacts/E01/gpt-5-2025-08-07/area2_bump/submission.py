import numpy as np
from sklearn.linear_model import Ridge
from sklearn.model_selection import GroupKFold

# Deterministic behavior
np.random.seed(0)


def _build_lagged_features(x, lag):
    """
    Build within-trial acausal lagged features with zero padding.
    x: array (n_trials, T, F) of floats (already transformed, e.g., log1p)
    lag: int, number of bins on each side to include
    Returns X2D (n_trials*T, F*(2*lag+1))
    """
    n, T, F = x.shape
    pieces = []
    for k in range(-lag, lag + 1):
        shifted = np.zeros_like(x)
        if k < 0:
            shifted[:, :T + k, :] = x[:, -k:, :]
        elif k > 0:
            shifted[:, k:, :] = x[:, :T - k, :]
        else:
            # center lag: copy to avoid modifying original
            shifted = x.copy()
        pieces.append(shifted)
    X = np.concatenate(pieces, axis=2)
    return X.reshape(n * T, -1)


def _standardize_fit(X):
    mu = X.mean(axis=0)
    sigma = X.std(axis=0)
    sigma[sigma < 1e-6] = 1e-6
    return mu, sigma


def _standardize_apply(X, mu, sigma):
    return (X - mu) / sigma


def _choose_alpha_cv(X, Y, groups, alphas, n_splits=5):
    # GroupKFold over trials
    n_unique = len(np.unique(groups))
    n_splits = max(2, min(n_splits, n_unique))
    gkf = GroupKFold(n_splits=n_splits)
    best_alpha = alphas[0]
    best_score = np.inf
    for a in alphas:
        fold_losses = []
        for tr_idx, va_idx in gkf.split(X, Y, groups):
            X_tr, X_va = X[tr_idx], X[va_idx]
            Y_tr, Y_va = Y[tr_idx], Y[va_idx]
            mu, sigma = _standardize_fit(X_tr)
            X_tr_s = _standardize_apply(X_tr, mu, sigma)
            X_va_s = _standardize_apply(X_va, mu, sigma)
            model = Ridge(alpha=a, fit_intercept=True)
            model.fit(X_tr_s, Y_tr)
            Y_hat = model.predict(X_va_s)
            # MSE on log-scale targets
            loss = np.mean((Y_hat - Y_va) ** 2)
            fold_losses.append(loss)
        avg = float(np.mean(fold_losses))
        if avg < best_score:
            best_score = avg
            best_alpha = a
    return best_alpha


def fit_predict(train_x, train_y, test_x):
    """
    Fit on (train_x, train_y) and predict held-out neuron counts for test_x.
    Inputs:
      - train_x: (99, 35, 107) observed counts per 20ms bin
      - train_y: (99, 35, 35) held-out counts per 20ms bin
      - test_x:  (100, 35, 107)
    Returns:
      - preds: (100, 35, 35) nonnegative expected counts per bin
    """
    # Basic shape checks (lightweight, do not raise on exact values to keep generic)
    if train_x.ndim != 3 or train_y.ndim != 3 or test_x.ndim != 3:
        raise ValueError("Inputs must be 3D arrays (trials, time, neurons)")
    n_tr, T, f_in = train_x.shape
    n_tr_y, T_y, f_out = train_y.shape
    n_te, T_te, f_in_te = test_x.shape
    if n_tr != n_tr_y or T != T_y or f_in != f_in_te or T != T_te:
        raise ValueError("Mismatched shapes between X and Y or test.")

    # Hyperparameters
    lag = 5  # +/- 5 bins (total window 11); within-trial only
    alpha_grid = np.array([0.03, 0.1, 0.3, 1.0, 3.0, 10.0, 30.0, 100.0])

    # Transform counts to stabilize variance
    X_tr_tf = np.log1p(train_x.astype(np.float64))
    X_te_tf = np.log1p(test_x.astype(np.float64))
    Y_tr_tf = np.log1p(train_y.astype(np.float64))

    # Build lagged features within trials (no cross-trial mixing)
    X_train = _build_lagged_features(X_tr_tf, lag)
    X_test = _build_lagged_features(X_te_tf, lag)

    # Flatten Y to 2D (samples, outputs)
    Y_train = Y_tr_tf.reshape(n_tr * T, f_out)

    # Group labels per row = trial index
    groups = np.repeat(np.arange(n_tr), T)

    # Select regularization via GroupKFold on trials
    alpha = _choose_alpha_cv(X_train, Y_train, groups, alpha_grid, n_splits=5)

    # Standardize using all training data, then fit final model
    mu, sigma = _standardize_fit(X_train)
    X_train_s = _standardize_apply(X_train, mu, sigma)
    X_test_s = _standardize_apply(X_test, mu, sigma)

    model = Ridge(alpha=alpha, fit_intercept=True)
    model.fit(X_train_s, Y_train)

    # Predict in log-domain, invert transform to counts; ensure finite, nonnegative
    Z_pred = model.predict(X_test_s)
    # Prevent overflow in expm1
    Z_pred = np.clip(Z_pred, -10.0, 10.0)
    Y_pred = np.expm1(Z_pred)
    # Clean any tiny negatives due to numerics and enforce finiteness
    Y_pred[~np.isfinite(Y_pred)] = 0.0
    Y_pred = np.maximum(Y_pred, 0.0)

    return Y_pred.reshape(n_te, T, f_out)
