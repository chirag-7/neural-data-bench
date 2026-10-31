import numpy as np
from scipy.fft import rfft
from scipy.ndimage import uniform_filter1d
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import maximum_bipartite_matching
from sklearn.ensemble import HistGradientBoostingClassifier
import gc

# Source attribution: Steinfath, Palacios-Munoz, Rottschaefer, Yuezak and
# Clemens (2021), DAS, https://doi.org/10.25625/ENKMJS (CC0-1.0).
# Underlying recordings: Nicholson, Queen and Sober,
# https://doi.org/10.6084/m9.figshare.4805749 (CC BY 4.0).
# Modification notice: waveforms are transformed into spectral/envelope
# features; merged annotations supervise binary acoustic-event prediction.


def _runs(mask):
    d = np.diff(np.r_[False, mask, False].astype(np.int8))
    return np.column_stack((np.flatnonzero(d == 1),
                            np.flatnonzero(d == -1))).astype(np.int32)


def _merge(events, gap):
    if len(events) < 2 or gap == 0:
        return events
    breaks = np.r_[True, events[1:, 0] - events[:-1, 1] > gap]
    starts = np.flatnonzero(breaks)
    ends = np.r_[starts[1:] - 1, len(events) - 1]
    return np.column_stack((events[starts, 0], events[ends, 1]))


def _event_f1(pred, ref):
    if len(pred) == 0 or len(ref) == 0:
        return float(len(pred) == len(ref))
    tolerance = np.maximum(20.0, .2 * (ref[:, 1] - ref[:, 0]))
    edges = ((np.abs(pred[:, None, 0] - ref[None, :, 0]) <= 20) &
             (np.abs(pred[:, None, 1] - ref[None, :, 1]) <=
              tolerance[None, :] + 1e-9))
    nr, nc = edges.sum(axis=1), edges.sum(axis=0)
    if nr.max() <= 1:
        tp = np.count_nonzero(nc)
    elif nc.max() <= 1:
        tp = np.count_nonzero(nr)
    else:
        assignment = maximum_bipartite_matching(csr_matrix(edges),
                                                perm_type='column')
        tp = np.count_nonzero(assignment >= 0)
    return 2.0 * tp / (len(pred) + len(ref))


def _features(row):
    n = int(np.count_nonzero(np.isfinite(row))) // 32
    if n == 0:
        return None
    x = np.asarray(row[:n * 32], dtype=np.float32)
    padded = np.pad(x, (112, 112), mode='reflect')
    windows = np.lib.stride_tricks.sliding_window_view(padded, 256)[::32]
    window = np.hanning(256).astype(np.float32)
    z = rfft(windows * window, axis=1, workers=1)
    power = (z.real * z.real + z.imag * z.imag)[:, 2:97]
    edges = np.linspace(0, 95, 25, dtype=np.int32)
    bands = np.add.reduceat(power, edges[:-1], axis=1)
    bands /= np.diff(edges).astype(np.float32)[None, :]
    logbands = 10.0 * np.log10(np.maximum(bands, 1e-20))
    floor = np.percentile(logbands, 20, axis=0).astype(np.float32)
    normalized = np.clip(logbands - floor, -30, 80)
    energy = 10.0 * np.log10(np.maximum(power.mean(axis=1), 1e-20))
    low, high = np.percentile(energy, [20, 95])
    relative = energy - low
    peakrelative = energy - high
    scale = max(float(high - low), 8.0)
    scalars = [relative, peakrelative, relative * (20.0 / scale)]
    for width in (5, 15, 51, 201):
        scalars.append(uniform_filter1d(relative, width, mode='nearest'))
        scalars.append(uniform_filter1d(peakrelative, width, mode='nearest'))
    indices = np.arange(n)
    for shift in (-20, -10, -5, -2, 2, 5, 10, 20):
        scalars.append(relative[np.clip(indices + shift, 0, n - 1)])
    proportions = bands / np.maximum(bands.sum(axis=1, keepdims=True), 1e-20)
    entropy = -(proportions * np.log(np.maximum(proportions, 1e-12))).sum(1)
    centroid = (proportions * np.arange(24, dtype=np.float32)).sum(1) / 24
    flatness = logbands.mean(1) - 10 * np.log10(
        np.maximum(bands.mean(1), 1e-20))
    scalars.extend([entropy, centroid, flatness, proportions.max(1),
                    proportions[:, :6].sum(1), proportions[:, 12:].sum(1)])
    change = np.diff(normalized, axis=0, prepend=normalized[:1])
    scalars.append(np.maximum(change, 0).mean(1))
    scalars.append(np.maximum(-change, 0).mean(1))
    scalar_features = np.column_stack(scalars).astype(np.float32)
    smooth = uniform_filter1d(normalized, 7, axis=0, mode='nearest')
    broad = (normalized[:, ::2] + normalized[:, 1::2]) * .5
    broad = uniform_filter1d(broad, 25, axis=0, mode='nearest')
    features = np.column_stack((normalized, smooth, broad, scalar_features))
    return np.nan_to_num(features, copy=False).astype(np.float32, copy=False)


def _model(small=False):
    return HistGradientBoostingClassifier(
        max_iter=110 if small else 140,
        max_leaf_nodes=15 if small else 23,
        learning_rate=.075, min_samples_leaf=60,
        l2_regularization=20.0, max_bins=128,
        early_stopping=False, random_state=20261031)


def _fit_predict(train_x, train_y, test_x):
    rng = np.random.default_rng(20261031)
    sample_x, sample_y, sample_rows = [], [], []
    validation_x, references = [], []
    scalar_start = 60
    for row_id in range(len(train_x)):
        features = _features(train_x[row_id])
        if features is None:
            continue
        labels = np.asarray(train_y[row_id, :len(features)])
        valid = np.flatnonzero(labels >= 0)
        uniform = rng.choice(valid, min(2200, len(valid)), replace=False)
        transitions = np.r_[False, labels[1:] != labels[:-1]]
        nearby = uniform_filter1d(transitions.astype(np.float32), 41,
                                  mode='nearest') > 0
        candidates = np.flatnonzero(nearby & (labels >= 0))
        boundary = rng.choice(candidates, min(600, len(candidates)),
                              replace=False)
        selected = np.union1d(uniform, boundary)
        sample_x.append(features[selected])
        sample_y.append(labels[selected])
        sample_rows.append(np.full(len(selected), row_id, dtype=np.int16))
        if row_id % 5 == 0:
            validation_x.append(features)
            references.append(_runs(labels == 1))
    x = np.concatenate(sample_x)
    y = np.concatenate(sample_y)
    rows = np.concatenate(sample_rows)
    del sample_x, sample_y, sample_rows
    fit_mask = rows % 5 != 0
    spectral = _model().fit(x[fit_mask], y[fit_mask])
    envelope = _model(True).fit(x[fit_mask, scalar_start:], y[fit_mask])
    spectral_prob = [spectral.predict_proba(v)[:, 1] for v in validation_x]
    envelope_prob = [envelope.predict_proba(v[:, scalar_start:])[:, 1]
                     for v in validation_x]
    best_score = -1.0
    best = (.5, 1, .5, 4, 10)
    for weight in (.5, .25, .75):
        combined = [weight * p + (1 - weight) * q
                    for p, q in zip(spectral_prob, envelope_prob)]
        for width in (1, 3, 5):
            probabilities = [uniform_filter1d(p, width, mode='nearest')
                             if width > 1 else p for p in combined]
            for threshold in (.3, .4, .5, .6, .7):
                raw = [_runs(p >= threshold) for p in probabilities]
                for gap in (0, 4, 8, 12):
                    merged = [_merge(e, gap) for e in raw]
                    for minimum in (5, 10, 20):
                        scores = []
                        for events, ref in zip(merged, references):
                            keep = events[:, 1] - events[:, 0] >= minimum
                            scores.append(_event_f1(events[keep], ref))
                        score = float(np.mean(scores))
                        if score > best_score + 1e-12:
                            best_score = score
                            best = (weight, width, threshold, gap, minimum)
    del spectral, envelope, validation_x, spectral_prob, envelope_prob
    gc.collect()
    spectral = _model().fit(x, y)
    envelope = _model(True).fit(x[:, scalar_start:], y)
    del x, y, rows
    gc.collect()
    weight, width, threshold, gap, minimum = best
    output = np.zeros((len(test_x), test_x.shape[1] // 32), dtype=np.int8)
    for row_id in range(len(test_x)):
        features = _features(test_x[row_id])
        if features is None:
            continue
        p = spectral.predict_proba(features)[:, 1]
        q = envelope.predict_proba(features[:, scalar_start:])[:, 1]
        probability = weight * p + (1 - weight) * q
        if width > 1:
            probability = uniform_filter1d(probability, width, mode='nearest')
        events = _merge(_runs(probability >= threshold), gap)
        for start, stop in events:
            if stop - start >= minimum:
                output[row_id, start:stop] = 1
    return output


def fit_predict(train_x, train_y, test_x, train_groups=None):
    # Restrict native numerical pools, including sklearn's OpenMP pool.
    try:
        from sklearn.utils.parallel import _get_threadpool_controller
        context = _get_threadpool_controller().limit(limits=1)
    except ImportError:
        from sklearn.utils.fixes import threadpool_limits
        context = threadpool_limits(limits=1)
    with context:
        return _fit_predict(train_x, train_y, test_x)
