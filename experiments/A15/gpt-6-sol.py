import numpy as np
from scipy import fft, ndimage, signal, sparse
from scipy.sparse.csgraph import maximum_bipartite_matching
from sklearn.ensemble import HistGradientBoostingClassifier

_WINDOW = signal.windows.hann(256, sym=False).astype(np.float32)
_EDGES = np.rint(np.geomspace(2, 97, 25)).astype(int)
for _j in range(1, len(_EDGES)):
    _EDGES[_j] = max(_EDGES[_j], _EDGES[_j - 1] + 1)
_TINY = np.finfo(np.float32).tiny


def _valid_samples(row):
    invalid = np.flatnonzero(~np.isfinite(row))
    return int(invalid[0]) if invalid.size else row.size


def _features(wave):
    count = len(wave) // 32
    padded = np.pad(wave[:count * 32], (112, 144), mode='reflect')
    frames = np.lib.stride_tricks.sliding_window_view(padded, 256)[::32][:count]
    spectrum = fft.rfft(frames * _WINDOW, axis=1, workers=1)
    power = (spectrum.real * spectrum.real + spectrum.imag * spectrum.imag).astype(np.float32)
    selected = power[:, 2:97]
    bands = np.add.reduceat(selected, _EDGES[:-1] - 2, axis=1)
    log_bands = np.log(np.maximum(bands, _TINY))
    log_bands -= np.percentile(log_bands, 20, axis=0)
    energy = np.log(np.maximum(selected.sum(axis=1), _TINY))
    energy -= np.percentile(energy, 20)
    smooth5 = ndimage.uniform_filter1d(energy, 5, mode='nearest')
    smooth15 = ndimage.uniform_filter1d(energy, 15, mode='nearest')
    change = np.zeros_like(energy)
    change[5:] = smooth5[5:] - smooth5[:-5]
    return np.column_stack((np.clip(log_bands, -8, 16),
                            np.clip(energy, -8, 16),
                            np.clip(smooth5, -8, 16),
                            np.clip(smooth15, -8, 16),
                            np.clip(change, -8, 8))).astype(np.float32)


def _runs(mask):
    edges = np.flatnonzero(np.diff(np.pad(mask.astype(np.int8), (1, 1))))
    return edges.reshape(-1, 2)


def _segments(probability, threshold, gap, minimum):
    runs = _runs(probability >= threshold)
    if len(runs) == 0:
        return runs
    merged = [[int(runs[0, 0]), int(runs[0, 1])]]
    for start, stop in runs[1:]:
        if start - merged[-1][1] <= gap:
            merged[-1][1] = int(stop)
        else:
            merged.append([int(start), int(stop)])
    return np.asarray([pair for pair in merged if pair[1] - pair[0] >= minimum],
                      dtype=np.int32).reshape(-1, 2)


def _event_f1(predicted, reference):
    p, r = len(predicted), len(reference)
    if p + r == 0:
        return 1.0
    if p == 0 or r == 0:
        return 0.0
    starts = reference[:, 0]
    row_ids, col_ids = [], []
    for i, (start, stop) in enumerate(predicted):
        left = np.searchsorted(starts, start - 20, side='left')
        right = np.searchsorted(starts, start + 20, side='right')
        for j in range(left, right):
            duration = reference[j, 1] - reference[j, 0]
            if abs(int(stop) - int(reference[j, 1])) <= max(20, 0.2 * duration):
                row_ids.append(i)
                col_ids.append(j)
    if not row_ids:
        return 0.0
    graph = sparse.csr_matrix((np.ones(len(row_ids), dtype=np.int8),
                               (row_ids, col_ids)), shape=(p, r))
    matches = maximum_bipartite_matching(graph, perm_type='column')
    return 2.0 * np.count_nonzero(matches >= 0) / (p + r)


def _fit_model(sampled, indices):
    features = np.concatenate([sampled[i][0] for i in indices], axis=0)
    labels = np.concatenate([sampled[i][1] for i in indices], axis=0)
    model = HistGradientBoostingClassifier(max_iter=80, max_leaf_nodes=15,
                                           learning_rate=0.1, l2_regularization=10,
                                           max_bins=128, early_stopping=False,
                                           random_state=20261031)
    model.fit(features, labels)
    return model


def fit_predict(train_x, train_y, test_x, train_groups):
    rng = np.random.default_rng(20261031)
    validation = list(range(0, len(train_x), 5))
    validation_set = set(validation)
    sampled = []
    valid_features = {}
    valid_references = {}
    for i, row in enumerate(train_x):
        samples = _valid_samples(row)
        features = _features(row[:samples])
        labels = np.asarray(train_y[i, :len(features)], dtype=np.int8)
        base = rng.choice(len(features), size=min(850, len(features)), replace=False)
        boundaries = np.flatnonzero(labels[1:] != labels[:-1]) + 1
        if len(boundaries):
            nearby = boundaries[rng.integers(len(boundaries), size=150)]
            nearby += rng.integers(-15, 16, size=len(nearby))
            indices = np.unique(np.r_[base, np.clip(nearby, 0, len(features) - 1)])
        else:
            indices = base
        sampled.append((features[indices], labels[indices]))
        if i in validation_set:
            valid_features[i] = features
            valid_references[i] = _runs(labels == 1)
    provisional = _fit_model(sampled, [i for i in range(len(train_x))
                                       if i not in validation_set])
    valid_probabilities = {i: provisional.predict_proba(valid_features[i])[:, 1]
                           for i in validation}
    best_score = -1.0
    best_settings = (0.5, 4, 10)
    for threshold in (0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8):
        for gap in (0, 4, 8):
            for minimum in (5, 10, 20):
                score = np.mean([
                    _event_f1(_segments(valid_probabilities[i], threshold, gap, minimum),
                              valid_references[i]) for i in validation
                ])
                if score > best_score + 1e-12:
                    best_score = score
                    best_settings = (threshold, gap, minimum)
    model = _fit_model(sampled, range(len(train_x)))
    output = np.zeros((len(test_x), test_x.shape[1] // 32), dtype=np.int8)
    for i, row in enumerate(test_x):
        samples = _valid_samples(row)
        features = _features(row[:samples])
        probability = model.predict_proba(features)[:, 1]
        for start, stop in _segments(probability, *best_settings):
            output[i, start:stop] = 1
    return output