import numpy as np
from scipy.signal import stft
from scipy.ndimage import uniform_filter1d
from sklearn.ensemble import HistGradientBoostingClassifier
import math

def _extract_feats(x, sr=32000, n_fft=256, hop_length=32, n_bands=24, fmin=250, fmax=12000):
    x = x.copy()
    isnan = np.isnan(x)
    if isnan.any():  # Remove trailing NaNs
        x = x[:np.where(isnan)[0][0]]
    f, t, Zxx = stft(x, fs=sr, nperseg=n_fft, noverlap=n_fft-hop_length, window='hann', padded=False, boundary=None)
    S = np.abs(Zxx) ** 2  # Power spectrogram
    S = np.maximum(S, 1e-12)
    # Construct log-frequency bands
    mel_f = np.geomspace(fmin, fmax, n_bands + 1)
    bands = np.zeros((n_bands, S.shape[1]), dtype=np.float32)
    for b in range(n_bands):
        lo, hi = mel_f[b], mel_f[b + 1]
        idx = np.where((f >= lo) & (f < hi))[0]
        if len(idx) == 0:
            bands[b] = 1e-12
        else:
            bands[b] = S[idx].sum(axis=0) + 1e-12
    log_bands = np.log(bands)
    # Noise floor normalization: subtract 20th percentile per recording
    log_bands = log_bands - np.percentile(log_bands, 20, axis=1, keepdims=True)
    # Add broadband feature (sum of all bands)
    broadband = np.log(S.sum(axis=0) + 1e-12)
    broadband -= np.percentile(broadband, 20)
    features = np.vstack([log_bands, broadband[None]])
    # Add smoothed features (5ms, 15ms window)
    for width in [5, 15]:  # in ms
        filt = uniform_filter1d(log_bands, int(width), axis=1, mode='nearest')
        features = np.vstack([features, filt])
    return features.T  # shape (num_frames, feat_dim)

def _extract_all_feats(X):
    features = []
    valid_ns = []
    for row in X:
        isnan = np.isnan(row)
        nvalid = (np.where(isnan)[0][0] if isnan.any() else len(row))
        feats = _extract_feats(row)
        features.append(feats)
        valid_ns.append(min(feats.shape[0], nvalid // 32))
    return features, np.array(valid_ns)

def _get_train_labels(train_y, valid_ns):
    feats_y = []
    for yrow, n_valid in zip(train_y, valid_ns):
        mask = yrow[:n_valid]
        # Ignore out-of-range and -1s
        ok = (mask != -1)
        feats_y.append(mask[ok])
    return feats_y

def _event_runs(labels):
    # Returns onset, offset bin indices for consecutive 1-labeled runs (on[:], off[:] such that labels[on[i]:off[i]]=1)
    labels = np.concatenate([[0], labels, [0]])
    diff = np.diff(labels)
    on = np.where(diff == 1)[0]
    off = np.where(diff == -1)[0]
    return on, off

def _metrics(pred_labels, true_labels):
    # Both are len N binary 1ms rasters
    pon, poff = _event_runs(pred_labels)
    ton, toff = _event_runs(true_labels)
    pred_events = np.stack([pon, poff], axis=1)
    true_events = np.stack([ton, toff], axis=1)
    matched_pred = set()
    matched_true = set()
    for p_idx, (p0, p1) in enumerate(pred_events):
        p0_sec, p1_sec = p0 * 0.001, p1 * 0.001
        best = -1
        best_dist = 1e9
        for t_idx, (t0, t1) in enumerate(true_events):
            t0_sec, t1_sec = t0 * 0.001, t1 * 0.001
            onset_err = abs(t0_sec - p0_sec)
            offset_err = abs(t1_sec - p1_sec)
            duration = t1_sec - t0_sec
            tol = max(0.02, 0.2 * duration)
            if onset_err <= 0.02 + 1e-12 and offset_err <= tol + 1e-12:
                dist = onset_err + offset_err
                if dist < best_dist:
                    best, best_dist = t_idx, dist
        if best >= 0 and best not in matched_true:
            matched_pred.add(p_idx)
            matched_true.add(best)
    TP = len(matched_pred)
    return TP, len(pred_events), len(true_events)

def fit_predict(train_x, train_y, test_x, train_groups):
    np.random.seed(20261031)
    # Extract features on train/test, and determine valid frame counts
    X_train_feats, train_valid_ns = _extract_all_feats(train_x)
    X_test_feats, test_valid_ns = _extract_all_feats(test_x)
    # Training/validation split: rows 0,5,...,55 for val
    train_idx = [i for i in range(60) if i % 5 != 0]
    val_idx = [i for i in range(60) if i % 5 == 0]
    # Get feature arrays and labels
    X_train = np.concatenate([X_train_feats[i][:train_valid_ns[i]] for i in train_idx], axis=0)
    y_train = np.concatenate(_get_train_labels(train_y[train_idx], train_valid_ns[train_idx]))
    X_val = np.concatenate([X_train_feats[i][:train_valid_ns[i]] for i in val_idx], axis=0)
    y_val = np.concatenate(_get_train_labels(train_y[val_idx], train_valid_ns[val_idx]))
    # Downsample for fitting
    if len(y_train) > 60000:
        idxs = np.linspace(0, len(y_train) - 1, 60000, dtype=int)
        X_train = X_train[idxs]
        y_train = y_train[idxs]
    clf = HistGradientBoostingClassifier(
        max_iter=80, max_leaf_nodes=15, learning_rate=0.1,
        l2_regularization=10, max_bins=128, random_state=20261031,
        verbose=0)
    clf.fit(X_train, y_train)
    # Threshold/gap fill/min duration tuning using val
    thresholds = [0.3, 0.5, 0.7]
    gap_fills = [0, 4, 8]
    min_durs = [5, 10, 20]
    best_f1 = -1
    for thresh in thresholds:
        for gap_fill in gap_fills:
            for min_dur in min_durs:
                val_pred = clf.predict_proba(X_val)[:, 1] > thresh
                # Gap fill: fill isolated 0s less than gap_fill wide between 1s
                if gap_fill > 0:
                    in_ = val_pred.astype(int)
                    on, off = _event_runs(in_)
                    for idx in range(1, len(on)):
                        gap = on[idx] - off[idx-1]
                        if 0 < gap <= gap_fill:
                            in_[off[idx-1]:on[idx]] = 1
                    val_pred = in_
                # Minimum duration
                in_ = val_pred.astype(int)
                on, off = _event_runs(in_)
                for o0, o1 in zip(on, off):
                    if (o1 - o0) < min_dur:
                        in_[o0:o1] = 0
                val_pred = in_
                # Evaluate per-recording F1 on val rows
                v_ns = train_valid_ns[val_idx]
                start = 0
                f1s = []
                for vlen, row in zip(v_ns, train_y[val_idx]):
                    stop = start + vlen
                    pred = val_pred[start:stop]
                    true = row[:vlen]
                    ok = (true != -1)
                    TP, Np, Nr = _metrics(pred[ok], true[ok])
                    if Np == 0 and Nr == 0:
                        f1s.append(1.0)
                    else:
                        f1s.append(2 * TP / (Np + Nr) if (Np + Nr) > 0 else 0)
                    start = stop
                mean_f1 = np.mean(f1s)
                if mean_f1 > best_f1:
                    best_f1 = mean_f1
                    best_params = (thresh, gap_fill, min_dur)
    # Retrain on all rows
    X_all = np.concatenate([X_train_feats[i][:train_valid_ns[i]] for i in range(60)], axis=0)
    y_all = np.concatenate(_get_train_labels(train_y, train_valid_ns))
    if len(y_all) > 60000:
        idxs = np.linspace(0, len(y_all) - 1, 60000, dtype=int)
        X_all = X_all[idxs]
        y_all = y_all[idxs]
    clf = HistGradientBoostingClassifier(
        max_iter=80, max_leaf_nodes=15, learning_rate=0.1,
        l2_regularization=10, max_bins=128, random_state=20261031,
        verbose=0)
    clf.fit(X_all, y_all)
    thresh, gap_fill, min_dur = best_params
    # Predict test recordings
    result = np.zeros((20, test_x.shape[1] // 32), dtype=np.int8)
    for i in range(20):
        n_valid = test_valid_ns[i]
        feats = X_test_feats[i][:n_valid]
        if len(feats) == 0:
            continue
        test_pred = clf.predict_proba(feats)[:, 1] > thresh
        # Gap fill
        if gap_fill > 0 and len(test_pred) > 0:
            in_ = test_pred.astype(int)
            on, off = _event_runs(in_)
            for idx in range(1, len(on)):
                gap = on[idx] - off[idx-1]
                if 0 < gap <= gap_fill:
                    in_[off[idx-1]:on[idx]] = 1
            test_pred = in_
        # Min duration
        in_ = test_pred.astype(int)
        on, off = _event_runs(in_)
        for o0, o1 in zip(on, off):
            if (o1 - o0) < min_dur:
                in_[o0:o1] = 0
        test_pred = in_
        # Fill output, pad as required
        result[i, :n_valid] = test_pred[:n_valid]
    return result.astype(np.int8)
