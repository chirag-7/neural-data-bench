import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import RobustScaler, FunctionTransformer
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.linear_model import RidgeClassifier, LogisticRegression


def _clip_scaled(z):
    return np.clip(z, -8.0, 8.0)


def _features(x):
    x = np.asarray(x, dtype=np.float64)
    if x.ndim != 3 or x.shape[1:] != (136, 8):
        raise ValueError("Expected input shape (trials, 136, 8)")
    x = np.nan_to_num(x, copy=True, nan=0.0, posinf=2.0, neginf=-2.0)
    x = np.clip(x, -2.0, 2.0)

    # Interleaved 760/850-nm channels become measurement-pair x wavelength.
    od = x.reshape(x.shape[0], 68, 2, 8)

    bases = np.asarray([
        [1, 1, 1, 1, 1, 1, 1, 1],
        [-7, -5, -3, -1, 1, 3, 5, 7],
        [1, 1, 0, 0, 0, 0, -1, -1],
        [-0.45, -0.20, 0.25, 0.60, 0.70, 0.45, 0.05, -0.35]
    ], dtype=np.float64)
    bases /= np.sqrt(np.sum(bases * bases, axis=1, keepdims=True))
    proj = np.einsum("ncwt,kt->ncwk", od, bases, optimize=True)

    spatial_mean = od.mean(axis=1)
    spatial_std = od.std(axis=1)
    raw = np.concatenate([
        od.reshape(len(od), -1),
        proj.reshape(len(od), -1),
        spatial_mean.reshape(len(od), -1),
        spatial_std.reshape(len(od), -1)
    ], axis=1)

    # Sources 1--7 and 8--14 form equally sized, ordered cap halves.
    left = od[:, :34]
    right = od[:, 34:]
    hemi_diff = left - right
    hemi_proj = np.einsum("ncwt,kt->ncwk", hemi_diff, bases,
                          optimize=True)
    hemi = np.concatenate([
        hemi_diff.reshape(len(od), -1),
        hemi_proj.reshape(len(od), -1),
        left.mean(axis=1).reshape(len(od), -1),
        right.mean(axis=1).reshape(len(od), -1),
        spatial_mean.reshape(len(od), -1)
    ], axis=1)

    # Trial-local common-mode removal retains spatial and lateralized patterns.
    centered = od - np.median(od, axis=1, keepdims=True)
    centered_proj = np.einsum("ncwt,kt->ncwk", centered, bases,
                              optimize=True)
    centered_view = np.concatenate([
        centered.reshape(len(od), -1),
        centered_proj.reshape(len(od), -1),
        hemi_diff.reshape(len(od), -1)
    ], axis=1)
    return (raw, centered_view, hemi)


def _make_model(k, kind, strength):
    if kind == "ridge":
        clf = RidgeClassifier(alpha=strength, class_weight="balanced",
                              solver="lsqr", tol=1e-4)
    else:
        clf = LogisticRegression(
            C=strength, class_weight="balanced", solver="liblinear",
            penalty="l2", max_iter=1500, random_state=1729
        )
    return Pipeline([
        ("scale", RobustScaler(quantile_range=(10.0, 90.0))),
        ("clip", FunctionTransformer(_clip_scaled, validate=False)),
        ("select", SelectKBest(f_classif, k=k)),
        ("classify", clf)
    ])


def _balanced_accuracy(y, p):
    y = np.asarray(y)
    p = np.asarray(p)
    vals = []
    for c in (0, 1):
        m = (y == c)
        if np.any(m):
            vals.append(np.mean(p[m] == c))
    return float(np.mean(vals)) if vals else 0.0


def fit_predict(train_x, train_y, test_x):
    y = np.asarray(train_y).reshape(-1).astype(np.int64)
    if len(y) != len(train_x):
        raise ValueError("train_x and train_y lengths differ")
    if np.any((y != 0) & (y != 1)):
        raise ValueError("Labels must be encoded as 0 and 1")

    train_views = _features(train_x)
    test_views = _features(test_x)
    n = len(y)

    # The supplied 378 trials comprise seven consecutive 54-trial subjects.
    if n == 378:
        folds = [np.arange(i * 54, (i + 1) * 54) for i in range(7)]
    else:
        folds = [a for a in np.array_split(np.arange(n), 7) if len(a)]

    settings = [
        (64, "ridge", 3.0),
        (128, "ridge", 10.0),
        (256, "ridge", 30.0),
        (384, "ridge", 100.0),
        ("all", "ridge", 300.0),
        (192, "logistic", 0.05)
    ]
    specs = []
    qualities = []

    for view_id in range(3):
        xv = train_views[view_id]
        for k, kind, strength in settings:
            fold_scores = []
            for va in folds:
                keep = np.ones(n, dtype=bool)
                keep[va] = False
                model = _make_model(k, kind, strength)
                model.fit(xv[keep], y[keep])
                pred = model.predict(xv[va]).astype(np.int64)
                fold_scores.append(_balanced_accuracy(y[va], pred))
            specs.append((view_id, k, kind, strength))
            qualities.append(float(np.mean(fold_scores)))

    qualities = np.asarray(qualities)
    selected = []
    for view_id in range(3):
        ids = [i for i, s in enumerate(specs) if s[0] == view_id]
        selected.append(max(ids, key=lambda i: qualities[i]))

    useful = [i for i in selected if qualities[i] > 0.505]
    if not useful:
        useful = [int(np.argmax(qualities))]

    combined = np.zeros(len(test_x), dtype=np.float64)
    total_weight = 0.0
    for i in useful:
        view_id, k, kind, strength = specs[i]
        model = _make_model(k, kind, strength)
        model.fit(train_views[view_id], y)
        train_decision = np.asarray(
            model.decision_function(train_views[view_id]), dtype=np.float64
        ).reshape(-1)
        test_decision = np.asarray(
            model.decision_function(test_views[view_id]), dtype=np.float64
        ).reshape(-1)
        scale = float(np.std(train_decision))
        if not np.isfinite(scale) or scale < 1e-8:
            scale = 1.0
        weight = max(qualities[i] - 0.5, 0.005) ** 2
        combined += weight * test_decision / scale
        total_weight += weight

    if total_weight == 0.0:
        return np.zeros(len(test_x), dtype=np.int64)
    return (combined >= 0.0).astype(np.int64)
