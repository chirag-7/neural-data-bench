
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.model_selection import KFold

# Variance-weighted R^2 evaluation (main metric)
def var_weighted_r2(y_true, y_pred):
    # y_true/y_pred: shape (n_samples, 2)
    ss_res = np.sum((y_true - y_pred)**2, axis=0)
    y_mean = np.mean(y_true, axis=0)
    ss_tot = np.sum((y_true - y_mean)**2, axis=0)
    # R2 per target
    r2s = 1 - ss_res / ss_tot
    # Variance-weighted
    var = np.var(y_true, axis=0)
    weighted_r2 = np.sum(var * r2s) / np.sum(var)
    return weighted_r2

# Chronological cross-validation splits, preserving sequence for time series
def chrono_kfold(n_samples, n_splits):
    fold_sizes = (n_samples // n_splits) * np.ones(n_splits, dtype=np.int32)
    fold_sizes[:n_samples % n_splits] += 1
    idxs = np.arange(n_samples)
    current = 0
    for fold_size in fold_sizes:
        val_start, val_end = current, current + fold_size
        train_idx = idxs[:val_start]
        val_idx = idxs[val_start:val_end]
        yield train_idx, val_idx
        current = val_end


def fit_predict(train_x, train_y, test_x):
    # Deterministic seed
    np.random.seed(42)
    # Ridge hyperparameters
default_alphas = [0.01, 0.1, 1.0, 10.0, 100.0]
    n_folds = 5
    n_train = train_x.shape[0]

    best_alpha = None
    best_score = -np.inf

    for alpha in default_alphas:
        fold_scores = []
        for train_idx, val_idx in chrono_kfold(n_train, n_folds):
            # If any train fold is empty, skip
            if len(train_idx) == 0 or len(val_idx) == 0:
                continue
            x_tr, y_tr = train_x[train_idx], train_y[train_idx]
            x_val, y_val = train_x[val_idx], train_y[val_idx]
            model = Ridge(alpha=alpha, fit_intercept=True, solver='auto', random_state=42, max_iter=1000)
            model.fit(x_tr, y_tr)
            y_pred = model.predict(x_val)
            score = var_weighted_r2(y_val, y_pred)
            fold_scores.append(score)
        if fold_scores:
            avg_score = np.mean(fold_scores)
            if avg_score > best_score:
                best_score = avg_score
                best_alpha = alpha

    # Fit on full train set with best alpha
    final_model = Ridge(alpha=best_alpha, fit_intercept=True, solver='auto', random_state=42, max_iter=1000)
    final_model.fit(train_x, train_y)
    y_test_pred = final_model.predict(test_x)
    # Ensure correct shape, finite outputs
    y_test_pred = np.asarray(y_test_pred, dtype=np.float32)
    if y_test_pred.shape != (test_x.shape[0], 2):
        y_test_pred = y_test_pred.reshape(test_x.shape[0], 2)
    y_test_pred = np.nan_to_num(y_test_pred, nan=0.0, posinf=0.0, neginf=0.0)
    return y_test_pred
