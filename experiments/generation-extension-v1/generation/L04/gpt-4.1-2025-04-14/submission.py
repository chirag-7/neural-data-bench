
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.preprocessing import SplineTransformer

def fit_predict(train_x, train_y, test_x):
    """
    Predict expected spike counts for extracellular spike train given behavior.
    Arguments:
        train_x: (n_train,2) behavioral covariates (position, velocity)
        train_y: (n_train,) nonnegative spike count per 20ms bin
        test_x: (n_test,2) behavioral covariates to predict
    Returns:
        preds: (n_test,) nonnegative expected spike count per 20ms bin
    """
    # All-NaN/constant edge case (shouldn't occur)
    if not np.all(np.isfinite(train_x)) or not np.all(np.isfinite(test_x)):
        raise ValueError('Non-finite inputs found.')
    if np.any(train_y < 0):
        raise ValueError('Negative spike count in train_y.')

    # Parameters
    degree = 3                 # Cubic splines
    n_knots = 6                # Number of spline knots per feature (can tune)
    reg_alpha = 1.0            # Regularization for stability
    random_seed = 13           # Determinism

    # Fit a spline expansion per feature on training input range only
    np.random.seed(random_seed)
    spline_tfm = SplineTransformer(degree=degree, n_knots=n_knots, include_bias=False)
    # Fit only on training set, apply same transform to train and test
    spline_tfm.fit(train_x)
    Phi_train = spline_tfm.transform(train_x)
    Phi_test  = spline_tfm.transform(test_x)

    # To enforce nonnegativity, model log(expected rate/20ms): y ~ Poisson(exp(linear)).
    # y ~ Poisson(mu), mu = c * exp(W*Phi + b)
    # Fit via IRLS log-link, but for stability use Ridge regression on log(y+1e-3)

    TINY = 1e-3
    clipped_train_y = np.clip(train_y, TINY, None)
    y_log = np.log(clipped_train_y)            # loglink, no test info
    # Optionally, subtract mean of features for better conditioning

    model = Ridge(alpha=reg_alpha, random_state=random_seed, fit_intercept=True)
    # Solve: log(mu) = Phi * W + b
    model.fit(Phi_train, y_log)
    # Predict log(mu) on test
    log_mu_pred = model.predict(Phi_test)
    # Safeguard: clip output for overflow/underflow
    log_mu_pred = np.clip(log_mu_pred, -10, 6) # min exp(-10) ~4e-5, max exp(6)~400
    mu_pred = np.exp(log_mu_pred)
    # Output expected count per 20ms bin ([Hz] * 0.02)
    count_per_bin = mu_pred * 0.02
    # Enforce non-negativity (should be already, but numerics)
    count_per_bin = np.clip(count_per_bin, 0, np.inf)
    if count_per_bin.shape[0] != test_x.shape[0]:
        raise RuntimeError('Output shape mismatch')
    return count_per_bin
