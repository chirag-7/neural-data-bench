import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupKFold
from sklearn.metrics import roc_auc_score
import gc

# Deterministic seed
RANDOM_STATE = 0


def _moving_average_edgepad(x, L):
    """Centered moving average along last axis with edge padding.
    x: ndarray (..., T)
    L: window length (int); will be made odd to keep output length T.
    Returns ndarray of same shape as x, dtype float64.
    """
    if L <= 1:
        return x.astype(np.float64, copy=False)
    # make L odd
    if (L % 2) == 0:
        L = L + 1
    pad = L // 2
    # pad along last axis
    pad_spec = [(0, 0)] * x.ndim
    pad_spec[-1] = (pad, pad)
    xp = np.pad(x.astype(np.float64, copy=False), pad_spec, mode='edge')
    # cumulative sum trick for sliding window sums
    csum = np.cumsum(xp, axis=-1, dtype=np.float64)
    # prepend 0 to enable exact L-wide window sums
    zero_pad = np.zeros_like(xp[..., :1])
    csum0 = np.concatenate([zero_pad, csum], axis=-1)
    # window sums: s[j] = csum0[j+L] - csum0[j]
    s = csum0[..., L:] - csum0[..., :-L]
    return s / float(L)


def _extract_features(x, smooth_len=5, ds=4):
    """ERP features: smooth then mean-bin downsample by factor ds, flatten time x channels.
    x: (n_trials, n_channels, n_times)
    Returns: (n_trials, n_features) float64
    """
    # smoothing (edge-padded centered moving average)
    if smooth_len > 1:
        x_s = _moving_average_edgepad(x, int(smooth_len))
    else:
        x_s = x.astype(np.float64, copy=False)
    n, c, t = x_s.shape
    if t % ds != 0:
        # robust fallback: truncate tail so it's divisible
        t_new = (t // ds) * ds
        x_s = x_s[..., :t_new]
        t = t_new
    n_bins = t // ds
    # mean over non-overlapping bins
    x_b = x_s.reshape(n, c, n_bins, ds).mean(axis=3)
    # flatten with time-first convention: [time, channel]
    feats = x_b.transpose(0, 2, 1).reshape(n, n_bins * c)
    return feats


def _fit_standardizer(X):
    mu = X.mean(axis=0)
    sd = X.std(axis=0)
    sd[sd < 1e-8] = 1.0
    return mu, sd


def _apply_standardizer(X, mu, sd):
    return (X - mu) / sd


def _mean_auc_by_person(y_true, y_score, groups):
    persons = np.unique(groups)
    aucs = []
    for p in persons:
        idx = (groups == p) & np.isfinite(y_score)
        if not np.any(idx):
            continue
        yt = y_true[idx]
        ys = y_score[idx]
        if np.unique(yt).size < 2:
            # Undefined AUC if only one class; fall back to 0.5
            aucs.append(0.5)
        else:
            try:
                aucs.append(roc_auc_score(yt, ys))
            except Exception:
                aucs.append(0.5)
    if len(aucs) == 0:
        return 0.5
    return float(np.mean(aucs))


def fit_predict(train_x, train_y, test_x, train_groups):
    """Return one real-valued target score per test trial (higher = more likely target).

    Parameters
    - train_x: (n_train, 16, 128) EEG epochs in microvolts
    - train_y: (n_train,) binary labels (1 target, 0 non-target)
    - test_x:  (n_test, 16, 128) EEG epochs
    - train_groups: (n_train,) subject IDs for group-aware validation

    Returns
    - scores: (n_test,) real-valued scores
    """
    # Ensure numpy arrays
    Xtr = np.asarray(train_x)
    ytr = np.asarray(train_y).astype(int)
    Xte = np.asarray(test_x)
    groups = np.asarray(train_groups)

    # Hyperparameters to search (small, subject-held-out CV)
    ds = 4
    smooth_grid = [1, 5]           # samples, centered moving average
    C_grid = [0.5, 1.0, 2.0]

    # Precompute features for all smoothing lengths for training (to avoid recomputation per fold)
    feat_cache = {}
    for L in smooth_grid:
        feat_cache[L] = _extract_features(Xtr, smooth_len=L, ds=ds)

    # Subject-held-out cross-validation
    unique_groups = np.unique(groups)
    n_splits = min(5, unique_groups.size) if unique_groups.size >= 2 else 2
    gkf = GroupKFold(n_splits=n_splits)

    best_score = -np.inf
    best_params = None

    for L in smooth_grid:
        Xf_all = feat_cache[L]
        for C in C_grid:
            # Collect CV predictions per trial (filled only on val indices)
            cv_pred = np.full(Xf_all.shape[0], np.nan, dtype=np.float64)
            for tr_idx, va_idx in gkf.split(Xf_all, ytr, groups):
                Xf_tr = Xf_all[tr_idx]
                Xf_va = Xf_all[va_idx]
                y_tr = ytr[tr_idx]
                # Standardize on training fold only
                mu, sd = _fit_standardizer(Xf_tr)
                Xf_tr = _apply_standardizer(Xf_tr, mu, sd)
                Xf_va = _apply_standardizer(Xf_va, mu, sd)
                # Classifier
                clf = LogisticRegression(
                    penalty='l2', C=float(C), solver='liblinear',
                    class_weight='balanced', max_iter=1000, random_state=RANDOM_STATE,
                    fit_intercept=True)
                clf.fit(Xf_tr, y_tr)
                cv_pred[va_idx] = clf.decision_function(Xf_va)
            # Evaluate mean AUC per person (equal weight) using only validation predictions
            mean_auc = _mean_auc_by_person(ytr, cv_pred, groups)
            # Track best (tie-break: prefer smaller L, then smaller C for stability)
            if (mean_auc > best_score + 1e-12) or (
                abs(mean_auc - best_score) <= 1e-12 and (
                    (best_params is not None and L < best_params[0]) or
                    (best_params is not None and L == best_params[0] and C < best_params[1])
                )
            ):
                best_score = mean_auc
                best_params = (L, C)

    # Fit final model on full training data with best hyperparameters
    best_L, best_C = best_params
    # Compute features for chosen smoothing length
    Xf_tr = feat_cache[best_L]
    # Standardize on full training set
    mu_full, sd_full = _fit_standardizer(Xf_tr)
    Xf_tr = _apply_standardizer(Xf_tr, mu_full, sd_full)

    clf = LogisticRegression(
        penalty='l2', C=float(best_C), solver='liblinear',
        class_weight='balanced', max_iter=1000, random_state=RANDOM_STATE,
        fit_intercept=True)
    clf.fit(Xf_tr, ytr)

    # Prepare test features (compute only for best L)
    Xf_te = _extract_features(Xte, smooth_len=best_L, ds=ds)
    Xf_te = _apply_standardizer(Xf_te, mu_full, sd_full)

    # Decision scores (higher => more likely target)
    scores = clf.decision_function(Xf_te)

    # Cleanup big intermediates
    del feat_cache, Xf_tr, Xf_te
    gc.collect()

    # Ensure finite real outputs
    scores = np.asarray(scores, dtype=np.float64)
    scores[~np.isfinite(scores)] = 0.0
    return scores
