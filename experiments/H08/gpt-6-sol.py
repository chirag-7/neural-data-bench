import numpy as np
from scipy.ndimage import gaussian_filter1d
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.metrics import f1_score


def _features(night):
    a = np.clip(np.asarray(night, dtype=np.float32), -1000, 1000)
    n = a.shape[0]
    seg = a.reshape(n, 6, 500)
    seg = seg - seg.mean(axis=2, keepdims=True)
    taper = np.hanning(500).astype(np.float32)
    spectrum = np.fft.rfft(seg * taper, n=512, axis=2)
    power = np.abs(spectrum) ** 2
    freq = np.fft.rfftfreq(512, 0.01)
    bands = ((0.4, 0.8), (0.8, 2), (2, 4), (4, 6),
             (6, 8), (8, 10), (10, 12), (12, 14),
             (14, 16), (16, 20), (20, 30), (30, 45),
             (0.5, 4), (4, 8), (8, 12), (12, 16))
    window_band = np.stack(
        [power[:, :, (freq >= lo) & (freq < hi)].sum(axis=2)
         for lo, hi in bands], axis=2)
    log_band = np.log(np.maximum(window_band.mean(axis=1), 1e-9))
    broad = (freq >= 0.4) & (freq < 45)
    mean_power = power.mean(axis=1)[:, broad]
    total = np.maximum(mean_power.sum(axis=1), 1e-9)
    relative = log_band - np.log(total)[:, None]
    centered_band = log_band - np.median(log_band, axis=0)
    q = mean_power / total[:, None]
    entropy = -np.sum(q * np.log(np.maximum(q, 1e-12)), axis=1)
    entropy /= np.log(mean_power.shape[1])
    alpha_sigma = (freq >= 8) & (freq < 16)
    peak_freq = freq[alpha_sigma][np.argmax(power.mean(axis=1)[:, alpha_sigma], axis=1)]
    centered_signal = a - a.mean(axis=1, keepdims=True)
    rms = np.sqrt(np.mean(centered_signal ** 2, axis=1))
    line = np.mean(np.abs(np.diff(a, axis=1)), axis=1)
    maximum = np.max(np.abs(centered_signal), axis=1)
    zero_cross = np.mean(centered_signal[:, 1:] * centered_signal[:, :-1] < 0, axis=1)
    selected = (2, 4, 8, 10)
    burst = window_band[:, :, selected]
    burst_ratio = np.log(np.maximum(burst.max(axis=1), 1e-9)) - np.log(
        np.maximum(burst.mean(axis=1), 1e-9))
    burst_cv = burst.std(axis=1) / np.maximum(burst.mean(axis=1), 1e-9)
    base = np.concatenate((relative[:, [2, 4, 6, 7, 8, 10, 12, 15]],
                           centered_band[:, [2, 4, 6, 7, 8, 10, 12, 15]]), axis=1)
    local = gaussian_filter1d(base, 2, axis=0, mode='nearest')
    context = gaussian_filter1d(base, 10, axis=0, mode='nearest')
    extras = np.column_stack((entropy, peak_freq, np.log1p(rms),
                              np.log1p(line), np.log1p(maximum), zero_cross,
                              np.arange(n) / float(n)))
    features = np.column_stack((log_band, relative, centered_band,
                                burst_ratio, burst_cv, extras, local, context))
    return np.nan_to_num(features, nan=0.0, posinf=30.0, neginf=-30.0).astype(np.float32)


def _model(x, y, trees, seed):
    counts = np.bincount(y, minlength=5)
    weights = np.sqrt(counts.max() / np.maximum(counts, 1))
    weights = np.minimum(weights, 3.0)
    model = ExtraTreesClassifier(n_estimators=trees, min_samples_leaf=2,
                                 max_depth=19, max_features=0.65,
                                 n_jobs=1, random_state=seed)
    model.fit(x, y, sample_weight=weights[y])
    return model


def _probabilities(model, x):
    p = np.full((len(x), 5), 1e-5, dtype=np.float64)
    p[:, model.classes_.astype(int)] = model.predict_proba(x)
    return p


def _decode(p, n1_bias, switch_penalty):
    emission = np.log(np.maximum(p, 1e-5))
    emission[:, 1] += n1_bias
    count = len(p)
    trace = np.empty((count, 5), dtype=np.int8)
    score = emission[0].copy()
    penalty = switch_penalty * (1 - np.eye(5))
    for t in range(1, count):
        candidates = score[:, None] - penalty
        trace[t] = np.argmax(candidates, axis=0)
        score = emission[t] + np.max(candidates, axis=0)
    answer = np.empty(count, dtype=np.int64)
    answer[-1] = np.argmax(score)
    for t in range(count - 1, 0, -1):
        answer[t - 1] = trace[t, answer[t]]
    return answer


def fit_predict(train_x, train_y, test_x):
    train_features = [_features(train_x[i]) for i in range(train_x.shape[0])]
    test_features = [_features(test_x[i]) for i in range(test_x.shape[0])]
    y_nights = [np.asarray(train_y[i], dtype=np.int64) for i in range(train_y.shape[0])]
    folds = []
    for held_out in (3, 4):
        x_parts = []
        y_parts = []
        for i in range(len(train_features)):
            if i != held_out:
                valid = y_nights[i] >= 0
                x_parts.append(train_features[i][valid])
                y_parts.append(y_nights[i][valid])
        model = _model(np.concatenate(x_parts), np.concatenate(y_parts), 120,
                       400 + held_out)
        folds.append((_probabilities(model, train_features[held_out]),
                      y_nights[held_out]))
    best_score = -np.inf
    best_setting = (0.0, 0.25)
    for bias in (-0.35, 0.0, 0.35):
        for penalty in (0.0, 0.25, 0.5, 0.75):
            actual = []
            predicted = []
            for probabilities, labels in folds:
                result = _decode(probabilities, bias, penalty)
                known = labels >= 0
                actual.append(labels[known])
                predicted.append(result[known])
            quality = f1_score(np.concatenate(actual), np.concatenate(predicted),
                               labels=[0, 1, 2, 3, 4], average='macro',
                               zero_division=0)
            quality -= 0.003 * (abs(bias) + abs(penalty - 0.25))
            if quality > best_score:
                best_score = quality
                best_setting = (bias, penalty)
    x_parts = []
    y_parts = []
    for features, labels in zip(train_features, y_nights):
        known = labels >= 0
        x_parts.append(features[known])
        y_parts.append(labels[known])
    model = _model(np.concatenate(x_parts), np.concatenate(y_parts), 300, 731)
    predictions = [_decode(_probabilities(model, features), *best_setting)
                   for features in test_features]
    return np.stack(predictions).astype(np.int64)