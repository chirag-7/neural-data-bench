import gc
import numpy as np
from scipy.fft import rfft, rfftfreq
from sklearn.ensemble import ExtraTreesClassifier, HistGradientBoostingClassifier
from sklearn.metrics import f1_score


def _rolling(a, width):
    h = width // 2
    p = np.pad(a, ((h, h), (0, 0)), mode="reflect")
    s = np.vstack((np.zeros((1, a.shape[1])), np.cumsum(p, axis=0)))
    return (s[width:] - s[:-width]) / float(width)


def _night_features(x, fs=100.0):
    a = np.asarray(x, dtype=np.float32)
    a = a - np.mean(a, axis=1, keepdims=True)
    np.nan_to_num(a, copy=False)
    eps = 1e-7
    sd = np.sqrt(np.mean(a * a, axis=1) + eps)

    d = np.diff(a, axis=1)
    dsd = np.sqrt(np.mean(d * d, axis=1) + eps)
    line = np.mean(np.abs(d), axis=1)
    zcr = np.mean((a[:, 1:] >= 0) != (a[:, :-1] >= 0), axis=1)
    q = np.percentile(np.abs(a), [50, 75, 90, 95], axis=1).T
    sq = a * a
    skew = np.mean(sq * a, axis=1) / (sd ** 3 + eps)
    kurt = np.mean(sq * sq, axis=1) / (sd ** 4 + eps) - 3.0
    ac = []
    var = sd * sd + eps
    for lag in (25, 50, 100):
        ac.append(np.mean(a[:, :-lag] * a[:, lag:], axis=1) / var)
    dd = np.diff(d, axis=1)
    d2sd = np.sqrt(np.mean(dd * dd, axis=1) + eps)
    mobility = dsd / (sd + eps)
    complexity = (d2sd / (dsd + eps)) / (mobility + eps)
    del d, dd, sq

    win = np.hanning(a.shape[1]).astype(np.float32)
    ft = rfft(a * win[None, :], axis=1, workers=1)
    spec = ft.real * ft.real + ft.imag * ft.imag
    freq = rfftfreq(a.shape[1], 1.0 / fs)
    bands = ((0.3, 0.8), (0.8, 1.5), (1.5, 2.0), (2.0, 4.0),
             (4.0, 6.0), (6.0, 8.0), (8.0, 10.0), (10.0, 12.0),
             (12.0, 15.0), (15.0, 18.0), (18.0, 25.0),
             (25.0, 35.0), (35.0, 45.0))
    bp = np.column_stack([
        np.sum(spec[:, (freq >= lo) & (freq < hi)], axis=1)
        for lo, hi in bands
    ])
    total = np.sum(spec[:, (freq >= 0.3) & (freq < 45.0)], axis=1) + eps
    logp = np.log(bp + eps)
    logrel = np.log(bp / total[:, None] + eps)
    slow = np.sum(bp[:, :4], axis=1)
    theta = np.sum(bp[:, 4:6], axis=1)
    alpha = np.sum(bp[:, 6:8], axis=1)
    sigma = bp[:, 8]
    beta = np.sum(bp[:, 10:12], axis=1)
    ratios = np.column_stack((
        np.log((slow + eps) / (theta + eps)),
        np.log((slow + eps) / (alpha + eps)),
        np.log((theta + eps) / (alpha + eps)),
        np.log((sigma + eps) / (bp[:, 7] + bp[:, 9] + eps)),
        np.log((beta + eps) / (slow + eps)),
        np.log((slow + eps) / (total + eps))))
    raw = np.column_stack((
        np.log(sd + eps), np.log(dsd + eps), np.log(line + eps), zcr,
        np.log(q + eps), np.clip(skew, -8, 8), np.clip(kurt, -8, 20),
        np.column_stack(ac), mobility, complexity))
    base = np.column_stack((logp, logrel, ratios, raw))
    base = np.nan_to_num(base, nan=0.0, posinf=30.0, neginf=-30.0)
    base = np.clip(base, -30.0, 30.0)

    med = np.median(base, axis=0)
    lo, hi = np.percentile(base, [25, 75], axis=0)
    scale = (hi - lo) / 1.349
    scale[scale < 1e-3] = 1.0
    z = np.clip((base - med) / scale, -8.0, 8.0)
    core_idx = np.r_[13:32, 32:36]
    core = z[:, core_idx]
    context = []
    for width in (3, 7, 15, 31):
        context.append(_rolling(core, width))
    for width in (7, 31):
        m = _rolling(core, width)
        v = np.maximum(_rolling(core * core, width) - m * m, 0.0)
        context.append(np.sqrt(v))
    p = np.pad(core, ((1, 1), (0, 0)), mode="edge")
    context.append(0.5 * (p[2:] - p[:-2]))

    n = a.shape[0]
    t = np.arange(n, dtype=np.float64) / max(n - 1, 1)
    hour = 20.0 + 12.0 * t
    ang = 2.0 * np.pi * hour / 24.0
    clock = np.column_stack((t, t * t, np.sin(ang), np.cos(ang),
                             np.sin(2 * ang), np.cos(2 * ang)))
    out = np.column_stack([base, z] + context + [clock])
    del a, ft, spec, bp
    return np.asarray(out, dtype=np.float32)


def _all_features(x):
    return np.vstack([_night_features(x[k]) for k in range(x.shape[0])])


def _weights(y):
    counts = np.bincount(y, minlength=5).astype(float)
    w = len(y) / (5.0 * np.maximum(counts[y], 1.0))
    w = np.minimum(w, 5.0)
    return w / np.mean(w)


def _models(seed, final=False):
    et = ExtraTreesClassifier(
        n_estimators=400 if final else 150,
        max_features=0.65, min_samples_leaf=2,
        class_weight="balanced", n_jobs=1, random_state=seed)
    hb = HistGradientBoostingClassifier(
        max_iter=140 if final else 75, learning_rate=0.07,
        max_leaf_nodes=23, min_samples_leaf=18,
        l2_regularization=2.0, early_stopping=False,
        random_state=seed + 1000)
    return et, hb


def _proba(model, x):
    p = model.predict_proba(x)
    out = np.zeros((len(x), 5), dtype=np.float64)
    out[:, np.asarray(model.classes_, dtype=int)] = p
    return out


def _transition(y_nights, omit=None):
    counts = np.ones((5, 5), dtype=np.float64)
    prior = np.ones(5, dtype=np.float64)
    for k, y in enumerate(y_nights):
        if k == omit:
            continue
        y = np.asarray(y, dtype=int)
        good = y >= 0
        prior += np.bincount(y[good], minlength=5)
        ok = good[:-1] & good[1:]
        np.add.at(counts, (y[:-1][ok], y[1:][ok]), 1.0)
    tr = counts / counts.sum(axis=1, keepdims=True)
    prior /= prior.sum()
    return np.clip(np.log(tr / prior[None, :]), -3.0, 3.0)


def _decode(p, assoc, bias, gamma, strength):
    emit = gamma * np.log(np.maximum(p, 1e-9)) + np.log(bias)[None, :]
    n = len(p)
    back = np.empty((n, 5), dtype=np.int8)
    dp = emit[0].copy()
    back[0] = 0
    for i in range(1, n):
        v = dp[:, None] + strength * assoc
        back[i] = np.argmax(v, axis=0)
        dp = emit[i] + np.max(v, axis=0)
    out = np.empty(n, dtype=np.int64)
    out[-1] = int(np.argmax(dp))
    for i in range(n - 1, 0, -1):
        out[i - 1] = back[i, out[i]]
    return out


def fit_predict(train_x, train_y, test_x):
    train_y = np.asarray(train_y, dtype=int)
    n_nights, n_epochs = train_y.shape
    xtr = _all_features(train_x)
    xte = _all_features(test_x)
    yflat = train_y.reshape(-1)
    groups = np.repeat(np.arange(n_nights), n_epochs)
    valid = yflat >= 0
    oof_et = np.zeros((len(yflat), 5), dtype=np.float64)
    oof_hb = np.zeros_like(oof_et)

    for g in range(n_nights):
        fit = valid & (groups != g)
        hold = groups == g
        et, hb = _models(101 + g, final=False)
        et.fit(xtr[fit], yflat[fit])
        hb.fit(xtr[fit], yflat[fit], sample_weight=_weights(yflat[fit]))
        oof_et[hold] = _proba(et, xtr[hold])
        oof_hb[hold] = _proba(hb, xtr[hold])
        del et, hb
        gc.collect()

    best_score = -1.0
    best_mix = 0.5
    best_bias = np.ones(5)
    factors = (0.75, 0.9, 1.0, 1.12, 1.3)
    for mix in (0.0, 0.25, 0.5, 0.75, 1.0):
        p = (1.0 - mix) * oof_et + mix * oof_hb
        bias = np.ones(5)
        for _ in range(2):
            for c in (0, 1, 3, 4):
                local_score, local_value = -1.0, bias[c]
                for value in factors:
                    b = bias.copy()
                    b[c] = value
                    pred = np.argmax(p * b[None, :], axis=1)
                    score = f1_score(yflat[valid], pred[valid],
                                     labels=np.arange(5), average="macro",
                                     zero_division=0)
                    if score > local_score:
                        local_score, local_value = score, value
                bias[c] = local_value
        pred = np.argmax(p * bias[None, :], axis=1)
        score = f1_score(yflat[valid], pred[valid], labels=np.arange(5),
                         average="macro", zero_division=0)
        if score > best_score:
            best_score, best_mix, best_bias = score, mix, bias.copy()

    poof = (1.0 - best_mix) * oof_et + best_mix * oof_hb
    best_seq_score, best_gamma, best_strength = -1.0, 1.0, 0.0
    fold_assoc = [_transition(train_y, omit=g) for g in range(n_nights)]
    for gamma in (0.85, 1.0, 1.15):
        for strength in (0.0, 0.08, 0.15, 0.25, 0.4, 0.6):
            pred = np.empty(len(yflat), dtype=np.int64)
            for g in range(n_nights):
                sl = slice(g * n_epochs, (g + 1) * n_epochs)
                pred[sl] = _decode(poof[sl], fold_assoc[g], best_bias,
                                   gamma, strength)
            score = f1_score(yflat[valid], pred[valid], labels=np.arange(5),
                             average="macro", zero_division=0)
            if score > best_seq_score:
                best_seq_score = score
                best_gamma, best_strength = gamma, strength

    et, hb = _models(777, final=True)
    et.fit(xtr[valid], yflat[valid])
    hb.fit(xtr[valid], yflat[valid], sample_weight=_weights(yflat[valid]))
    ptest = ((1.0 - best_mix) * _proba(et, xte) +
             best_mix * _proba(hb, xte))
    assoc = _transition(train_y)
    result = np.empty((test_x.shape[0], test_x.shape[1]), dtype=np.int64)
    for g in range(test_x.shape[0]):
        sl = slice(g * test_x.shape[1], (g + 1) * test_x.shape[1])
        result[g] = _decode(ptest[sl], assoc, best_bias,
                            best_gamma, best_strength)
    return result
