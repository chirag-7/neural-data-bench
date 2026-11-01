import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupKFold
from sklearn.metrics import log_loss

# Deterministic seed for reproducibility
np.random.seed(42)

def fit_predict(train_x, train_y, test_x, train_groups):
    # Hyperparameter grid for regularization
    C_grid = np.logspace(-3, 2, 11)
    n_splits = 5

    # Prepare arrays
    train_x = np.asarray(train_x, dtype=float)
    test_x = np.asarray(test_x, dtype=float)
    train_y = np.asarray(train_y, dtype=int)
    train_groups = np.asarray(train_groups)

    # Standardize continuous features (contrastLeft, contrastRight, probabilityLeft)
    # Only fit scaler on train_x
    scaler = StandardScaler()
    scaler.fit(train_x[:, :3])
    train_x_scale = train_x.copy()
    test_x_scale = test_x.copy()
    train_x_scale[:, :3] = scaler.transform(train_x[:, :3])
    test_x_scale[:, :3] = scaler.transform(test_x[:, :3])

    # Historical features (columns 3-12) remain as is: choices (-1,0,1), feedbacks (-1,0,1)

    # Cross-validation for C selection (mouse-disjoint)
    best_C = None
    best_cv_loss = np.inf
    for C in C_grid:
        cv_losses = []
        # 5-fold grouped (by mouse) cross-validation
        cv = GroupKFold(n_splits=n_splits)
        for train_idx, val_idx in cv.split(train_x_scale, train_y, groups=train_groups):
            X_train = train_x_scale[train_idx]
            y_train = train_y[train_idx]
            X_val = train_x_scale[val_idx]
            y_val = train_y[val_idx]
            # Fit on this train fold
            clf = LogisticRegression(C=C, solver='liblinear', penalty='l2', random_state=42, max_iter=200)
            clf.fit(X_train, y_train)
            pred_prob = clf.predict_proba(X_val)[:,1]
            pred_prob = np.clip(pred_prob, 1e-6, 1-1e-6)
            # Per-mouse mean log loss
            val_mice = train_groups[val_idx]
            losses = []
            for mouse_id in np.unique(val_mice):
                idx = (val_mice == mouse_id)
                # mean negative log-likelihood for this mouse
                loss = log_loss(y_val[idx], pred_prob[idx], labels=[0,1])
                losses.append(loss)
            cv_losses.append(np.mean(losses))
        mean_cv_loss = np.mean(cv_losses)
        if mean_cv_loss < best_cv_loss:
            best_cv_loss = mean_cv_loss
            best_C = C

    # Refit on ALL grouped training data with chosen C
    final_clf = LogisticRegression(C=best_C, solver='liblinear', penalty='l2', random_state=42, max_iter=200)
    final_clf.fit(train_x_scale, train_y)

    # Predict on test_x_scale
    test_probs = final_clf.predict_proba(test_x_scale)[:,1]
    test_probs = np.clip(test_probs, 1e-6, 1-1e-6)
    return test_probs.tolist()
