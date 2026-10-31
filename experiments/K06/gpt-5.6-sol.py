import numpy as np
from sklearn.svm import SVC
from sklearn.ensemble import ExtraTreesClassifier

_SEED = 20261031


def _unique(a):
    return list(dict.fromkeys(np.asarray(a).tolist()))


def _features(x, mode):
    x = np.asarray(x, dtype=float)
    s = x[:, :6]
    miss = (~np.isfinite(s)).astype(float)
    w = x[:, 6:]
    w = np.where(np.isfinite(w), w, 0.0)
    n = len(w)
    t = np.linspace(-0.5, 1.5, 81)
    z = w - np.mean(w[:, :10], axis=1, keepdims=True)
    d = np.diff(z, axis=1) / (t[1] - t[0])
    rows = np.arange(n)
    imin = np.argmin(z, axis=1)
    imax = np.argmax(z, axis=1)
    ipre = np.empty(n, dtype=int)
    ipost = np.empty(n, dtype=int)
    for i in range(n):
        ipre[i] = int(np.argmax(z[i, :imin[i] + 1]))
        ipost[i] = imin[i] + int(np.argmax(z[i, imin[i]:]))

    neg = np.maximum(-z, 0.0)
    pos = np.maximum(z, 0.0)
    ns = np.sum(neg, axis=1) + 1e-12
    ps = np.sum(pos, axis=1) + 1e-12
    nmu = np.sum(neg * t, axis=1) / ns
    pmu = np.sum(pos * t, axis=1) / ps
    nsd = np.sqrt(np.sum(neg * (t - nmu[:, None]) ** 2, axis=1) / ns)
    psd = np.sqrt(np.sum(pos * (t - pmu[:, None]) ** 2, axis=1) / ps)

    morph = np.column_stack((
        z[rows, imin], z[rows, imax], t[imin], t[imax],
        z[rows, ipre], t[ipre], z[rows, ipost], t[ipost],
        t[ipost] - t[imin], z[rows, ipost] - z[rows, imin],
        np.min(d, axis=1), np.max(d, axis=1),
        np.mean(np.abs(z), axis=1), np.sqrt(np.mean(z * z, axis=1)),
        np.mean(z[:, :20], axis=1), np.mean(z[:, 20:40], axis=1),
        np.mean(z[:, 40:60], axis=1), np.mean(z[:, 60:], axis=1),
        nmu, nsd, pmu, psd,
        np.sum(neg, axis=1), np.sum(pos, axis=1)
    ))

    if mode == 'scalar':
        return np.hstack((s, miss))
    if mode == 'morph':
        return np.hstack((s, miss, morph))
    if mode == 'coarse':
        return np.hstack((s, miss, z[:, ::4], morph))
    if mode == 'shape':
        return np.hstack((s, miss, z[:, ::3], d[:, ::3], morph))
    return np.hstack((s, miss, w, morph))


def _prep_fit(a, robust):
    a = np.asarray(a, dtype=float)
    med = np.nanmedian(a, axis=0)
    med = np.where(np.isfinite(med), med, 0.0)
    b = np.where(np.isfinite(a), a, med)
    if robust:
        center = np.median(b, axis=0)
        q25, q75 = np.percentile(b, [25.0, 75.0], axis=0)
        scale = q75 - q25
    else:
        center = np.mean(b, axis=0)
        scale = np.std(b, axis=0)
    scale = np.where(np.isfinite(scale) & (scale > 1e-9), scale, 1.0)
    return np.clip((b - center) / scale, -10.0, 10.0), (med, center, scale)


def _prep_apply(a, state):
    med, center, scale = state
    a = np.asarray(a, dtype=float)
    b = np.where(np.isfinite(a), a, med)
    return np.clip((b - center) / scale, -10.0, 10.0)


def _weights(y, groups):
    y = np.asarray(y, dtype=int)
    groups = np.asarray(groups)
    gids = _unique(groups)
    group_class = {}
    for g in gids:
        q = y[groups == g]
        group_class[g] = int(np.mean(q) >= 0.5)
    ng = {
        c: max(1, sum(group_class[g] == c for g in gids))
        for c in (0, 1)
    }
    out = np.empty(len(y), dtype=float)
    for g in gids:
        mask = groups == g
        out[mask] = 1.0 / (ng[group_class[g]] * np.sum(mask))
    return out * (len(out) / np.sum(out))


def _metric(y, pred, groups):
    y = np.asarray(y, dtype=int)
    pred = np.asarray(pred, dtype=int)
    groups = np.asarray(groups)
    class_scores = []
    for c in (0, 1):
        mouse_scores = []
        for g in _unique(groups):
            mask = groups == g
            if np.any(mask) and int(np.mean(y[mask]) >= 0.5) == c:
                mouse_scores.append(float(np.mean(pred[mask] == y[mask])))
        if mouse_scores:
            class_scores.append(float(np.mean(mouse_scores)))
    return float(np.mean(class_scores)) if class_scores else 0.0


def _make_model(spec, seed):
    if spec['kind'] == 'rbf':
        return SVC(C=spec['c'], kernel='rbf', gamma='scale',
                   cache_size=256, tol=1e-4, shrinking=True,
                   random_state=seed)
    if spec['kind'] == 'linear':
        return SVC(C=spec['c'], kernel='linear', cache_size=256,
                   tol=1e-4, shrinking=True, random_state=seed)
    return ExtraTreesClassifier(
        n_estimators=350, criterion='gini', max_features=spec['mf'],
        min_samples_leaf=spec['leaf'], bootstrap=False,
        random_state=seed, n_jobs=1
    )


def _candidates():
    out = []
    reps = ('scalar', 'morph', 'coarse', 'shape', 'full')
    for rep in reps:
        for c in (0.1, 1.0, 10.0, 100.0):
            out.append({'rep': rep, 'scale': 'std', 'kind': 'rbf', 'c': c})
        for c in (1.0, 10.0):
            out.append({'rep': rep, 'scale': 'robust', 'kind': 'rbf', 'c': c})
    for rep in ('morph', 'shape', 'full'):
        for c in (0.01, 0.1, 1.0):
            out.append({'rep': rep, 'scale': 'std', 'kind': 'linear', 'c': c})
    for rep in ('morph', 'shape', 'full'):
        for mf, leaf in (('sqrt', 1), ('sqrt', 2), (0.5, 2)):
            out.append({'rep': rep, 'scale': 'std', 'kind': 'trees',
                        'mf': mf, 'leaf': leaf})
    return out


def fit_predict(train_x, train_y, test_x, train_groups):
    x = np.asarray(train_x, dtype=float)
    y = np.asarray(train_y).reshape(-1).astype(int)
    tx = np.asarray(test_x, dtype=float)
    groups = np.asarray(train_groups['group_ids'])
    fold = np.asarray(train_groups['cv_fold'])
    folds = _unique(fold)
    specs = _candidates()
    cache_train = {r: _features(x, r) for r in
                   ('scalar', 'morph', 'coarse', 'shape', 'full')}
    cache_test = {r: _features(tx, r) for r in cache_train}
    results = []

    for j, spec in enumerate(specs):
        a = cache_train[spec['rep']]
        oof = np.empty(len(y), dtype=int)
        fold_scores = []
        for k, f in enumerate(folds):
            va = fold == f
            tr = ~va
            atr, state = _prep_fit(a[tr], spec['scale'] == 'robust')
            ava = _prep_apply(a[va], state)
            model = _make_model(spec, _SEED + 97 * j + k)
            model.fit(atr, y[tr], sample_weight=_weights(y[tr], groups[tr]))
            oof[va] = model.predict(ava).astype(int)
            fold_scores.append(_metric(y[va], oof[va], groups[va]))
        score = _metric(y, oof, groups)
        stability = float(np.std(fold_scores))
        results.append((score, stability, j, spec))

    per_rep = []
    for rep in ('scalar', 'morph', 'coarse', 'shape', 'full'):
        pool = [r for r in results if r[3]['rep'] == rep]
        pool.sort(key=lambda r: (r[0] - 0.01 * r[1], r[0], -r[2]),
                  reverse=True)
        per_rep.append(pool[0])
    per_rep.sort(key=lambda r: (r[0] - 0.01 * r[1], r[0]), reverse=True)
    best_score = per_rep[0][0]
    chosen = [r for r in per_rep if r[0] >= best_score - 0.04][:4]

    votes = np.zeros(len(tx), dtype=float)
    total = 0.0
    best_pred = None
    for rank, (score, stability, j, spec) in enumerate(chosen):
        atr, state = _prep_fit(cache_train[spec['rep']],
                               spec['scale'] == 'robust')
        ate = _prep_apply(cache_test[spec['rep']], state)
        model = _make_model(spec, _SEED + 10000 + j)
        model.fit(atr, y, sample_weight=_weights(y, groups))
        pred = model.predict(ate).astype(int)
        if rank == 0:
            best_pred = pred
        weight = float(np.exp(20.0 * (score - best_score)) / (1.0 + stability))
        votes += weight * pred
        total += weight

    out = (votes > 0.5 * total).astype(int)
    ties = np.isclose(votes, 0.5 * total, atol=1e-12, rtol=0.0)
    if np.any(ties):
        out[ties] = best_pred[ties]
    return out
