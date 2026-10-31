import numpy as np
from scipy.ndimage import gaussian_filter1d, percentile_filter
from sklearn.ensemble import ExtraTreesRegressor, GradientBoostingRegressor
import gc


def _ar1_events(signal, gamma):
    n = len(signal)
    values = np.empty(n)
    weights = np.empty(n)
    lengths = np.empty(n, dtype=int)
    starts = np.empty(n, dtype=int)
    decay = gamma ** np.arange(n + 1)
    top = -1
    for t in range(n):
        top += 1
        values[top] = signal[t]
        weights[top] = 1.0
        lengths[top] = 1
        starts[top] = t
        while top > 0:
            factor = decay[lengths[top - 1]]
            if values[top - 1] * factor <= values[top]:
                break
            total = weights[top - 1] + factor * factor * weights[top]
            values[top - 1] = (weights[top - 1] * values[top - 1] +
                               factor * weights[top] * values[top]) / total
            weights[top - 1] = total
            lengths[top - 1] += lengths[top]
            top -= 1
    calcium = np.zeros(n)
    for j in range(top + 1):
        start, length = starts[j], lengths[j]
        calcium[start:start + length] = max(values[j], 0.0) * decay[:length]
    events = np.maximum(calcium - gamma * np.r_[0.0, calcium[:-1]], 0.0)
    events[0] = 0.0
    return events


def _record_features(row):
    valid = np.flatnonzero(row[1] > 0.5)
    if not len(valid):
        return None
    n = int(valid[-1]) + 1
    f = np.asarray(row[0, :n], dtype=float).copy()
    finite = np.isfinite(f)
    f[~finite] = np.median(f[finite]) if np.any(finite) else 0.0
    intervals = row[2, valid]
    intervals = intervals[np.isfinite(intervals) & (intervals > 0)]
    dt = float(np.median(intervals)) if len(intervals) else 0.13
    dt = max(dt, 0.001)
    index = np.arange(n)
    def smooth(a, seconds):
        return gaussian_filter1d(a, max(seconds / dt, 0.05), mode='reflect')
    def shift(a, seconds):
        return a[np.clip(index + int(round(seconds / dt)), 0, n - 1)]
    def baseline(seconds):
        width = max(3, int(round(seconds / dt)) | 1)
        return smooth(percentile_filter(f, 15, size=width, mode='reflect'), 0.7)
    short_base = baseline(12.0)
    long_base = baseline(40.0)
    x = f - short_base
    delta = np.diff(f)
    noise = (1.4826 * np.median(np.abs(delta - np.median(delta))) /
             np.sqrt(2.0)) if len(delta) else 0.0
    noise = max(float(noise), 1e-6)
    columns = [f, x, f - long_base, short_base - long_base,
               np.full(n, noise), np.full(n, dt),
               np.minimum(index * dt, 3.0),
               np.minimum((n - 1 - index) * dt, 3.0)]
    for seconds in (0.10, 0.25, 0.5, 1.0, 2.0):
        s = smooth(x, seconds)
        derivative = gaussian_filter1d(x, max(seconds / dt, 0.05),
                                       order=1, mode='reflect') / dt
        columns.extend([s, s / noise, derivative, derivative / noise])
    local = smooth(x, 0.20)
    for lag in (-2.0, -1.0, -0.6, -0.3, 0.3, 0.6, 1.0, 2.0):
        shifted = shift(local, lag)
        columns.extend([shifted, shifted / noise])
    bases = []
    for tau in (0.5, 1.0, 2.0, 4.0):
        estimates = []
        for offset in (0.0, 1.0):
            events = _ar1_events(x - offset * noise, np.exp(-dt / tau))
            estimate = smooth(events, 0.20)
            estimates.append(estimate)
            columns.extend([estimate, estimate / noise, smooth(events, 0.5),
                            shift(estimate, -0.3), shift(estimate, 0.3)])
        bases.append(0.5 * (estimates[0] + estimates[1]))
    features = np.column_stack(columns)
    features = np.nan_to_num(features, nan=0.0, posinf=1e6, neginf=-1e6)
    features = np.clip(features, -1e6, 1e6).astype(np.float32)
    return features, np.column_stack(bases), valid, dt


def _fit_models(x, y, base, weights, seed):
    weights = weights / max(np.mean(weights), 1e-12)
    total = np.sum(weights * y)
    scales = total / np.maximum(np.sum(weights[:, None] * base, axis=0), 1e-10)
    scales = np.clip(scales, 0.0, 1e6)
    if len(y) < 50 or np.std(y) < 1e-10:
        return None, None, scales, float(np.average(y, weights=weights))
    extra = ExtraTreesRegressor(n_estimators=128, max_depth=16,
                               min_samples_leaf=10, max_features=0.7,
                               n_jobs=1, random_state=seed)
    boost = GradientBoostingRegressor(n_estimators=112, learning_rate=0.045,
                                     max_depth=3, min_samples_leaf=40,
                                     max_features=0.65, subsample=0.8,
                                     loss='squared_error', random_state=seed)
    extra.fit(x, y, sample_weight=weights)
    boost.fit(x, y, sample_weight=weights)
    return extra, boost, scales, 0.0


def _predict_models(model, x, base):
    extra, boost, scales, constant = model
    if extra is None:
        return np.full((len(x), 3), constant)
    return np.column_stack([extra.predict(x), np.maximum(boost.predict(x), 0.0),
                            np.mean(base * scales[None, :], axis=1)])


def _smooth_blocks(predictions, blocks):
    result = predictions.copy()
    for indices, dt in blocks:
        result[indices] = gaussian_filter1d(predictions[indices], 0.08 / dt,
                                           axis=0, mode='reflect')
    return np.maximum(result, 0.0)


def _validation_score(y, prediction, blocks, row_groups):
    scores = {}
    for (indices, _), group in zip(blocks, row_groups):
        truth = y[indices]
        estimate = prediction[indices]
        a, b = truth - truth.mean(), estimate - estimate.mean()
        denominator = np.sqrt(np.sum(a * a) * np.sum(b * b))
        correlation = np.sum(a * b) / denominator if denominator > 1e-12 else 0.0
        scores.setdefault(int(group), []).append(correlation)
    animal_scores = np.array([np.mean(v) for v in scores.values()])
    return float(animal_scores.mean() - 0.03 * animal_scores.std())


def fit_predict(train_x, train_y, test_x, train_groups):
    train_x = np.asarray(train_x)
    train_y = np.asarray(train_y, dtype=float)
    test_x = np.asarray(test_x)
    _, groups = np.unique(np.asarray(train_groups).reshape(-1), return_inverse=True)
    train_records = [_record_features(row) for row in train_x]
    matrices, bases, targets, memberships, blocks, row_groups = [], [], [], [], [], []
    position = 0
    for row_id, record in enumerate(train_records):
        if record is None:
            continue
        features, base, valid, dt = record
        keep = valid[np.isfinite(train_y[row_id, valid]) & (train_y[row_id, valid] >= 0)]
        if not len(keep):
            continue
        matrices.append(features[keep])
        bases.append(base[keep])
        targets.append(train_y[row_id, keep])
        memberships.append(np.full(len(keep), groups[row_id], dtype=int))
        blocks.append((np.arange(position, position + len(keep)), dt))
        row_groups.append(groups[row_id])
        position += len(keep)
    output = np.zeros((len(test_x), test_x.shape[-1]), dtype=float)
    if not targets:
        return output
    x, base, y = np.concatenate(matrices), np.concatenate(bases), np.concatenate(targets)
    membership = np.concatenate(memberships)
    weights = np.zeros(len(y))
    for (indices, _), group in zip(blocks, row_groups):
        recording_count = np.sum(np.asarray(row_groups) == group)
        weights[indices] = 1.0 / (recording_count * len(indices))
    weights /= weights.mean()
    prior = np.array([0.55, 0.35, 0.10])
    mixture, calibration = prior.copy(), 1.0
    unique_groups = np.unique(membership)
    if len(unique_groups) > 1:
        oof = np.zeros((len(y), 3))
        for group in unique_groups:
            held = membership == group
            fitted = ~held
            model = _fit_models(x[fitted], y[fitted], base[fitted], weights[fitted], 1729)
            oof[held] = _predict_models(model, x[held], base[held])
            del model
            gc.collect()
        oof = _smooth_blocks(oof, blocks)
        best = -np.inf
        for base_fraction in (0.0, 0.15, 0.30):
            for tree_fraction in (0.0, 0.25, 0.5, 0.75, 1.0):
                candidate = np.array([(1 - base_fraction) * tree_fraction,
                                      (1 - base_fraction) * (1 - tree_fraction),
                                      base_fraction])
                prediction = np.sum(oof * candidate, axis=1)
                score = _validation_score(y, prediction, blocks, row_groups)
                score -= 0.004 * np.sum((candidate - prior) ** 2)
                if score > best:
                    best, mixture = score, candidate
        prediction = np.sum(oof * mixture, axis=1)
        calibration = np.clip(np.sum(weights * y) /
                              max(np.sum(weights * prediction), 1e-10), 0.5, 2.0)
    model = _fit_models(x, y, base, weights, 1729)
    for row_id, row in enumerate(test_x):
        record = _record_features(row)
        if record is None:
            continue
        features, test_base, valid, dt = record
        prediction = _predict_models(model, features, test_base)
        prediction = gaussian_filter1d(prediction, 0.08 / dt, axis=0, mode='reflect')
        prediction = calibration * np.sum(prediction * mixture, axis=1)
        prediction = np.nan_to_num(prediction, nan=0.0, posinf=0.0, neginf=0.0)
        output[row_id, valid] = np.maximum(prediction[valid], 0.0)
    return output
