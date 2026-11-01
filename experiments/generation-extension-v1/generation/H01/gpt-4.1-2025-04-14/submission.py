import numpy as np
from scipy.signal import butter, lfilter, welch
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import StratifiedKFold, GridSearchCV

def _butter_bandpass(lowcut, highcut, fs, order=4):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a

def _apply_bandpass(data, lowcut, highcut, fs, order=4):
    b, a = _butter_bandpass(lowcut, highcut, fs, order=order)
    return lfilter(b, a, data)

def _extract_bandpower(data, fs, band):
    # data: (n_channels, n_samples)
    band = np.asarray(band)
    n_channels = data.shape[0]
    pwr = np.zeros(n_channels)
    for ch in range(n_channels):
        freqs, psd = welch(data[ch], fs=fs, nperseg=256)
        idx = np.logical_and(freqs >= band[0], freqs <= band[1])
        pwr[ch] = np.log(np.trapz(psd[idx], freqs[idx]) + 1e-10)
    return pwr

def _compute_logvar(arr, axis=-1):
    return np.log(np.var(arr, axis=axis) + 1e-10)

def extract_features(X, channel_names, fs=160):
    # X: (n_trials, n_channels, n_samples)
    n_trials, n_channels, n_samples = X.shape
    extracts = []
    # Target motor imagery channels
    c3_idx = channel_names.index('C3') if 'C3' in channel_names else None
    c4_idx = channel_names.index('C4') if 'C4' in channel_names else None
    cz_idx = channel_names.index('CZ') if 'CZ' in channel_names else None
    motor_idxs = [ix for ix in [c3_idx, c4_idx, cz_idx] if ix is not None]
    # Overlapping log-var windows (short-term energy)
    win_size = int(0.5 * fs)
    step = int(0.25 * fs)
    wins = [(i, min(i + win_size, n_samples)) for i in range(0, n_samples - win_size + 1, step)]
    for trial in range(n_trials):
        feat = []
        x = X[trial]
        # 1. Log-variance in C3, C4, CZ over windows
        for ch_idx in motor_idxs:
            for (start, end) in wins:
                feat.append(_compute_logvar(x[ch_idx, start:end]))
        # 2. Mean and std of all channels
        feat.extend(np.mean(x, axis=1))
        feat.extend(np.std(x, axis=1))
        # 3. Bandpower in mu and beta bands (all channels)
        feat.extend(_extract_bandpower(x, fs, [8,13]))  # mu
        feat.extend(_extract_bandpower(x, fs, [13,30])) # beta
        extracts.append(np.array(feat, dtype=np.float32))
    return np.vstack(extracts)

def fit_predict(train_x, train_y, test_x):
    """
    Multi-subject EEG epoch decoding (left vs right hand imagery) using extracted features and regularized logistic regression.
    Args:
        train_x: np.ndarray, shape (n_train_trials, 64, 480)
        train_y: np.ndarray, shape (n_train_trials,)
        test_x: np.ndarray, shape (n_test_trials, 64, 480)
    Returns:
        y_pred: np.ndarray, shape (n_test_trials,), integer labels 0/1
    """
    np.random.seed(42)
    channel_names = [
        'FC5','FC3','FC1','FCZ','FC2','FC4','FC6','C5','C3','C1','CZ','C2','C4','C6',
        'CP5','CP3','CP1','CPZ','CP2','CP4','CP6','FP1','FPZ','FP2','AF7','AF3',
        'AFZ','AF4','AF8','F7','F5','F3','F1','FZ','F2','F4','F6','F8',
        'FT7','FT8','T7','T8','T9','T10','TP7','TP8','P7','P5','P3','P1','PZ',
        'P2','P4','P6','P8','PO7','PO3','POZ','PO4','PO8','O1','OZ','O2','IZ'
    ]
    fs = 160
    # Feature extraction
    X_train = extract_features(train_x, channel_names, fs)
    X_test = extract_features(test_x, channel_names, fs)
    # Feature normalization
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)
    # Classifier training with optimal hyperparameter selection (C)
    clf = LogisticRegression(class_weight='balanced', solver='liblinear', random_state=42, max_iter=300)
    param_grid = {'C': np.logspace(-2, 2, 7)}
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    grid = GridSearchCV(clf, param_grid, scoring='balanced_accuracy', cv=cv)
    grid.fit(X_train, train_y)
    best_clf = grid.best_estimator_
    y_pred = best_clf.predict(X_test)
    return y_pred.astype(np.int64)
