"""Held-out-bird acoustic-event detector.
Dataset attribution: Steinfath et al. (2021), DAS Bengalese finch data,
and Nicholson, Queen and Sober, Bengalese Finch Song Repository.
Modified here into a binary source-annotation detection procedure.
"""
import gc
import numpy as np
from scipy.signal import stft
from scipy.ndimage import uniform_filter1d
from sklearn.ensemble import HistGradientBoostingClassifier
_SEED = 20261031

def _finite_length(a):
    lo, hi = (0, int(a.shape[0]))
    while lo < hi:
        mid = (lo + hi) // 2
        if np.isfinite(a[mid]):
            lo = mid + 1
        else:
            hi = mid
    return lo

def _valid_bins(y):
    lo, hi = (0, int(y.shape[0]))
    while lo < hi:
        mid = (lo + hi) // 2
        if y[mid] >= 0:
            lo = mid + 1
        else:
            hi = mid
    return lo

def _edges():
    m0 = 2595.0 * np.log10(1.0 + 250.0 / 700.0)
    m1 = 2595.0 * np.log10(1.0 + 12000.0 / 700.0)
    mel = np.linspace(m0, m1, 25)
    hz = 700.0 * (10.0 ** (mel / 2595.0) - 1.0)
    e = np.rint(hz / 125.0).astype(np.int32)
    e[0], e[-1] = (2, 97)
    for i in range(1, 24):
        e[i] = max(e[i], e[i - 1] + 1)
    for i in range(23, 0, -1):
        e[i] = min(e[i], e[i + 1] - 1)
    return e
_BAND_EDGES = _edges()

def _features(row, nb):
    n = _finite_length(row)
    x = np.asarray(row[:n], dtype=np.float32)
    shifted = np.empty(n + 16, dtype=np.float32)
    shifted[:16] = 0.0
    shifted[16:] = x
    _, _, z = stft(shifted, fs=32000.0, window='hann', nperseg=256, noverlap=224, nfft=256, detrend=False, return_onesided=True, boundary='zeros', padded=True, axis=-1)
    z = z[:, 1:nb + 1]
    power = z.real * z.real + z.imag * z.imag
    bands = np.empty((nb, 24), dtype=np.float32)
    for k in range(24):
        a, b = (int(_BAND_EDGES[k]), int(_BAND_EDGES[k + 1]))
        bands[:, k] = np.log10(np.mean(power[a:b], axis=0) + 1e-10)
    bands -= np.percentile(bands, 20.0, axis=0)
    broad = np.log10(np.mean(power[2:97], axis=0) + 1e-10)
    broad -= np.percentile(broad, 20.0)
    out = np.empty((nb, 27), dtype=np.float32)
    out[:, :24] = bands
    out[:, 24] = broad
    out[:, 25] = uniform_filter1d(broad, size=5, mode='nearest')
    out[:, 26] = uniform_filter1d(broad, size=15, mode='nearest')
    return out

def _sample_map(counts, rows, seed):
    total = int(sum((counts[r] for r in rows)))
    take = min(60000, total)
    rng = np.random.default_rng(seed)
    chosen = np.sort(rng.choice(total, size=take, replace=False))
    result = {}
    offset = 0
    for r in rows:
        end = offset + counts[r]
        left = int(np.searchsorted(chosen, offset, side='left'))
        right = int(np.searchsorted(chosen, end, side='left'))
        result[r] = (chosen[left:right] - offset).astype(np.int64)
        offset = end
    return result

def _runs(mask):
    b = np.asarray(mask, dtype=np.int8)
    d = np.diff(np.concatenate((np.zeros(1, np.int8), b, np.zeros(1, np.int8))))
    return (np.flatnonzero(d == 1), np.flatnonzero(d == -1))

def _processed_intervals(prob, threshold, gap, minimum):
    starts, stops = _runs(prob >= threshold)
    if starts.size == 0:
        return np.empty((0, 2), dtype=np.int32)
    merged = []
    a, b = (int(starts[0]), int(stops[0]))
    for s, e in zip(starts[1:], stops[1:]):
        s, e = (int(s), int(e))
        if s - b <= gap:
            b = e
        else:
            if b - a >= minimum:
                merged.append((a, b))
            a, b = (s, e)
    if b - a >= minimum:
        merged.append((a, b))
    if not merged:
        return np.empty((0, 2), dtype=np.int32)
    return np.asarray(merged, dtype=np.int32)

def _reference_intervals(y):
    s, e = _runs(np.asarray(y) == 1)
    if s.size == 0:
        return np.empty((0, 2), dtype=np.int32)
    return np.column_stack((s, e)).astype(np.int32)

def _matches(pred, ref):
    npred, nref = (len(pred), len(ref))
    if npred == 0 or nref == 0:
        return 0
    adjacency = []
    for p in pred:
        onset_ok = np.abs(ref[:, 0] - p[0]) <= 20
        tolerance = np.maximum(20.0, 0.2 * (ref[:, 1] - ref[:, 0]))
        offset_ok = np.abs(ref[:, 1] - p[1]) <= tolerance + 1e-09
        adjacency.append(np.flatnonzero(onset_ok & offset_ok).tolist())
    matched = np.full(nref, -1, dtype=np.int32)

    def augment(i, seen):
        for j in adjacency[i]:
            if seen[j]:
                continue
            seen[j] = True
            old = int(matched[j])
            if old < 0 or augment(old, seen):
                matched[j] = i
                return True
        return False
    total = 0
    for i in range(npred):
        if augment(i, np.zeros(nref, dtype=bool)):
            total += 1
    return total

def _event_f1(pred, ref):
    denom = len(pred) + len(ref)
    if denom == 0:
        return 1.0
    return 2.0 * _matches(pred, ref) / float(denom)

def _classifier():
    return HistGradientBoostingClassifier(max_iter=80, max_leaf_nodes=15, learning_rate=0.1, l2_regularization=10.0, max_bins=128, early_stopping=False, random_state=_SEED)

def fit_predict(train_x, train_y, test_x, train_groups):
    del train_groups
    ntrain = int(train_x.shape[0])
    counts = [_valid_bins(train_y[r]) for r in range(ntrain)]
    validation_rows = list(range(0, ntrain, 5))
    validation_set = set(validation_rows)
    fitting_rows = [r for r in range(ntrain) if r not in validation_set]
    provisional_map = _sample_map(counts, fitting_rows, _SEED)
    final_map = _sample_map(counts, list(range(ntrain)), _SEED + 1)
    provisional_x, provisional_y = ([], [])
    final_x, final_y = ([], [])
    validation_features = []
    for r in range(ntrain):
        nb = counts[r]
        feat = _features(train_x[r], nb)
        labels = np.asarray(train_y[r, :nb], dtype=np.int8)
        idx = final_map[r]
        final_x.append(feat[idx])
        final_y.append(labels[idx])
        if r in validation_set:
            validation_features.append((r, feat, _reference_intervals(labels)))
        else:
            idx = provisional_map[r]
            provisional_x.append(feat[idx])
            provisional_y.append(labels[idx])
    px = np.concatenate(provisional_x, axis=0)
    py = np.concatenate(provisional_y, axis=0)
    fx = np.concatenate(final_x, axis=0)
    fy = np.concatenate(final_y, axis=0)
    del provisional_x, provisional_y, final_x, final_y
    provisional = _classifier()
    provisional.fit(px, py)
    del px, py
    validation = []
    for r, feat, reference in validation_features:
        probability = provisional.predict_proba(feat)[:, 1].astype(np.float32)
        validation.append((probability, reference))
    del validation_features, provisional, feat
    gc.collect()
    best_score = -1.0
    best_parameters = (0.3, 0, 5)
    for threshold in (0.3, 0.5, 0.7):
        for gap in (0, 4, 8):
            for minimum in (5, 10, 20):
                score = 0.0
                for probability, reference in validation:
                    pred = _processed_intervals(probability, threshold, gap, minimum)
                    score += _event_f1(pred, reference)
                score /= len(validation)
                if score > best_score:
                    best_score = score
                    best_parameters = (threshold, gap, minimum)
    del validation
    model = _classifier()
    model.fit(fx, fy)
    del fx, fy
    gc.collect()
    output_bins = int(test_x.shape[1] // 32)
    output = np.zeros((test_x.shape[0], output_bins), dtype=np.int8)
    threshold, gap, minimum = best_parameters
    for r in range(test_x.shape[0]):
        nb = min(_finite_length(test_x[r]) // 32, output_bins)
        if nb == 0:
            continue
        feat = _features(test_x[r], nb)
        probability = model.predict_proba(feat)[:, 1]
        intervals = _processed_intervals(probability, threshold, gap, minimum)
        for start, stop in intervals:
            output[r, int(start):int(stop)] = 1
    return output
