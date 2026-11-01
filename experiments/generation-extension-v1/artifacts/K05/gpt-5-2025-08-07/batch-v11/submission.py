import numpy as np
from sklearn.linear_model import Ridge
from sklearn.model_selection import GroupKFold

# Deterministic seed (no stochastic components used by Ridge, but fix anyway)
np.random.seed(20261031)


def _topk_variance_idx(X, k):
    # Use unbiased variance; break ties deterministically by stable sort
    v = np.var(X, axis=0, ddof=1)
    if not np.all(np.isfinite(v)):
        v = np.nan_to_num(v, nan=0.0, posinf=0.0, neginf=0.0)
    k = int(min(k, X.shape[1]))
    order = np.argsort(-v, kind='mergesort')
    return order[:k]


def _zscore_fit(X):
    mu = X.mean(axis=0)
    sd = X.std(axis=0, ddof=1)
    sd = np.where((sd <= 0) | ~np.isfinite(sd), 1.0, sd)
    return mu, sd


def _zscore_apply(X, mu, sd):
    return (X - mu) / sd


def _sample_weights_for_subset(group_ids, block_ids, subset_idx):
    # Equal donor weight; equal block weight within donor; replicates share block weight
    subset_idx = np.asarray(subset_idx)
    g_sub = np.asarray(group_ids)[subset_idx]
    b_sub = np.asarray(block_ids)[subset_idx]
    donors = np.unique(g_sub)
    D = len(donors)
    w = np.zeros(len(subset_idx), dtype=float)
    if D == 0:
        return w
    donor_w = 1.0 / D
    for d in donors:
        m_d = np.where(g_sub == d)[0]
        if m_d.size == 0:
            continue
        blocks = b_sub[m_d]
        u_blocks = np.unique(blocks)
        B = len(u_blocks)
        if B == 0:
            continue
        block_w = donor_w / B
        for b in u_blocks:
            m_db = m_d[blocks == b]
            if m_db.size == 0:
                continue
            w[m_db] = block_w / m_db.size
    return w


def _donor_block_macro_rmse(y_true, y_pred, donors, blocks):
    # Returns per-target RMSE after donor->block macro averaging
    donors = np.asarray(donors)
    blocks = np.asarray(blocks)
    ud = np.unique(donors)
    per_donor_mse = []
    for d in ud:
        m_d = donors == d
        if not np.any(m_d):
            continue
        bd = blocks[m_d]
        ytd = y_true[m_d]
        ypd = y_pred[m_d]
        ub = np.unique(bd)
        block_errs = []
        for b in ub:
            m_b = bd == b
            yt_b = ytd[m_b].mean(axis=0)
            yp_b = ypd[m_b].mean(axis=0)
            block_errs.append((yp_b - yt_b) ** 2)
        if block_errs:
            per_donor_mse.append(np.mean(block_errs, axis=0))
    if not per_donor_mse:
        return np.full(y_true.shape[1], np.inf)
    mse = np.mean(per_donor_mse, axis=0)
    return np.sqrt(mse)


def _cv_select_alpha(X, Y, donors, blocks, alphas, max_splits=4, k_feats=1000):
    donors = np.asarray(donors)
    blocks = np.asarray(blocks)
    n_groups = len(np.unique(donors))
    n_splits = max(2, min(max_splits, n_groups))
    gkf = GroupKFold(n_splits=n_splits)
    scores = np.zeros(len(alphas), dtype=float)
    nfolds = 0
    for tr_idx, va_idx in gkf.split(X, Y, groups=donors):
        nfolds += 1
        feats = _topk_variance_idx(X[tr_idx], k_feats)
        Xtr = X[tr_idx][:, feats]
        Xva = X[va_idx][:, feats]
        mu, sd = _zscore_fit(Xtr)
        Xtr = _zscore_apply(Xtr, mu, sd)
        Xva = _zscore_apply(Xva, mu, sd)
        w = _sample_weights_for_subset(donors, blocks, tr_idx)
        for i, a in enumerate(alphas):
            mdl = Ridge(alpha=float(a), fit_intercept=True, random_state=0)
            mdl.fit(Xtr, Y[tr_idx], sample_weight=w)
            pred = mdl.predict(Xva)
            rmse_vec = _donor_block_macro_rmse(Y[va_idx], pred, donors[va_idx], blocks[va_idx])
            scores[i] += float(np.mean(rmse_vec))
    scores /= max(nfolds, 1)
    best_i = int(np.argmin(scores))
    return float(alphas[best_i])


def fit_predict(train_x, train_y, test_x, train_groups):
    # Convert inputs
    X = np.asarray(train_x, dtype=float)
    Y = np.asarray(train_y, dtype=float)
    Xte = np.asarray(test_x, dtype=float)
    group_ids = np.asarray(train_groups.get('group_ids'))
    block_ids = np.asarray(train_groups.get('block_ids'))

    # Basic checks
    if X.ndim != 2 or Y.ndim != 2 or Xte.ndim != 2:
        raise ValueError('Inputs must be 2D arrays.')
    if X.shape[0] != Y.shape[0]:
        raise ValueError('train_x and train_y row counts must match.')
    if group_ids.shape[0] != X.shape[0] or block_ids.shape[0] != X.shape[0]:
        raise ValueError('group_ids and block_ids must align with training rows.')

    # Hyperparameters and CV selection
    alphas = [1.0, 10.0, 100.0, 1000.0, 10000.0]
    best_alpha = _cv_select_alpha(X, Y, group_ids, block_ids, alphas, max_splits=4, k_feats=1000)

    # Final fit using all training data
    feats = _topk_variance_idx(X, 1000)
    Xtr = X[:, feats]
    Xtes = Xte[:, feats]
    mu, sd = _zscore_fit(Xtr)
    Xtr = _zscore_apply(Xtr, mu, sd)
    Xtes = _zscore_apply(Xtes, mu, sd)

    w_all = _sample_weights_for_subset(group_ids, block_ids, np.arange(X.shape[0]))
    model = Ridge(alpha=float(best_alpha), fit_intercept=True, random_state=0)
    model.fit(Xtr, Y, sample_weight=w_all)
    preds = model.predict(Xtes)

    # Clip to valid fraction range and ensure finite
    preds = np.clip(np.nan_to_num(preds, nan=0.0, posinf=1.0, neginf=0.0), 0.0, 1.0)
    return preds
