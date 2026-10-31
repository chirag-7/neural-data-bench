import numpy as np
from scipy.optimize import minimize
from scipy.special import expit
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler


def _features(x):
    x = np.nan_to_num(np.asarray(x, dtype=float), nan=0.0, posinf=0.0, neginf=0.0)
    l, r, p = x[:, 0], x[:, 1], x[:, 2]
    c, f = x[:, 3:8], x[:, 8:13]
    d = r - l
    a = np.abs(d)
    prior = np.log(np.clip(p, 0.01, 0.99) / np.clip(1.0 - p, 0.01, 0.99))
    cf = c * f
    win = c * (f > 0)
    lose = c * (f < 0)
    w = np.array([1.0, 0.65, 0.42, 0.27, 0.18])
    hc = (c * w).sum(axis=1)
    hr = (cf * w).sum(axis=1)
    hw = (win * w).sum(axis=1)
    hl = (lose * w).sum(axis=1)
    root = np.sign(d) * np.sqrt(a)
    logd = np.sign(d) * np.log1p(16.0 * a)

    z = [l, r, p, prior, d, a, root, logd,
         np.sqrt(r) - np.sqrt(l), r ** 0.25 - l ** 0.25,
         r ** 2 - l ** 2, c, f, cf, win, lose,
         (c == 0).astype(float), (f == 0).astype(float),
         hc, hr, hw, hl]
    for k in (0.03, 0.1, 0.25, 0.5):
        z.extend([np.maximum(d - k, 0), np.minimum(d + k, 0)])
    for h in (c, cf, win, lose):
        for j in (2, 3, 5):
            z.append(h[:, :j].mean(axis=1))
    z.extend([c[:, 0] * c[:, 1], c[:, 1] * c[:, 2],
              f[:, 0] * f[:, 1], c[:, 0] * c[:, 1] * c[:, 2]])
    for h in (hc, hr, c[:, 0], cf[:, 0]):
        z.extend([h * d, h * root, h * prior])
    z.extend([d * prior, root * prior, a * prior])
    linear = np.column_stack(z)
    tree = np.column_stack([x, d, a, root, logd, cf, win, lose,
                            hc, hr, hw, hl, prior])
    return linear, tree


def fit_predict(train_x, train_y, test_x, train_groups):
    y = np.asarray(train_y, dtype=int).ravel()
    linear, tree = _features(train_x)
    test_linear, test_tree = _features(test_x)
    _, group = np.unique(np.asarray(train_groups).ravel(), return_inverse=True)
    group_count = np.bincount(group)
    weight = 1.0 / group_count[group]
    weight *= len(y) / weight.sum()

    rng = np.random.RandomState(2026)
    permutation = rng.permutation(len(group_count))
    group_fold = np.empty(len(group_count), dtype=int)
    group_fold[permutation] = np.arange(len(group_count)) % 4
    fold = group_fold[group]

    cs = (0.04, 0.4, 4.0)
    oof_linear = np.empty((len(cs), len(y)), dtype=float)
    oof_tree = np.empty(len(y), dtype=float)
    tree_args = dict(max_iter=130, learning_rate=0.045,
                     max_leaf_nodes=7, min_samples_leaf=60,
                     l2_regularization=8.0, early_stopping=False,
                     random_state=2026)

    for k in range(4):
        tr = np.flatnonzero(fold != k)
        va = np.flatnonzero(fold == k)
        sw = weight[tr] * (len(tr) / weight[tr].sum())
        scaler = StandardScaler().fit(linear[tr])
        a = scaler.transform(linear[tr])
        b = scaler.transform(linear[va])
        for j, reg in enumerate(cs):
            model = LogisticRegression(C=reg, solver='lbfgs', max_iter=350)
            model.fit(a, y[tr], sample_weight=sw)
            oof_linear[j, va] = model.predict_proba(b)[:, 1]
        model = HistGradientBoostingClassifier(**tree_args)
        model.fit(tree[tr], y[tr], sample_weight=sw)
        oof_tree[va] = model.predict_proba(tree[va])[:, 1]

    def score(prob):
        q = np.clip(prob, 1e-6, 1.0 - 1e-6)
        return np.average(-y * np.log(q) - (1 - y) * np.log1p(-q),
                          weights=weight)

    best = int(np.argmin([score(p) for p in oof_linear]))
    blends = np.linspace(0.0, 1.0, 6)
    blend_scores = [score((1.0 - t) * oof_linear[best] + t * oof_tree)
                    for t in blends]
    t = float(blends[int(np.argmin(blend_scores))])
    oof = np.clip((1.0 - t) * oof_linear[best] + t * oof_tree,
                  1e-6, 1.0 - 1e-6)
    logits = np.log(oof / (1.0 - oof))

    def calibration_loss(params):
        slope, intercept = params
        p = expit(slope * logits + intercept)
        return score(p) + 0.002 * ((slope - 1.0) ** 2 + intercept ** 2)

    calibration = minimize(calibration_loss, [1.0, 0.0], method='L-BFGS-B',
                           bounds=[(0.65, 1.35), (-0.4, 0.4)]).x

    scaler = StandardScaler().fit(linear)
    model = LogisticRegression(C=cs[best], solver='lbfgs', max_iter=350)
    model.fit(scaler.transform(linear), y, sample_weight=weight)
    prediction = (1.0 - t) * model.predict_proba(
        scaler.transform(test_linear))[:, 1]
    if t > 0.0:
        boosted = HistGradientBoostingClassifier(**tree_args)
        boosted.fit(tree, y, sample_weight=weight)
        prediction += t * boosted.predict_proba(test_tree)[:, 1]
    prediction = np.clip(prediction, 1e-6, 1.0 - 1e-6)
    test_logits = np.log(prediction / (1.0 - prediction))
    prediction = expit(calibration[0] * test_logits + calibration[1])
    return np.clip(np.nan_to_num(prediction, nan=0.5), 1e-6, 1.0 - 1e-6)
