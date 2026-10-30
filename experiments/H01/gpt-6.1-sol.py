import numpy as np
from scipy.signal import butter, sosfiltfilt, detrend
from scipy.linalg import eigh
from sklearn.model_selection import StratifiedKFold


def _prepare(train_x, test_x):
    x = np.concatenate((train_x, test_x), axis=0).astype(np.float64)
    x = np.nan_to_num(x, nan=0.0, posinf=0.0, neginf=0.0)
    x = detrend(x, axis=-1, type='linear')
    centers = [1, 2, 3, 4, 5, 8, 9, 10, 11, 12,
               15, 16, 17, 18, 19]
    neighbors = [
        [0, 2, 8, 31], [1, 3, 9, 32], [2, 4, 10, 33],
        [3, 5, 11, 34], [4, 6, 12, 35],
        [7, 9, 1, 15], [8, 10, 2, 16], [9, 11, 3, 17],
        [10, 12, 4, 18], [11, 13, 5, 19],
        [14, 16, 8, 48], [15, 17, 9, 49], [16, 18, 10, 50],
        [17, 19, 11, 51], [18, 20, 12, 52]]
    bands = [(6, 10), (10, 14), (14, 18), (18, 24),
             (24, 32), (8, 30)]
    n = len(x)
    covs = [np.empty((n, len(bands), d, d)) for d in (21, 15)]
    powers = [np.empty((n, len(bands), d)) for d in (21, 15)]
    for b, (low, high) in enumerate(bands):
        sos = butter(4, [low, high], btype='bandpass', fs=160,
                     output='sos')
        filtered = sosfiltfilt(sos, x, axis=-1)
        lap = np.stack([filtered[:, c] - filtered[:, nb].mean(axis=1)
                        for c, nb in zip(centers, neighbors)], axis=1)
        for v, z in enumerate((filtered[:, :21], lap)):
            z = z - z.mean(axis=-1, keepdims=True)
            c = z @ z.transpose(0, 2, 1) / z.shape[-1]
            diagonal = np.diagonal(c, axis1=1, axis2=2)
            powers[v][:, b] = np.log(np.maximum(diagonal, 1e-12))
            trace = np.maximum(np.trace(c, axis1=1, axis2=2), 1e-12)
            c = c / trace[:, None, None]
            d = c.shape[-1]
            covs[v][:, b] = 0.96 * c + 0.04 * np.eye(d) / d
    del x, filtered, lap
    pairs = [
        [(0, 6), (1, 5), (2, 4), (7, 13), (8, 12), (9, 11),
         (14, 20), (15, 19), (16, 18)],
        [(0, 4), (1, 3), (5, 9), (6, 8), (10, 14), (11, 13)]]
    features = []
    for p, pair in zip(powers, pairs):
        spatial = p - p.mean(axis=2, keepdims=True)
        spectral = p - p.mean(axis=1, keepdims=True)
        asymmetry = np.stack([p[:, :, a] - p[:, :, b]
                              for a, b in pair], axis=-1)
        features.extend([spatial.reshape(n, -1),
                         spectral.reshape(n, -1),
                         asymmetry.reshape(n, -1)])
    return covs, np.concatenate(features, axis=1)


def _features(covs, power, fit_idx, apply_idx, y):
    csp_features, tangent_features = [], []
    for view in covs:
        d = view.shape[-1]
        ii, jj = np.triu_indices(d)
        triangle_weight = np.where(ii == jj, 1.0, np.sqrt(2.0))
        for b in range(view.shape[1]):
            training = view[fit_idx, b]
            applying = view[apply_idx, b]
            class_covs = []
            for label in (0, 1):
                c = training[y[fit_idx] == label].mean(axis=0)
                class_covs.append(0.8 * c + 0.2 * np.eye(d) / d)
            a, other = class_covs
            _, vectors = eigh(a, a + other, check_finite=False)
            chosen = np.r_[0:3, d-3:d]
            w = vectors[:, chosen]
            variance = np.einsum('ic,nij,jc->nc', w, applying, w,
                                 optimize=True)
            variance = np.maximum(variance, 1e-12)
            variance /= variance.sum(axis=1, keepdims=True)
            csp_features.append(np.log(variance))
            reference = training.mean(axis=0)
            eigenvalues, eigenvectors = eigh(reference, check_finite=False)
            inverse_root = ((eigenvectors / np.sqrt(
                np.maximum(eigenvalues, 1e-12))) @ eigenvectors.T)
            whitened = np.einsum('ij,njk,kl->nil', inverse_root,
                                 applying, inverse_root, optimize=True)
            whitened = 0.5 * (whitened + whitened.transpose(0, 2, 1))
            eigenvalues, eigenvectors = np.linalg.eigh(whitened)
            logs = np.log(np.maximum(eigenvalues, 1e-10))
            matrix_log = ((eigenvectors * logs[:, None, :]) @
                          eigenvectors.transpose(0, 2, 1))
            tangent_features.append(matrix_log[:, ii, jj] * triangle_weight)
    return [power[apply_idx], np.concatenate(csp_features, axis=1),
            np.concatenate(tangent_features, axis=1)]


def _ridge_predictions(features, fit_idx, predict_idx, y, alphas):
    labels = y[fit_idx]
    counts = np.bincount(labels, minlength=2)
    weights = len(labels) / (2.0 * counts[labels])
    training = features[fit_idx]
    mean = np.average(training, axis=0, weights=weights)
    variance = np.average((training - mean) ** 2, axis=0,
                          weights=weights)
    scale = np.maximum(np.sqrt(variance), 0.05)
    z_train = np.clip((training - mean) / scale, -6.0, 6.0)
    z_predict = np.clip((features[predict_idx] - mean) / scale, -6.0, 6.0)
    center = np.average(z_train, axis=0, weights=weights)
    normalization = np.sqrt(features.shape[1])
    z_train = (z_train - center) / normalization
    z_predict = (z_predict - center) / normalization
    weighted = z_train * np.sqrt(weights[:, None])
    kernel = weighted @ weighted.T
    values, vectors = eigh(kernel, check_finite=False)
    values = np.maximum(values, 0.0)
    target = (2.0 * labels - 1.0) * np.sqrt(weights)
    coefficients = vectors @ ((vectors.T @ target)[:, None] /
                              (values[:, None] + np.asarray(alphas)[None, :]))
    return (z_predict @ weighted.T) @ coefficients


def _balanced_accuracy(y, prediction):
    return 0.5 * (np.mean(prediction[y == 0] == 0) +
                  np.mean(prediction[y == 1] == 1))


def fit_predict(train_x, train_y, test_x):
    y = np.asarray(train_y, dtype=np.int64).reshape(-1)
    n, nt = len(y), len(test_x)
    if nt == 0:
        return np.empty(0, dtype=np.int64)
    if np.unique(y).size == 1:
        return np.full(nt, y[0], dtype=np.int64)
    if np.min(np.bincount(y, minlength=2)) < 2:
        return np.full(nt, int(np.mean(y) >= 0.5), dtype=np.int64)
    covs, power = _prepare(train_x, test_x)
    train_indices = np.arange(n)
    blocks = np.array_split(train_indices, 5)
    if all(len(v) >= 10 and np.unique(y[v]).size == 2 for v in blocks):
        folds = [(np.setdiff1d(train_indices, v), v) for v in blocks]
    else:
        k = min(5, int(np.min(np.bincount(y, minlength=2))))
        folds = list(StratifiedKFold(k, shuffle=True, random_state=29).split(
            np.zeros(n), y))
    alphas = np.array([0.03, 0.3, 3.0, 30.0])
    oof = np.zeros((n, 3, len(alphas)))
    for fitting, validation in folds:
        families = _features(covs, power, fitting, train_indices, y)
        for family, features in enumerate(families):
            oof[validation, family, :] = _ridge_predictions(
                features, fitting, validation, y, alphas)
    strengths, quality, scales = [], [], []
    for family in range(3):
        scores = []
        for a in range(len(alphas)):
            scores.append(np.mean([
                _balanced_accuracy(y[v], (oof[v, family, a] >= 0).astype(int))
                for _, v in folds]))
        best = int(np.argmax(np.asarray(scores) +
                             1e-9 * np.arange(len(alphas))))
        strengths.append(best)
        quality.append(scores[best])
        scales.append(max(np.sqrt(np.mean(oof[:, family, best] ** 2)), 0.03))
    quality = np.asarray(quality)
    weights = np.array([0.45, 0.25, 0.30]) * np.exp(
        8.0 * (quality - quality.max()))
    weights /= weights.sum()
    all_indices = np.arange(n + nt)
    test_indices = np.arange(n, n + nt)
    families = _features(covs, power, train_indices, all_indices, y)
    combined = np.zeros(nt)
    for family, features in enumerate(families):
        prediction = _ridge_predictions(
            features, train_indices, test_indices, y,
            [alphas[strengths[family]]])[:, 0]
        combined += weights[family] * np.tanh(prediction / scales[family])
    return (combined >= 0.0).astype(np.int64)
