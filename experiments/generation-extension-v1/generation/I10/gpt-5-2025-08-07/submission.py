import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold


def _balanced_accuracy(y_true, y_pred):
    y_true = y_true.astype(int)
    y_pred = y_pred.astype(int)
    pos = (y_true == 1)
    neg = (y_true == 0)
    tp = np.sum((y_pred == 1) & pos)
    fn = np.sum((y_pred == 0) & pos)
    tn = np.sum((y_pred == 0) & neg)
    fp = np.sum((y_pred == 1) & neg)
    tpr = tp / (tp + fn) if (tp + fn) > 0 else 0.5
    tnr = tn / (tn + fp) if (tn + fp) > 0 else 0.5
    return 0.5 * (tpr + tnr)


def _impute_with_median(X_train, X_test):
    med = np.nanmedian(X_train, axis=0)
    med = np.where(np.isfinite(med), med, 0.0)
    Xtr_imp = np.where(np.isnan(X_train), med[np.newaxis, :], X_train)
    Xte_imp = np.where(np.isnan(X_test), med[np.newaxis, :], X_test)
    return Xtr_imp, Xte_imp, med


def _standardize_train_only(X_train, X_test):
    mean = X_train.mean(axis=0)
    std = X_train.std(axis=0)
    std[std < 1e-12] = 1.0
    Xtr = (X_train - mean) / std
    Xte = (X_test - mean) / std
    return Xtr, Xte


def fit_predict(train_x, train_y, test_x):
    np.random.seed(42)
    X_tr = np.asarray(train_x, dtype=float)
    y = np.asarray(train_y, dtype=int).ravel()
    X_te = np.asarray(test_x, dtype=float)

    # Replace inf with NaN for imputation
    X_tr = X_tr.copy()
    X_te = X_te.copy()
    X_tr[~np.isfinite(X_tr)] = np.nan
    X_te[~np.isfinite(X_te)] = np.nan

    # Train-only median imputation and missingness indicators
    miss_tr = np.isnan(X_tr).astype(float)
    miss_te = np.isnan(X_te).astype(float)
    X_tr_imp, X_te_imp, _ = _impute_with_median(X_tr, X_te)

    # Augment with missingness indicators
    X_tr_aug = np.hstack([X_tr_imp, miss_tr])
    X_te_aug = np.hstack([X_te_imp, miss_te])

    # Train-only standardization
    X_tr_std, X_te_std = _standardize_train_only(X_tr_aug, X_te_aug)

    # OOF predictions for blending/threshold selection focused on balanced accuracy
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    n = X_tr_std.shape[0]
    p_rf_oof = np.zeros(n, dtype=float)
    p_lr_oof = np.zeros(n, dtype=float)

    for fold_id, (tr_idx, va_idx) in enumerate(skf.split(X_tr_std, y)):
        Xtr_cv, ytr_cv = X_tr_std[tr_idx], y[tr_idx]
        Xva_cv = X_tr_std[va_idx]

        rf = RandomForestClassifier(
            n_estimators=400,
            max_depth=8,
            min_samples_leaf=5,
            max_features='sqrt',
            bootstrap=True,
            class_weight='balanced_subsample',
            random_state=42 + fold_id,
            n_jobs=1,
        )
        try:
            rf.fit(Xtr_cv, ytr_cv)
            p_rf_oof[va_idx] = rf.predict_proba(Xva_cv)[:, 1]
        except Exception:
            p_rf_oof[va_idx] = 0.5

        lr = LogisticRegression(
            penalty='l2',
            C=1.0,
            class_weight='balanced',
            solver='lbfgs',
            max_iter=1000,
        )
        try:
            lr.fit(Xtr_cv, ytr_cv)
            p_lr_oof[va_idx] = lr.predict_proba(Xva_cv)[:, 1]
        except Exception:
            p_lr_oof[va_idx] = 0.5

    # Blend weight and threshold selection via grid search on OOF preds
    alphas = np.linspace(0.0, 1.0, 11)
    thresholds = np.linspace(0.05, 0.95, 181)
    best_alpha, best_thr, best_score = 1.0, 0.5, -1.0
    for a in alphas:
        p = a * p_rf_oof + (1.0 - a) * p_lr_oof
        for t in thresholds:
            pred = (p >= t).astype(int)
            score = _balanced_accuracy(y, pred)
            if score > best_score:
                best_score, best_alpha, best_thr = score, a, t

    # Fit final models on full training
    rf_final = RandomForestClassifier(
        n_estimators=400,
        max_depth=8,
        min_samples_leaf=5,
        max_features='sqrt',
        bootstrap=True,
        class_weight='balanced_subsample',
        random_state=42,
        n_jobs=1,
    )
    try:
        rf_final.fit(X_tr_std, y)
        p_rf_te = rf_final.predict_proba(X_te_std)[:, 1]
    except Exception:
        p_rf_te = np.full(X_te_std.shape[0], 0.5, dtype=float)

    lr_final = LogisticRegression(
        penalty='l2',
        C=1.0,
        class_weight='balanced',
        solver='lbfgs',
        max_iter=1000,
    )
    try:
        lr_final.fit(X_tr_std, y)
        p_lr_te = lr_final.predict_proba(X_te_std)[:, 1]
    except Exception:
        p_lr_te = np.full(X_te_std.shape[0], 0.5, dtype=float)

    p_te = best_alpha * p_rf_te + (1.0 - best_alpha) * p_lr_te
    y_pred = (p_te >= best_thr).astype(int)
    return y_pred
