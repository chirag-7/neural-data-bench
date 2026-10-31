import numpy as np
from scipy import linalg, sparse
from sklearn.linear_model import LogisticRegression


def fit_predict(train_x, train_y, test_x, train_groups):
    def dense(a):
        if sparse.issparse(a):
            a = a.toarray()
        return np.asarray(a, dtype=np.float64)

    x = dense(train_x)
    xt = dense(test_x)
    y = np.asarray(train_y, dtype=np.int64).reshape(-1)
    groups = np.asarray(train_groups).reshape(-1)
    donors = np.unique(groups)
    if len(donors) < 2:
        raise ValueError('Donor-held-out validation requires at least two donors.')
    bases = [('linear', r) for r in (0.001, 0.01, 0.1)]
    bases += [('lda', s) for s in (0.05, 0.2, 0.6)]
    bases += [('rbf', g, a) for g in (1.0, 4.0) for a in (1.0, 10.0, 100.0)]
    bases += [('logistic', 0.05)]
    corrections = (0.0, 0.35)
    ncandidates = len(bases) * len(corrections)

    def fit_models(a, labels, query, donor_ids, wanted=None):
        needed = set(range(ncandidates)) if wanted is None else set(wanted)
        base_needed = {k // 2 for k in needed}
        n = len(labels)
        a = a - 0.5 * a.mean(axis=1, keepdims=True)
        query = query - 0.5 * query.mean(axis=1, keepdims=True)
        center = a.mean(axis=0)
        scale = np.sqrt(a.var(axis=0) + 0.1)
        z = np.clip((a - center) / scale, -8.0, 8.0)
        q = np.clip((query - center) / scale, -8.0, 8.0)
        del a, query
        counts = np.bincount(labels, minlength=7).astype(np.float64)
        prior = counts / n
        present = counts > 0
        target = np.eye(7, dtype=np.float64)[labels]
        zm = z.mean(axis=0)
        gram = z.T @ z - n * np.outer(zm, zm)
        rhs = z.T @ target - n * np.outer(zm, prior)
        means = np.zeros((7, z.shape[1]), dtype=np.float64)
        for c in np.flatnonzero(present):
            means[c] = z[labels == c].mean(axis=0)
        delta = means - zm
        between = delta.T @ (prior[:, None] * delta)
        within = gram / n - between
        within = (within + within.T) * 0.5
        output = {}

        def emit(base_id, probabilities):
            probabilities = np.maximum(probabilities, 1e-9)
            probabilities[:, ~present] = 0.0
            for j, power in enumerate(corrections):
                key = 2 * base_id + j
                if key in needed:
                    p = probabilities / np.maximum(prior, 1e-8)[None, :] ** power
                    p /= p.sum(axis=1, keepdims=True)
                    output[key] = p.astype(np.float32)

        linear_ids = [i for i in base_needed if bases[i][0] == 'linear']
        if linear_ids:
            ev, vec = linalg.eigh(gram, check_finite=False)
            ev = np.maximum(ev, 0.0)
            projected_rhs = vec.T @ rhs
            for i in linear_ids:
                penalty = n * bases[i][1]
                coef = vec @ (projected_rhs / (ev[:, None] + penalty))
                emit(i, q @ coef + prior - zm @ coef)

        lda_ids = [i for i in base_needed if bases[i][0] == 'lda']
        if lda_ids:
            ev, vec = linalg.eigh(within, check_finite=False)
            ev = np.maximum(ev, 0.0)
            tau = max(float(ev.mean()), 1e-6)
            projected_means = vec.T @ means.T
            for i in lda_ids:
                shrink = bases[i][1]
                denom = (1.0 - shrink) * ev + shrink * tau
                coef = vec @ (projected_means / denom[:, None])
                scores = q @ coef - 0.5 * np.sum(means * coef.T, axis=1)
                scores += np.log(np.maximum(prior, 1e-12))
                scores[:, ~present] = -1e12
                scores /= 3.0
                scores -= scores.max(axis=1, keepdims=True)
                emit(i, np.exp(scores))

        rbf_ids = [i for i in base_needed if bases[i][0] == 'rbf']
        if rbf_ids:
            signal = np.diag(between) / (np.maximum(np.diag(within), 0) + 0.1)
            weights = np.clip((signal + 0.02) ** 0.25, 0.4, 1.8)
            u = z * weights
            v = q * weights
            u /= np.maximum(np.linalg.norm(u, axis=1, keepdims=True), 1e-8)
            v /= np.maximum(np.linalg.norm(v, axis=1, keepdims=True), 1e-8)
            rng = np.random.RandomState(731)
            m = min(512, n)
            selected = []
            quota = max(1, m // int(present.sum()))
            for c in np.flatnonzero(present):
                indices = np.flatnonzero(labels == c)
                selected.extend(rng.choice(indices, min(quota, len(indices)), replace=False))
            if len(selected) < m:
                available = np.ones(n, dtype=bool)
                available[np.asarray(selected, dtype=np.int64)] = False
                selected.extend(rng.choice(np.flatnonzero(available), m - len(selected), replace=False))
            landmark_indices = np.asarray(selected[:m], dtype=np.int64)
            landmarks = u[landmark_indices]
            dtrain = np.maximum(2.0 - 2.0 * (u @ landmarks.T), 0.0)
            dquery = np.maximum(2.0 - 2.0 * (v @ landmarks.T), 0.0)
            dland = np.maximum(2.0 - 2.0 * (landmarks @ landmarks.T), 0.0)
            del u, v
            for gamma in sorted({bases[i][1] for i in rbf_ids}):
                k = np.exp(-gamma * dtrain)
                kq = np.exp(-gamma * dquery)
                km = np.exp(-gamma * dland)
                km = (km + km.T) * 0.5
                kmean = k.mean(axis=0)
                kg = k.T @ k - n * np.outer(kmean, kmean)
                krhs = k.T @ target - n * np.outer(kmean, prior)
                kg = (kg + kg.T) * 0.5
                for i in rbf_ids:
                    if bases[i][1] != gamma:
                        continue
                    system = kg + bases[i][2] * km
                    system.flat[::m + 1] += 1e-5
                    factor = linalg.cho_factor(system, lower=True, check_finite=False)
                    coef = linalg.cho_solve(factor, krhs, check_finite=False)
                    emit(i, kq @ coef + prior - kmean @ coef)

        logistic_ids = [i for i in base_needed if bases[i][0] == 'logistic']
        for i in logistic_ids:
            if present.sum() == 1:
                emit(i, np.tile(prior, (len(q), 1)))
                continue
            _, donor_index, donor_counts = np.unique(donor_ids, return_inverse=True, return_counts=True)
            sample_weight = counts[labels] ** -0.35 / donor_counts[donor_index]
            sample_weight /= sample_weight.mean()
            model = LogisticRegression(C=bases[i][1], solver='lbfgs', max_iter=120,
                                       tol=0.002, random_state=731)
            model.fit(z, labels, sample_weight=sample_weight)
            p = np.zeros((len(q), 7), dtype=np.float64)
            p[:, model.classes_.astype(int)] = model.predict_proba(q)
            emit(i, p)
        return output

    oof = np.empty((ncandidates, len(y), 7), dtype=np.float32)
    validation_indices = []
    for donor in donors:
        valid = np.flatnonzero(groups == donor)
        fitting = np.flatnonzero(groups != donor)
        predictions = fit_models(x[fitting], y[fitting], x[valid], groups[fitting])
        for key, p in predictions.items():
            oof[key, valid] = p
        validation_indices.append(valid)

    def score(p):
        pred = np.argmax(p, axis=1)
        result = []
        for indices in validation_indices:
            cm = np.bincount(7 * y[indices] + pred[indices], minlength=49).reshape(7, 7)
            denom = cm.sum(axis=0) + cm.sum(axis=1)
            f1 = np.divide(2.0 * np.diag(cm), denom, out=np.zeros(7), where=denom > 0)
            result.append(f1.mean())
        return float(np.mean(result))

    individual_scores = np.asarray([score(p) for p in oof])
    first = int(np.argmax(individual_scores))
    selected = [first]
    accumulated = oof[first].copy()
    best_score = individual_scores[first]
    for step in range(5):
        trial_scores = [score(accumulated + oof[k]) for k in range(ncandidates)]
        winner = int(np.argmax(trial_scores))
        if trial_scores[winner] <= best_score + 1e-4:
            break
        selected.append(winner)
        accumulated += oof[winner]
        best_score = trial_scores[winner]
    del oof, accumulated
    final_models = fit_models(x, y, xt, groups, wanted=set(selected))
    combined = np.zeros((len(xt), 7), dtype=np.float64)
    for key in selected:
        combined += final_models[key]
    return np.argmax(combined, axis=1).astype(np.int64)
