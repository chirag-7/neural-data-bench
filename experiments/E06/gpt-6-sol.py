import numpy as np
from scipy.optimize import minimize


def _features(x, mean, scale=None):
    n, _, p = x.shape
    history = x.transpose(0, 2, 1)
    last = history[:, :, -1]
    f = np.empty((n, p, 8), dtype=np.float64)
    f[:, :, 0] = last - mean[None, :]
    for j, width in enumerate((2, 4, 8, 16, 32, 64), 1):
        f[:, :, j] = history[:, :, -width:].mean(axis=2) - last
    f[:, :, 7] = 1.0
    if scale is None:
        scale = np.maximum(np.sqrt(np.mean(f[:, :, :7] ** 2, axis=(0, 1))), 1e-8)
    f[:, :, :7] /= scale[None, None, :]
    return f, scale


def _fit(x, y):
    n, _, p = x.shape
    last = x[:, -1, :]
    past = (x - last[:, None, :]).transpose(0, 2, 1).reshape(-1, 64)
    future = (y - last[:, None, :]).transpose(0, 2, 1).reshape(-1, 32)
    past_mean = past.mean(axis=0)
    future_mean = future.mean(axis=0)
    past -= past_mean
    future -= future_mean
    gram = np.einsum('ni,nj->ij', past, past)
    rhs = np.einsum('ni,nh->ih', past, future)
    ridge_scale = max(len(past) * np.mean(past * past), 1e-12)
    temporal = [np.linalg.solve(gram + strength * ridge_scale * np.eye(64), rhs)
                for strength in (0.003, 0.05)]

    mean = (x.sum(axis=(0, 1)) + y.sum(axis=(0, 1))) / (96.0 * n)
    f, scale = _features(x, mean)
    target = (y - last[:, None, :]).transpose(0, 2, 1)
    flat_f = f.reshape(-1, 8)
    flat_target = target.reshape(-1, 32)
    small_gram = np.einsum('ni,nj->ij', flat_f, flat_f)
    small_rhs = np.einsum('ni,nh->ih', flat_f, flat_target)
    penalty = np.diag([0.003 * len(flat_f)] * 7 + [0.0])
    shared = np.linalg.solve(small_gram + penalty, small_rhs)
    neuron_gram = np.einsum('npi,npj->pij', f, f)
    neuron_rhs = np.einsum('npi,nph->pih', f, target)
    shrink = 120.0
    personal = np.linalg.solve(neuron_gram + shrink * np.eye(8)[None, :, :],
                               neuron_rhs + shrink * shared[None, :, :])

    dx = x - mean[None, None, :]
    dy = y - mean[None, None, :]
    numerator = (np.sum(dx[:, :-1] * dx[:, 1:], axis=(0, 1))
                 + np.sum(dy[:, :-1] * dy[:, 1:], axis=(0, 1))
                 + np.sum(dx[:, -1] * dy[:, 0], axis=0))
    denominator = (np.sum(dx[:, :-1] ** 2, axis=(0, 1))
                   + np.sum(dy[:, :-1] ** 2, axis=(0, 1))
                   + np.sum(dx[:, -1] ** 2, axis=0))
    decay = np.clip(numerator / np.maximum(denominator, 1e-12), 0.0, 0.999)
    return temporal, past_mean, future_mean, mean, scale, shared, personal, decay


def _predict(model, x):
    temporal, past_mean, future_mean, mean, scale, shared, personal, decay = model
    n, _, p = x.shape
    last = x[:, -1, :]
    past = (x - last[:, None, :]).transpose(0, 2, 1).reshape(-1, 64)
    centered = past - past_mean
    predictions = []
    for coefficients in temporal:
        residual = np.einsum('ni,ih->nh', centered, coefficients) + future_mean
        predictions.append(last[:, None, :] + residual.reshape(n, p, 32).transpose(0, 2, 1))
    f, _ = _features(x, mean, scale)
    shared_residual = np.einsum('npi,ih->nph', f, shared)
    personal_residual = np.einsum('npi,pih->nph', f, personal)
    predictions.append(last[:, None, :] + shared_residual.transpose(0, 2, 1))
    predictions.append(last[:, None, :] + personal_residual.transpose(0, 2, 1))
    powers = decay[None, :] ** np.arange(1, 33)[:, None]
    predictions.append(mean[None, None, :] +
                       powers[None, :, :] * (last[:, None, :] - mean[None, None, :]))
    return predictions


def fit_predict(train_x, train_y, test_x, train_groups):
    train_x = np.asarray(train_x, dtype=np.float64)
    train_y = np.asarray(train_y, dtype=np.float64)
    test_x = np.asarray(test_x, dtype=np.float64)
    indices = np.arange(len(train_x))
    error_gram = np.zeros((5, 5), dtype=np.float64)
    count = 0

    for phase in (0, 2):
        valid = indices[(indices // 20) % 4 == phase]
        distance = np.min(np.abs(indices[:, None] - valid[None, :]), axis=1)
        fitting = indices[distance > 5]
        model = _fit(train_x[fitting], train_y[fitting])
        predictions = _predict(model, train_x[valid])
        errors = np.stack([(prediction - train_y[valid]).reshape(-1)
                           for prediction in predictions])
        error_gram += np.einsum('ki,li->kl', errors, errors)
        count += train_y[valid].size

    error_gram /= count
    prior = np.array([0.25, 0.25, 0.15, 0.25, 0.10])
    magnitude = np.median(np.diag(error_gram))
    weights = prior
    if np.isfinite(magnitude) and magnitude > 0:
        regularization = 0.01
        quadratic = error_gram / magnitude + regularization * np.eye(5)
        linear = regularization * prior
        result = minimize(lambda w: w @ quadratic @ w - 2.0 * linear @ w,
                          prior,
                          jac=lambda w: 2.0 * (quadratic @ w - linear),
                          bounds=[(0.0, 1.0)] * 5,
                          constraints={'type': 'eq',
                                       'fun': lambda w: np.sum(w) - 1.0,
                                       'jac': lambda w: np.ones(5)},
                          method='SLSQP',
                          options={'ftol': 1e-12, 'maxiter': 200})
        if result.success and np.all(np.isfinite(result.x)):
            weights = result.x

    model = _fit(train_x, train_y)
    predictions = _predict(model, test_x)
    output = sum(weight * prediction for weight, prediction in zip(weights, predictions))
    return np.nan_to_num(output, nan=0.0, posinf=0.0, neginf=0.0)