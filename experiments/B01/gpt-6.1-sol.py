import numpy as np
from scipy.ndimage import maximum_filter1d
from scipy.fft import rfft, irfft, next_fast_len
from sklearn.cluster import KMeans


def _one_mode(a, b):
    v = np.concatenate((a, b)).astype(np.float64)
    if len(v) > 1600:
        v = v[np.linspace(0, len(v) - 1, 1600).astype(int)]
    scale = np.std(v) + 1e-9
    center = np.mean(v)
    v = np.clip((v - center) / scale, -5, 5)
    m1 = (np.mean(a) - center) / scale
    m2 = (np.mean(b) - center) / scale
    p = np.clip(len(a) / (len(a) + len(b)), .05, .95)
    var = max(.1, 1 - p * (1 - p) * (m1 - m2) ** 2)
    for _ in range(28):
        l1 = np.log(p) - (v - m1) ** 2 / (2 * var)
        l2 = np.log(1 - p) - (v - m2) ** 2 / (2 * var)
        q = 1 / (1 + np.exp(np.clip(l2 - l1, -40, 40)))
        w1, w2 = q.sum() + 1e-8, (1 - q).sum() + 1e-8
        m1, m2 = np.dot(q, v) / w1, np.dot(1 - q, v) / w2
        p = np.clip(w1 / len(v), .025, .975)
        var = max(.025, np.mean(q * (v - m1) ** 2 + (1 - q) * (v - m2) ** 2))
    l1 = np.log(p) - (v - m1) ** 2 / (2 * var)
    l2 = np.log(1 - p) - (v - m2) ** 2 / (2 * var)
    ll2 = np.logaddexp(l1, l2).sum() - .5 * len(v) * np.log(var)
    v0 = np.var(v) + 1e-9
    ll1 = -.5 * len(v) * (1 + np.log(v0))
    gain = ll2 - ll1 - np.log(len(v))
    return abs(m1 - m2) / np.sqrt(var) < 2.7 or gain < 8


def _merge(f, z, labels):
    groups = [np.flatnonzero(labels == k) for k in range(labels.max() + 1)]
    groups = [g for g in groups if len(g)]
    means = np.array([f[g].mean(axis=0) for g in groups])
    means /= np.linalg.norm(means, axis=1, keepdims=True) + 1e-10
    similarity = means @ means.T
    np.fill_diagonal(similarity, -np.inf)
    alive = np.ones(len(groups), dtype=bool)
    while len(groups) > 1:
        i, j = np.unravel_index(np.argmax(similarity), similarity.shape)
        if similarity[i, j] < .72:
            break
        ga, gb = groups[i], groups[j]
        direction = z[ga].mean(axis=0) - z[gb].mean(axis=0)
        direction /= np.linalg.norm(direction) + 1e-12
        merge = _one_mode(z[ga] @ direction, z[gb] @ direction)
        if not merge:
            similarity[i, j] = similarity[j, i] = -np.inf
            continue
        groups[i] = np.concatenate((ga, gb))
        groups[j] = np.empty(0, dtype=int)
        alive[j] = False
        means[i] = f[groups[i]].mean(axis=0)
        means[i] /= np.linalg.norm(means[i]) + 1e-12
        row = means @ means[i]
        row[~alive] = -np.inf
        row[i] = -np.inf
        similarity[i, :] = row
        similarity[:, i] = row
        similarity[j, :] = similarity[:, j] = -np.inf
    return [g for g in groups if len(g) >= 8]


def _templates(clips, groups, h):
    templates = []
    for g in groups:
        if len(g) < 8:
            continue
        if len(g) > 1200:
            g = g[np.linspace(0, len(g) - 1, 1200).astype(int)]
        a = clips[g]
        t = np.median(a, axis=0)
        t += np.mean(np.clip(a - t, -2, 2), axis=0)
        peak = -t.min()
        if peak < 2.5:
            continue
        trough = np.unravel_index(np.argmin(t[h-6:h+7]), t[h-6:h+7].shape)[0] + h - 6
        shift = h - trough
        t = np.roll(t, shift, axis=0)
        if shift > 0:
            t[:shift] = 0
        elif shift < 0:
            t[shift:] = 0
        support = np.max(np.abs(t), axis=0) >= max(.45, .10 * peak)
        t[:, ~support] = 0
        u, s, vh = np.linalg.svd(t, full_matrices=False)
        t = (u[:, :3] * s[:3]) @ vh[:3]
        templates.append(t.astype(np.float32))
    return np.asarray(templates, dtype=np.float32)


def _match(x, templates, fs):
    k, length, channels = templates.shape
    n, h = len(x), length // 2
    nf = next_fast_len(n + length - 1)
    norms = np.sqrt(np.sum(templates ** 2, axis=(1, 2))) + 1e-9
    scores = np.empty((k, n), dtype=np.float32)
    threshold = np.empty(k)
    for j, t in enumerate(templates):
        u, s, vh = np.linalg.svd(t, full_matrices=False)
        y = x @ vh[:3].T
        fy = rfft(y, n=nf, axis=0, workers=1)
        ft = rfft(u[:, :3] * s[:3], n=nf, axis=0, workers=1)
        raw = irfft(np.sum(fy * np.conj(ft), axis=1), n=nf, workers=1) / norms[j]
        scores[j, :h] = raw[-h:]
        scores[j, h:] = raw[:n-h]
        v = scores[j, ::max(1, n // 20000)]
        noise = np.median(np.abs(v - np.median(v))) / .67448975
        threshold[j] = max(4.5 * noise, .38 * norms[j], 1e-4)
    scores[:, :h] = scores[:, n-h:] = -1e9
    nc = next_fast_len(2 * length - 1)
    ft = rfft(templates, n=nc, axis=1, workers=1)
    cross = np.empty((k, k, 2 * length - 1), dtype=np.float32)
    for j in range(k):
        raw = irfft(np.sum(ft[j][None] * np.conj(ft), axis=2), n=nc, axis=1, workers=1)
        cross[j] = np.concatenate((raw[:, -(length-1):], raw[:, :length]), axis=1) / norms[:, None]
    events = []
    refractory = max(1, int(.0008 * fs))
    peak_width = 2 * max(1, int(.00025 * fs)) + 1
    for _ in range(3):
        candidates = []
        for j in range(k):
            maxima = maximum_filter1d(scores[j], size=peak_width, mode='constant', cval=-1e9)
            times = np.flatnonzero((scores[j] >= maxima) & (scores[j] > threshold[j]))
            candidates.extend((float(scores[j, t]), j, int(t)) for t in times)
        candidates.sort(reverse=True)
        accepted = 0
        for _, j, t in candidates:
            lo, hi = max(h, t - 2), min(n - h, t + 3)
            if lo >= hi:
                continue
            t = lo + int(np.argmax(scores[j, lo:hi]))
            value = float(scores[j, t])
            if value < threshold[j]:
                continue
            amplitude = min(2.5, value / norms[j])
            events.append((t, j))
            accepted += 1
            lo, hi = max(0, t - length + 1), min(n, t + length)
            offset = lo - t + length - 1
            scores[:, lo:hi] -= amplitude * cross[j, :, offset:offset + hi - lo]
            scores[j, max(0, t-refractory):min(n, t+refractory+1)] = -1e9
        if not accepted:
            break
    return np.asarray(events, dtype=np.int64).reshape(-1, 2)


def sort(recording_uv, fs, channel_positions_um):
    x = np.array(recording_uv, dtype=np.float32, copy=True)
    n, channels = x.shape
    h = max(12, int(round(.001 * fs)))
    if n < 2 * h + 1:
        return np.empty((0, 2), dtype=np.int64)
    x -= np.median(x, axis=0)
    scale = np.median(np.abs(x), axis=0) / .67448975
    x /= np.maximum(scale, 1e-3)
    sample = np.clip(x[::7], -3, 3)
    covariance = sample.T @ sample / len(sample)
    eig, vec = np.linalg.eigh(covariance)
    whitening = (vec * (1 / np.sqrt(np.maximum(eig, .10)))) @ vec.T
    x = np.asarray(x @ whitening, dtype=np.float32)
    scale = np.median(np.abs(x[::7]), axis=0) / .67448975
    x /= np.maximum(scale, .1)
    positions = np.asarray(channel_positions_um, dtype=float)
    distance = np.linalg.norm(positions[:, None] - positions[None, :], axis=2)
    positive = np.where(distance > 0, distance, np.inf).min(axis=1)
    finite = positive[np.isfinite(positive)]
    radius = max(60., 2.5 * np.median(finite)) if len(finite) else np.inf
    maxima = maximum_filter1d(-x, size=2 * max(2, int(.0003 * fs)) + 1, axis=0)
    times, amplitudes = [], []
    for c in range(channels):
        t = np.flatnonzero((-x[:, c] >= maxima[:, c]) & (-x[:, c] > 4.2))
        t = t[(t >= h) & (t < n-h)]
        neighbors = np.flatnonzero(distance[c] <= radius)
        if len(t):
            t = t[-x[t, c] >= np.max(maxima[t[:, None], neighbors], axis=1)]
            times.extend(t.tolist())
            amplitudes.extend((-x[t, c]).tolist())
    del maxima
    times = np.asarray(times, dtype=np.int64)
    if len(times) < 8:
        return np.empty((0, 2), dtype=np.int64)
    if len(times) > 20000:
        times = times[np.argsort(amplitudes)[-20000:]]
    times = np.unique(times)
    offsets = np.arange(-h, h + 1)
    clips = x[times[:, None] + offsets]
    waves = clips.transpose(0, 2, 1).reshape(-1, 2*h+1)
    waves = waves[::max(1, len(waves) // 14000)]
    eig, basis = np.linalg.eigh(waves.T @ waves / len(waves))
    basis = basis[:, -5:]
    features = np.einsum('ntc,tp->ncp', clips, basis, optimize=True).reshape(len(times), -1)
    features /= np.maximum(np.linalg.norm(features, axis=1, keepdims=True), 1e-8)
    centered = features - features.mean(axis=0)
    eig, basis = np.linalg.eigh(centered.T @ centered)
    z = np.asarray(centered @ basis[:, -min(24, len(eig)):], dtype=np.float32)
    count = min(80, max(2, len(times) // 35))
    labels = KMeans(n_clusters=count, n_init=1, max_iter=80, random_state=0).fit_predict(z)
    groups = _merge(features, z, labels)
    templates = _templates(clips, groups, h)
    del clips, features, centered, z, waves
    if len(templates) == 0:
        return np.empty((0, 2), dtype=np.int64)
    events = _match(x, templates, fs)
    if len(events) == 0:
        return events
    clips = x[events[:, 0, None] + offsets]
    groups = [np.flatnonzero(events[:, 1] == j) for j in range(len(templates))]
    refined = _templates(clips, groups, h)
    del clips
    if len(refined):
        events = _match(x, refined, fs)
    if not len(events):
        return np.empty((0, 2), dtype=np.int64)
    units, counts = np.unique(events[:, 1], return_counts=True)
    events = events[np.isin(events[:, 1], units[counts >= 8])]
    if not len(events):
        return np.empty((0, 2), dtype=np.int64)
    events = np.unique(events, axis=0)
    events[:, 1] = np.unique(events[:, 1], return_inverse=True)[1]
    return events[np.lexsort((events[:, 1], events[:, 0]))].astype(np.int64)
