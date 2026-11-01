import numpy as np
from sklearn.model_selection import KFold
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from math import log

def _poisson_nll(y_true, y_pred):
    # Clip y_pred to avoid log(0) and excessive penalization in tail
    y_pred = np.clip(y_pred, 1e-6, None)
    # Standard mean Poisson NLL ignoring the const for optimization
    return np.mean(y_pred - y_true * np.log(y_pred))

def _get_unique_test_images(test_x, atol=1e-7):
    # Find unique image feature rows (since test_x has repeated images in blocks of 30)
    # Use np.unique with tolerance to floating point errors
    # Return: unique_x (nunique, features), inverse indices (to map predictions back)
    # Quantizing to avoid small floating point variance
    quant = np.round(test_x / atol).astype(np.int64)
    unique_q, inv_idx = np.unique(quant, axis=0, return_inverse=True)
    unique_x = test_x[np.arange(test_x.shape[0])[np.unique(inv_idx, return_index=True)[1]]]
    return unique_x, inv_idx

def _fit_poisson_glm(train_x, train_y, val_splits=3, l2_grid=(0.1,1,3,10,30,100), seed=0):
    num_neurons = train_y.shape[1]
    num_features = train_x.shape[1]
    coef_ = np.zeros((num_neurons, num_features))
    intercept_ = np.zeros(num_neurons)
    best_l2 = np.zeros(num_neurons)
    scaler = StandardScaler()
    X = scaler.fit_transform(train_x)
    rng = np.random.RandomState(seed)
    kf = KFold(n_splits=val_splits, shuffle=True, random_state=seed)
    for neuron in range(num_neurons):
        y = train_y[:, neuron]
        min_score = np.inf
        best_alpha = l2_grid[0]
        # Mask for valid (non-negative) target values
        for alpha in l2_grid:
            cv_scores = []
            for train_idx, val_idx in kf.split(X):
                Xtr, Xtst = X[train_idx], X[val_idx]
                ytr, ytst = y[train_idx], y[val_idx]
                # Poisson regression via log-link:
                # Fit via Ridge on log(1 + y) to get strictly positive rates
                log_ytr = np.log1p(ytr)  # Effective link function for regression surrogate
                reg = Ridge(alpha=alpha, fit_intercept=True, random_state=seed)
                reg.fit(Xtr, log_ytr)
                pred_log = reg.predict(Xtst)
                # Convert log-count to expected count
                pred = np.expm1(pred_log).clip(min=1e-3)
                cv_scores.append(_poisson_nll(ytst, pred))
            mean_cv = np.mean(cv_scores)
            if mean_cv < min_score:
                min_score = mean_cv
                best_alpha = alpha
        # Fit final model on all data
        log_y = np.log1p(y)
        reg = Ridge(alpha=best_alpha, fit_intercept=True, random_state=seed)
        reg.fit(X, log_y)
        coef_[neuron] = reg.coef_
        intercept_[neuron] = reg.intercept_
        best_l2[neuron] = best_alpha
    return scaler, coef_, intercept_, best_l2

def _predict_poisson_glm(scaler, coef_, intercept_, X):
    # Predict for all neurons at once
    Xs = scaler.transform(X)
    pred_log = np.inner(Xs, coef_) + intercept_  # shape: (nsamples, neurons)
    rates = np.expm1(pred_log)
    rates = np.clip(rates, 1e-3, 1e5)  # enforce positive, reasonable rates
    return rates

def fit_predict(train_x, train_y, test_x):
    # Step 1: Unique test image reduction to ensure identical images get identical predictions
    unique_x, inv_idx = _get_unique_test_images(test_x)
    # Step 2: Fit GLMs (linear-Poisson regressions) for all neurons
    scaler, coef_, intercept_, best_l2 = _fit_poisson_glm(train_x, train_y)
    # Step 3: Predict spike rates (expected per 300ms) for unique test images
    unique_preds = _predict_poisson_glm(scaler, coef_, intercept_, unique_x)  # shape (unique_images, neurons)
    # Step 4: Broadcast predictions to all test rows (reconstruct full test set predictions)
    pred = unique_preds[inv_idx]
    # Ensure shape is (900,41), strictly positive finite values
    if not (np.all(np.isfinite(pred)) and (pred > 0).all() and pred.shape == (test_x.shape[0], train_y.shape[1])):
        raise ValueError("Prediction array is not correct shape, positive, and finite")
    return pred
