import numpy as np
from sklearn.linear_model import RidgeCV
from sklearn.model_selection import GroupKFold
from sklearn.base import clone
from functools import partial
import math

SEED = 42
np.random.seed(SEED)

# Helper for z-score normalization using only valid frames
def maskzscore(x, mask):
    # x: (C, T), mask: (T,)
    x_valid = x[:, mask == 1]
    mean = x_valid.mean(axis=1, keepdims=True)
    std = x_valid.std(axis=1, keepdims=True)
    std[std == 0] = 1. # avoid div0
    normed = (x - mean) / std
    return normed, mean, std

def maskzscore_apply(x, mean, std):
    return (x - mean) / std

def maskinverse(normed, mean, std):
    return normed * std + mean

def flatten_masked(arr, mask):
    # arr: (*, T), mask: (T,)  --> reshape to [N, F]
    needsqueeze = arr.ndim == 2
    arr = arr if arr.ndim == 2 else arr[None, ...]
    result = arr[..., mask == 1]
    if needsqueeze:
        return result
    return result.squeeze(0)

def reconstruct_masked(y_valid, mask, fill=0.):
    # y_valid: (N_valid,), mask: (N_all,)
    out = np.full(mask.shape, fill, dtype=y_valid.dtype)
    out[mask == 1] = y_valid
    return out

def fit_predict(train_x, train_y, test_x, train_groups):
    # Each row: (C=3, L=900)
    ntrain, c, l = train_x.shape
    ntest = test_x.shape[0]
    
    # Extract fluo, mask, dt
    def extract(x):
        fluo = x[:,0,:]
        mask = x[:,1,:]
        dt = x[:,2,:]  # (N,900), one median value, repeated. Per-row.
        return fluo, mask, dt
    tra_fluo, tra_mask, tra_dt = extract(train_x)
    tes_fluo, tes_mask, tes_dt = extract(test_x)
    
    # Masked Z-score normalize each train record (valid frames only)
    norm_tra = []
    tra_mean, tra_std = [], []
    for i in range(ntrain):
        xnorm, xm, xs = maskzscore(tra_fluo[i:i+1], tra_mask[i])
        norm_tra.append(xnorm.squeeze(0))
        tra_mean.append(xm.squeeze(0))
        tra_std.append(xs.squeeze(0))
    norm_tra = np.stack(norm_tra)
    tra_mean = np.stack(tra_mean)
    tra_std  = np.stack(tra_std)
    
    # Similarly for test
    norm_tes = []
    tes_mean, tes_std = [], []
    for i in range(ntest):
        xnorm, xm, xs = maskzscore(tes_fluo[i:i+1], tes_mask[i])
        norm_tes.append(xnorm.squeeze(0))
        tes_mean.append(xm.squeeze(0))
        tes_std.append(xs.squeeze(0))
    norm_tes = np.stack(norm_tes)

    # Feature extraction: 
    # Use windowed means and derivatives; for simplicity, context 10 frames (~1.2s)
    def features(fluo_norm):
        N,T = fluo_norm.shape
        win = 10
        feats = []
        for i in range(N):
            x = fluo_norm[i]
            # Rolling mean
            mean_10 = np.convolve(x, np.ones(win)/win, 'same')
            # Rolling std
            sq = np.convolve(x**2, np.ones(win)/win, 'same')
            std_10 = np.sqrt(sq - mean_10**2)
            # Derivative (1-step)
            dx = np.zeros_like(x)
            dx[1:] = x[1:] - x[:-1]
            # Derivative (win-step)
            dxw = np.zeros_like(x)
            dxw[win:] = x[win:] - x[:-win]
            feats.append(np.stack([
                x, mean_10, std_10, dx, dxw
            ], axis=1))  # (T, 5)
        return np.stack(feats)

    tra_X = features(norm_tra)
    tes_X = features(norm_tes)
    
    # Assemble valid data for training (only valid frames, target not -1)
    X_list, y_list, group_list = [], [], []
    for i in range(ntrain):
        mask = tra_mask[i] == 1
        # also remove training targets that are padding (-1)
        valid = np.where(np.logical_and(mask, train_y[i] != -1))[0]
        X_list.append(tra_X[i, valid])
        y_list.append(train_y[i, valid])
        group_list.extend([train_groups[i]] * len(valid))
    X_train = np.concatenate(X_list, axis=0)
    y_train = np.concatenate(y_list, axis=0)
    groups = np.array(group_list)

    # GroupKFold for specimen-based cross-validation
    n_splits = min(5, len(np.unique(train_groups)))
    cv = GroupKFold(n_splits=n_splits)
    alphas = [0.1, 1.0, 10.0]
    reg = RidgeCV(alphas=alphas, cv=cv, scoring='neg_mean_squared_error', fit_intercept=True)
    reg.fit(X_train, y_train)
    model = reg

    # Fit again on all training data for actual predictions.
    model = clone(reg)
    model.fit(X_train, y_train)

    # Prediction for test set
    outputs = np.zeros((ntest, l), dtype=np.float32)
    for i in range(ntest):
        # Model expects (n_samples, n_features)
        mask = tes_mask[i] == 1
        preds = np.zeros(l, dtype=np.float32)
        if np.any(mask):
            Xi = tes_X[i, mask]
            yi = model.predict(Xi)
            # clip negatives
            yi = np.clip(yi, 0, None)
            preds[mask] = yi
        outputs[i,:] = preds
    return outputs

# End of fit_predict
