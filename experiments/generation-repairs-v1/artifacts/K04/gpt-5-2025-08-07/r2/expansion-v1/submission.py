import numpy as np
from collections import Counter
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupKFold
from sklearn.metrics import f1_score


def _fit_scaler(X):
    mu = X.mean(axis=0)
    sd = X.std(axis=0)
    sd[sd < 1e-8] = 1.0
    return mu, sd


def _apply_scaler(X, mu, sd):
    return (X - mu) / sd


def _compute_sample_weights(y, groups, n_classes=7):
    # Class weights: n / (k * n_c) for present classes
    y = np.asarray(y, dtype=int)
    n = y.shape[0]
    counts = np.bincount(y, minlength=n_classes)
    present = counts > 0
    cw = np.zeros(n_classes, dtype=float)
    if present.any():
        k = present.sum()
        cw[present] = n / (k * counts[present].astype(float))
    # Group weights: equal total weight per donor
    groups = np.asarray(groups)
    gcnt = Counter(groups.tolist())
    ug = list(gcnt.keys())
    gw = {g: (n / (len(ug) * gcnt[g])) for g in ug}
    # Combine
    sw = np.empty(n, dtype=float)
    for i in range(n):
        sw[i] = cw[y[i]] * gw[groups[i]]
    return sw


def fit_predict(train_x, train_y, test_x, train_groups):
    np.random.seed(0)
    X_tr = np.asarray(train_x, dtype=np.float32)
    y_tr = np.asarray(train_y, dtype=int)
    X_te = np.asarray(test_x, dtype=np.float32)
    groups = np.asarray(train_groups)

    n_classes = 7
    # Hyperparameter grid (kept small for robustness/speed)
    C_grid = [0.3, 1.0, 3.0]

    # Grouped CV over donors if >=2 groups
    unique_groups = np.unique(groups)
    use_cv = unique_groups.size >= 2
    best_C = 1.0
    best_score = -np.inf

    if use_cv:
        gkf = GroupKFold(n_splits=unique_groups.size)
        for C in C_grid:
            fold_scores = []
            for tr_idx, va_idx in gkf.split(X_tr, y_tr, groups):
                X_tr_f, X_va_f = X_tr[tr_idx], X_tr[va_idx]
                y_tr_f, y_va_f = y_tr[tr_idx], y_tr[va_idx]
                g_tr_f = groups[tr_idx]
                # Fit scaler on fold-train only
                mu_f, sd_f = _fit_scaler(X_tr_f)
                X_tr_fs = _apply_scaler(X_tr_f, mu_f, sd_f)
                X_va_fs = _apply_scaler(X_va_f, mu_f, sd_f)
                # Sample weights: class-balanced and donor-balanced within fold
                sw_f = _compute_sample_weights(y_tr_f, g_tr_f, n_classes=n_classes)
                clf = LogisticRegression(
                    penalty='l2', solver='lbfgs', 
                    C=C, max_iter=300, tol=1e-3, random_state=0
                )
                clf.fit(X_tr_fs, y_tr_f, sample_weight=sw_f)
                y_pred = clf.predict(X_va_fs)
                score = f1_score(y_va_f, y_pred, labels=list(range(n_classes)), average='macro', zero_division=0)
                fold_scores.append(score)
            mean_score = float(np.mean(fold_scores)) if fold_scores else -np.inf
            if mean_score > best_score:
                best_score = mean_score
                best_C = C
    else:
        best_C = 1.0

    # Final training on all donors with training-only scaler
    mu, sd = _fit_scaler(X_tr)
    X_trs = _apply_scaler(X_tr, mu, sd)
    X_tes = _apply_scaler(X_te, mu, sd)

    sw_full = _compute_sample_weights(y_tr, groups, n_classes=n_classes)
    final_clf = LogisticRegression(
        penalty='l2', solver='lbfgs', 
        C=best_C, max_iter=300, tol=1e-3, random_state=0
    )
    final_clf.fit(X_trs, y_tr, sample_weight=sw_full)
    y_hat = final_clf.predict(X_tes)
    return y_hat.astype(int)