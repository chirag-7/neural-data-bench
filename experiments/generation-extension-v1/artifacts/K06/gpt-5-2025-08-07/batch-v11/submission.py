import numpy as np
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.ensemble import ExtraTreesClassifier

SEED = 20261031


def _majority_label(arr):
    a = np.asarray(arr, dtype=int)
    counts = np.bincount(a, minlength=2)
    return int(1 if counts[1] > counts[0] else 0)


def _cbma(y_true, y_pred, groups):
    y_true = np.asarray(y_true, dtype=int).ravel()
    y_pred = np.asarray(y_pred, dtype=int).ravel()
    groups = np.asarray(groups)
    mouse_to_idx = {}
    for i, g in enumerate(groups):
        mouse_to_idx.setdefault(g, []).append(i)
    per_class_accs = {0: [], 1: []}
    for g, idxs in mouse_to_idx.items():
        idxs = np.asarray(idxs, dtype=int)
        if idxs.size == 0:
            continue
        true_g = y_true[idxs]
        pred_g = y_pred[idxs]
        acc = float(np.mean(pred_g == true_g)) if idxs.size > 0 else 0.0
        cls = _majority_label(true_g)
        per_class_accs.setdefault(cls, []).append(acc)
    avgs = []
    for c in (0, 1):
        vals = per_class_accs.get(c, [])
        if len(vals) > 0:
            avgs.append(float(np.mean(vals)))
    if len(avgs) == 2:
        return 0.5 * (avgs[0] + avgs[1])
    elif len(avgs) == 1:
        return avgs[0]
    return 0.0


def _sample_weights(y, groups):
    y = np.asarray(y, dtype=int).ravel()
    groups = np.asarray(groups)
    n = y.shape[0]
    w = np.zeros(n, dtype=float)
    mouse_to_idx = {}
    for i, g in enumerate(groups):
        mouse_to_idx.setdefault(g, []).append(i)
    # Determine class per mouse via majority vote on y (training-only)
    mice_by_class = {0: [], 1: []}
    for g, idxs in mouse_to_idx.items():
        cls = _majority_label(y[np.asarray(idxs, dtype=int)])
        mice_by_class[cls].append(g)
    for c in (0, 1):
        mice = mice_by_class.get(c, [])
        if len(mice) == 0:
            continue
        class_factor = 1.0 / float(len(mice))
        for m in mice:
            idxs = mouse_to_idx[m]
            m_size = float(len(idxs)) if len(idxs) > 0 else 1.0
            wm = class_factor / m_size
            for i in idxs:
                w[i] = wm
    return w


def fit_predict(train_x, train_y, test_x, train_groups):
    X_tr = np.asarray(train_x, dtype=float)
    y_tr = np.asarray(train_y, dtype=int).ravel()
    X_te = np.asarray(test_x, dtype=float)
    groups = np.asarray(train_groups.get('group_ids'))
    cv_fold = np.asarray(train_groups.get('cv_fold'))

    if X_tr.ndim != 2 or X_te.ndim != 2:
        raise ValueError('train_x and test_x must be 2D arrays')
    if y_tr.shape[0] != X_tr.shape[0]:
        raise ValueError('train_y length must match train_x rows')
    if groups.shape[0] != X_tr.shape[0] or cv_fold.shape[0] != X_tr.shape[0]:
        raise ValueError('group_ids and cv_fold must match train_x rows')

    candidates = []
    for C in [0.1, 1.0, 10.0, 100.0]:
        candidates.append({'type': 'svm', 'C': float(C)})
    for mf in ['sqrt', 1]:
        candidates.append({'type': 'et', 'n_estimators': 500, 'max_features': mf})

    unique_folds = list(np.unique(cv_fold))
    best_spec, best_score = None, -1.0

    for spec in candidates:
        fold_scores = []
        for f in unique_folds:
            val_mask = (cv_fold == f)
            tr_mask = ~val_mask
            X_tr_f, y_tr_f, g_tr_f = X_tr[tr_mask], y_tr[tr_mask], groups[tr_mask]
            X_val_f, y_val_f, g_val_f = X_tr[val_mask], y_tr[val_mask], groups[val_mask]

            imp = SimpleImputer(strategy='median')
            X_tr_i = imp.fit_transform(X_tr_f)
            X_val_i = imp.transform(X_val_f)

            if spec['type'] == 'svm':
                scl = StandardScaler()
                X_tr_p = scl.fit_transform(X_tr_i)
                X_val_p = scl.transform(X_val_i)
                clf = SVC(C=spec['C'], kernel='rbf', gamma='scale')
            else:
                scl = None
                X_tr_p = X_tr_i
                X_val_p = X_val_i
                clf = ExtraTreesClassifier(
                    n_estimators=spec['n_estimators'],
                    max_features=spec['max_features'],
                    random_state=SEED,
                    n_jobs=1,
                )

            sw = _sample_weights(y_tr_f, g_tr_f)
            try:
                clf.fit(X_tr_p, y_tr_f, sample_weight=sw)
            except TypeError:
                clf.fit(X_tr_p, y_tr_f)
            y_pred_val = clf.predict(X_val_p)
            sc = _cbma(y_val_f, y_pred_val, g_val_f)
            if not np.isfinite(sc):
                sc = 0.0
            fold_scores.append(sc)
        mean_sc = float(np.mean(fold_scores)) if fold_scores else -1.0
        if mean_sc > best_score:
            best_score = mean_sc
            best_spec = spec

    if best_spec is None:
        best_spec = {'type': 'svm', 'C': 1.0}

    imp = SimpleImputer(strategy='median')
    X_tr_i = imp.fit_transform(X_tr)
    X_te_i = imp.transform(X_te)

    if best_spec['type'] == 'svm':
        scl = StandardScaler()
        X_tr_p = scl.fit_transform(X_tr_i)
        X_te_p = scl.transform(X_te_i)
        clf = SVC(C=best_spec['C'], kernel='rbf', gamma='scale')
    else:
        scl = None
        X_tr_p = X_tr_i
        X_te_p = X_te_i
        clf = ExtraTreesClassifier(
            n_estimators=best_spec.get('n_estimators', 500),
            max_features=best_spec.get('max_features', 'sqrt'),
            random_state=SEED,
            n_jobs=1,
        )

    sw_full = _sample_weights(y_tr, groups)
    try:
        clf.fit(X_tr_p, y_tr, sample_weight=sw_full)
    except TypeError:
        clf.fit(X_tr_p, y_tr)

    y_te_pred = clf.predict(X_te_p)
    y_te_pred = np.asarray(y_te_pred, dtype=int).ravel()
    y_te_pred = np.where(y_te_pred > 0, 1, 0)
    return y_te_pred
