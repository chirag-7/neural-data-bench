import numpy as np
from scipy.signal import butter, sosfiltfilt
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis

# Fixed channel order (PhysioNet 64-ch montage as provided)
CH_NAMES = [
    "FC5","FC3","FC1","FCZ","FC2","FC4","FC6","C5","C3","C1","CZ","C2","C4","C6",
    "CP5","CP3","CP1","CPZ","CP2","CP4","CP6","FP1","FPZ","FP2","AF7","AF3","AFZ","AF4","AF8",
    "F7","F5","F3","F1","FZ","F2","F4","F6","F8","FT7","FT8","T7","T8","T9","T10","TP7","TP8",
    "P7","P5","P3","P1","PZ","P2","P4","P6","P8","PO7","PO3","POZ","PO4","PO8","O1","OZ","O2","IZ"
]

EPS = 1e-10
FS = 160.0

# Symmetric pairs for lateralization features
ROI_PAIRS = [("C3","C4"), ("CP3","CP4"), ("FC3","FC4"), ("C1","C2")]

BANDS = [(8.0, 12.0), (12.0, 18.0), (18.0, 26.0)]


def _sos_bandpass(low, high, fs, order=4):
    ny = fs * 0.5
    low_n = max(0.001, low / ny)
    high_n = min(0.99, high / ny)
    if high_n <= low_n:
        high_n = min(0.99, low_n + 0.01)
    sos = butter(order, [low_n, high_n], btype='bandpass', output='sos')
    return sos


def _apply_sos(x, sos):
    # x: (trials, channels, samples)
    return sosfiltfilt(sos, x, axis=-1)


def _mean_norm_cov(X):
    # X: (n_trials, n_ch, n_samp); per-trial mean removed inside caller if desired
    n_t, n_ch, _ = X.shape
    covs = X @ np.transpose(X, (0, 2, 1))  # (t, ch, ch)
    tr = np.trace(covs, axis1=1, axis2=2)[:, None, None] + EPS
    covs = covs / tr
    return covs.mean(axis=0)


def _csp_filters(X, y, m=3, reg=0.05):
    # X: (n_trials, n_ch, n_samp) band-passed
    Xc = X - X.mean(axis=2, keepdims=True)
    cls0 = Xc[y == 0]
    cls1 = Xc[y == 1]
    n_ch = X.shape[1]
    if cls0.shape[0] == 0 or cls1.shape[0] == 0:
        # Fallback: identity filters (unlikely in provided data)
        I = np.eye(n_ch)
        pick = np.hstack([np.arange(0, m), np.arange(n_ch - m, n_ch)])
        return I[:, pick]
    R0 = _mean_norm_cov(cls0)
    R1 = _mean_norm_cov(cls1)
    # Shrinkage towards identity for robustness
    tr0 = np.trace(R0)
    tr1 = np.trace(R1)
    R0 = (1.0 - reg) * R0 + reg * (tr0 / n_ch) * np.eye(n_ch)
    R1 = (1.0 - reg) * R1 + reg * (tr1 / n_ch) * np.eye(n_ch)
    R = R0 + R1 + EPS * np.eye(n_ch)
    # Whiten composite covariance
    d, U = np.linalg.eigh(R)
    d = np.clip(d, EPS, None)
    W = U @ (np.diag(1.0 / np.sqrt(d))) @ U.T  # symmetric whitening
    S0 = W.T @ R0 @ W  # == W @ R0 @ W for symmetric W
    s, B = np.linalg.eigh(S0)
    order = np.argsort(s)[::-1]
    B = B[:, order]
    Wf = W @ B  # columns are spatial filters
    n_comp = Wf.shape[1]
    m = int(min(m, n_comp // 2))
    idx = np.hstack([np.arange(0, m), np.arange(n_comp - m, n_comp)])
    F = Wf[:, idx]  # (ch, 2m)
    return F


def _csp_transform(X, F):
    # X: (t, ch, s), F: (ch, k). Return (t, k) log-normalized variances
    proj = np.tensordot(X, F, axes=([1], [0]))  # (t, s, k)
    proj = np.swapaxes(proj, 1, 2)  # (t, k, s)
    v = (proj * proj).mean(axis=2)
    v = v / (v.sum(axis=1, keepdims=True) + EPS)
    return np.log(v + EPS)


def _roi_pair_features(X, chan_to_idx, pairs):
    # X: (t, ch, s)
    feats = []
    for a, b in pairs:
        if a in chan_to_idx and b in chan_to_idx:
            ia = chan_to_idx[a]
            ib = chan_to_idx[b]
            pa = (X[:, ia, :] ** 2).mean(axis=1)
            pb = (X[:, ib, :] ** 2).mean(axis=1)
            feats.append(np.log(pa + EPS) - np.log(pb + EPS))
    if len(feats) == 0:
        return np.zeros((X.shape[0], 0), dtype=np.float64)
    return np.stack(feats, axis=1)


def fit_predict(train_x, train_y, test_x):
    np.random.seed(0)
    Xtr = np.asarray(train_x, dtype=np.float64)
    Xte = np.asarray(test_x, dtype=np.float64)
    y = np.asarray(train_y, dtype=int)

    n_tr = Xtr.shape[0]
    n_te = Xte.shape[0]

    chan_to_idx = {ch: i for i, ch in enumerate(CH_NAMES)}

    feats_tr = []
    feats_te = []

    # Filter-bank feature extraction
    for (low, high) in BANDS:
        sos = _sos_bandpass(low, high, FS, order=4)
        Xtr_f = _apply_sos(Xtr, sos)
        Xte_f = _apply_sos(Xte, sos)

        # CSP features
        F = _csp_filters(Xtr_f, y, m=3, reg=0.05)
        csp_tr = _csp_transform(Xtr_f, F)
        csp_te = _csp_transform(Xte_f, F)

        # Lateralization band-power differences on symmetric pairs
        roi_tr = _roi_pair_features(Xtr_f, chan_to_idx, ROI_PAIRS)
        roi_te = _roi_pair_features(Xte_f, chan_to_idx, ROI_PAIRS)

        feats_tr.append(np.hstack([csp_tr, roi_tr]))
        feats_te.append(np.hstack([csp_te, roi_te]))

        # free memory for next band
        del Xtr_f, Xte_f

    Xf_tr = np.hstack(feats_tr)
    Xf_te = np.hstack(feats_te)

    # Standardize
    mu = Xf_tr.mean(axis=0)
    sd = Xf_tr.std(axis=0)
    sd[sd < 1e-8] = 1.0
    Xf_tr = (Xf_tr - mu) / sd
    Xf_te = (Xf_te - mu) / sd

    # Classifier: shrinkage LDA
    clf = LinearDiscriminantAnalysis(solver='lsqr', shrinkage='auto')
    clf.fit(Xf_tr, y)
    pred = clf.predict(Xf_te)
    return pred.astype(int)
