import numpy as np
from scipy import signal
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GroupKFold
from sklearn.impute import SimpleImputer
import math

_BAND_LIMITS = {
    'delta': (0.5, 4),
    'theta': (4, 8),
    'alpha': (8, 12),
    'sigma': (12, 16),
    'beta': (16, 30),
}
_SAMPLING_RATE = 100
_EPOCH_LEN = 3000
_SEED = 42

np.random.seed(_SEED)

def zscore_nightwise(x):
    # x shape: (epochs, samples)
    mean = x.mean(axis=1, keepdims=True)
    std = x.std(axis=1, keepdims=True)
    std[std == 0] = 1.0
    return (x - mean) / std

def compute_bandpower(epoch, band, sf=_SAMPLING_RATE):
    band_low, band_high = _BAND_LIMITS[band]
    freqs, psd = signal.welch(epoch, sf, nperseg=sf*2, noverlap=sf, scaling='density')
    freq_mask = (freqs >= band_low) & (freqs < band_high)
    return np.trapz(psd[freq_mask], freqs[freq_mask])

def compute_all_bandpowers(epoch):
    bp = [compute_bandpower(epoch, b) for b in _BAND_LIMITS]
    return bp

def zero_crossing_rate(signal_):
    return ((signal_[:-1]*signal_[1:]) < 0).sum() / len(signal_)

def extract_epoch_features(epoch):
    f = []
    # simple time-domain features
    f.append(epoch.mean())
    f.append(epoch.std())
    f.append(epoch.ptp())
    f.append(np.median(epoch))
    f.append(np.percentile(epoch, 10))
    f.append(np.percentile(epoch, 90))
    # spectral features
    f.extend(compute_all_bandpowers(epoch))
    # ratios: delta/theta, alpha/theta, sigma/total
    bandpowers = f[-5:]
    total_power = sum(bandpowers) + 1e-8
    f.append(bandpowers[0] / (bandpowers[1] + 1e-8)) # delta/theta
    f.append(bandpowers[2] / (bandpowers[1] + 1e-8)) # alpha/theta
    f.append(bandpowers[3] / (total_power)) # sigma/total
    # zero-crossing rate
    f.append(zero_crossing_rate(epoch))
    # Hjorth parameters
    diff1 = np.diff(epoch)
    diff2 = np.diff(diff1)
    var_zero = np.var(epoch)
    var_d1 = np.var(diff1)
    var_d2 = np.var(diff2)
    mobility = np.sqrt(var_d1/(var_zero+1e-8))
    complexity = np.sqrt(var_d2/(var_d1+1e-8)) / (mobility+1e-8)
    f.append(mobility)
    f.append(complexity)
    return np.array(f, dtype=np.float32)

def extract_features_block(x):
    # x shape: (epochs, samples)
    n_epochs = x.shape[0]
    feats = np.zeros((n_epochs, 18), dtype=np.float32)
    for i in range(n_epochs):
        feats[i] = extract_epoch_features(x[i])
    return feats

def build_feature_matrix(X):
    # X shape: (nights, epochs, samples)
    nights, epochs, samples = X.shape
    features = []
    for i in range(nights):
        x_night = X[i]
        x_night_norm = zscore_nightwise(x_night)
        feats = extract_features_block(x_night_norm)
        features.append(feats)
    return np.stack(features, axis=0)

def flatten_for_training(feature3d, label2d):
    # Convert shape (nights,epochs,features), (nights,epochs) --> (N,features), (N,), group (night_number repeated)
    nights, epochs, feats = feature3d.shape
    flat_features = feature3d.reshape(-1, feats)
    flat_labels = label2d.flatten()
    groups = np.broadcast_to(np.arange(nights)[:,None], (nights,epochs)).flatten()
    return flat_features, flat_labels, groups

def fit_predict(train_x, train_y, test_x):
    # Feature extraction
    train_feat = build_feature_matrix(train_x) # (5,1440,18)
    test_feat = build_feature_matrix(test_x)   # (3,1440,18)
    # Prepare training data: only use epochs with known expert labels
    Xtr, ytr, groups = flatten_for_training(train_feat, train_y)
    mask = ytr != -1
    Xtr = Xtr[mask]
    ytr = ytr[mask]
    groups = groups[mask]
    # Impute per-feature means (robust against any all-NaN features)
    imp = SimpleImputer(strategy='mean')
    Xtr = imp.fit_transform(Xtr)
    # Train a classifier (stratified by night with cross-validation for hyperparam selection)
    best_params = None
    best_macroF1 = -1
    splits = list(GroupKFold(n_splits=5).split(Xtr, ytr, groups))
    n_estimators_choices = [75, 100, 150]
    max_depth_choices = [8, 12, None]
    for n_estimators in n_estimators_choices:
        for max_depth in max_depth_choices:
            macroF1s = []
            for train_idx, val_idx in splits:
                clf = RandomForestClassifier(n_estimators=n_estimators, max_depth=max_depth, random_state=_SEED, n_jobs=1)
                clf.fit(Xtr[train_idx], ytr[train_idx])
                yval_pred = clf.predict(Xtr[val_idx])
                macroF1 = macro_f1(ytr[val_idx], yval_pred)
                macroF1s.append(macroF1)
            mean_macroF1 = np.mean(macroF1s)
            if mean_macroF1 > best_macroF1:
                best_macroF1 = mean_macroF1
                best_params = dict(n_estimators=n_estimators, max_depth=max_depth)
    clf = RandomForestClassifier(n_estimators=best_params['n_estimators'], max_depth=best_params['max_depth'], random_state=_SEED, n_jobs=1)
    clf.fit(Xtr, ytr)
    # Transform and impute test features
    nights_test, epochs_test, _ = test_feat.shape
    Xtest = test_feat.reshape(-1, test_feat.shape[2])
    Xtest = imp.transform(Xtest)
    ytest_pred = clf.predict(Xtest)
    # Reshape output (3,1440)
    return ytest_pred.reshape(nights_test, epochs_test).astype(int)

def macro_f1(y_true, y_pred):
    # Treat only the classes present in both y_true and y_pred (0,1,2,3,4)
    labels = [0,1,2,3,4]
    f1s = []
    for lab in labels:
        tp = np.sum((y_true == lab) & (y_pred == lab))
        fp = np.sum((y_true != lab) & (y_pred == lab))
        fn = np.sum((y_true == lab) & (y_pred != lab))
        if tp+fp == 0 or tp+fn == 0:
            f1s.append(0.0)
        else:
            prec = tp / (tp+fp)
            rec = tp / (tp+fn)
            if prec+rec == 0:
                f1s.append(0.0)
            else:
                f1s.append(2*prec*rec/(prec+rec))
    return np.mean(f1s)
