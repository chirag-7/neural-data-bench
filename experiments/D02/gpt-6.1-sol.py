import numpy as np
from scipy.interpolate import BSpline


def _smooth_candidates(y):
    n = y.shape[1]
    if n < 12:
        return [y.copy()]
    t = np.arange(n, dtype=float) * 0.002
    u = np.log1p(t / 0.015)
    u /= u[-1]
    k = min(64, max(8, n // 5))
    interior = np.linspace(0.0, 1.0, k - 2)[1:-1]
    knots = np.r_[np.zeros(4), interior, np.ones(4)]
    b = BSpline(knots, np.eye(k), 3)(u)
    left, singular, right = np.linalg.svd(b, full_matrices=False)
    keep = singular > singular[0] * 1e-10
    left = left[:, keep]
    singular = singular[keep]
    right = right[keep]
    d = np.diff(np.eye(k), n=2, axis=0)
    rough = (d @ right.T) / singular[None, :]
    eigen, rotation = np.linalg.eigh(rough.T @ rough)
    eigen = np.maximum(eigen, 0.0)
    positive = eigen[eigen > 1e-9]
    if positive.size:
        eigen /= np.median(positive)
    h = left @ rotation
    coefficients = y @ h
    rank = h.shape[1]
    targets = sorted(set(min(rank, v) for v in [5, 8, 12, 18, 27, 40, 55, rank]))
    result = []
    for target in targets:
        if target >= rank:
            attenuation = np.ones(rank)
        else:
            lo, hi = -30.0, 40.0
            for _ in range(65):
                mid = (lo + hi) * 0.5
                attenuation = 1.0 / (1.0 + np.exp(mid) * eigen)
                if attenuation.sum() > target:
                    lo = mid
                else:
                    hi = mid
            attenuation = 1.0 / (1.0 + np.exp((lo + hi) * 0.5) * eigen)
        result.append((coefficients * attenuation) @ h.T)
    return result


def _amplitude_specs():
    specs = []
    def add(powers, penalties, prior):
        specs.append((powers, penalties, prior))
    add((1,), (0.0,), 0.30)
    add((0, 1), (0.0, 0.0), 0.10)
    for r in [0.1, 1.0]:
        add((0, 1), (r, 0.0), 0.025)
    for r in [0.0, 0.001, 0.01, 0.1, 1.0]:
        add((1, 2), (0.0, r), 0.05)
    for r in [0.001, 0.01, 0.1, 1.0]:
        add((1, 2, 3), (0.0, r, 4.0 * r), 0.025)
    for r in [0.001, 0.01, 0.1]:
        add((0, 1, 2), (0.0, 0.0, r), 0.05 / 3.0)
    specs.append((None, None, 0.15))
    return specs


def _amplitude_weights(a, query, spec):
    powers, penalties, _ = spec
    if powers is not None:
        f = np.column_stack([a ** p for p in powers])
        fq = np.column_stack([query ** p for p in powers])
        penalty = len(a) * np.diag(penalties)
        normal = f.T @ f + penalty
        normal += np.eye(len(powers)) * 1e-10
        return fq @ np.linalg.solve(normal, f.T)
    # Include the known zero-current, zero-deflection anchor.
    nodes = np.r_[0.0, a]
    mapping = np.vstack([np.zeros((1, len(a))), np.eye(len(a))])
    order = np.argsort(nodes)
    nodes, mapping = nodes[order], mapping[order]
    weights = np.empty((len(query), len(a)))
    for j, q in enumerate(query):
        i = np.searchsorted(nodes, q) - 1
        i = int(np.clip(i, 0, len(nodes) - 2))
        width = nodes[i + 1] - nodes[i]
        if abs(width) < 1e-12:
            weights[j] = mapping[i]
        else:
            fraction = (q - nodes[i]) / width
            weights[j] = (1.0 - fraction) * mapping[i] + fraction * mapping[i + 1]
    return weights


def fit_predict(train_x, train_y, test_x):
    x = np.asarray(train_x, dtype=float)
    y = np.asarray(train_y, dtype=float)
    tx = np.asarray(test_x, dtype=float)
    y = np.nan_to_num(y, nan=0.0, posinf=0.0, neginf=0.0)
    amplitude = -np.mean(x, axis=1)
    query = -np.mean(tx, axis=1)
    scale = max(float(np.max(np.abs(amplitude))), 1e-8)
    a, q = amplitude / scale, query / scale
    order = np.argsort(a)
    a, y = a[order], y[order]
    n, samples = y.shape
    smooth = _smooth_candidates(y)
    if n == 1:
        denom = a[0] if abs(a[0]) > 1e-12 else 1.0
        return np.nan_to_num((q[:, None] / denom) * smooth[len(smooth) // 2][0])
    specs = _amplitude_specs()
    count = len(specs)
    cv_weights = np.zeros((count, n, n))
    test_weights = np.zeros((count, len(q), n))
    for m, spec in enumerate(specs):
        test_weights[m] = _amplitude_weights(a, q, spec)
        for held in range(n):
            ids = np.flatnonzero(np.arange(n) != held)
            cv_weights[m, held, ids] = _amplitude_weights(a[ids], a[held:held + 1], spec)[0]
    sweep_weight = np.ones(n)
    if n > 2:
        sweep_weight[[0, -1]] = 0.25
    sweep_weight /= sweep_weight.sum()
    errors, predictions, priors = [], [], []
    for smoothed in smooth:
        validation = np.einsum('mij,jt->mit', cv_weights, smoothed)
        errors.append((validation - y[None, :, :]) ** 2)
        predictions.append(np.einsum('mij,jt->mit', test_weights, smoothed))
        priors.extend(spec[2] / len(smooth) for spec in specs)
    errors = np.concatenate(errors, axis=0)
    predictions = np.concatenate(predictions, axis=0)
    scores = errors.mean(axis=2) @ sweep_weight
    best = int(np.argmin(scores))
    # Estimate uncertainty from paired validation losses in contiguous time blocks.
    blocks = min(10, samples)
    length = samples // blocks
    used = blocks * length
    difference = errors[:, :, :used] - errors[best:best + 1, :, :used]
    block_difference = difference.reshape(len(scores), n, blocks, length).mean(axis=3)
    if blocks > 1:
        variance = block_difference.var(axis=2, ddof=1) / blocks
        standard_error = np.sqrt(variance @ (sweep_weight ** 2))
    else:
        standard_error = np.zeros(len(scores))
    nearest = np.argsort(scores)[:min(10, len(scores))]
    temperature = max(float(np.median(standard_error[nearest])),
                      0.02 * float(scores[best]), 1e-12)
    log_weight = -(scores - scores[best]) / temperature
    weight = np.asarray(priors) * np.exp(np.clip(log_weight, -700.0, 0.0))
    weight /= weight.sum()
    prediction = np.einsum('m,mij->ij', weight, predictions)
    return np.nan_to_num(prediction, nan=0.0, posinf=0.0, neginf=0.0).reshape(tx.shape)
