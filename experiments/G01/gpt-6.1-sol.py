import numpy as np
from scipy.linalg import eigh


def _scale(a):
    s = np.std(a, axis=0, dtype=np.float64)
    positive = s[s > 1e-8]
    floor = max(1e-6, 0.05 * float(np.median(positive))) if positive.size else 1.0
    return np.maximum(s, floor).astype(np.float32)


def _fit_features(x, w, b):
    x = np.asarray(x, dtype=np.float32)
    valid = np.isfinite(x)
    counts = np.maximum(valid.sum(axis=0), 1)
    mu = (np.where(valid, x, 0).sum(axis=0, dtype=np.float64) / counts).astype(np.float32)
    a = np.where(valid, x, mu).astype(np.float32)
    scale = _scale(a)
    z = np.clip((a - mu) / scale, -8.0, 8.0)
    root = np.sign(a) * np.sqrt(np.abs(a))
    root_mu = root.mean(axis=0, dtype=np.float64).astype(np.float32)
    root_scale = _scale(root)
    root = np.clip((root - root_mu) / root_scale, -8.0, 8.0)
    h = np.tanh(z @ w + b)
    h_mu = h.mean(axis=0, dtype=np.float64).astype(np.float32)
    h_scale = np.maximum(_scale(h), 0.1)
    h = (h - h_mu) / h_scale
    phi = np.concatenate((z, 0.7 * root, 0.4 * h), axis=1)
    phi_mu = phi.mean(axis=0, dtype=np.float64).astype(np.float32)
    phi -= phi_mu
    state = (mu, scale, root_mu, root_scale, h_mu, h_scale, phi_mu)
    return np.ascontiguousarray(phi), state


def _apply_features(x, state, w, b):
    mu, scale, root_mu, root_scale, h_mu, h_scale, phi_mu = state
    a = np.asarray(x, dtype=np.float32)
    a = np.where(np.isfinite(a), a, mu)
    z = np.clip((a - mu) / scale, -8.0, 8.0)
    root = np.sign(a) * np.sqrt(np.abs(a))
    root = np.clip((root - root_mu) / root_scale, -8.0, 8.0)
    h = (np.tanh(z @ w + b) - h_mu) / h_scale
    phi = np.concatenate((z, 0.7 * root, 0.4 * h), axis=1)
    phi -= phi_mu
    return np.ascontiguousarray(phi)


def _ridge_family(phi, y, alphas, linear_dim):
    n = len(phi)
    mean_y = y.mean(axis=0, dtype=np.float64)
    centered_y = np.asarray(y - mean_y, dtype=np.float32)
    gram = np.asarray(phi.T @ phi, dtype=np.float64)
    cross = np.asarray(phi.T @ centered_y, dtype=np.float64)
    families = []
    for d in (linear_dim, phi.shape[1]):
        values, vectors = eigh(gram[:d, :d], check_finite=False)
        values = np.maximum(values, 0.0)
        projected = vectors.T @ cross[:d]
        coefficients = []
        for alpha in alphas:
            coef = vectors @ (projected / (values[:, None] + n * alpha))
            coefficients.append(coef.astype(np.float32))
        families.append(np.stack(coefficients))
    return families[0], families[1], mean_y


def _predict_family(phi, coefficients, mean_y):
    k, d, outputs = coefficients.shape
    matrix = coefficients.transpose(1, 0, 2).reshape(d, k * outputs)
    predictions = phi[:, :d] @ matrix
    return predictions.reshape(len(phi), k, outputs).transpose(1, 0, 2) + mean_y


def fit_predict(train_x, train_y, test_x):
    x = np.asarray(train_x, dtype=np.float32)
    y = np.asarray(train_y, dtype=np.float32).reshape(-1, 2)
    good = np.isfinite(y).all(axis=1)
    if not np.all(good):
        x, y = x[good], y[good]
    n, p = x.shape
    n_test = len(test_x)
    if n == 0:
        return np.zeros((n_test, 2), dtype=np.float32)
    if n < 32:
        return np.tile(y.mean(axis=0), (n_test, 1)).astype(np.float32)

    rng = np.random.RandomState(731)
    w = (rng.normal(size=(p, 128)) / np.sqrt(max(p, 1))).astype(np.float32)
    b = rng.uniform(-0.8, 0.8, size=128).astype(np.float32)
    alphas = np.asarray([1e-5, 1e-4, 1e-3, 1e-2, 1e-1, 1.0, 10.0])
    k = len(alphas)
    candidates = [(i, 0, 0.0) for i in range(k)]
    candidates += [(0, j, 1.0) for j in range(k)]
    candidates += [(i, j, mix) for mix in (0.25, 0.5, 0.75)
                   for i in range(k) for j in range(k)]
    losses = np.zeros(len(candidates), dtype=np.float64)
    if n >= 1000:
        folds = [(n // 2, 3 * n // 4), (3 * n // 4, n)]
    else:
        folds = [(int(0.75 * n), n)]
    gap = min(128, max(1, n // 100))

    for start, end in folds:
        stop = max(16, start - gap)
        phi, state = _fit_features(x[:stop], w, b)
        linear, nonlinear, mean_y = _ridge_family(phi, y[:stop], alphas, p)
        del phi
        validation_phi = _apply_features(x[start:end], state, w, b)
        pl = _predict_family(validation_phi, linear, mean_y)
        pn = _predict_family(validation_phi, nonlinear, mean_y)
        target = y[start:end].astype(np.float64)
        for c, (i, j, mix) in enumerate(candidates):
            prediction = (1.0 - mix) * pl[i] + mix * pn[j]
            residual = prediction - target
            losses[c] += np.sum(residual * residual, dtype=np.float64)
        del validation_phi, pl, pn

    # A small preference for the linear model resolves nearly equivalent fits.
    adjusted = losses * np.asarray([1.0 + 0.002 * c[2] for c in candidates])
    order = np.argsort(adjusted, kind='stable')
    best = float(adjusted[order[0]])
    chosen = [int(i) for i in order[:5]
              if adjusted[i] <= best + max(1e-12, 0.003 * abs(best))]
    weights = np.exp(-(adjusted[chosen] - best) / max(1e-12, 0.002 * abs(best)))
    weights /= weights.sum()

    phi, state = _fit_features(x, w, b)
    linear, nonlinear, mean_y = _ridge_family(phi, y, alphas, p)
    coefficient = np.zeros((phi.shape[1], 2), dtype=np.float32)
    for weight, c in zip(weights, chosen):
        i, j, mix = candidates[c]
        coefficient += np.float32(weight * mix) * nonlinear[j]
        coefficient[:p] += np.float32(weight * (1.0 - mix)) * linear[i]
    del phi

    predictions = np.empty((n_test, 2), dtype=np.float32)
    for start in range(0, n_test, 8192):
        end = min(start + 8192, n_test)
        test_phi = _apply_features(test_x[start:end], state, w, b)
        predictions[start:end] = test_phi @ coefficient + mean_y
    for column in range(2):
        bad = ~np.isfinite(predictions[:, column])
        predictions[bad, column] = mean_y[column]
    return predictions
