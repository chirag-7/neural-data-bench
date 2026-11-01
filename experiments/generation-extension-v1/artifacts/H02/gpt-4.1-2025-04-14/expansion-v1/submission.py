import numpy as np
from scipy.signal import detrend
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.model_selection import LeaveOneGroupOut
from sklearn.preprocessing import StandardScaler
from functools import partial
np.random.seed(42)

# Time window parameters for P300 (in samples)
FS = 128
WIN_START = int(0.3 * FS)  # 300ms
WIN_END = int(0.6 * FS)    # 600ms (typical P300 latency window)

class P300Extractor:
    def __init__(self, win_start, win_end):
        self.win_start = win_start
        self.win_end = win_end
        self.scaler = None
        self.ch_mean_ = None
        self.ch_std_ = None
    def fit(self, X):
        # X: [n_trials, n_chan, n_times]
        # Channel-wise z-score using the train data
        shape = X.shape
        Xf = X.reshape(-1, shape[-1])
        self.ch_mean_ = Xf.mean(axis=0)
        self.ch_std_ = Xf.std(axis=0) + 1e-8
        return self
    def transform(self, X):
        # Z-score each channel per timepoint using training statistics
        shape = X.shape
        Xf = X.reshape(-1, shape[-1])
        Xf = (Xf - self.ch_mean_) / self.ch_std_
        Xn = Xf.reshape(shape)
        # Extract features: mean signal in window per channel
        feats = Xn[:, :, self.win_start:self.win_end].mean(axis=2)
        return feats   # shape: [n_trials, n_chan]


def fit_predict(train_x, train_y, test_x, train_groups):
    # 1. Feature extraction and normalization
    extractor = P300Extractor(WIN_START, WIN_END)
    extractor.fit(train_x)
    X_train_feat = extractor.transform(train_x)  # [n_trials, n_chan]
    X_test_feat = extractor.transform(test_x)

    # 2. Channel weights via meta-LDA on cross-validated training
    logo = LeaveOneGroupOut()
    n_channels = X_train_feat.shape[1]
    # Channel-wise single-feature LDA, then aggregate
    # To keep things simple, use ridge regularized LDA
    best_shrinkage = None
    best_auc = -np.inf
    shrinkages = [None, 'auto', 0.05, 0.1, 0.2, 0.5]  # Candidate shrinkages
    # Estimate generalization performance to select regularization
    from sklearn.metrics import roc_auc_score
    for shrink in shrinkages:
        aucs = []
        for train_idx, val_idx in logo.split(X_train_feat, train_y, groups=train_groups):
            X_tr_cv, X_val_cv = X_train_feat[train_idx], X_train_feat[val_idx]
            y_tr_cv, y_val_cv = train_y[train_idx], train_y[val_idx]
            lda = LinearDiscriminantAnalysis(solver='lsqr', shrinkage=shrink)
            lda.fit(X_tr_cv, y_tr_cv)
            val_score = lda.decision_function(X_val_cv)
            # All positive samples should have higher scores
            if np.any(np.isnan(val_score)):
                continue
            auc = roc_auc_score(y_val_cv, val_score)
            aucs.append(auc)
        mean_auc = np.mean(aucs) if aucs else -np.inf
        if mean_auc > best_auc:
            best_auc = mean_auc
            best_shrinkage = shrink
    # Fit on all training with chosen shrinkage
    clf = LinearDiscriminantAnalysis(solver='lsqr', shrinkage=best_shrinkage)
    clf.fit(X_train_feat, train_y)
    # 3. Apply to test feature matrix
    test_scores = clf.decision_function(X_test_feat)  # shape: [n_test,]
    # Ensure scores are finite, orientation is correct (higher = more target-like)
    test_scores = np.nan_to_num(test_scores, nan=0.0, posinf=0.0, neginf=0.0)
    return test_scores
