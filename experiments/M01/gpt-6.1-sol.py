import numpy as np
from scipy.optimize import minimize
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier


def fit_predict(train_x, train_y, test_x, train_groups):
    def clean(x):
        a = np.asarray(x, dtype=np.float64).copy()
        a = np.nan_to_num(a, nan=0.0, posinf=0.0, neginf=0.0)
        a[:, :3] = np.clip(a[:, :3], 0.0, 1.0)
        a[:, 3:] = np.clip(np.rint(a[:, 3:]), -1.0, 1.0)
        return a

    def features(a):
        left, right, prior = a[:, 0], a[:, 1], a[:, 2]
        c, f = a[:, 3:8], a[:, 8:13]
        cf = c * f
        sl, sr = np.sqrt(left), np.sqrt(right)
        d = sr - sl
        strength = np.maximum(sl, sr)
        b = 2.0 * prior - 1.0
        pp = np.clip(prior, 0.001, 0.999)
        parts = [a, cf, (c == 0).astype(float), (f == 0).astype(float)]
        for power in (0.25, 0.5, 2.0):
            l, r = left ** power, right ** power
            parts.append(np.column_stack((r - l, r + l)))
        parts.append(np.column_stack((
            d, np.abs(d), strength, np.minimum(sl, sr),
            (strength == 0).astype(float),
            ((left > 0) & (right > 0)).astype(float),
            b, np.log(pp / (1.0 - pp)), b * b
        )))
        for decay in (0.4, 0.75, 1.0):
            w = decay ** np.arange(5, dtype=float)
            w /= w.sum()
            parts.append(np.column_stack((c @ w, cf @ w, f @ w)))
        parts.extend((c[:, :-1] * c[:, 1:], f[:, :-1] * f[:, 1:]))
        same = (c == c[:, :1]) & (c[:, :1] != 0)
        run = np.cumprod(same.astype(float), axis=1).sum(axis=1)
        recent = np.zeros(len(a))
        for lag in range(4, -1, -1):
            recent = np.where(c[:, lag] != 0, c[:, lag], recent)
        parts.append(np.column_stack((
            run, recent, np.abs(c.mean(axis=1)),
            np.abs(cf.mean(axis=1))
        )))
        tree = np.column_stack(parts)
        extra = []
        for knot in (0.15, 0.35, 0.6, 0.85):
            hl = np.maximum(sl - knot, 0.0)
            hr = np.maximum(sr - knot, 0.0)
            extra.append(np.column_stack((hr - hl, hr + hl)))
        history = np.column_stack((c, cf))
        extra.extend((
            b[:, None] * history,
            strength[:, None] * history,
            d[:, None] * f,
            np.column_stack((
                b * strength, b * strength ** 2, b * np.abs(d),
                d * b, d * c[:, 0] * c[:, 1],
                d * (f[:, 0] == -1)
            ))
        ))
        linear = np.column_stack([tree] + extra)
        return linear, tree

    y = np.asarray(train_y, dtype=int).reshape(-1)
    test = np.asarray(test_x)
    if len(test) == 0:
        return np.empty(0, dtype=float)
    _, group = np.unique(np.asarray(train_groups).reshape(-1), return_inverse=True)
    ng = int(group.max()) + 1
    counts = np.bincount(group)
    weights = 1.0 / counts[group]
    weights *= len(y) / weights.sum()
    prevalence = float(np.average(y, weights=weights))
    if np.unique(y).size < 2 or ng < 2:
        return np.full(len(test), np.clip(prevalence, 1e-6, 1 - 1e-6))

    linear, tree = features(clean(train_x))
    test_linear, test_tree = features(clean(test_x))
    cs = (0.015, 0.15, 1.5)
    tree_specs = (
        dict(max_iter=180, learning_rate=0.06, max_leaf_nodes=7,
             max_depth=3, min_samples_leaf=80, l2_regularization=15.0),
        dict(max_iter=200, learning_rate=0.045, max_leaf_nodes=15,
             max_depth=4, min_samples_leaf=65, l2_regularization=25.0)
    )

    def local_weights(indices):
        cnt = np.bincount(group[indices], minlength=ng)
        w = 1.0 / cnt[group[indices]]
        return w * (len(indices) / w.sum())

    def logistic(cvalue):
        return LogisticRegression(
            C=cvalue, solver='lbfgs', max_iter=300,
            tol=1e-5, random_state=1729
        )

    def booster(spec):
        return HistGradientBoostingClassifier(
            loss='log_loss', max_bins=63, early_stopping=False,
            random_state=1729, **spec
        )

    rng = np.random.RandomState(1729)
    nf = min(4, ng)
    fold_of_group = np.empty(ng, dtype=int)
    fold_of_group[rng.permutation(ng)] = np.arange(ng) % nf
    oof = np.zeros((len(y), 6), dtype=float)
    oof[:, 5] = 0.5
    for fold in range(nf):
        va = np.flatnonzero(fold_of_group[group] == fold)
        tr = np.flatnonzero(fold_of_group[group] != fold)
        w = local_weights(tr)
        if np.unique(y[tr]).size < 2:
            oof[va, :5] = np.average(y[tr], weights=w)
            continue
        scaler = StandardScaler()
        ztr = scaler.fit_transform(linear[tr])
        zva = scaler.transform(linear[va])
        for j, cv in enumerate(cs):
            model = logistic(cv)
            model.fit(ztr, y[tr], sample_weight=w)
            oof[va, j] = model.predict_proba(zva)[:, 1]
        for j, spec in enumerate(tree_specs):
            model = booster(spec)
            model.fit(tree[tr], y[tr], sample_weight=w)
            oof[va, 3 + j] = model.predict_proba(tree[va])[:, 1]

    oof = np.clip(oof, 1e-6, 1.0 - 1e-6)
    score_weights = weights / weights.sum()
    anchor = np.array([0.20, 0.25, 0.15, 0.25, 0.15, 0.0])

    def objective(mix):
        p = np.clip(oof @ mix, 1e-8, 1.0 - 1e-8)
        loss = -np.sum(score_weights * (y * np.log(p) +
                                      (1 - y) * np.log1p(-p)))
        residual = score_weights * (p - y) / (p * (1.0 - p))
        penalty = 0.002 * np.sum((mix - anchor) ** 2)
        gradient = oof.T @ residual + 0.004 * (mix - anchor)
        return loss + penalty, gradient

    result = minimize(
        objective, anchor, jac=True, method='SLSQP',
        bounds=[(0.0, 1.0)] * 5 + [(0.0, 0.08)],
        constraints=[dict(type='eq', fun=lambda v: v.sum() - 1.0,
                          jac=lambda v: np.ones_like(v))],
        options=dict(maxiter=100, ftol=1e-10)
    )
    mix = result.x if result.success and np.all(np.isfinite(result.x)) else anchor
    mix = np.maximum(mix, 0.0)
    mix /= mix.sum()

    prediction = np.full(len(test), 0.5 * mix[5], dtype=float)
    scaler = StandardScaler()
    ztrain = scaler.fit_transform(linear)
    ztest = scaler.transform(test_linear)
    for j, cv in enumerate(cs):
        if mix[j] > 1e-8:
            model = logistic(cv)
            model.fit(ztrain, y, sample_weight=weights)
            prediction += mix[j] * model.predict_proba(ztest)[:, 1]
    for j, spec in enumerate(tree_specs):
        if mix[3 + j] > 1e-8:
            model = booster(spec)
            model.fit(tree, y, sample_weight=weights)
            prediction += mix[3 + j] * model.predict_proba(test_tree)[:, 1]
    prediction = np.nan_to_num(prediction, nan=prevalence, posinf=1.0, neginf=0.0)
    return np.clip(prediction, 1e-6, 1.0 - 1e-6)
