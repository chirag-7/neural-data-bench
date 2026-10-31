import numpy as np
from scipy.linalg import solve
from sklearn.metrics import roc_auc_score


def _features(x):
    x = np.asarray(x, dtype=np.float64)
    x = np.nan_to_num(x, nan=0.0, posinf=80.0, neginf=-80.0)
    x = np.clip(x, -80.0, 80.0)
    rms = np.sqrt(np.mean(x * x, axis=(1, 2)))
    binned = x.reshape(-1, 16, 16, 8).mean(axis=3).reshape(len(x), -1)
    scale = np.clip(10.0 / np.maximum(rms, 1.0), 0.5, 2.0)
    return (binned, binned * scale[:, None])


def _statistics(x, y, groups):
    out = {}
    for group in np.unique(groups):
        in_group = groups == group
        parts = []
        for label in (0, 1):
            a = x[in_group & (y == label)]
            parts.append((len(a), a.sum(axis=0), a.T @ a))
        out[group] = parts
    return out


def _base(stats, selected):
    totals = []
    for label in (0, 1):
        items = [stats[group][label] for group in selected]
        n = sum(item[0] for item in items)
        s = sum((item[1] for item in items))
        gram = sum((item[2] for item in items))
        totals.append((n, s, gram))
    n0, s0, gram0 = totals[0]
    n1, s1, gram1 = totals[1]
    mean0, mean1 = s0 / n0, s1 / n1
    covariance = (gram0 + gram1 - np.outer(s0, s0) / n0
                  - np.outer(s1, s1) / n1) / (n0 + n1 - 2)
    covariance = (covariance + covariance.T) * 0.5
    sd = np.sqrt(np.maximum(np.diag(covariance), 1e-4))
    correlation = covariance / sd[:, None] / sd[None, :]
    delta = (mean1 - mean0) / sd
    n = n0 + n1
    overall_sum = s0 + s1
    overall_gram = gram0 + gram1
    return correlation, delta, sd, n, overall_sum, overall_gram


def _weights(base, shrinkage):
    correlation, delta, sd, n, overall_sum, overall_gram = base
    p = len(sd)
    matrix = (1.0 - shrinkage) * correlation + shrinkage * np.eye(p)
    w = solve(matrix, delta, assume_a='pos', check_finite=False) / sd
    mean_score = (overall_sum @ w) / n
    variance = (w @ overall_gram @ w) / n - mean_score ** 2
    return w / np.sqrt(max(variance, 1e-8))


def _group_auc(y, scores, groups):
    aucs = []
    for group in np.unique(groups):
        mask = groups == group
        if np.unique(y[mask]).size == 2:
            aucs.append(roc_auc_score(y[mask], scores[mask]))
    return float(np.mean(aucs))


def fit_predict(train_x, train_y, test_x, train_groups):
    y = np.asarray(train_y).ravel().astype(int)
    groups = np.asarray(train_groups).ravel()
    train_views = _features(train_x)
    test_views = _features(test_x)
    unique_groups = np.unique(groups)
    shuffled = np.random.RandomState(2026).permutation(unique_groups)
    folds = np.array_split(shuffled, min(5, len(shuffled)))
    shrinkages = (0.03, 0.1, 0.25, 0.5)
    oof = np.zeros((2, len(shrinkages), len(y)), dtype=np.float64)
    all_stats = []

    for view_index, x in enumerate(train_views):
        stats = _statistics(x, y, groups)
        all_stats.append(stats)
        for held_out in folds:
            fit_groups = unique_groups[~np.isin(unique_groups, held_out)]
            validation = np.isin(groups, held_out)
            base = _base(stats, fit_groups)
            for j, shrinkage in enumerate(shrinkages):
                w = _weights(base, shrinkage)
                oof[view_index, j, validation] = x[validation] @ w

    choices = []
    for view_index in range(2):
        results = np.array([_group_auc(y, oof[view_index, j], groups)
                            for j in range(len(shrinkages))])
        near_best = np.flatnonzero(results >= results.max() - 0.001)
        choices.append(int(near_best[-1]))

    raw = oof[0, choices[0]]
    scaled = oof[1, choices[1]]
    alphas = np.linspace(0.0, 1.0, 5)
    blend_auc = np.array([_group_auc(y, a * raw + (1.0 - a) * scaled, groups)
                          for a in alphas])
    near_best = np.flatnonzero(blend_auc >= blend_auc.max() - 0.001)
    blend_index = min(near_best, key=lambda i: abs(alphas[i] - 0.5))
    alpha = alphas[blend_index]

    predictions = []
    for view_index in range(2):
        base = _base(all_stats[view_index], unique_groups)
        w = _weights(base, shrinkages[choices[view_index]])
        predictions.append(test_views[view_index] @ w)
    scores = alpha * predictions[0] + (1.0 - alpha) * predictions[1]
    return np.nan_to_num(scores, nan=0.0, posinf=1e6, neginf=-1e6)
