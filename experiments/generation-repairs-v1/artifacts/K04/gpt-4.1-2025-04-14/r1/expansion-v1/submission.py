import numpy as np
from collections import Counter
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GroupKFold
from sklearn.preprocessing import StandardScaler
from sklearn.base import clone
from sklearn.utils import resample
import gc

# Fixed random state for determinism
SEED = 57463
np.random.seed(SEED)

# Robust scaler: Median + MAD
class RobustStandardizer:
    def fit(self, X):
        self.medians = np.median(X, axis=0)
        self.mads = np.median(np.abs(X - self.medians), axis=0)
        self.mads[self.mads == 0] = 1.0  # Avoid division by zero
        return self
    def transform(self, X):
        return (X - self.medians) / self.mads
    def fit_transform(self, X):
        self.fit(X)
        return self.transform(X)

def fit_predict(train_x, train_y, test_x, train_groups):
    # Apply robust standardization using only training data
    scaler = RobustStandardizer().fit(train_x)
    X_train = scaler.transform(train_x)
    X_test  = scaler.transform(test_x)

    # Models: Logistic regression (multinomial, balanced), RF
    lr = LogisticRegression(
        
        solver='saga',
        max_iter=400,
        random_state=SEED,
        class_weight='balanced'
    )
    rf = RandomForestClassifier(
        n_estimators=100,
        max_depth=15,
        class_weight='balanced',
        random_state=SEED,
        n_jobs=1
    )

    n_classes = len(np.unique(train_y))  # May not encounter all 7 every fold

    # Storage for test probabilities from each model
    test_pred_proba_lr = np.zeros((X_test.shape[0], 7))
    test_pred_proba_rf = np.zeros((X_test.shape[0], 7))

    # To approximate validation robustness, do GroupKFold (donor) splitting
    # Use 2 splits, as only two donors present, but stratify to preserve class distribution
    gkf = GroupKFold(n_splits=2)

    # Out-of-fold validation (used for tuning model weights & as regularizer)
    oof_pred_proba_lr = np.zeros((X_train.shape[0], 7))
    oof_pred_proba_rf = np.zeros((X_train.shape[0], 7))

    for i, (train_idx, val_idx) in enumerate(gkf.split(X_train, train_y, groups=train_groups)):
        X_tr, y_tr = X_train[train_idx], train_y[train_idx]
        X_val = X_train[val_idx]
        # What unique classes are present?
        present_lbls = np.unique(y_tr)
        # Fit models on this donor's (group's) fold
        lr_i = clone(lr)
        rf_i = clone(rf)
        lr_i.fit(X_tr, y_tr)
        rf_i.fit(X_tr, y_tr)
        # Predict probabilities on held-in validation set, fill as-needed for missing classes
        proba_lr = np.zeros((X_val.shape[0], 7))
        proba_rf = np.zeros((X_val.shape[0], 7))
        proba_lr[:, present_lbls] = lr_i.predict_proba(X_val)
        proba_rf[:, present_lbls] = rf_i.predict_proba(X_val)
        oof_pred_proba_lr[val_idx] = proba_lr
        oof_pred_proba_rf[val_idx] = proba_rf
    # Memory cleanup
    gc.collect()

    # Tune blend: Take val macro-F1 for each model and weighted average
    # Use macro F1, tolerating missing classes per fold -- recode to strict 7-class
    def stable_macro_f1(y_true, probas):
        y_pred = np.argmax(probas, axis=1)
        # For each class (0..6), get precision/recall, ignore if never occurs in y_true (per rules), avg.
        f1s = []
        for c in range(7):
            tp = np.sum((y_true == c) & (y_pred == c))
            fp = np.sum((y_true != c) & (y_pred == c))
            fn = np.sum((y_true == c) & (y_pred != c))
            denom = (2 * tp + fp + fn)
            f1 = (2*tp) / denom if denom > 0 else 0.0
            f1s.append(f1)
        return np.mean(f1s)

    val_f1_lr = stable_macro_f1(train_y, oof_pred_proba_lr)
    val_f1_rf = stable_macro_f1(train_y, oof_pred_proba_rf)
    # Blend weights: proportional to F1 (avoid zero weights)
    f1_sum = val_f1_lr + val_f1_rf + 1e-8
    w_lr = val_f1_lr / f1_sum
    w_rf = val_f1_rf / f1_sum

    # Now fit models on ALL training data (as submission rules wish)
    lr.fit(X_train, train_y)
    rf.fit(X_train, train_y)
    # May not have seen all classes in some donors:
    # Get unique classes observed in training
    present_lbls_all = np.unique(train_y)
    # Predict proba on test, fill zeros for missing classes
    pred_proba_lr = np.zeros((X_test.shape[0], 7))
    pred_proba_rf = np.zeros((X_test.shape[0], 7))
    pred_proba_lr[:, present_lbls_all] = lr.predict_proba(X_test)
    pred_proba_rf[:, present_lbls_all] = rf.predict_proba(X_test)
    
    # Renormalize rows so each row sums to 1, even if missing a class (rare)
    pred_proba_lr /= (pred_proba_lr.sum(1, keepdims=True) + 1e-8)
    pred_proba_rf /= (pred_proba_rf.sum(1, keepdims=True) + 1e-8)

    # Weighted average (blend)
    test_pred_proba = w_lr * pred_proba_lr + w_rf * pred_proba_rf

    # Final labels: argmax of rows
    pred_labels = np.argmax(test_pred_proba, axis=1)
    return pred_labels
