import numpy as np
from scipy.signal import butter, sosfiltfilt
from scipy.linalg import eigh
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score

FS = 160.0
BANDS = [(7, 10), (10, 13), (13, 18), (18, 24), (24, 30)]
LAT_PAIRS = [(0, 6), (1, 5), (2, 4),
             (7, 13), (8, 12), (9, 11),
             (14, 20), (15, 19), (16, 18)]


def _subject_groups(n):
    # The supplied construction has exactly 45 trials per subject.
    if n % 45 == 0:
        return np.arange(n) // 45
    # Conservative fallback for compatible inputs with a different count.
    k = 5 if n >= 180 else 3
    return np.minimum((np.arange(n) * k) // n, k - 1)


def _bandpass(x, lo, hi, order=4):
    sos = butter(order, (lo, hi), btype="bandpass", fs=FS, output="sos")
    return sosfiltfilt(sos, x, axis=-1)


def _prepare_motor(x):
    x = np.asarray(x[:, :21, :], dtype=np.float64)
    x = x - x.mean(axis=-1, keepdims=True)
    return x


def _euclidean_align(x, groups):
    out = np.empty_like(x)
    d = x.shape[1]
    eye = np.eye(d) / d
    for g in np.unique(groups):
        ind = np.flatnonzero(groups == g)
        z = x[ind]
        cov = np.einsum("nct,ndt->ncd", z, z, optimize=True)
        tr = np.trace(cov, axis1=1, axis2=2)
        cov /= np.maximum(tr[:, None, None], 1e-18)
        ref = cov.mean(axis=0)
        ref = 0.95 * ref + 0.05 * eye
        val, vec = eigh(ref, check_finite=False)
        val = np.maximum(val, 1e-10)
        whitener = (vec * (1.0 / np.sqrt(val))) @ vec.T
        out[ind] = np.einsum("ab,nbt->nat", whitener, z, optimize=True)
    return out


def _filter_bank(x, groups):
    broad = _bandpass(x, 5, 35, order=4)
    broad = _euclidean_align(broad, groups)
    result = []
    for lo, hi in BANDS:
        z = _bandpass(broad, lo, hi, order=3)
        result.append(np.ascontiguousarray(z[..., 16:-16:2]))
    return result


def _trial_cov(z):
    cov = np.einsum("nct,ndt->ncd", z, z, optimize=True)
    tr = np.trace(cov, axis1=1, axis2=2)
    return cov / np.maximum(tr[:, None, None], 1e-18)


def _fit_csp(bank, y, n_side=3):
    filters = []
    for z in bank:
        cov = _trial_cov(z)
        c0 = cov[y == 0].mean(axis=0)
        c1 = cov[y == 1].mean(axis=0)
        d = c0.shape[0]
        eye = np.eye(d) / d
        c0 = 0.90 * c0 + 0.10 * eye
        c1 = 0.90 * c1 + 0.10 * eye
        _, vec = eigh(c1, c0 + c1, check_finite=False)
        choose = np.r_[np.arange(n_side), np.arange(d - n_side, d)]
        filters.append(vec[:, choose].T)
    return filters


def _csp_features(bank, filters):
    feats = []
    for z, w in zip(bank, filters):
        projected = np.einsum("kc,nct->nkt", w, z, optimize=True)
        var = np.mean(projected * projected, axis=-1)
        var /= np.maximum(var.sum(axis=1, keepdims=True), 1e-18)
        feats.append(np.log(np.maximum(var, 1e-14)))
    return np.concatenate(feats, axis=1)


def _lateral_features(x):
    n = x.shape[-1]
    window = np.hanning(n)[None, None, :]
    spectrum = np.fft.rfft(x * window, axis=-1)
    power = spectrum.real * spectrum.real + spectrum.imag * spectrum.imag
    freq = np.fft.rfftfreq(n, 1.0 / FS)
    feats = []
    manual_bands = BANDS + [(7, 13), (13, 30)]
    for lo, hi in manual_bands:
        mask = (freq >= lo) & (freq <= hi)
        lp = np.log(np.maximum(power[..., mask].mean(axis=-1), 1e-12))
        feats.append(np.stack([lp[:, l] - lp[:, r]
                               for l, r in LAT_PAIRS], axis=1))
    return np.concatenate(feats, axis=1)


def _model(spec):
    if spec[0] == "lda":
        clf = LinearDiscriminantAnalysis(solver="lsqr", shrinkage="auto",
                                         priors=np.array([0.5, 0.5]))
    else:
        clf = LogisticRegression(C=spec[1], class_weight="balanced",
                                 solver="liblinear", max_iter=1000,
                                 random_state=0)
    return make_pipeline(StandardScaler(), clf)


def _combine(kind, csp, lateral):
    if kind == "csp":
        return csp
    if kind == "lateral":
        return lateral
    return np.concatenate((csp, lateral), axis=1)


def fit_predict(train_x, train_y, test_x):
    y = np.asarray(train_y, dtype=np.int64).reshape(-1)
    train = _prepare_motor(train_x)
    test = _prepare_motor(test_x)
    train_groups = _subject_groups(len(train))
    test_groups = _subject_groups(len(test))

    train_lateral = _lateral_features(train)
    test_lateral = _lateral_features(test)
    train_bank = _filter_bank(train, train_groups)
    test_bank = _filter_bank(test, test_groups)

    kinds = ("csp", "lateral", "both")
    specs = (("lda", None), ("lr", 0.03), ("lr", 0.1),
             ("lr", 0.3), ("lr", 1.0))
    scores = {(kind, spec): [] for kind in kinds for spec in specs}

    for held_out in np.unique(train_groups):
        va = train_groups == held_out
        tr = ~va
        fold_filters = _fit_csp([z[tr] for z in train_bank], y[tr])
        csp_tr = _csp_features([z[tr] for z in train_bank], fold_filters)
        csp_va = _csp_features([z[va] for z in train_bank], fold_filters)
        for kind in kinds:
            a = _combine(kind, csp_tr, train_lateral[tr])
            b = _combine(kind, csp_va, train_lateral[va])
            for spec in specs:
                mdl = _model(spec)
                mdl.fit(a, y[tr])
                pred = mdl.predict(b)
                scores[(kind, spec)].append(
                    balanced_accuracy_score(y[va], pred))

    best = max(scores, key=lambda key: np.mean(scores[key]))
    final_filters = _fit_csp(train_bank, y)
    train_csp = _csp_features(train_bank, final_filters)
    test_csp = _csp_features(test_bank, final_filters)
    final_train = _combine(best[0], train_csp, train_lateral)
    final_test = _combine(best[0], test_csp, test_lateral)
    final_model = _model(best[1])
    final_model.fit(final_train, y)
    return final_model.predict(final_test).astype(np.int64)
