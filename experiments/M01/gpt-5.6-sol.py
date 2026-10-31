import numpy as np
from scipy.optimize import minimize
from scipy.special import expit
from sklearn.model_selection import GroupKFold
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier, ExtraTreesClassifier


def _features(x):
    x = np.asarray(x, dtype=np.float64)
    x = np.nan_to_num(x, nan=0.0, posinf=1.0, neginf=-1.0)
    l, r, p = x[:, 0], x[:, 1], x[:, 2]
    c, f = x[:, 3:8], x[:, 8:13]

    e = r - l
    total = r + l
    sqe = np.sqrt(np.maximum(r, 0.0)) - np.sqrt(np.maximum(l, 0.0))
    loge = np.log1p(12.0 * np.maximum(r, 0.0)) - np.log1p(12.0 * np.maximum(l, 0.0))
    pc = p - 0.5
    pp = np.clip(p, 0.01, 0.99)
    plog = np.log(pp / (1.0 - pp))

    stim = np.column_stack([
        e, sqe, loge, total, np.abs(e), e * np.abs(e), e ** 3,
        r * l, np.maximum(r, l), (r > 0), (l > 0),
        pc, plog, pc ** 2, plog * e, plog * sqe, plog * loge,
        pc * total, (p < 0.4), (p > 0.6)
    ]).astype(np.float64)

    knots = np.array([-0.75, -0.4, -0.2, -0.1, 0.0, 0.1, 0.2, 0.4, 0.75])
    hinges_e = np.maximum(e[:, None] - knots[None, :], 0.0)
    hinges_s = np.maximum(sqe[:, None] - knots[None, :], 0.0)

    rewarded = (f > 0).astype(np.float64)
    error = (f < 0).astype(np.float64)
    valid_choice = (c != 0).astype(np.float64)
    cf = c * f
    win_choice = c * rewarded
    lose_choice = c * error

    summaries = []
    for decay in (0.25, 0.5, 0.75, 1.0):
        w = decay ** np.arange(5, dtype=np.float64)
        for h in (c, f, cf, win_choice, lose_choice, valid_choice):
            summaries.append((h * w).sum(axis=1, keepdims=True))
    summary = np.hstack(summaries)

    pair = np.hstack([
        c[:, :-1] * c[:, 1:],
        f[:, :-1] * f[:, 1:],
        c[:, :-1] - c[:, 1:],
        win_choice[:, :-1] * win_choice[:, 1:]
    ])

    interactions = np.hstack([
        c * e[:, None], c * sqe[:, None], c * plog[:, None],
        cf * e[:, None], cf * plog[:, None],
        win_choice * e[:, None], lose_choice * e[:, None],
        summary[:, :8] * e[:, None], summary[:, :8] * plog[:, None]
    ])

    return np.hstack([
        x, stim, hinges_e, hinges_s, cf, win_choice, lose_choice,
        valid_choice, rewarded, error, summary, pair, interactions
    ]).astype(np.float64)


def _mouse_weights(groups):
    groups = np.asarray(groups).ravel()
    _, inv, counts = np.unique(groups, return_inverse=True, return_counts=True)
    w = 1.0 / counts[inv].astype(np.float64)
    return w * (len(w) / w.sum())


def _make_model(spec, seed):
    kind, arg = spec
    if kind == "lr":
        return Pipeline([
            ("scale", StandardScaler()),
            ("model", LogisticRegression(
                C=arg, solver="lbfgs", max_iter=700, tol=1e-7,
                random_state=seed
            ))
        ])
    if kind == "hgb":
        leaves, min_leaf, reg = arg
        return HistGradientBoostingClassifier(
            loss="log_loss", learning_rate=0.045, max_iter=170,
            max_leaf_nodes=leaves, min_samples_leaf=min_leaf,
            l2_regularization=reg, early_stopping=False,
            random_state=seed
        )
    return ExtraTreesClassifier(
        n_estimators=280, criterion="entropy", max_features=0.75,
        min_samples_leaf=arg, max_depth=None, bootstrap=False,
        n_jobs=1, random_state=seed
    )


def _fit(model, spec, z, y, weights):
    if spec[0] == "lr":
        model.fit(z, y, model__sample_weight=weights)
    else:
        model.fit(z, y, sample_weight=weights)
    return model


def _p1(model, z):
    classes = np.asarray(model.classes_)
    j = int(np.flatnonzero(classes == 1)[0])
    return np.asarray(model.predict_proba(z)[:, j], dtype=np.float64)


def fit_predict(train_x, train_y, test_x, train_groups):
    y = np.asarray(train_y, dtype=np.int64).ravel()
    groups = np.asarray(train_groups).ravel()
    z = _features(train_x)
    ztest = _features(test_x)

    specs = [
        ("lr", 0.03),
        ("lr", 0.12),
        ("lr", 0.50),
        ("hgb", (7, 38, 3.0)),
        ("hgb", (15, 26, 5.0)),
        ("et", 12)
    ]
    n_models = len(specs)
    oof = np.zeros((len(y), n_models), dtype=np.float64)
    n_splits = min(5, len(np.unique(groups)))
    splitter = GroupKFold(n_splits=n_splits)

    for fold, (tr, va) in enumerate(splitter.split(z, y, groups)):
        sw = _mouse_weights(groups[tr])
        for j, spec in enumerate(specs):
            model = _make_model(spec, 1701 + 37 * fold + j)
            _fit(model, spec, z[tr], y[tr], sw)
            oof[va, j] = _p1(model, z[va])

    oof = np.clip(oof, 1e-6, 1.0 - 1e-6)
    vw = _mouse_weights(groups)
    vw /= vw.sum()

    def blend_loss(w):
        q = np.clip(oof.dot(w), 1e-7, 1.0 - 1e-7)
        ll = -np.sum(vw * (y * np.log(q) + (1 - y) * np.log1p(-q)))
        return ll + 2e-4 * np.dot(w, w)

    single_losses = np.array([blend_loss(np.eye(n_models)[j]) for j in range(n_models)])
    starts = [np.full(n_models, 1.0 / n_models), np.eye(n_models)[np.argmin(single_losses)]]
    best_w, best_obj = starts[0], np.inf
    for start in starts:
        res = minimize(
            blend_loss, start, method="SLSQP",
            bounds=[(0.0, 1.0)] * n_models,
            constraints={"type": "eq", "fun": lambda w: w.sum() - 1.0},
            options={"maxiter": 250, "ftol": 1e-10, "disp": False}
        )
        if res.success and np.isfinite(res.fun) and res.fun < best_obj:
            best_w, best_obj = res.x, res.fun
    best_w = np.maximum(best_w, 0.0)
    best_w /= best_w.sum()

    base_oof = np.clip(oof.dot(best_w), 1e-6, 1.0 - 1e-6)
    base_logit = np.log(base_oof / (1.0 - base_oof))

    def calibration_loss(ab):
        q = expit(ab[0] * base_logit + ab[1])
        q = np.clip(q, 1e-7, 1.0 - 1e-7)
        ll = -np.sum(vw * (y * np.log(q) + (1 - y) * np.log1p(-q)))
        return ll + 1e-3 * ((ab[0] - 1.0) ** 2 + ab[1] ** 2)

    cal = minimize(
        calibration_loss, np.array([1.0, 0.0]), method="L-BFGS-B",
        bounds=[(0.65, 1.40), (-0.30, 0.30)],
        options={"maxiter": 150, "ftol": 1e-12}
    )
    a, b = cal.x if cal.success and np.all(np.isfinite(cal.x)) else (1.0, 0.0)

    full_sw = _mouse_weights(groups)
    test_predictions = np.zeros((len(ztest), n_models), dtype=np.float64)
    for j, spec in enumerate(specs):
        model = _make_model(spec, 9103 + j)
        _fit(model, spec, z, y, full_sw)
        test_predictions[:, j] = _p1(model, ztest)

    base_test = np.clip(test_predictions.dot(best_w), 1e-6, 1.0 - 1e-6)
    result = expit(a * np.log(base_test / (1.0 - base_test)) + b)
    return np.clip(np.nan_to_num(result, nan=0.5, posinf=1.0, neginf=0.0), 1e-6, 1.0 - 1e-6)
