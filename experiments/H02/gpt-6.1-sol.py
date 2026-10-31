import numpy as np
from scipy.linalg import eigh
from sklearn.metrics import roc_auc_score


def fit_predict(train_x, train_y, test_x, train_groups):
    y = np.asarray(train_y, dtype=int).reshape(-1)
    _, groups = np.unique(np.asarray(train_groups).reshape(-1), return_inverse=True)
    if np.unique(y).size < 2:
        return np.zeros(len(test_x), dtype=float)

    def prepare(a):
        a = np.asarray(a, dtype=np.float64)
        a = np.nan_to_num(a, nan=0.0, posinf=100.0, neginf=-100.0)
        a = np.clip(a, -100.0, 100.0)
        return a.reshape(len(a), 16, 32, 4).mean(axis=-1)

    X, Xt = prepare(train_x), prepare(test_x)
    Xn = X / np.maximum(np.sqrt(np.mean(X * X, axis=(1, 2), keepdims=True)), 2.0)
    Xtn = Xt / np.maximum(np.sqrt(np.mean(Xt * Xt, axis=(1, 2), keepdims=True)), 2.0)
    grid = [(e, a) for e in (0.25, 1.0) for a in (0.02, 0.08, 0.25, 0.6)]

    def group_info(g):
        ids = [np.flatnonzero(g == v) for v in np.unique(g)]
        weights = np.empty(len(g), dtype=float)
        for ix in ids:
            weights[ix] = 1.0 / (len(ids) * len(ix))
        return ids, weights

    def class_means(A, labels, ids):
        means = []
        for c in (0, 1):
            pieces = [A[ix[labels[ix] == c]].mean(axis=0)
                      for ix in ids if np.any(labels[ix] == c)]
            means.append(np.mean(pieces, axis=0))
        return np.asarray(means)

    def lda_family(F, labels, g, configs):
        ids, weights = group_info(g)
        mu = class_means(F, labels, ids)
        residual = F - mu[labels]
        C = residual.T @ (residual * weights[:, None])
        between = np.zeros_like(C)
        for ix in ids:
            for c in (0, 1):
                ii = ix[labels[ix] == c]
                if len(ii):
                    d = F[ii].mean(axis=0) - mu[c]
                    between += (len(ii) / (len(ids) * len(ix))) * np.outer(d, d)
        scale = np.sqrt(np.maximum(np.diag(C), 1e-12))
        scale = np.maximum(scale, 0.01 * np.median(scale))
        S = C / scale[:, None] / scale[None, :]
        B = between / scale[:, None] / scale[None, :]
        delta = (mu[1] - mu[0]) / scale
        coefficients = np.zeros((F.shape[1], len(configs)))
        for eta in sorted(set(c[0] for c in configs)):
            columns = [j for j, c in enumerate(configs) if c[0] == eta]
            covariance = S + (eta - 1.0) * B
            covariance = (covariance + covariance.T) * 0.5
            eigenvalues, vectors = eigh(covariance, check_finite=False)
            eigenvalues = np.maximum(eigenvalues, 1e-10)
            alpha = np.array([configs[j][1] for j in columns])
            denominator = ((1.0 - alpha) * eigenvalues[:, None]
                           + alpha * np.mean(eigenvalues))
            W = vectors @ ((vectors.T @ delta)[:, None] / denominator)
            sd = np.sqrt(np.maximum(np.sum(W * (S @ W), axis=0), 1e-12))
            coefficients[:, columns] = W / scale[:, None] / sd
        intercept = -0.5 * (mu[0] + mu[1]) @ coefficients
        return coefficients, intercept

    def power(A, exponent):
        ev, U = eigh((A + A.T) * 0.5, check_finite=False)
        return (U * np.maximum(ev, 1e-10) ** exponent) @ U.T

    def covariance_epochs(A, filters, template):
        Z = np.einsum('fc,nct->nft', filters, A, optimize=True)
        Z -= Z.mean(axis=-1, keepdims=True)
        Z /= np.maximum(np.sqrt(np.mean(Z * Z, axis=(1, 2), keepdims=True)), 1e-8)
        Q = np.concatenate((np.broadcast_to(template, Z.shape), Z), axis=1)
        C = Q @ Q.transpose(0, 2, 1) / Q.shape[-1]
        d = C.shape[-1]
        trace = np.trace(C, axis1=1, axis2=2) / d
        C *= 0.94
        diagonal = np.arange(d)
        C[:, diagonal, diagonal] += 0.06 * trace[:, None]
        return C

    def covariance_fit(A, labels, g):
        ids, weights = group_info(g)
        Z = A - A.mean(axis=-1, keepdims=True)
        evoked = class_means(Z, labels, ids)
        noise = np.einsum('nct,ndt,n->cd', Z, Z, weights, optimize=True) / Z.shape[-1]
        noise += np.eye(noise.shape[0]) * (1e-3 * np.trace(noise) / noise.shape[0] + 1e-10)
        filters, templates = [], []
        for P in evoked:
            signal = P @ P.T / P.shape[-1]
            _, U = eigh(signal, noise, check_finite=False)
            W = U[:, -4:].T
            filters.append(W)
            templates.append(W @ P)
        filters = np.concatenate(filters, axis=0)
        template = np.concatenate(templates, axis=0)
        template /= np.maximum(np.sqrt(np.mean(template * template, axis=1, keepdims=True)), 1e-8)
        C = covariance_epochs(A, filters, template)
        reference = np.tensordot(weights, C, axes=(0, 0))
        subset = np.linspace(0, len(C) - 1, min(1024, len(C)), dtype=int)
        _, small_weights = group_info(g[subset])
        for _ in range(5):
            root = power(reference, 0.5)
            inverse = power(reference, -0.5)
            whitened = inverse @ C[subset] @ inverse
            ev, U = np.linalg.eigh(whitened)
            logs = (U * np.log(np.maximum(ev, 1e-10))[:, None, :]) @ U.transpose(0, 2, 1)
            update = np.tensordot(small_weights, logs, axes=(0, 0))
            ev, U = eigh((update + update.T) * 0.5, check_finite=False)
            reference = root @ ((U * np.exp(np.clip(ev, -20, 20))) @ U.T) @ root
            if np.linalg.norm(update) < 1e-5:
                break
        inverse = power(reference, -0.5)
        return filters, template, inverse, C

    def tangent(C, inverse):
        d = C.shape[-1]
        rows, columns = np.triu_indices(d)
        factors = np.where(rows == columns, 1.0, np.sqrt(2.0))
        features = np.empty((len(C), len(rows)))
        for start in range(0, len(C), 1024):
            stop = min(start + 1024, len(C))
            whitened = inverse @ C[start:stop] @ inverse
            ev, U = np.linalg.eigh(whitened)
            logs = (U * np.log(np.maximum(ev, 1e-10))[:, None, :]) @ U.transpose(0, 2, 1)
            features[start:stop] = logs[:, rows, columns] * factors
        return features

    ids, _ = group_info(groups)
    valid_ids = [ix for ix in ids if np.unique(y[ix]).size == 2]

    def average_auc(scores):
        return float(np.mean([roc_auc_score(y[ix], scores[ix]) for ix in valid_ids]))

    rng = np.random.RandomState(1729)
    number_groups = len(ids)
    selected = [np.array([2, 6]) for _ in range(3)]
    blend = np.array([0.5, 0.25, 0.25])
    if number_groups >= 2 and valid_ids:
        folds = min(3, number_groups)
        assignment = np.empty(number_groups, dtype=int)
        assignment[rng.permutation(number_groups)] = np.arange(number_groups) % folds
        oof = np.empty((len(y), 3 * len(grid)))
        for fold in range(folds):
            va = np.flatnonzero(assignment[groups] == fold)
            tr = np.flatnonzero(assignment[groups] != fold)
            for branch, A in enumerate((X, Xn)):
                F = A[tr].reshape(len(tr), -1)
                V = A[va].reshape(len(va), -1)
                W, b = lda_family(F, y[tr], groups[tr], grid)
                oof[va, branch * 8:(branch + 1) * 8] = V @ W + b
            filters, template, inverse, C = covariance_fit(X[tr], y[tr], groups[tr])
            F = tangent(C, inverse)
            V = tangent(covariance_epochs(X[va], filters, template), inverse)
            W, b = lda_family(F, y[tr], groups[tr], grid)
            oof[va, 16:24] = V @ W + b
        quality = np.array([average_auc(oof[:, j]) for j in range(oof.shape[1])])
        branch_scores = np.empty((len(y), 3))
        for branch in range(3):
            selected[branch] = np.argsort(quality[branch * 8:(branch + 1) * 8], kind='stable')[-2:]
            branch_scores[:, branch] = oof[:, branch * 8 + selected[branch]].mean(axis=1)
        best = -np.inf
        for i in range(5):
            for j in range(5 - i):
                weights = np.array([i, j, 4 - i - j], dtype=float) / 4.0
                objective = average_auc(branch_scores @ weights) - 0.0005 * np.sum(weights * weights)
                if objective > best:
                    best, blend = objective, weights

    result = np.zeros(len(Xt), dtype=float)
    for branch in range(3):
        if blend[branch] == 0:
            continue
        configs = [grid[j] for j in selected[branch]]
        if branch < 2:
            A, At = (X, Xt) if branch == 0 else (Xn, Xtn)
            F, V = A.reshape(len(A), -1), At.reshape(len(At), -1)
        else:
            filters, template, inverse, C = covariance_fit(X, y, groups)
            F = tangent(C, inverse)
            V = tangent(covariance_epochs(Xt, filters, template), inverse)
        W, b = lda_family(F, y, groups, configs)
        result += blend[branch] * (V @ W + b).mean(axis=1)
    return np.nan_to_num(result, nan=0.0, posinf=1e6, neginf=-1e6)
