import numpy as np
from sklearn.linear_model import PoissonRegressor

_EPS = 1e-12


def _quantile_centers(x, n_centers, lo_q=0.05, hi_q=0.95):
    x = np.asarray(x, dtype=float)
    if n_centers <= 0:
        return np.zeros(0, dtype=float), 1.0
    lo, hi = np.quantile(x, [lo_q, hi_q])
    if not np.isfinite(lo) or not np.isfinite(hi) or hi <= lo:
        lo = np.min(x)
        hi = np.max(x)
    q = np.linspace(lo_q, hi_q, n_centers)
    centers = np.quantile(x, q)
    centers = np.unique(centers)
    if centers.size == 0:
        centers = np.array([np.mean(x)])
    diffs = np.diff(centers)
    if diffs.size > 0:
        width = float(np.median(diffs))
    else:
        width = float(np.std(x))
    if not np.isfinite(width) or width <= _EPS:
        # fallback: robust scale
        width = float(np.quantile(np.abs(x - np.median(x)), 0.75) * 1.4826)
        if not np.isfinite(width) or width <= _EPS:
            width = 1.0
    # Slightly widen for smoother coverage
    width *= 1.25
    return centers.astype(float), float(width)


def _rbf_transform(x, centers, width):
    x = np.asarray(x, dtype=float)
    centers = np.asarray(centers, dtype=float)
    if centers.size == 0:
        return np.zeros((x.shape[0], 0), dtype=float)
    w = max(float(width), _EPS)
    diff = x[:, None] - centers[None, :]
    return np.exp(-0.5 * (diff / w) ** 2, dtype=float)


def _build_design(X, cfg):
    # X: (n, 2) with columns [position_cm, velocity_cm_per_s]
    pos = X[:, 0].astype(float)
    vel = X[:, 1].astype(float)
    spd = np.abs(vel)

    # Radial features
    phi_pos = _rbf_transform(pos, cfg['pos_centers'], cfg['pos_width'])
    phi_spd = _rbf_transform(spd, cfg['spd_centers'], cfg['spd_width'])

    # Interactions pos-by-speed RBFs
    if phi_pos.shape[1] > 0 and phi_spd.shape[1] > 0:
        inter = (phi_pos[:, :, None] * phi_spd[:, None, :]).reshape(X.shape[0], -1)
    else:
        inter = np.zeros((X.shape[0], 0), dtype=float)

    # Low-order polynomials (provide global trends)
    poly = np.column_stack([
        pos, pos * pos, pos * pos * pos,
        vel, vel * vel, vel * vel * vel,
        spd, spd * spd,
    ]).astype(float)

    feats = [poly, phi_pos, phi_spd, inter]
    return np.hstack(feats)


def _standardize_fit(X):
    mu = X.mean(axis=0)
    sd = X.std(axis=0)
    sd[sd < 1e-12] = 1.0
    Z = (X - mu) / sd
    return Z, mu, sd


def _standardize_apply(X, mu, sd):
    sd = np.where(sd < 1e-12, 1.0, sd)
    return (X - mu) / sd


def _fillna_inplace(train_x, test_x):
    med = np.nanmedian(train_x, axis=0)
    med = np.where(np.isfinite(med), med, 0.0)
    for X in (train_x, test_x):
        for j in range(X.shape[1]):
            col = X[:, j]
            mask = ~np.isfinite(col)
            if np.any(mask):
                col = col.copy()
                col[mask] = med[j]
                X[:, j] = col


def _poisson_ll(y, mu):
    mu = np.maximum(mu, _EPS)
    # Constant log(y!) omitted (does not affect model selection)
    return float(np.sum(y * np.log(mu) - mu))


def fit_predict(train_x, train_y, test_x):
    train_x = np.asarray(train_x, dtype=float)
    train_y = np.asarray(train_y, dtype=float)
    test_x = np.asarray(test_x, dtype=float)

    if train_x.ndim != 2 or train_x.shape[1] != 2:
        raise ValueError("train_x must have shape (n_samples, 2)")
    if test_x.ndim != 2 or test_x.shape[1] != 2:
        raise ValueError("test_x must have shape (n_samples, 2)")

    # Clean NaNs/Infs using training medians
    _fillna_inplace(train_x, test_x)

    # Ensure valid nonnegative targets
    train_y = np.where(np.isfinite(train_y), train_y, 0.0)
    train_y = np.clip(train_y, 0.0, None)

    # Basis configuration
    K_pos = 20  # number of RBFs over position
    K_spd = 8   # number of RBFs over absolute speed
    pos_centers, pos_w = _quantile_centers(train_x[:, 0], K_pos, lo_q=0.05, hi_q=0.95)
    spd_centers, spd_w = _quantile_centers(np.abs(train_x[:, 1]), K_spd, lo_q=0.05, hi_q=0.95)
    cfg = {
        'pos_centers': pos_centers,
        'pos_width': pos_w,
        'spd_centers': spd_centers,
        'spd_width': spd_w,
    }

    # Build design matrices
    Xtr = _build_design(train_x, cfg)
    Xte = _build_design(test_x, cfg)

    # Standardize by training statistics
    Ztr, mu_col, sd_col = _standardize_fit(Xtr)
    Zte = _standardize_apply(Xte, mu_col, sd_col)

    n = train_y.shape[0]
    n_fit = max(int(0.8 * n), 1)
    n_fit = min(n_fit, n - 1)  # ensure non-empty validation

    # Alpha grid for L2 regularization
    alphas = np.array([1e-4, 3e-4, 1e-3, 3e-3, 1e-2, 3e-2, 1e-1], dtype=float)

    Z_fit = Ztr[:n_fit]
    y_fit = train_y[:n_fit]
    Z_val = Ztr[n_fit:]
    y_val = train_y[n_fit:]

    best_alpha = float(alphas[0])
    best_ll = -np.inf

    for a in alphas:
        try:
            model = PoissonRegressor(alpha=float(a), fit_intercept=True, max_iter=300, tol=1e-8, warm_start=False)
            model.fit(Z_fit, y_fit)
            mu_val = model.predict(Z_val)
            ll = _poisson_ll(y_val, mu_val)
            if ll > best_ll:
                best_ll = ll
                best_alpha = float(a)
        except Exception:
            # If any alpha fails to converge, skip it
            continue

    # Fit final model on full training set with best alpha
    final_model = PoissonRegressor(alpha=best_alpha, fit_intercept=True, max_iter=500, tol=1e-8, warm_start=False)
    final_model.fit(Ztr, train_y)

    mu_test = final_model.predict(Zte)
    # Ensure valid, finite, nonnegative expected counts per 20 ms bin
    mu_test = np.where(np.isfinite(mu_test), mu_test, np.nan)
    if np.isnan(mu_test).any():
        fallback = float(np.maximum(train_y.mean(), _EPS))
        mu_test = np.where(np.isnan(mu_test), fallback, mu_test)
    mu_test = np.maximum(mu_test, _EPS)
    return mu_test.ravel()