import numpy as np
from sklearn.linear_model import LogisticRegression

FS = 100
EPOCH_SAMPLES = 3000
CLASSES = 5
EPS = 1e-12

# Frequency band masks helper
def _band_masks(n_samples=EPOCH_SAMPLES, fs=FS):
    freqs = np.fft.rfftfreq(n_samples, 1.0/fs)
    m_total = (freqs >= 0.5) & (freqs <= 30.0)
    m_delta = (freqs >= 0.5) & (freqs < 4.0)
    m_theta = (freqs >= 4.0) & (freqs < 8.0)
    m_alpha = (freqs >= 8.0) & (freqs < 12.0)
    m_sigma = (freqs >= 12.0) & (freqs < 15.0)
    m_beta  = (freqs >= 15.0) & (freqs <= 30.0)
    return freqs, m_total, m_delta, m_theta, m_alpha, m_sigma, m_beta

# Feature extraction per night (epochs x samples)
def _extract_features_night(night, fs=FS):
    # night: (1440, 3000)
    x = night.astype(np.float64)
    # Detrend per epoch by mean
    x = x - x.mean(axis=1, keepdims=True)
    e, n = x.shape

    # Time-domain features (vectorized)
    std = x.std(axis=1) + EPS
    ptp = x.ptp(axis=1)
    meanabs = np.mean(np.abs(x), axis=1)
    dx = np.diff(x, axis=1)
    ll = np.mean(np.abs(dx), axis=1)  # line length per sample
    zc = np.mean((x[:, :-1] * x[:, 1:]) < 0.0, axis=1)
    varx = x.var(axis=1) + EPS
    vardx = dx.var(axis=1) + EPS
    ddx = np.diff(dx, axis=1)
    varddx = ddx.var(axis=1) + EPS
    mob = np.sqrt(vardx / varx)
    comp = np.sqrt(varddx / vardx)
    mu = x.mean(axis=1)
    x0 = x - mu[:, None]
    m3 = np.mean(x0**3, axis=1)
    m4 = np.mean(x0**4, axis=1)
    s = std
    skew = m3 / (s**3)
    kurt = m4 / (s**4) - 3.0

    # Frequency-domain features via rFFT with Hamming window
    w = np.hamming(n)
    Xf = np.fft.rfft(x * w[None, :], axis=1)
    P = (np.abs(Xf) ** 2)
    freqs, m_tot, m_d, m_t, m_a, m_s, m_b = _band_masks(n, fs)
    Pt = P[:, m_tot]
    tot = Pt.sum(axis=1) + EPS
    b_d = P[:, m_d].sum(axis=1) + EPS
    b_t = P[:, m_t].sum(axis=1) + EPS
    b_a = P[:, m_a].sum(axis=1) + EPS
    b_s = P[:, m_s].sum(axis=1) + EPS
    b_b = P[:, m_b].sum(axis=1) + EPS

    # Relative bandpowers
    d_rel = b_d / tot
    t_rel = b_t / tot
    a_rel = b_a / tot
    s_rel = b_s / tot
    b_rel = b_b / tot

    # Log band ratios (use absolute to keep complementary info)
    ratio_ad = np.log(b_a / b_d)
    ratio_sd = np.log(b_s / b_d)
    ratio_tb = np.log(b_t / b_b)

    # Spectral centroid, entropy, SEF90 within 0.5-30 Hz
    ft = freqs[m_tot]
    centroid = (Pt * ft[None, :]).sum(axis=1) / tot
    p_norm = Pt / tot[:, None]
    ent = -np.sum(p_norm * np.log(p_norm + EPS), axis=1) / np.log(p_norm.shape[1])
    csum = np.cumsum(Pt, axis=1)
    targets = 0.90 * tot
    idxs = (csum >= targets[:, None]).argmax(axis=1)
    sef90 = ft[idxs]

    # Time-of-night covariates
    t = np.arange(e, dtype=float) / float(e)
    sin_t = np.sin(2.0 * np.pi * t)
    cos_t = np.cos(2.0 * np.pi * t)

    feats = np.column_stack([
        std, ptp, meanabs, ll, zc, mob, comp, skew, kurt,
        d_rel, t_rel, a_rel, s_rel, b_rel,
        ratio_ad, ratio_sd, ratio_tb,
        centroid, ent, sef90,
        t, sin_t, cos_t
    ])

    # Unsupervised per-night normalization
    muF = feats.mean(axis=0)
    sdF = feats.std(axis=0)
    sdF[sdF == 0.0] = 1.0
    feats = (feats - muF) / sdF
    return feats

def _estimate_markov(train_y):
    K = CLASSES
    trans = np.zeros((K, K), dtype=np.float64)
    prior = np.zeros(K, dtype=np.float64)
    for y in train_y:
        y = np.asarray(y, dtype=int)
        m = (y >= 0)
        # prior from any labeled epoch
        if m.any():
            prior += np.bincount(y[m], minlength=K)
        # transitions within labeled runs
        for t in range(1, len(y)):
            a = y[t-1]
            b = y[t]
            if a >= 0 and b >= 0:
                trans[a, b] += 1.0
    # Laplace smoothing and self-bias to encourage persistence
    alpha = 0.05
    self_bias = 2.0
    trans += alpha
    for i in range(K):
        trans[i, i] += self_bias
    trans = trans / trans.sum(axis=1, keepdims=True)

    prior = prior + 1.0
    prior = prior / prior.sum()
    return trans, prior

def _viterbi_decode(emiss, trans, pi):
    # emiss: (T, K) probabilities
    Tlen, K = emiss.shape
    logE = np.log(emiss + EPS)
    logT = np.log(trans + EPS)
    logPi = np.log(pi + EPS)
    dp = np.empty((Tlen, K), dtype=np.float64)
    ptr = np.zeros((Tlen, K), dtype=np.int16)
    dp[0] = logPi + logE[0]
    for t in range(1, Tlen):
        m = dp[t-1][:, None] + logT  # (K, K)
        ptr[t] = np.argmax(m, axis=0)
        dp[t] = m[ptr[t], np.arange(K)] + logE[t]
    states = np.empty(Tlen, dtype=np.int16)
    states[-1] = np.argmax(dp[-1])
    for t in range(Tlen-2, -1, -1):
        states[t] = ptr[t+1, states[t+1]]
    return states.astype(int)

def _de_island(seq, passes=1):
    y = seq.copy()
    n = len(y)
    for _ in range(passes):
        for t in range(1, n-1):
            if y[t-1] == y[t+1] and y[t] != y[t-1]:
                y[t] = y[t-1]
    return y

def fit_predict(train_x, train_y, test_x):
    np.random.seed(0)
    # Estimate Markov model from labels (ignore -1)
    trans, prior = _estimate_markov(train_y)

    # Build training set features
    X_list = []
    y_list = []
    for n in range(train_x.shape[0]):
        feats = _extract_features_night(train_x[n])
        y = np.asarray(train_y[n], dtype=int)
        m = y >= 0
        if m.any():
            X_list.append(feats[m])
            y_list.append(y[m])
    if len(X_list) == 0:
        # Fallback: if no labels at all (unlikely), predict all wake
        return np.zeros((test_x.shape[0], test_x.shape[1]), dtype=int)
    Xtr = np.vstack(X_list)
    ytr = np.concatenate(y_list)

    # Train classifier (deterministic)
    clf = LogisticRegression(
        random_state=0,
        solver='lbfgs',
        multi_class='multinomial',
        max_iter=300,
        class_weight='balanced',
        C=1.0
    )
    clf.fit(Xtr, ytr)
    classes_in_model = clf.classes_.astype(int)

    # Predict per-night with Viterbi decoding
    n_test, T = test_x.shape[0], test_x.shape[1]
    preds = np.zeros((n_test, T), dtype=int)
    for n in range(n_test):
        feats = _extract_features_night(test_x[n])
        prob_sub = clf.predict_proba(feats)  # (T, k_present)
        # Map to 5 classes with tiny floor
        prob = np.full((prob_sub.shape[0], CLASSES), 1e-8, dtype=np.float64)
        for j, c in enumerate(classes_in_model):
            prob[:, c] = prob_sub[:, j] + 1e-8
        prob /= prob.sum(axis=1, keepdims=True)
        states = _viterbi_decode(prob, trans, prior)
        states = _de_island(states, passes=2)
        preds[n] = states
    return preds
