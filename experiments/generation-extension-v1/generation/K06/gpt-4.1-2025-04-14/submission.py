import numpy as np
from math import ceil
from collections import defaultdict
from functools import partial
from itertools import groupby
from sklearn.svm import SVC
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.model_selection import StratifiedKFold

# Helper to stratify folds by group (mouse) and label (class)
def _make_stratified_group_folds(y, groups, n_folds, seed):
    uniq_labels = np.unique(y)
    mice_by_label = defaultdict(list)
    for idx, (m, cl) in enumerate(zip(groups, y)):
        mice_by_label[cl].append(m)
    # unique + stable (seeded)
    rng = np.random.default_rng(seed)
    mice_folds = {}
    all_mice = []
    for cl in uniq_labels:
        mice = np.unique(mice_by_label[cl])
        rng.shuffle(mice)
        n = len(mice)
        splits = np.array_split(mice, n_folds)
        for fold, mice_in_fold in enumerate(splits):
            for m in mice_in_fold:
                mice_folds[m] = fold
        all_mice.extend(mice)
    # assign fold to each instance
    fold_vec = np.empty(len(y), dtype=int)
    for i, m in enumerate(groups):
        fold_vec[i] = mice_folds[m]
    return fold_vec

def fit_predict(train_x,train_y,test_x,train_groups):
    # Deterministic seed
    SEED = 20261031
    np.random.seed(SEED)
    rng = np.random.default_rng(SEED)

    # Prepare preprocessing (fit train only, apply test at end)
    imputer = SimpleImputer(strategy='median')
    scaler = StandardScaler()
    X_train_imp = imputer.fit_transform(train_x)
    X_train_std = scaler.fit_transform(X_train_imp)

    # Prepare test transformations
    X_test_imp = imputer.transform(test_x)
    X_test_std = scaler.transform(X_test_imp)

    # Get groups and folds for train
    group_ids = np.asarray(train_groups['group_ids'])
    cv_fold = np.asarray(train_groups['cv_fold'])
    y = np.array(train_y)

    # Model configs
    models = [
        ('svc_rbf_C.1', SVC(C=0.1, kernel='rbf', gamma='scale', random_state=SEED, probability=False, shrinking=True, tol=1e-3, max_iter=100000)),
        ('svc_rbf_C1',  SVC(C=1,   kernel='rbf', gamma='scale', random_state=SEED, probability=False, shrinking=True, tol=1e-3, max_iter=100000)),
        ('svc_rbf_C10', SVC(C=10,  kernel='rbf', gamma='scale', random_state=SEED, probability=False, shrinking=True, tol=1e-3, max_iter=100000)),
        ('svc_rbf_C100',SVC(C=100, kernel='rbf', gamma='scale', random_state=SEED, probability=False, shrinking=True, tol=1e-3, max_iter=100000)),
        ('et500_sqrt',  ExtraTreesClassifier(n_estimators=500, max_features='sqrt', bootstrap=False, random_state=SEED, n_jobs=1)),
        ('et500_1',     ExtraTreesClassifier(n_estimators=500, max_features=1, bootstrap=False, random_state=SEED, n_jobs=1))
    ]

    # Grouping logic: folds are fixed, only train splits used -- match cv_fold vector
    n_folds = 3
    mouse_ids = np.asarray(group_ids)
    # Map unique mouse IDs to group-wise indices for scoring
    unique_mice = np.unique(mouse_ids)
    classes = np.unique(y)

    # Class-balanced mouse-average accuracy metric
    def class_bal_mouse_acc(y_true, y_pred, mice, classes):
        # For each class, for each mouse, mean accuracy (within mouse), mean over mice, mean over classes
        class_mouse_accs = []
        for cl in classes:
            mouse_accs = []
            for m in np.unique(mice[y_true==cl]):
                idx = np.where((y_true==cl)&(mice==m))[0]
                acc = np.mean(y_pred[idx] == y_true[idx])
                mouse_accs.append(acc)
            if mouse_accs:
                class_mouse_accs.append(np.mean(mouse_accs))
        return np.mean(class_mouse_accs)

    # Fixed CV fold assignments used for inner validation
    val_scores = []
    for label, model in models:
        fold_accs = []
        for fold in range(n_folds):
            train_idx = np.where(cv_fold != fold)[0]
            valid_idx = np.where(cv_fold == fold)[0]
            # Impute and scale from training split only
            imp = SimpleImputer(strategy='median')
            sc  = StandardScaler()
            X_tr = sc.fit_transform(imp.fit_transform(X_train_std[train_idx]))
            X_va = sc.transform(imp.transform(X_train_std[valid_idx]))
            mdl = model
            try:
                mdl.fit(X_tr, y[train_idx])
                y_pred = mdl.predict(X_va)
            except Exception:
                y_pred = np.full(y[valid_idx].shape, np.bincount(y[train_idx]).argmax())
            acc = class_bal_mouse_acc(y[valid_idx], y_pred, mouse_ids[valid_idx], classes)
            fold_accs.append(acc)
        val_scores.append(np.mean(fold_accs))

    best_idx = int(np.argmax(val_scores))
    best_label, best_model = models[best_idx]
    # Retrain best model on all train
    # (imputer, scaler already fitted on full train)
    best_model.fit(X_train_std, y)
    y_test_pred = best_model.predict(X_test_std)
    return y_test_pred.astype(int)
