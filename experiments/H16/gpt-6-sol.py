import numpy as np
from scipy.fft import dct, idct


def _features(x):
    x = np.asarray(x, dtype=np.float64)
    n, t = x.shape
    spectrum = dct(x, type=2, axis=1, norm='ortho')
    frequencies = np.pi * np.arange(t) / t
    scales = (2, 4, 8, 16, 32, 64, 128)
    smooth = []
    for scale in scales:
        response = np.exp(-0.5 * (scale * frequencies) ** 2)
        smooth.append(idct(spectrum * response[None, :], type=2,
                           axis=1, norm='ortho'))

    bands = np.empty((n, t, len(scales) + 1), dtype=np.float64)
    bands[:, :, 0] = x - smooth[0]
    for j in range(len(scales) - 1):
        bands[:, :, j + 1] = smooth[j] - smooth[j + 1]
    bands[:, :, -1] = smooth[-1]

    high = np.sqrt(np.mean((x - smooth[1]) ** 2, axis=1) + 1e-8)
    slow = np.sqrt(np.mean(smooth[4] ** 2, axis=1) + 1e-8)
    local = np.abs(smooth[3]) / (high[:, None] + 0.1)
    local = np.minimum(local, 10.0)
    local = local / (1.0 + local)
    gates = (np.ones((n, 1)), high[:, None], high[:, None] ** 2,
             slow[:, None], local, local ** 2)

    width = bands.shape[2]
    features = np.empty((n, t, width * len(gates)), dtype=np.float64)
    for j, gate in enumerate(gates):
        features[:, :, j * width:(j + 1) * width] = bands * gate[:, :, None]
    return features


def _statistics(features, target, weights):
    n, t, p = features.shape
    design = features.reshape(n * t, p)
    weighted = design * np.repeat(weights, t)[:, None]
    gram = design.T @ weighted
    rhs = weighted.T @ target.reshape(-1)
    return gram, rhs


def _solve(gram, rhs, strength):
    diagonal = np.diag(gram)
    floor = max(float(np.mean(diagonal)) * 1e-8, 1e-12)
    penalty = np.maximum(diagonal, floor)
    return np.linalg.solve(gram + strength * np.diag(penalty), rhs)


def fit_predict(train_x, train_y, test_x):
    x = np.asarray(train_x, dtype=np.float64)
    y = np.asarray(train_y, dtype=np.float64)
    z = np.asarray(test_x, dtype=np.float64)
    residual = x - y
    features = _features(x)

    clean_power = np.mean(y ** 2, axis=1)
    weights = 1.0 / (clean_power + 1e-5)
    weights /= np.mean(weights)

    rng = np.random.default_rng(20261030)
    permutation = rng.permutation(len(x))
    n_valid = max(1, int(round(0.2 * len(x))))
    valid = permutation[:n_valid]
    train = permutation[n_valid:]

    gram, rhs = _statistics(features[train], residual[train], weights[train])
    valid_features = features[valid]
    valid_norm = np.linalg.norm(y[valid], axis=1) + 1e-8
    best_score = np.inf
    best_strength = None
    best_scale = None
    for strength in (1e-4, 1e-3, 1e-2, 1e-1):
        coefficients = _solve(gram, rhs, strength)
        correction = np.tensordot(valid_features, coefficients, axes=([2], [0]))
        for scale in (0.8, 1.0, 1.2):
            error = residual[valid] - scale * correction
            score = np.mean(np.linalg.norm(error, axis=1) / valid_norm)
            if score < best_score:
                best_score = score
                best_strength = strength
                best_scale = scale

    gram, rhs = _statistics(features, residual, weights)
    coefficients = _solve(gram, rhs, best_strength)
    test_features = _features(z)
    correction = np.tensordot(test_features, coefficients, axes=([2], [0]))
    prediction = z - best_scale * correction
    return np.asarray(prediction, dtype=np.float32)
