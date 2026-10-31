import numpy as np
from scipy.ndimage import gaussian_filter1d, percentile_filter
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler


def fit_predict(train_x, train_y, test_x, train_groups):
    train_x = np.asarray(train_x, dtype=float)
    train_y = np.asarray(train_y, dtype=float)
    test_x = np.asarray(test_x, dtype=float)
    if train_x.ndim != 3 or test_x.ndim != 3 or train_y.shape != train_x.shape[:1] + train_x.shape[2:]:
        raise ValueError('Unexpected input shapes')

    def features(row):
        mask = row[1] > 0.5
        n = int(np.count_nonzero(mask))
        if n == 0:
            return np.empty((0, 1), dtype=float), mask
        f = np.asarray(row[0, :n], dtype=float)
        finite = np.isfinite(f)
        fill = float(np.median(f[finite])) if np.any(finite) else 0.0
        f = np.where(finite, f, fill)
        intervals = row[2, :n]
        intervals = intervals[np.isfinite(intervals) & (intervals > 0)]
        dt = float(np.median(intervals)) if intervals.size else 0.13
        dt = float(np.clip(dt, 0.05, 0.5))

        window = max(5, int(round(18.0 / dt)) | 1)
        baseline = percentile_filter(f, percentile=20, size=window, mode='reflect')
        baseline = gaussian_filter1d(baseline, sigma=max(1.0, 1.5 / dt), mode='reflect')
        residual = f - baseline
        noise = float(np.median(np.abs(np.diff(f))) / 0.954) if n > 1 else 0.0
        noise = max(noise, 0.005)
        span = float(np.percentile(residual, 90) - np.percentile(residual, 10))
        scale = max(span, 3.0 * noise, 0.02)
        z = np.clip(residual / noise, -15.0, 25.0)
        u = np.clip(residual / scale, -6.0, 9.0)
        idx = np.arange(n)
        cols = []
        layouts = (
            (0.5, (-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 8, 10)),
            (1.5, (-7, -5, -3, -1, 0, 1, 3, 5, 7, 9, 12)),
            (4.0, (-10, -6, -3, 0, 3, 6, 10, 14)),
        )
        for signal in (z, u):
            for sigma, offsets in layouts:
                smoothed = gaussian_filter1d(signal, sigma=sigma, mode='reflect')
                for offset in offsets:
                    cols.append(smoothed[np.clip(idx + offset, 0, n - 1)])
            smoothed = gaussian_filter1d(signal, sigma=0.8, mode='reflect')
            previous = np.concatenate((smoothed[:1], smoothed[:-1]))
            for tau in (0.45, 1.2, 2.5):
                innovation = smoothed - np.exp(-dt / tau) * previous
                for offset in (-3, -2, -1, 0, 1, 2, 3, 4):
                    cols.append(innovation[np.clip(idx + offset, 0, n - 1)])
        cols.extend((
            np.full(n, np.log1p(noise)),
            np.full(n, np.log1p(scale)),
            np.full(n, dt),
        ))
        return np.column_stack(cols), mask

    train_parts = []
    target_parts = []
    row_groups = []
    for i, row in enumerate(train_x):
        part, mask = features(row)
        n = part.shape[0]
        if n == 0:
            continue
        valid = mask[:n] & np.isfinite(train_y[i, :n]) & (train_y[i, :n] >= 0)
        if np.any(valid):
            train_parts.append(part[valid])
            target_parts.append(train_y[i, :n][valid])
            row_groups.extend([train_groups[i]] * int(np.count_nonzero(valid)))
    if not train_parts:
        return np.zeros((test_x.shape[0], test_x.shape[2]), dtype=float)

    X = np.vstack(train_parts)
    y = np.concatenate(target_parts)
    _, group_index = np.unique(np.asarray(row_groups), return_inverse=True)
    group_counts = np.bincount(group_index)
    weights = len(y) / (len(group_counts) * group_counts[group_index])

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    linear = Ridge(alpha=400.0, fit_intercept=True, solver='cholesky')
    linear.fit(X_scaled, y, sample_weight=weights)
    linear_train = np.maximum(0.0, linear.predict(X_scaled))
    linear_gain = float(np.dot(weights, y) / max(np.dot(weights, linear_train), 1e-12))
    linear_gain = float(np.clip(linear_gain, 0.0, 10.0))

    forest = ExtraTreesRegressor(
        n_estimators=256,
        min_samples_leaf=12,
        max_features=0.7,
        max_depth=22,
        n_jobs=1,
        random_state=271828,
    )
    forest.fit(X, y, sample_weight=weights)

    output = np.zeros((test_x.shape[0], test_x.shape[2]), dtype=float)
    for i, row in enumerate(test_x):
        part, mask = features(row)
        n = part.shape[0]
        if n == 0:
            continue
        tree_pred = forest.predict(part)
        linear_pred = np.maximum(0.0, linear.predict(scaler.transform(part)))
        pred = 0.8 * tree_pred + 0.2 * linear_gain * linear_pred
        output[i, :n] = np.maximum(0.0, np.nan_to_num(pred, nan=0.0, posinf=0.0, neginf=0.0))
    return output