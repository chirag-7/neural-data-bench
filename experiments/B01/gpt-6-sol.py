import numpy as np
from scipy.ndimage import maximum_filter1d
from scipy.spatial.distance import cdist
from sklearn.decomposition import PCA
from sklearn.cluster import MiniBatchKMeans


def _detect(z, positions):
    n, c = z.shape
    dist = np.linalg.norm(positions[:, None, :] - positions[None, :, :], axis=2)
    neighbors = [np.flatnonzero(dist[j] <= 70) for j in range(c)]
    neg = -z
    nlocal = maximum_filter1d(neg, size=13, axis=0)
    plocal = maximum_filter1d(z, size=13, axis=0)
    nwide = maximum_filter1d(neg, size=41, axis=0)
    times, channels, heights = [], [], []
    for j in range(c):
        nearby_neg = np.max(nlocal[:, neighbors[j]], axis=1)
        keep = (neg[:, j] >= 3.25) & (neg[:, j] >= nearby_neg - 1e-5)
        t = np.flatnonzero(keep)
        times.append(t)
        channels.append(np.full(len(t), j, dtype=np.int32))
        heights.append(neg[t, j])
        nearby_pos = np.max(plocal[:, neighbors[j]], axis=1)
        opposite = np.max(nwide[:, neighbors[j]], axis=1)
        keep = (z[:, j] >= 3.6) & (z[:, j] >= nearby_pos - 1e-5)
        keep &= z[:, j] > 1.25 * opposite
        t = np.flatnonzero(keep)
        times.append(t)
        channels.append(np.full(len(t), j, dtype=np.int32))
        heights.append(z[t, j])
    t = np.concatenate(times)
    ch = np.concatenate(channels)
    h = np.concatenate(heights)
    valid = (t >= 16) & (t < n - 26)
    return t[valid], ch[valid], h[valid]


def _features(z, times, offsets):
    channels = np.arange(z.shape[1])
    f = z[times[:, None, None] + offsets[None, :, None],
          channels[None, None, :]].reshape(len(times), -1)
    f = f.astype(np.float32, copy=False)
    scale = np.maximum(1.0, np.linalg.norm(f, axis=1) / 22.0) ** 0.5
    return f / scale[:, None]


def sort(recording_uv, fs, channel_positions_um):
    x = np.asarray(recording_uv, dtype=np.float32)
    n, c = x.shape
    empty = np.empty((0, 2), dtype=np.int64)
    if n < 50 or c == 0:
        return empty
    med = np.median(x, axis=0)
    sigma = np.maximum(np.median(np.abs(x - med), axis=0) / 0.67448975, 0.1)
    z = np.nan_to_num((x - med) / sigma, nan=0.0, posinf=0.0, neginf=0.0)
    times, channels, heights = _detect(z, np.asarray(channel_positions_um))
    high = heights >= 4.4
    ht = times[high]
    if len(ht) < 25:
        return empty
    taps = np.array([-12, -9, -6, -4, -2, 0, 2, 4, 6, 9, 12, 17, 23])
    f = _features(z, ht, taps)
    pca = PCA(n_components=min(16, len(ht) - 1, f.shape[1]),
              svd_solver='randomized', iterated_power=2, random_state=0)
    embedded = pca.fit_transform(f).astype(np.float32)
    k = min(96, max(1, len(ht) // 75))
    if k == 1:
        labels = np.zeros(len(ht), dtype=np.int32)
    else:
        model = MiniBatchKMeans(n_clusters=k, batch_size=2048, n_init=3,
                                max_iter=120, random_state=0)
        labels = model.fit_predict(embedded)
    offsets = np.arange(-16, 26)
    all_channels = np.arange(c)
    wave = z[ht[:, None, None] + offsets[None, :, None],
             all_channels[None, None, :]]
    counts = np.bincount(labels, minlength=k)
    templates = np.zeros((k, len(offsets), c), dtype=np.float32)
    for j in range(k):
        if counts[j]:
            templates[j] = wave[labels == j].mean(axis=0)
    flat = templates.reshape(k, -1)
    norms = np.linalg.norm(flat, axis=1)
    cosine = (flat @ flat.T) / np.maximum(norms[:, None] * norms[None, :], 1e-6)
    ratio = norms[:, None] / np.maximum(norms[None, :], 1e-6)
    parent = np.arange(k)

    def root(j):
        while parent[j] != j:
            parent[j] = parent[parent[j]]
            j = parent[j]
        return j

    for i in range(k):
        if counts[i] < 8:
            continue
        for j in range(i + 1, k):
            if counts[j] >= 8 and cosine[i, j] > 0.94 and 0.6 < ratio[i, j] < 1.67:
                parent[root(j)] = root(i)
    groups = {}
    for j in range(k):
        groups.setdefault(root(j), []).append(j)
    merged, centers = [], []
    for members in groups.values():
        total = int(np.sum(counts[members]))
        if total < 20:
            continue
        template = np.tensordot(counts[members], templates[members], axes=(0, 0)) / total
        energy = np.sum(template * template, axis=0)
        top = np.argsort(energy)[-min(8, c):]
        if np.max(np.abs(template)) < 3.3 or np.sqrt(np.sum(energy[top])) < 7.5:
            continue
        masked = np.zeros_like(template)
        masked[:, top] = template[:, top]
        merged.append(masked)
        centers.append(np.mean(embedded[np.isin(labels, members)], axis=0))
    if not merged:
        return empty
    tm = np.asarray(merged, dtype=np.float32)
    centers = np.asarray(centers, dtype=np.float32)
    tn2 = np.sum(tm * tm, axis=(1, 2))
    tn = np.sqrt(tn2)
    all_features = _features(z, times, taps)
    projected = pca.transform(all_features).astype(np.float32)
    distances = cdist(projected, centers, metric='sqeuclidean')
    choices = min(5, len(tm))
    candidates = np.argpartition(distances, choices - 1, axis=1)[:, :choices]
    best_unit = np.full(len(times), -1, dtype=np.int32)
    best_quality = np.full(len(times), -np.inf, dtype=np.float32)
    best_score = np.zeros(len(times), dtype=np.float32)
    best_amplitude = np.zeros(len(times), dtype=np.float32)
    for start in range(0, len(times), 768):
        end = min(start + 768, len(times))
        t = times[start:end]
        w = z[t[:, None, None] + offsets[None, :, None],
              all_channels[None, None, :]]
        for rank in range(choices):
            unit = candidates[start:end, rank]
            dot = np.einsum('ijk,ijk->i', w, tm[unit], optimize=True)
            score = dot / tn[unit]
            amplitude = dot / tn2[unit]
            quality = score - 1.2 * np.abs(np.log(np.clip(amplitude, 0.1, 10.0)))
            better = quality > best_quality[start:end]
            best_quality[start:end][better] = quality[better]
            best_unit[start:end][better] = unit[better]
            best_score[start:end][better] = score[better]
            best_amplitude[start:end][better] = amplitude[better]
    valid = (best_score >= 6.4) & (best_amplitude >= 0.35)
    valid &= best_amplitude <= 2.5
    rows = []
    refractory = max(1, int(round(0.00075 * fs)))
    for unit in range(len(tm)):
        indices = np.flatnonzero(valid & (best_unit == unit))
        indices = indices[np.argsort(-best_score[indices], kind='stable')]
        occupied = np.zeros(n, dtype=bool)
        selected = []
        for index in indices:
            t = int(times[index])
            lo, hi = max(0, t - refractory), min(n, t + refractory + 1)
            if not occupied[lo:hi].any():
                selected.append(t)
                occupied[lo:hi] = True
        if len(selected) >= 15:
            rows.extend((t, unit) for t in selected)
    if not rows:
        return empty
    result = np.asarray(rows, dtype=np.int64)
    order = np.lexsort((result[:, 1], result[:, 0]))
    return result[order]
