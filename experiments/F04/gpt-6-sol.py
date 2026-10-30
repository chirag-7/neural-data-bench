import numpy as np
from scipy.fft import dctn
from scipy.ndimage import gaussian_filter
from scipy.linalg import eigh
from scipy.optimize import minimize


def _group(x, y=None):
    unique, inverse, counts = np.unique(x, axis=0, return_inverse=True,
                                        return_counts=True)
    if y is None:
        return unique, inverse
    sums = np.zeros((len(unique), y.shape[1]), dtype=float)
    np.add.at(sums, inverse, y)
    return unique, counts.astype(float), sums / counts[:, None]


def _features(train, test):
    scale = max(float(np.std(train)), 1e-6)

    def transform(x):
        im = x.reshape(-1, 18, 18)
        smooth = gaussian_filter(im, sigma=(0, 1.3, 1.3), mode='reflect')
        energy = gaussian_filter((im - smooth) ** 2,
                                 sigma=(0, 1.5, 1.5), mode='reflect')
        texture = np.sqrt(np.maximum(energy, 0))
        a = dctn(im, axes=(1, 2), norm='ortho').reshape(len(x), -1) / scale
        b = dctn(texture, axes=(1, 2), norm='ortho')[:, :6, :6]
        b = b.reshape(len(x), -1) / scale
        return a, b

    a, b = transform(train)
    at, bt = transform(test)
    am, bm = a.mean(axis=0), b.mean(axis=0)
    return a - am, b - bm, at - am, bt - bm


def fit_predict(train_x, train_y, test_x):
    train_x = np.asarray(train_x, dtype=float)
    train_y = np.asarray(train_y, dtype=float)
    test_x = np.asarray(test_x, dtype=float)
    images, repetitions, targets = _group(train_x, train_y)
    test_images, test_inverse = _group(test_x)
    a, b, at, bt = _features(images, test_images)
    n, neurons = targets.shape

    ii, jj = np.indices((18, 18))
    frequency = np.sqrt(ii * ii + jj * jj).ravel()
    designs = []
    for bandwidth in (4.0, 9.0):
        shrink = 1.0 / (1.0 + (frequency / bandwidth) ** 2)
        base = a * shrink
        test_base = at * shrink
        designs.append((base, test_base))
        designs.append((np.column_stack((base, 0.6 * b)),
                        np.column_stack((test_base, 0.6 * bt))))

    rng = np.random.default_rng(1729)
    order = rng.permutation(n)
    nv = max(1, min(n - 1, int(round(0.25 * n))))
    validation, fitting = order[:nv], order[nv:]
    lambdas = (0.003, 0.03, 0.3, 3.0, 30.0)
    best_loss = np.full(neurons, np.inf)
    best_design = np.zeros(neurons, dtype=int)
    best_lambda = np.full(neurons, lambdas[0])
    best_coef = [None] * neurons
    weight = repetitions[fitting]
    weight_sum = weight.sum()
    fit_targets = targets[fitting]
    mean_rate = np.maximum((weight[:, None] * fit_targets).sum(axis=0)
                           / weight_sum, 1e-8)

    for design_index, (x, _) in enumerate(designs):
        xt = x[fitting]
        xv = x[validation]
        center = (weight[:, None] * xt).sum(axis=0) / weight_sum
        centered = xt - center
        pseudo_rate = (repetitions[fitting, None] * fit_targets
                       + mean_rate[None, :]) / (repetitions[fitting, None] + 1.0)
        response = np.log(np.maximum(pseudo_rate, 1e-8))
        response_mean = (weight[:, None] * response).sum(axis=0) / weight_sum
        response -= response_mean
        gram = centered.T @ (weight[:, None] * centered) / weight_sum
        rhs = centered.T @ (weight[:, None] * response) / weight_sum
        values, vectors = eigh(gram, check_finite=False)
        values = np.maximum(values, 0.0)
        projected = vectors.T @ rhs
        for lam in lambdas:
            coef = vectors @ (projected / (values[:, None] + lam))
            train_log = centered @ coef + response_mean
            train_prediction = np.exp(np.clip(train_log, -12, 10))
            predicted_mean = (weight[:, None] * train_prediction).sum(axis=0)
            predicted_mean /= weight_sum
            shift = np.log(mean_rate / np.maximum(predicted_mean, 1e-8))
            val_log = np.clip((xv - center) @ coef + response_mean + shift,
                              -12, 10)
            loss = np.mean(np.exp(val_log)
                           - targets[validation] * val_log, axis=0)
            improved = loss < best_loss
            best_loss[improved] = loss[improved]
            best_design[improved] = design_index
            best_lambda[improved] = lam
            for neuron in np.flatnonzero(improved):
                best_coef[neuron] = coef[:, neuron].copy()

    predictions = np.empty((len(test_images), neurons), dtype=float)
    total_weight = repetitions.sum()
    for neuron in range(neurons):
        x, tx = designs[best_design[neuron]]
        y = targets[:, neuron]
        mean_y = float(repetitions @ y / total_weight)
        if mean_y < 1e-8:
            predictions[:, neuron] = 1e-5
            continue
        initial_coef = best_coef[neuron]
        initial_log = x @ initial_coef
        initial_mean = np.dot(repetitions,
                              np.exp(np.clip(initial_log, -12, 10)))
        initial_mean /= total_weight
        initial_intercept = np.log(mean_y / max(initial_mean, 1e-8))
        initial = np.r_[initial_intercept, initial_coef]
        penalty = best_lambda[neuron] * mean_y

        def objective(parameters):
            intercept, coef = parameters[0], parameters[1:]
            log_rate = x @ coef + intercept
            clipped = np.clip(log_rate, -12, 10)
            rate = np.exp(clipped)
            loss = np.dot(repetitions, rate - y * clipped) / total_weight
            loss += 0.5 * penalty * np.dot(coef, coef)
            active = (log_rate > -12) & (log_rate < 10)
            residual = repetitions * (rate - y) * active / total_weight
            gradient = np.r_[residual.sum(), x.T @ residual + penalty * coef]
            return loss, gradient

        result = minimize(objective, initial, method='L-BFGS-B', jac=True,
                          options={'maxiter': 85, 'ftol': 1e-8})
        parameters = result.x if np.all(np.isfinite(result.x)) else initial
        rates = np.exp(np.clip(tx @ parameters[1:] + parameters[0], -12, 10))
        lower = max(1e-5, mean_y * 0.005)
        upper = max(5.0, 4.0 * float(np.max(y)))
        predictions[:, neuron] = np.clip(rates, lower, upper)

    return predictions[test_inverse]
