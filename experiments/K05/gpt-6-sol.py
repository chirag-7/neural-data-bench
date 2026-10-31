import numpy as np

try:
    from sklearn.utils.fixes import threadpool_limits
except ImportError:
    class threadpool_limits:
        def __init__(self, limits):
            pass
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass


def _weights(groups, blocks):
    weights = np.zeros(len(groups), dtype=float)
    donors = np.unique(groups)
    for donor in donors:
        donor_rows = np.flatnonzero(groups == donor)
        donor_blocks = np.unique(blocks[donor_rows])
        for block in donor_blocks:
            rows = donor_rows[blocks[donor_rows] == block]
            weights[rows] = 1.0 / (len(donors) * len(donor_blocks) * len(rows))
    return weights


def _collapse(x, y, groups, blocks):
    keys = list(dict.fromkeys(zip(groups.tolist(), blocks.tolist())))
    xx, yy, gg, bb = [], [], [], []
    for donor, block in keys:
        rows = np.flatnonzero((groups == donor) & (blocks == block))
        xx.append(x[rows].mean(axis=0))
        yy.append(y[rows].mean(axis=0))
        gg.append(donor)
        bb.append(block)
    return np.asarray(xx), np.asarray(yy), np.asarray(gg), np.asarray(bb)


def _ridge_predictions(x, y, groups, blocks, test_x, count, scaled, alphas):
    weights = _weights(groups, blocks)
    y_mean = weights @ y
    mean = weights @ x
    variance = weights @ ((x - mean) ** 2)
    chosen = np.lexsort((np.arange(x.shape[1]), -variance))[:min(count, x.shape[1])]
    divisor = np.sqrt(np.maximum(variance[chosen], 1e-10)) if scaled else 1.0
    fit = (x[:, chosen] - mean[chosen]) / divisor
    test = (test_x[:, chosen] - mean[chosen]) / divisor
    norm = max(float(weights @ np.sum(fit * fit, axis=1)), 1e-12)
    train_kernel = (fit @ fit.T) / norm
    test_kernel = (test @ fit.T) / norm
    root_w = np.sqrt(weights)
    symmetric = (root_w[:, None] * train_kernel) * root_w[None, :]
    eigenvalues, eigenvectors = np.linalg.eigh(symmetric)
    eigenvalues = np.maximum(eigenvalues, 0.0)
    target_projection = eigenvectors.T @ (root_w[:, None] * (y - y_mean))
    test_projection = (test_kernel * root_w[None, :]) @ eigenvectors
    return np.stack([
        y_mean + test_projection @ (target_projection / (eigenvalues[:, None] + alpha))
        for alpha in alphas
    ])


def _score_predictions(predictions, truth, groups, blocks):
    squared = (predictions - truth) ** 2
    donor_errors = []
    for donor in np.unique(groups):
        donor_rows = groups == donor
        block_errors = []
        for block in np.unique(blocks[donor_rows]):
            rows = donor_rows & (blocks == block)
            block_errors.append(squared[rows].mean(axis=0))
        donor_errors.append(np.mean(block_errors, axis=0))
    return np.sqrt(np.mean(donor_errors, axis=0))


def _fit_predict(train_x, train_y, test_x, train_groups):
    x = np.asarray(train_x, dtype=float)
    y = np.asarray(train_y, dtype=float)
    test = np.asarray(test_x, dtype=float)
    groups = np.asarray(train_groups['group_ids']).astype(str)
    blocks = np.asarray(train_groups['block_ids']).astype(str)

    valid = np.isfinite(x)
    fill = np.where(valid, x, 0.0).sum(axis=0) / np.maximum(valid.sum(axis=0), 1)
    x = np.where(valid, x, fill)
    test = np.where(np.isfinite(test), test, fill)

    alphas = (0.005, 0.05, 0.5, 5.0)
    bases = [(mode, count, scaled)
             for mode in (0, 1)
             for count in (100, 500, 2000)
             for scaled in (False, True)]
    n_models = 1 + len(bases) * len(alphas)
    cv_predictions = np.empty((n_models, len(x), y.shape[1]), dtype=float)

    for donor in np.unique(groups):
        held = groups == donor
        fit = ~held
        xf, yf = x[fit], y[fit]
        gf, bf = groups[fit], blocks[fit]
        cv_predictions[0, held] = _weights(gf, bf) @ yf
        collapsed = _collapse(xf, yf, gf, bf)
        for base_index, (mode, count, scaled) in enumerate(bases):
            if mode == 0:
                xx, yy, gg, bb = xf, yf, gf, bf
            else:
                xx, yy, gg, bb = collapsed
            predictions = _ridge_predictions(
                xx, yy, gg, bb, x[held], count, scaled, alphas
            )
            start = 1 + base_index * len(alphas)
            cv_predictions[start:start + len(alphas), held] = predictions

    losses = np.stack([
        _score_predictions(prediction, y, groups, blocks)
        for prediction in cv_predictions
    ])
    selected = []
    for target in range(y.shape[1]):
        order = np.argsort(losses[:, target], kind='stable')[:6]
        local = losses[order, target]
        temperature = max(float(local[0]), 0.02)
        weights = np.exp(-8.0 * (local - local[0]) / temperature)
        weights /= weights.sum()
        selected.append((order, weights))

    needed = set(int(index) for order, _ in selected for index in order)
    full = {0: np.repeat((_weights(groups, blocks) @ y)[None, :], len(test), axis=0)}
    collapsed = _collapse(x, y, groups, blocks)
    for base_index, (mode, count, scaled) in enumerate(bases):
        start = 1 + base_index * len(alphas)
        if not any(start + offset in needed for offset in range(len(alphas))):
            continue
        if mode == 0:
            xx, yy, gg, bb = x, y, groups, blocks
        else:
            xx, yy, gg, bb = collapsed
        predictions = _ridge_predictions(
            xx, yy, gg, bb, test, count, scaled, alphas
        )
        for offset, prediction in enumerate(predictions):
            if start + offset in needed:
                full[start + offset] = prediction

    result = np.zeros((len(test), y.shape[1]), dtype=float)
    for target, (order, weights) in enumerate(selected):
        for index, weight in zip(order, weights):
            result[:, target] += weight * full[int(index)][:, target]
    return np.clip(np.nan_to_num(result, nan=0.5, posinf=1.0, neginf=0.0), 0.0, 1.0)


def fit_predict(train_x, train_y, test_x, train_groups):
    with threadpool_limits(limits=1):
        return _fit_predict(train_x, train_y, test_x, train_groups)
