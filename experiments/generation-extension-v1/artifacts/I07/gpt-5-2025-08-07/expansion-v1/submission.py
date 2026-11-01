import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.svm import LinearSVC
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import balanced_accuracy_score
from sklearn.pipeline import Pipeline
from sklearn.base import clone
import gc

SEED = 0


def _compute_features(X):
    """Compute deterministic features from optical-density input.
    X: (n_trials, 136, 8) float32/float64
    Returns: features array (n_trials, n_features) float64
    Assumes channels alternate [.. 760, 850, 760, 850, ..] as provided.
    """
    X = np.asarray(X, dtype=np.float64)
    n, C, T = X.shape
    # Base flattened OD features
    base_flat = X.reshape(n, C * T)

    # Wavelength-pair features (assuming even idx=760, odd idx=850)
    x760 = X[:, 0::2, :]
    x850 = X[:, 1::2, :]
    pairs = x760.shape[1]
    diff = x850 - x760  # 850 - 760
    summ = x850 + x760  # 850 + 760

    diff_flat = diff.reshape(n, pairs * T)
    summ_flat = summ.reshape(n, pairs * T)

    # Temporal summaries
    # Time axis centered for slope
    t = np.arange(T, dtype=np.float64)
    tc = t - t.mean()
    denom = np.sum(tc * tc) if T > 1 else 1.0

    # Per-pair difference temporal summaries
    early_mean = diff[:, :, :max(1, T // 2)].mean(axis=2)  # first 4 bins (3–6 s) when T=8
    late_mean = diff[:, :, max(1, T // 2):].mean(axis=2)   # last 4 bins (7–11 s) when T=8
    dle = late_mean - early_mean
    diff_slope = (diff * tc[None, None, :]).sum(axis=2) / denom

    # Per-channel OD slope across time
    base_slope = (X * tc[None, None, :]).sum(axis=2) / denom

    # Global time-wise means (OD and pair-diff)
    g_time_mean = X.mean(axis=1)            # (n, T)
    gd_time_mean = diff.mean(axis=1)        # (n, T)

    feats = [
        base_flat,
        diff_flat,
        summ_flat,
        early_mean, late_mean, dle,
        diff_slope,
        base_slope,
        g_time_mean, gd_time_mean,
    ]
    F = np.concatenate([f.reshape(n, -1) for f in feats], axis=1)
    return F


def _build_pipeline(pca_dim, clf_kind, C):
    steps = []
    steps.append(("scaler", StandardScaler(with_mean=True, with_std=True)))
    if pca_dim is not None:
        steps.append(("pca", PCA(n_components=int(pca_dim), svd_solver="auto", whiten=False, random_state=SEED)))
    # classifier
    if clf_kind == 'svc':
        clf = LinearSVC(C=float(C), class_weight='balanced', tol=1e-4, max_iter=5000, random_state=SEED)
    elif clf_kind == 'logreg':
        clf = LogisticRegression(C=float(C), penalty='l2', solver='lbfgs', class_weight='balanced', max_iter=2000, n_jobs=None)
    else:
        raise ValueError("Unknown clf_kind")
    steps.append(("clf", clf))
    return Pipeline(steps)


def _cv_select_model(X, y):
    # Small, deterministic grid
    dims = [64, 128]
    clf_grid = [
        ("svc", 0.5),
        ("svc", 1.0),
        ("logreg", 0.5),
        ("logreg", 1.0),
    ]
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)

    best_score = -np.inf
    best_cfg = None
    for dim in dims:
        for kind, C in clf_grid:
            pipe = _build_pipeline(dim, kind, C)
            scores = []
            for tr, va in skf.split(X, y):
                p = clone(pipe)
                p.fit(X[tr], y[tr])
                yp = p.predict(X[va])
                # Ensure integer labels 0/1
                yp = np.asarray(yp).astype(int)
                scores.append(balanced_accuracy_score(y[va], yp))
            mean_score = float(np.mean(scores))
            # Tie-breaker preference: larger dim, then svc
            if (mean_score > best_score) or (
                np.isclose(mean_score, best_score) and (
                    (dim > (best_cfg[0] if best_cfg else -1)) or (
                        (dim == (best_cfg[0] if best_cfg else -1)) and (kind == 'svc')
                    )
                )
            ):
                best_score = mean_score
                best_cfg = (dim, kind, C)
    return best_cfg, best_score


def fit_predict(train_x, train_y, test_x):
    """Train on train_x/train_y and return integer predictions for test_x.
    Inputs:
      - train_x: np.ndarray, shape (n_train, 136, 8)
      - train_y: np.ndarray, shape (n_train,)
      - test_x: np.ndarray, shape (n_test, 136, 8)
    Output:
      - np.ndarray of int, shape (n_test,)
    """
    # Compute features
    Xtr = _compute_features(train_x)
    Xte = _compute_features(test_x)
    y = np.asarray(train_y).astype(int)

    # Model selection via balanced-accuracy CV
    (best_dim, best_kind, best_C), _ = _cv_select_model(Xtr, y)

    # Fit final model on all training data
    final_pipe = _build_pipeline(best_dim, best_kind, best_C)
    final_pipe.fit(Xtr, y)

    # Predict on test set
    y_pred = final_pipe.predict(Xte)
    y_pred = np.asarray(y_pred).astype(int).ravel()

    # Housekeeping
    del Xtr, Xte
    gc.collect()

    return y_pred
