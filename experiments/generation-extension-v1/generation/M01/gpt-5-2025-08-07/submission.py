import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GroupKFold

# Deterministic small epsilon
_EPS = 1e-6

def _safelogit(p):
    p = np.clip(p, _EPS, 1.0 - _EPS)
    return np.log(p) - np.log(1.0 - p)

def _engineer_features(X):
    # X columns: [contrastLeft, contrastRight, probabilityLeft,
    #             previous_choice_lag1..lag5, previous_feedback_lag1..lag5]
    X = np.asarray(X, dtype=float)
    cL = X[:, 0]
    cR = X[:, 1]
    pL = X[:, 2]
    ch = X[:, 3:8]
    fb = X[:, 8:13]

    # Sensory evidence features
    delta = cR - cL
    s = cR + cL
    ratio = delta / (s + 1e-3)  # relative evidence
    cmax = np.maximum(cL, cR)
    cmin = np.minimum(cL, cR)
    abs_delta = np.abs(delta)

    # Prior features
    pl_centered = pL - 0.5
    pl_logit = _safelogit(pL)

    # Interactions with prior
    inter_delta_logit = delta * pl_logit
    inter_ratio_logit = ratio * pl_logit

    # History features
    # Raw last 5 choices and feedbacks
    rcombo = ch * fb  # reinforcement-like signed signal

    # Aggregates
    decay = np.power(0.65, np.arange(5))  # strong recency
    dec_choice = ch @ decay
    dec_rcombo = rcombo @ decay
    sum_choice = np.sum(ch, axis=1)
    sum_rcombo = np.sum(rcombo, axis=1)
    cnt_choice_obs = np.sum(ch != 0.0, axis=1).astype(float)
    cnt_fb_obs = np.sum(fb != 0.0, axis=1).astype(float)

    # Stack features
    feats = [
        cL, cR, pL,
        delta, s, ratio, cmax, cmin, abs_delta,
        pl_centered, pl_logit,
        inter_delta_logit, inter_ratio_logit,
    ]

    # Add raw history terms (choices, feedback, reinforcement products)
    feats.extend([ch[:, i] for i in range(5)])
    feats.extend([fb[:, i] for i in range(5)])
    feats.extend([rcombo[:, i] for i in range(5)])

    # Add aggregates
    feats.extend([dec_choice, dec_rcombo, sum_choice, sum_rcombo,
                  cnt_choice_obs, cnt_fb_obs])

    F = np.vstack(feats).T
    return F

def _per_group_mean_logloss(y_true, p, groups):
    p = np.clip(p, _EPS, 1.0 - _EPS)
    nll = -(y_true * np.log(p) + (1 - y_true) * np.log(1 - p))
    # Average per group, then mean across groups (each mouse equal)
    groups = np.asarray(groups)
    uniq = np.unique(groups)
    vals = []
    for g in uniq:
        idx = (groups == g)
        if np.any(idx):
            vals.append(np.mean(nll[idx]))
    return float(np.mean(vals)) if len(vals) else float(np.mean(nll))

def _equalize_mouse_weights(groups):
    groups = np.asarray(groups)
    uniq, counts = np.unique(groups, return_counts=True)
    count_map = {g: c for g, c in zip(uniq, counts)}
    w = np.array([1.0 / count_map[g] for g in groups], dtype=float)
    # Normalize to keep average weight ~1
    w *= (len(w) / np.sum(w))
    return w

def fit_predict(train_x, train_y, test_x, train_groups):
    # Convert inputs
    X_tr_raw = np.asarray(train_x, dtype=float)
    y_tr = np.asarray(train_y, dtype=int).ravel()
    X_te_raw = np.asarray(test_x, dtype=float)
    groups = np.asarray(train_groups)

    # Engineer features
    X_tr = _engineer_features(X_tr_raw)
    X_te = _engineer_features(X_te_raw)

    # Group-aware CV to pick C
    uniq_groups = np.unique(groups)
    n_splits = int(min(5, max(2, len(uniq_groups))))
    gkf = GroupKFold(n_splits=n_splits)
    C_grid = [0.05, 0.1, 0.3, 1.0, 3.0]

    best_score = float('inf')
    best_C = C_grid[0]

    for C in C_grid:
        fold_scores = []
        for tr_idx, va_idx in gkf.split(X_tr, y_tr, groups):
            Xt, Xv = X_tr[tr_idx], X_tr[va_idx]
            yt, yv = y_tr[tr_idx], y_tr[va_idx]
            gt, gv = groups[tr_idx], groups[va_idx]

            wt = _equalize_mouse_weights(gt)

            scaler = StandardScaler()
            Xt_s = scaler.fit_transform(Xt)
            Xv_s = scaler.transform(Xv)

            clf = LogisticRegression(
                C=C,
                penalty='l2',
                solver='lbfgs',
                max_iter=1000,
                random_state=0,
                n_jobs=None,
            )
            clf.fit(Xt_s, yt, sample_weight=wt)
            pv = clf.predict_proba(Xv_s)[:, 1]
            score = _per_group_mean_logloss(yv, pv, gv)
            fold_scores.append(score)
        mean_score = float(np.mean(fold_scores))
        if mean_score < best_score - 1e-9:
            best_score = mean_score
            best_C = C

    # Final fit on all training data with per-mouse equalization
    w_full = _equalize_mouse_weights(groups)
    scaler = StandardScaler()
    X_tr_s = scaler.fit_transform(X_tr)
    X_te_s = scaler.transform(X_te)

    final_clf = LogisticRegression(
        C=best_C,
        penalty='l2',
        solver='lbfgs',
        max_iter=1000,
        random_state=0,
        n_jobs=None,
    )
    final_clf.fit(X_tr_s, y_tr, sample_weight=w_full)

    p_te = final_clf.predict_proba(X_te_s)[:, 1]
    p_te = np.clip(p_te, _EPS, 1.0 - _EPS)
    return p_te
