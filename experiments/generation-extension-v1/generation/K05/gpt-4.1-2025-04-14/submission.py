
import numpy as np
from collections import defaultdict, Counter
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
from sklearn.model_selection import KFold
import math


def fit_predict(train_x, train_y, test_x, train_groups):
    # Deterministic seed
    rng = np.random.default_rng(20261031)

    train_x = np.asarray(train_x)
    train_y = np.asarray(train_y)
    test_x = np.asarray(test_x)

    n_train, n_feat = train_x.shape
    n_targets = train_y.shape[1]

    # Get group information
    group_ids = np.array(train_groups['group_ids'])    # donor IDs
    block_ids = np.array(train_groups['block_ids'])    # block IDs

    # Compute sample weights: Each donor (group) gets equal total weight, blocks equal within donor
    unique_donors = np.unique(group_ids)
    donor_counts = Counter(group_ids)
    block_ids_per_donor = defaultdict(list)
    for i, donor in enumerate(group_ids):
        block_ids_per_donor[donor].append(block_ids[i])
    sample_weights = np.zeros(n_train, dtype=float)
    n_donors = len(unique_donors)
    for donor in unique_donors:
        # Find the indices for this donor
        donor_mask = (group_ids == donor)
        donor_indices = np.flatnonzero(donor_mask)
        donor_blocks = np.unique(block_ids[donor_indices])
        n_blocks = len(donor_blocks)
        # For each block, find how many samples
        for block in donor_blocks:
            block_mask = (group_ids == donor) & (block_ids == block)
            block_indices = np.flatnonzero(block_mask)
            block_weight = 1.0 / n_blocks / np.sum(block_mask)     # block splits donor equally, block's samples split block equally
            sample_weights[block_indices] = (1.0 / n_donors) * block_weight

    # Prepare cross-validation splits: group kfold on donor_ids (not block_ids)
    n_cv = min(4, n_donors)
    kf = KFold(n_splits=n_cv, shuffle=True, random_state=20261031)
    
    # Hyperparams and feature CV grid
    ALPHAS = [1, 10, 100, 1000, 10000]
    N_TOPGENES_CV = 1000
    
    # For feature selection: train_x is already 2000 features (variance-ranked outer-training/non-test)
    n_feat_select = N_TOPGENES_CV if N_TOPGENES_CV <= train_x.shape[1] else train_x.shape[1]
    # Compute variance
    feature_var = np.var(train_x, axis=0)
    sort_idx = np.argsort(-feature_var, kind='stable')[:n_feat_select]
    train_x_sel = train_x[:, sort_idx]
    test_x_sel = test_x[:, sort_idx]
    
    # Standardization: fit on train only
    scaler = StandardScaler().fit(train_x_sel)
    train_x_scaled = scaler.transform(train_x_sel)
    test_x_scaled = scaler.transform(test_x_sel)

    # Use grouped CV for alpha selection
    cv_scores = dict()
    for alpha in ALPHAS:
        y_true = []
        y_pred = []
        for train_idx, val_idx in kf.split(np.zeros(n_train), group_ids):
            # Each split is by donor
            xtr, xval = train_x_scaled[train_idx], train_x_scaled[val_idx]
            ytr, yval = train_y[train_idx], train_y[val_idx]
            wtr = sample_weights[train_idx]
            # Fit multioutput ridge
            model = Ridge(alpha=alpha, fit_intercept=True, random_state=20261031)
            model.fit(xtr, ytr, sample_weight=wtr)
            ypred_val = model.predict(xval)
            y_true.append(yval)
            y_pred.append(ypred_val)
        # Aggregate error per macro-rmse contract (donor_block_macro_rmse)
        y_true = np.vstack(y_true)
        y_pred = np.vstack(y_pred)
        agg_rmse = macro_rmse(y_true, y_pred, group_ids, block_ids)
        cv_scores[alpha] = agg_rmse
    # Choose alpha with lowest mean RMSE
    best_alpha = sorted(cv_scores, key=cv_scores.get)[0]

    # Retrain on full training set, output on test
    final_model = Ridge(alpha=best_alpha, fit_intercept=True, random_state=20261031)
    final_model.fit(train_x_scaled, train_y, sample_weight=sample_weights)
    y_test_pred = final_model.predict(test_x_scaled)
    # Clip to [0,1], finite output
    y_test_pred = np.clip(y_test_pred, 0.0, 1.0)
    return y_test_pred


def macro_rmse(y_true, y_pred, group_ids, block_ids):
    # y_true/y_pred: (n,3). group_ids: donor_id per row, block_ids: block_id per row.
    macro_rmse = []
    for t in range(y_true.shape[1]):
        # Target-wise aggregation
        per_donor = []
        for donor in np.unique(group_ids):
            donor_mask = (group_ids == donor)
            ids_in_donor = np.flatnonzero(donor_mask)
            blockids_donor = np.unique(block_ids[ids_in_donor])
            per_block = []
            for block in blockids_donor:
                block_mask = donor_mask & (block_ids == block)
                block_rows = np.flatnonzero(block_mask)
                if len(block_rows) == 0:
                    continue
                true_block = np.mean(y_true[block_rows, t])
                pred_block = np.mean(y_pred[block_rows, t])
                per_block.append((true_block, pred_block))
            # donor mean over blocks
            if per_block:
                true_blocks, pred_blocks = zip(*per_block)
                donor_rmse = np.sqrt(np.mean(np.square(np.subtract(true_blocks, pred_blocks))))
                per_donor.append(donor_rmse)
        # mean over donors
        if per_donor:
            macro_rmse.append(float(np.mean(per_donor)))
    if macro_rmse:
        return float(np.mean(macro_rmse))
    else:
        return float('nan')
