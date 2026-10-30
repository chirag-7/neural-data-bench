import numpy as np
from scipy.signal import butter, sosfiltfilt
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score


def _features(x):
    x = np.nan_to_num(np.asarray(x, dtype=np.float32), copy=True)
    left = [0, 1, 2, 7, 8, 9, 14, 15, 16]
    right = [6, 5, 4, 13, 12, 11, 20, 19, 18]
    specs = [
        (1, [0, 2, 31, 8]), (8, [1, 7, 9, 15]),
        (15, [8, 14, 16, 48]),
        (5, [6, 4, 35, 12]), (12, [5, 13, 11, 19]),
        (19, [12, 20, 18, 52]),
    ]
    lap = np.stack([x[:, c, :] - x[:, nb, :].mean(axis=1)
                    for c, nb in specs], axis=1)
    v = np.concatenate((x[:, left, :], lap[:, :3, :],
                        x[:, right, :], lap[:, 3:, :]), axis=1)
    asym, topo = [], []
    bands = [(8, 12), (12, 16), (16, 22), (22, 30), (8, 30)]
    windows = [(16, -16), (16, 240), (240, -16)]
    for lo, hi in bands:
        sos = butter(4, [lo, hi], btype='bandpass', fs=160, output='sos')
        f = sosfiltfilt(sos, v, axis=-1)
        for j, (a, b) in enumerate(windows):
            p = np.log(np.mean(f[:, :, a:b] ** 2, axis=-1) + 1e-8)
            asym.append(p[:, 12:] - p[:, :12])
            if j == 0:
                topo.append(p - p.mean(axis=1, keepdims=True))
    return np.concatenate((np.concatenate(asym, axis=1),
                           np.concatenate(topo, axis=1)), axis=1)


def _center_blocks(z):
    z = z.copy()
    n = len(z)
    if n < 20:
        return z
    block = 45 if n % 45 == 0 else n
    for a in range(0, n, block):
        b = min(a + block, n)
        z[a:b] -= np.median(z[a:b], axis=0)
    return z


def _predict_scores(scores):
    n = len(scores)
    if n < 20:
        return (scores > 0).astype(int)
    block = 45 if n % 45 == 0 else n
    out = np.empty(n, dtype=int)
    for a in range(0, n, block):
        b = min(a + block, n)
        out[a:b] = scores[a:b] > np.median(scores[a:b])
    return out


def _fit_score(x_train, y_train, x_eval, columns, c):
    scaler = StandardScaler()
    a = np.clip(scaler.fit_transform(x_train[:, columns]), -6, 6)
    b = np.clip(scaler.transform(x_eval[:, columns]), -6, 6)
    model = LogisticRegression(C=c, solver='liblinear',
                               class_weight='balanced', max_iter=300,
                               random_state=7)
    model.fit(a, y_train)
    return model.decision_function(b)


def fit_predict(train_x, train_y, test_x):
    y = np.asarray(train_y, dtype=int).ravel()
    train = _center_blocks(_features(train_x))
    test = _center_blocks(_features(test_x))
    focus_pairs = [1, 4, 7, 9, 10, 11]
    focus = np.array([12 * k + j for k in range(15)
                      for j in focus_pairs], dtype=int)
    families = [focus, np.arange(180), np.arange(train.shape[1])]
    candidates = [(cols, c) for cols in families for c in (0.03, 0.3, 3.0)]
    if len(y) % 45 == 0 and len(y) >= 135:
        groups = np.arange(len(y)) // 45
        folds = [(np.flatnonzero(groups != g), np.flatnonzero(groups == g))
                 for g in np.unique(groups)]
    else:
        from sklearn.model_selection import StratifiedKFold
        count = np.bincount(y, minlength=2).min()
        folds = list(StratifiedKFold(n_splits=min(5, count), shuffle=True,
                                    random_state=7).split(train, y)) if count >= 2 else []
    best = candidates[1]
    best_accuracy = -1.0
    for cols, c in candidates:
        accuracies = []
        for tr, va in folds:
            if np.unique(y[tr]).size < 2:
                continue
            scores = _fit_score(train[tr], y[tr], train[va], cols, c)
            accuracies.append(balanced_accuracy_score(y[va],
                                                       _predict_scores(scores)))
        accuracy = float(np.mean(accuracies)) if accuracies else -1.0
        if accuracy > best_accuracy:
            best_accuracy = accuracy
            best = (cols, c)
    scores = _fit_score(train, y, test, *best)
    return _predict_scores(scores).astype(int)
