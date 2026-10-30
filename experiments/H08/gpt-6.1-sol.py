import numpy as np
from scipy import signal, ndimage
from sklearn.ensemble import HistGradientBoostingClassifier


def _features(night):
    x = np.nan_to_num(np.asarray(night, dtype=np.float32),
                      nan=0.0, posinf=0.0, neginf=0.0)
    x = x - np.median(x, axis=1, keepdims=True)
    f, _, spec = signal.spectrogram(
        x, fs=100, window='hann', nperseg=400, noverlap=200,
        nfft=512, detrend='constant', scaling='density', axis=-1)
    psd = spec.mean(axis=-1)
    df = f[1] - f[0]
    edges = [.5, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12,
             13, 14, 15, 16, 18, 20, 25, 30, 40, 49]
    fine = list(zip(edges[:-1], edges[1:]))
    broad = [(.5, 4), (4, 8), (8, 12), (12, 16),
             (16, 30), (.5, 40)]
    bands = fine + broad
    masks = [(f >= lo) & (f < hi) for lo, hi in bands]
    bp = np.column_stack([psd[:, m].sum(axis=1) * df for m in masks])
    lp = np.log10(bp + 1e-10)
    parts = [lp, lp[:, :-1] - lp[:, -1:]]
    for m in masks[len(fine):len(fine) + 5]:
        a = np.log10(spec[:, m, :].sum(axis=1) * df + 1e-10)
        parts.append(np.column_stack([
            a.std(axis=1), a.max(axis=1) - a.mean(axis=1),
            np.percentile(a, 90, axis=1) - np.percentile(a, 10, axis=1)]))
    keep = (f >= .5) & (f < 40)
    p = psd[:, keep].astype(np.float64) + 1e-12
    p /= p.sum(axis=1, keepdims=True)
    entropy = -(p * np.log(p)).sum(axis=1) / np.log(p.shape[1])
    flatness = np.log(p.mean(axis=1)) - np.log(p).mean(axis=1)
    cumulative = np.cumsum(p, axis=1)
    spectral_edges = [f[keep][(cumulative >= q).argmax(axis=1)]
                      for q in (.5, .9, .95)]
    m = (f >= 2) & (f <= 30)
    lf = np.log(f[m]); lf -= lf.mean()
    slope = (np.log(psd[:, m] + 1e-12) @ lf) / (lf @ lf)
    entropy_index = sum(a.shape[1] for a in parts)
    parts.append(np.column_stack([entropy, flatness] + spectral_edges + [slope]))
    sos = signal.butter(3, [.5, 35], btype='bandpass', fs=100, output='sos')
    z = signal.sosfiltfilt(sos, x, axis=-1).astype(np.float32)
    z -= z.mean(axis=1, keepdims=True)
    sd = z.std(axis=1) + 1e-6
    d = np.diff(z, axis=1)
    ds = d.std(axis=1) + 1e-6
    dds = np.diff(d, axis=1).std(axis=1) + 1e-6
    az = np.abs(z)
    quant = np.percentile(az, [50, 90, 99], axis=1).T
    standardized = np.clip(z / sd[:, None], -12, 12)
    amp = np.column_stack([
        np.log10(sd), np.log10(az.mean(axis=1) + 1e-6),
        np.log10(ds), np.log10(np.abs(d).mean(axis=1) + 1e-6),
        np.log(ds / sd), np.log(dds * sd / (ds * ds)),
        np.log10(quant[:, 0] + 1e-6),
        np.log((quant[:, 1] + 1e-6) / (quant[:, 0] + 1e-6)),
        np.log((quant[:, 2] + 1e-6) / (quant[:, 1] + 1e-6)),
        (standardized ** 4).mean(axis=1),
        (standardized ** 3).mean(axis=1),
        ((z[:, 1:] >= 0) != (z[:, :-1] >= 0)).mean(axis=1)])
    amp_index = sum(a.shape[1] for a in parts)
    parts.append(amp)
    base = np.nan_to_num(np.column_stack(parts), nan=0, posinf=20, neginf=-20)
    med = np.median(base, axis=0)
    spread = np.percentile(base, 75, axis=0) - np.percentile(base, 25, axis=0)
    normalized = np.clip((base - med) / np.maximum(spread, .15), -8, 8)
    nb = len(bands); nf = len(fine)
    core_indices = np.r_[np.arange(nf, nb),
                         np.arange(nb + nf, nb + nf + 5),
                         entropy_index, entropy_index + 5,
                         amp_index, amp_index + 4].astype(int)
    norm_indices = np.unique(np.r_[np.arange(nb), core_indices,
                                   np.arange(amp_index, amp_index + 12)])
    core = np.column_stack([base[:, core_indices],
                            normalized[:, nf:nb]])
    t = np.linspace(0, 1, len(x))
    clock = np.column_stack([t, t * t, np.sin(2 * np.pi * t),
                             np.cos(2 * np.pi * t)])
    context = [ndimage.uniform_filter1d(core, size=w, axis=0, mode='nearest')
               for w in (3, 7, 21, 61)]
    features = np.column_stack([base, normalized[:, norm_indices]] + context + [clock])
    return features.astype(np.float32), np.column_stack([core, clock]).astype(np.float32)


def _fit(x, y, iterations, meta=False):
    counts = np.bincount(y, minlength=5).astype(float)
    weights = (len(y) / (5 * np.maximum(counts, 1))) ** .35
    model = HistGradientBoostingClassifier(
        learning_rate=.075, max_iter=iterations, max_leaf_nodes=7 if meta else 15,
        min_samples_leaf=65 if meta else 25, l2_regularization=8 if meta else 4,
        max_bins=63, early_stopping=False, random_state=1729)
    model.fit(x, y, sample_weight=weights[y])
    return model


def _prob(model, x):
    p = np.full((len(x), 5), 1e-7, dtype=np.float64)
    p[:, model.classes_.astype(int)] = model.predict_proba(x)
    return p / p.sum(axis=1, keepdims=True)


def _meta(p, core):
    blocks = [p, np.log(np.maximum(p, 1e-6))]
    blocks += [ndimage.uniform_filter1d(p, w, axis=0, mode='nearest')
               for w in (3, 7, 21, 61)]
    indices = np.arange(len(p))
    blocks += [p[np.clip(indices + shift, 0, len(p) - 1)] for shift in (-2, 2)]
    return np.column_stack(blocks + [core]).astype(np.float32)


def _smooth(p, transition, prior, strength):
    if strength == 0:
        return p.copy()
    a = transition ** strength
    a /= a.sum(axis=1, keepdims=True)
    e = np.maximum(p, 1e-8) / (prior[None, :] ** (.65 * strength))
    forward = np.empty_like(e)
    backward = np.ones_like(e)
    forward[0] = e[0] / e[0].sum()
    for j in range(1, len(e)):
        v = e[j] * (forward[j - 1] @ a)
        forward[j] = v / (v.sum() + 1e-30)
    for j in range(len(e) - 2, -1, -1):
        v = a @ (e[j + 1] * backward[j + 1])
        backward[j] = v / (v.sum() + 1e-30)
    result = forward * backward
    return result / result.sum(axis=1, keepdims=True)


def _f1(y, pred):
    cm = np.bincount(y * 5 + pred, minlength=25).reshape(5, 5)
    return np.mean(2 * np.diag(cm) / np.maximum(cm.sum(0) + cm.sum(1), 1))


def fit_predict(train_x, train_y, test_x):
    labels = np.asarray(train_y, dtype=int)
    valid = (labels >= 0) & (labels < 5)
    unique = np.unique(labels[valid])
    output_shape = np.asarray(test_x).shape[:2]
    if len(unique) < 2:
        return np.full(output_shape, unique[0] if len(unique) else 0, dtype=int)
    train_features, train_core, test_features, test_core = [], [], [], []
    for night in train_x:
        a, b = _features(night)
        train_features.append(a); train_core.append(b)
    for night in test_x:
        a, b = _features(night)
        test_features.append(a); test_core.append(b)
    x = np.concatenate(train_features)
    xt = np.concatenate(test_features)
    y = labels.ravel(); good = valid.ravel()
    groups = np.concatenate([np.full(len(a), i) for i, a in enumerate(train_features)])
    oof = np.zeros((len(x), 5))
    pt = np.zeros((len(xt), 5))
    n = len(train_features)
    for held in range(n):
        fitting = good & (groups != held)
        model = _fit(x[fitting], y[fitting], 105)
        oof[groups == held] = _prob(model, x[groups == held])
        pt += _prob(model, xt) / n
    model = _fit(x[good], y[good], 145)
    pt = .5 * pt + .5 * _prob(model, xt)
    train_offsets = np.cumsum([0] + [len(a) for a in train_features])
    test_offsets = np.cumsum([0] + [len(a) for a in test_features])
    mx = np.concatenate([_meta(oof[train_offsets[i]:train_offsets[i + 1]], train_core[i])
                         for i in range(n)])
    mt = np.concatenate([_meta(pt[test_offsets[i]:test_offsets[i + 1]], test_core[i])
                         for i in range(len(test_features))])
    moof = np.zeros_like(oof); mtest = np.zeros_like(pt)
    for held in range(n):
        fitting = good & (groups != held)
        model = _fit(mx[fitting], y[fitting], 75, meta=True)
        moof[groups == held] = _prob(model, mx[groups == held])
        mtest += _prob(model, mt) / n
    model = _fit(mx[good], y[good], 100, meta=True)
    mtest = .5 * mtest + .5 * _prob(model, mt)
    oof = .35 * oof + .65 * moof
    pt = .35 * pt + .65 * mtest
    counts = np.full((5, 5), .5)
    for night in labels:
        ok = (night[:-1] >= 0) & (night[:-1] < 5) & (night[1:] >= 0) & (night[1:] < 5)
        counts += np.bincount(night[:-1][ok] * 5 + night[1:][ok], minlength=25).reshape(5, 5)
    transition = counts / counts.sum(axis=1, keepdims=True)
    prior = np.bincount(y[good], minlength=5).astype(float) + 1
    prior /= prior.sum()
    best = (-1, 0, np.ones(5))
    for strength in (0, .2, .4, .6):
        smooth = np.concatenate([_smooth(oof[train_offsets[i]:train_offsets[i + 1]],
                                        transition, prior, strength) for i in range(n)])
        p = smooth[good]; target = y[good]; weights = np.ones(5)
        for _ in range(2):
            for c in (1, 4, 3, 2, 0):
                options = []
                for factor in (.8, 1, 1.25):
                    w = weights.copy(); w[c] *= factor
                    score = _f1(target, (p * w).argmax(axis=1))
                    options.append((score - .001 * np.sum(np.log(w) ** 2), factor))
                weights[c] *= max(options, key=lambda item: item[0])[1]
        score = _f1(target, (p * weights).argmax(axis=1)) - .001 * strength
        if score > best[0]:
            best = (score, strength, weights.copy())
    predictions = []
    for i in range(len(test_features)):
        p = _smooth(pt[test_offsets[i]:test_offsets[i + 1]], transition, prior, best[1])
        predictions.append((p * (best[2] ** .85)).argmax(axis=1))
    return np.asarray(predictions, dtype=np.int64).reshape(output_shape)
