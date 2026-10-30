import numpy as np
from scipy.signal import savgol_filter
from scipy.interpolate import PchipInterpolator


def _predict_at_current(currents, responses, target, model):
    if model == 0:  # Linear response constrained to zero at zero current
        gain = np.tensordot(currents, responses, axes=(0, 0)) / np.dot(currents, currents)
        return target * gain
    if model == 1:  # Quadratic response constrained to zero
        design = np.column_stack((currents, currents ** 2))
        coefficients = np.linalg.lstsq(design, responses, rcond=None)[0]
        return target * coefficients[0] + target ** 2 * coefficients[1]
    if model == 2:  # Linear interpolation between neighboring amplitudes
        left = int(np.clip(np.searchsorted(currents, target) - 1, 0, len(currents) - 2))
        weight = (target - currents[left]) / (currents[left + 1] - currents[left])
        return (1.0 - weight) * responses[left] + weight * responses[left + 1]
    return PchipInterpolator(currents, responses, axis=0)(target)


def fit_predict(train_x, train_y, test_x):
    train_x = np.asarray(train_x, dtype=float)
    train_y = np.nan_to_num(np.asarray(train_y, dtype=float), nan=0.0, posinf=0.0, neginf=0.0)
    test_x = np.asarray(test_x, dtype=float)

    currents = np.median(train_x, axis=1)
    order = np.argsort(currents)
    currents = currents[order]
    responses = train_y[order]

    best_score = np.inf
    best_window, best_model = 15, 2
    for window in (9, 15, 25, 35):
        smoothed = savgol_filter(responses, window, 3, axis=1, mode='interp')
        for model in range(4):
            squared_error = 0.0
            count = 0
            for held_out in (1, 2):
                keep = np.arange(len(currents)) != held_out
                prediction = _predict_at_current(
                    currents[keep], smoothed[keep], currents[held_out], model
                )
                residual = prediction - responses[held_out]
                squared_error += np.dot(residual, residual)
                count += residual.size
            score = squared_error / count
            if score < best_score:
                best_score = score
                best_window, best_model = window, model

    smoothed = savgol_filter(responses, best_window, 3, axis=1, mode='interp')
    test_currents = np.median(test_x, axis=1)
    predictions = np.stack([
        _predict_at_current(currents, smoothed, float(np.clip(current, currents[0], currents[-1])), best_model)
        for current in test_currents
    ], axis=0)
    return np.nan_to_num(predictions, nan=0.0, posinf=0.0, neginf=0.0)
