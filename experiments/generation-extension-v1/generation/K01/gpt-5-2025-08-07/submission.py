import numpy as np
from math import inf
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import f1_score, balanced_accuracy_score
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier
try:
    from sklearn.ensemble import HistGradientBoostingClassifier as _HGB
    HAS_HGB = True
except Exception:
    from sklearn.ensemble import GradientBoostingClassifier as _GBC
    HAS_HGB = False

# ---------------------- Helpers ----------------------

def _to_numpy(x):
    arr = np.asarray(x)
    if arr.ndim == 1:
        return arr.copy()
    return arr.copy()

def _clean_infs(X):
    # Replace +/- inf with NaN so imputers / HGB can handle
    X = np.asarray(X, dtype=float)
    mask = ~np.isfinite(X)
    if mask.any():
        X[mask] = np.nan
    return X

def _balanced_sample_weight(y):
    y = np.asarray(y)
    classes, counts = np.unique(y, return_counts=True)
    n = float(len(y))
    k = float(len(classes))
    w = {c: n / (k * cnt) for c, cnt in zip(classes, counts)}
    return np.array([w[yy] for yy in y], dtype=float)

def _build_logreg(seed):
    return Pipeline([
        ("imp", SimpleImputer(strategy="median", add_indicator=True)),
        ("sc", StandardScaler()),
        ("lr", LogisticRegression(C=0.8, max_iter=2000, solver="liblinear", class_weight="balanced", random_state=seed))
    ])

def _build_rf(seed):
    return Pipeline([
        ("imp", SimpleImputer(strategy="median", add_indicator=True)),
        ("rf", RandomForestClassifier(
            n_estimators=400,
            max_depth=None,
            min_samples_leaf=2,
            max_features="sqrt",
            class_weight="balanced_subsample",
            bootstrap=True,
            oob_score=False,
            n_jobs=1,
            random_state=seed,
        ))
    ])

def _build_et(seed):
    return Pipeline([
        ("imp", SimpleImputer(strategy="median", add_indicator=True)),
        ("et", ExtraTreesClassifier(
            n_estimators=400,
            max_depth=None,
            min_samples_leaf=2,
            max_features="sqrt",
            class_weight="balanced",
            bootstrap=False,
            n_jobs=1,
            random_state=seed,
        ))
    ])

def _build_hgb(seed):
    if HAS_HGB:
        # HistGradientBoosting handles NaNs natively; balance via sample_weight during fit
        return _HGB(
            loss="log_loss",
            learning_rate=0.06,
            max_iter=400,
            max_depth=None,
            l2_regularization=0.1,
            min_samples_leaf=20,
            early_stopping=False,
            random_state=seed,
        )
    else:
        # Fallback: GradientBoosting (requires imputation)
        return Pipeline([
            ("imp", SimpleImputer(strategy="median", add_indicator=True)),
            ("gb", _GBC(
                learning_rate=0.06,
                n_estimators=350,
                max_depth=3,
                random_state=seed,
            ))
        ])

def _predict_pos_proba(model, X):
    proba = model.predict_proba(X)
    # Determine index for class label 1
    idx = None
    if hasattr(model, "classes_"):
        classes = np.asarray(model.classes_)
        w = np.where(classes == 1)[0]
        if w.size > 0:
            idx = int(w[0])
    if idx is None:
        # Fall back to column 1 if binary, else last column
        if proba.shape[1] >= 2:
            idx = 1
        else:
            idx = 0
    return proba[:, idx]

def _find_best_threshold(y_true, proba):
    y_true = np.asarray(y_true)
    proba = np.asarray(proba)
    # Candidate thresholds: mixture of unique probs and a dense grid around [0,1]
    uniq = np.unique(proba)
    grid_a = np.linspace(0.0, 1.0, 201)
    qs = np.quantile(proba, np.linspace(0.0, 1.0, 201), interpolation="linear") if hasattr(np, 'quantile') else np.percentile(proba, np.linspace(0, 100, 201))
    cands = np.unique(np.clip(np.concatenate([uniq, grid_a, qs, np.array([0.5])]), 0.0, 1.0))

    best_thr = 0.5
    best_f1 = -1.0
    best_ba = -1.0
    for thr in cands:
        yp = (proba >= thr).astype(int)
        f1 = f1_score(y_true, yp, average="macro", zero_division=0)
        if f1 < best_f1 - 1e-12:
            continue
        ba = balanced_accuracy_score(y_true, yp)
        if (f1 > best_f1 + 1e-12) or (abs(f1 - best_f1) <= 1e-12 and ba > best_ba + 1e-12) or (abs(f1 - best_f1) <= 1e-12 and abs(ba - best_ba) <= 1e-12 and abs(thr - 0.5) < abs(best_thr - 0.5)):
            best_f1 = f1
            best_ba = ba
            best_thr = float(thr)
    return best_thr

# ---------------------- Main API ----------------------

def fit_predict(train_x, train_y, test_x):
    """
    Train an ensemble to predict spiny (1) vs aspiny (0) from 11 ephys features.
    Returns integer labels of shape (n_test,).
    """
    seed = 1337
    X = _to_numpy(train_x).astype(float)
    y = _to_numpy(train_y).astype(int)
    T = _to_numpy(test_x).astype(float)

    X = _clean_infs(X)
    T = _clean_infs(T)

    # Basic sanity: ensure binary labels
    uy = np.unique(y)
    if uy.size != 2:
        # Degenerate case: predict the only observed class
        return np.full(T.shape[0], int(uy[0]), dtype=int)

    # Define base models
    model_names = ["logreg", "hgb", "rf", "et"]
    def make_model(name, fold_seed):
        if name == "logreg":
            return _build_logreg(fold_seed)
        elif name == "hgb":
            return _build_hgb(fold_seed)
        elif name == "rf":
            return _build_rf(fold_seed)
        elif name == "et":
            return _build_et(fold_seed)
        else:
            raise ValueError("Unknown model name")

    # Stratified 5-fold OOF ensemble
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=seed)
    oof_ens = np.zeros(X.shape[0], dtype=float)
    test_ens_sum = np.zeros(T.shape[0], dtype=float)

    offsets = {"logreg": 0, "hgb": 1000, "rf": 2000, "et": 3000}

    for fold_idx, (tr_idx, va_idx) in enumerate(skf.split(X, y)):
        X_tr, X_va = X[tr_idx], X[va_idx]
        y_tr, y_va = y[tr_idx], y[va_idx]
        sw_tr = _balanced_sample_weight(y_tr)

        val_probs = []
        tst_probs = []
        for name in model_names:
            rs = seed + offsets[name] + fold_idx
            model = make_model(name, rs)
            # Fit with or without sample_weight depending on model
            if name == "hgb":
                # If fallback pipeline (GBC) is used, it still accepts sample_weight via .fit
                try:
                    model.fit(X_tr, y_tr, sample_weight=sw_tr)
                except TypeError:
                    model.fit(X_tr, y_tr)
            else:
                # Pipelines internally contain estimators with class_weight set
                try:
                    # Some tree estimators also accept sample_weight; we avoid double balancing
                    model.fit(X_tr, y_tr)
                except Exception:
                    model.fit(X_tr, y_tr)

            # Validation probabilities
            vp = _predict_pos_proba(model, X_va)
            val_probs.append(vp)
            # Test probabilities
            tp = _predict_pos_proba(model, T)
            tst_probs.append(tp)

        # Average across base models for this fold
        val_mean = np.mean(np.vstack(val_probs), axis=0)
        tst_mean = np.mean(np.vstack(tst_probs), axis=0)
        oof_ens[va_idx] = val_mean
        test_ens_sum += tst_mean

    # Aggregate test predictions across folds
    test_ens = test_ens_sum / skf.get_n_splits()

    # Tune threshold on OOF to maximize macro-F1; balanced accuracy as tie-breaker
    thr = _find_best_threshold(y, oof_ens)

    y_pred_test = (test_ens >= thr).astype(int)
    return y_pred_test
