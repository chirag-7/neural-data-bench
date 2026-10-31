import numpy as np
from scipy.ndimage import gaussian_filter1d


def _trace(raster, sigma, mode):
    x = np.asarray(raster, dtype=np.float64)
    x = np.maximum(np.nan_to_num(x, nan=0.0, posinf=0.0, neginf=0.0), 0.0)
    n_time, n_depth = x.shape
    x = x / np.maximum(x.sum(axis=1, keepdims=True), 1.0)
    grid = np.arange(n_depth, dtype=np.float64)
    shifts = np.arange(-14.0, 14.0001, 0.25)
    base = x.mean(axis=0)
    template = base.copy()
    obs = x
    if mode == 1:
        obs = gaussian_filter1d(x, sigma, axis=1, mode='constant')
        obs = obs - gaussian_filter1d(obs, 12.0, axis=1, mode='constant')
    estimate = np.zeros(n_time, dtype=np.float64)

    for iteration in range(5):
        profile = gaussian_filter1d(template, sigma, mode='constant')
        if mode == 1:
            profile = profile - gaussian_filter1d(profile, 12.0, mode='constant')
        candidates = np.empty((len(shifts), n_depth), dtype=np.float64)
        for j, shift in enumerate(shifts):
            shifted = np.interp(grid - shift, grid, profile, left=0.0, right=0.0)
            if mode == 0:
                shifted = 0.975 * shifted + 0.025 / n_depth
                shifted /= max(shifted.sum(), 1e-12)
                candidates[j] = np.log(np.maximum(shifted, 1e-12))
            else:
                candidates[j] = shifted / max(np.sqrt(np.sum(shifted * shifted)), 1e-12)

        scores = np.einsum('tb,sb->ts', obs, candidates, optimize=False)
        index = np.argmax(scores, axis=1)
        rows = np.arange(n_time)
        left = scores[rows, np.maximum(index - 1, 0)]
        middle = scores[rows, index]
        right = scores[rows, np.minimum(index + 1, len(shifts) - 1)]
        curvature = left - 2.0 * middle + right
        offset = np.zeros(n_time, dtype=np.float64)
        valid = (index > 0) & (index < len(shifts) - 1) & (curvature < -1e-12)
        offset[valid] = 0.5 * (left[valid] - right[valid]) / curvature[valid]
        estimate = shifts[index] + 0.25 * np.clip(offset, -0.5, 0.5)

        if iteration < 4:
            aligned_shifts = gaussian_filter1d(estimate, 0.5)
            total = np.zeros(n_depth, dtype=np.float64)
            coverage = np.zeros(n_depth, dtype=np.float64)
            for t in range(n_time):
                sample_points = grid + aligned_shifts[t]
                total += np.interp(sample_points, grid, x[t], left=0.0, right=0.0)
                coverage += np.interp(sample_points, grid, np.ones(n_depth), left=0.0, right=0.0)
            template = (total + 0.15 * base) / np.maximum(coverage + 0.15, 1e-12)
            template /= max(template.sum(), 1e-12)

    return 5.0 * estimate


def fit_predict(train_x, train_y, test_x, train_groups):
    train_x = np.asarray(train_x)
    test_x = np.asarray(test_x)
    y = np.asarray(train_y, dtype=np.float64)
    y = y - y.mean(axis=1, keepdims=True)
    settings = [(sigma, mode) for sigma in (2.0, 3.0, 4.0) for mode in (0, 1)]
    smoothings = (0.0, 0.6, 1.2)
    predictions = {}

    for setting in settings:
        predictions[setting] = np.stack([_trace(row, *setting) for row in train_x])

    best_error = np.inf
    best_setting = settings[0]
    best_smoothing = 0.0
    best_train_prediction = None
    n_train = len(train_x)

    for setting in settings:
        raw = predictions[setting]
        for smoothing in smoothings:
            p = raw if smoothing == 0.0 else gaussian_filter1d(raw, smoothing, axis=1)
            p = p - p.mean(axis=1, keepdims=True)
            errors = []
            for held_out in range(n_train):
                keep = np.arange(n_train) != held_out
                denominator = np.sum(p[keep] * p[keep])
                scale = np.sum(p[keep] * y[keep]) / max(denominator, 1e-12)
                scale = np.clip(scale, 0.5, 2.0)
                errors.append(np.sqrt(np.mean((scale * p[held_out] - y[held_out]) ** 2)))
            error = float(np.mean(errors))
            if error < best_error:
                best_error = error
                best_setting = setting
                best_smoothing = smoothing
                best_train_prediction = p

    denominator = np.sum(best_train_prediction * best_train_prediction)
    scale = np.sum(best_train_prediction * y) / max(denominator, 1e-12)
    scale = float(np.clip(scale, 0.5, 2.0))

    output = np.empty((len(test_x), test_x.shape[1]), dtype=np.float64)
    for row_index, raster in enumerate(test_x):
        trace = _trace(raster, *best_setting)
        if best_smoothing > 0.0:
            trace = gaussian_filter1d(trace, best_smoothing)
        trace = trace - trace.mean()
        output[row_index] = np.clip(scale * trace, -60.0, 60.0)

    return np.nan_to_num(output, nan=0.0, posinf=60.0, neginf=-60.0)