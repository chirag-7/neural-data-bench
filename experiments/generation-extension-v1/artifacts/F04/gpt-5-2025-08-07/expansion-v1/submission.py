import numpy as np
from sklearn.model_selection import KFold

# Try to use PoissonRegressor; fall back to TweedieRegressor if unavailable
try:
    from sklearn.linear_model import PoissonRegressor as _BasePoisson
    _USE_TWEEDIE = False
except Exception:  # pragma: no cover
    from sklearn.linear_model import TweedieRegressor as _Tweedie
    _BasePoisson = _Tweedie  # type: ignore
    _USE_TWEEDIE = True


def _poisson_nll(y_true, mu, eps=1e-9):
    # Mean Poisson negative log-likelihood up to additive const (ignores log y!)
    mu = np.clip(mu, eps, None)
    return np.sum(mu - y_true * np.log(mu))


def _standardize(X):
    X = np.asarray(X, dtype=float)
    mean = X.mean(axis=0)
    scale = X.std(axis=0)
    # protect against zero variance features
    scale[scale < 1e-12] = 1.0
    Xs = (X - mean) / scale
    return Xs, mean, scale


def _apply_standardize(X, mean, scale):
    return (np.asarray(X, dtype=float) - mean) / scale


def _unique_rows(X):
    # Deduplicate rows exactly; returns unique rows and inverse index mapping
    X = np.asarray(X)
    uniq, inv = np.unique(X, axis=0, return_inverse=True)
    return uniq, inv


def _fit_single_neuron(X, y, folds, alpha_grid, max_iter=300, tol=1e-7):
    y = np.asarray(y, dtype=float)
    # Ensure non-negative counts
    y[y < 0] = 0.0

    best_alpha = None
    best_obj = np.inf

    for alpha in alpha_grid:
        fold_obj = 0.0
        for tr, va in folds:
            if _USE_TWEEDIE:
                model = _BasePoisson(power=1, link='log', alpha=alpha, max_iter=max_iter, tol=tol)
            else:
                model = _BasePoisson(alpha=alpha, fit_intercept=True, max_iter=max_iter, tol=tol, warm_start=False)
            model.fit(X[tr], y[tr])
            mu = model.predict(X[va])
            fold_obj += _poisson_nll(y[va], mu)
        if fold_obj < best_obj:
            best_obj = fold_obj
            best_alpha = alpha

    # Fit final model on all training data with chosen alpha
    if _USE_TWEEDIE:
        final_model = _BasePoisson(power=1, link='log', alpha=best_alpha, max_iter=max_iter, tol=tol)
    else:
        final_model = _BasePoisson(alpha=best_alpha, fit_intercept=True, max_iter=max_iter, tol=tol, warm_start=False)
    final_model.fit(X, y)
    return final_model, best_alpha


def fit_predict(train_x, train_y, test_x):
    """
    Fit per-neuron Poisson GLMs with L2 regularization and predict expected counts for test images.
    train_x: array (n_train, 324)
    train_y: array (n_train, 41) integer counts per 300 ms
    test_x:  array (n_test, 324) with duplicates (same image repeated); predictions must be identical for identical rows
    Returns: array (n_test, 41) positive finite expected spike counts per 300ms
    """
    np.random.seed(1)

    Xtr = np.asarray(train_x, dtype=float)
    Ytr = np.asarray(train_y, dtype=float)
    Xte = np.asarray(test_x, dtype=float)

    # Standardize features using train stats only
    Xtr_s, mu_x, sd_x = _standardize(Xtr)

    # Deduplicate test images before scaling to guarantee identical predictions for repeats
    Xte_uniq_raw, inv = _unique_rows(Xte)
    Xte_uniq = _apply_standardize(Xte_uniq_raw, mu_x, sd_x)

    n_train, n_feat = Xtr_s.shape
    n_neurons = Ytr.shape[1]

    # 3-fold CV for alpha selection, shuffled for robustness
    n_splits = 3
    kf = KFold(n_splits=n_splits, shuffle=True, random_state=123)
    folds = [(tr_idx, va_idx) for tr_idx, va_idx in kf.split(Xtr_s)]

    # Log-spaced modest grid of alphas (L2 strength)
    alpha_grid = np.array([1e-4, 3e-4, 1e-3, 3e-3, 1e-2, 3e-2])

    # Fit a model per neuron
    models = []
    for nn in range(n_neurons):
        y = Ytr[:, nn]
        model, _ = _fit_single_neuron(Xtr_s, y, folds, alpha_grid, max_iter=300, tol=1e-7)
        models.append(model)

    # Predict for unique test rows then broadcast back
    preds_uniq = np.zeros((Xte_uniq.shape[0], n_neurons), dtype=float)
    for nn, model in enumerate(models):
        mu = model.predict(Xte_uniq)
        # Ensure strictly positive finite values
        mu = np.clip(mu, 1e-9, 1e9)
        preds_uniq[:, nn] = mu

    preds = preds_uniq[inv]
    return preds
