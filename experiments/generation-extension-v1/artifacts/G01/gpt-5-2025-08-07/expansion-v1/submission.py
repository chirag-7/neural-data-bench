import numpy as np
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import TimeSeriesSplit
import gc

def _featurize(X):
    # Per-row, causal-safe feature mapping (no temporal context used)
    X = np.asarray(X, dtype=np.float64)
    # Ensure finite
    if not np.isfinite(X).all():
        X = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)
    # Counts are nonnegative; clip to avoid log issues if any small negatives appear
    Xp = np.clip(X, 0.0, None)
    s = np.sqrt(Xp + 0.5)
    l = np.log1p(Xp)
    s2 = s * s
    sum_x = np.sum(Xp, axis=1, keepdims=True)
    sum_s = np.sum(s, axis=1, keepdims=True)
    sqrt_sumx = np.sqrt(sum_x + 0.5)
    log1p_sumx = np.log1p(sum_x)
    s_norm2 = np.sum(s2, axis=1, keepdims=True)
    F = np.hstack([Xp, s, l, s2, sum_x, sum_s, sqrt_sumx, log1p_sumx, s_norm2])
    return F

def _ramp_weights(n, w_end):
    # Exponential ramp from 1 to w_end over the series
    if w_end <= 1.0:
        return np.ones(n, dtype=np.float64)
    pos = np.linspace(0.0, 1.0, n)
    w = (w_end ** pos).astype(np.float64)
    # Normalize for numerical stability (mean ~ 1)
    m = w.mean()
    if m > 0:
        w /= m
    return w

def _var_weighted_r2_accumulate(y_true, y_pred, sse_accum, sst_accum):
    resid = y_true - y_pred
    sse_accum += np.sum(resid ** 2, axis=0)
    yv = y_true
    sst_accum += np.sum((yv - yv.mean(axis=0)) ** 2, axis=0) + 1e-12

def _select_hyperparams(X, y, alphas, w_ends, n_splits=4):
    tscv = TimeSeriesSplit(n_splits=n_splits)
    best = None
    best_score = -1e18
    for w_end in w_ends:
        w_full = _ramp_weights(X.shape[0], w_end)
        for alpha in alphas:
            sse_accum = np.zeros(y.shape[1], dtype=np.float64)
            sst_accum = np.zeros(y.shape[1], dtype=np.float64)
            for tr_idx, va_idx in tscv.split(X):
                scaler = StandardScaler(with_mean=True, with_std=True)
                Xtr = scaler.fit_transform(X[tr_idx])
                Xva = scaler.transform(X[va_idx])
                model = Ridge(alpha=float(alpha), fit_intercept=True, random_state=0)
                model.fit(Xtr, y[tr_idx], sample_weight=w_full[tr_idx])
                yhat = model.predict(Xva)
                _var_weighted_r2_accumulate(y[va_idx], yhat, sse_accum, sst_accum)
                # free memory
                del Xtr, Xva, model, yhat
                gc.collect()
            score = 1.0 - (sse_accum.sum() / sst_accum.sum())
            if score > best_score:
                best_score = score
                best = (float(alpha), float(w_end))
    return best

def fit_predict(train_x, train_y, test_x):
    # Deterministic behavior
    np.random.seed(0)

    # Build per-row features (no temporal context)
    Xtr = _featurize(train_x)
    Xte = _featurize(test_x)
    ytr = np.asarray(train_y, dtype=np.float64)

    # Hyperparameter grids (compact to respect time/memory constraints)
    alphas = np.array([0.01, 0.05, 0.2, 1.0, 5.0, 20.0, 100.0], dtype=np.float64)
    w_ends = np.array([1.0, 3.0, 10.0], dtype=np.float64)

    # Time-ordered CV to pick alpha and recency-weight strength
    alpha_best, wend_best = _select_hyperparams(Xtr, ytr, alphas, w_ends, n_splits=4)

    # Final train on all training data with chosen hyperparameters
    w_full = _ramp_weights(Xtr.shape[0], wend_best)
    scaler = StandardScaler(with_mean=True, with_std=True)
    Xtr_s = scaler.fit_transform(Xtr)
    Xte_s = scaler.transform(Xte)

    model = Ridge(alpha=alpha_best, fit_intercept=True, random_state=0)
    model.fit(Xtr_s, ytr, sample_weight=w_full)
    yhat = model.predict(Xte_s)

    # Ensure finite continuous outputs, correct shape
    yhat = np.asarray(yhat, dtype=np.float64)
    if not np.isfinite(yhat).all():
        yhat = np.nan_to_num(yhat, nan=0.0, posinf=0.0, neginf=0.0)

    return yhat
