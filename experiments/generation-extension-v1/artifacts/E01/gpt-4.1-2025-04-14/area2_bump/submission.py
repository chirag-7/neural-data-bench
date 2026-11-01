import numpy as np
from sklearn.linear_model import Ridge

def fit_predict(train_x, train_y, test_x):
    # train_x: (99, 35, 107), held-in neuron counts
    # train_y: (99, 35, 35), held-out neuron counts
    # test_x:  (100, 35, 107)
    # Returns: (100, 35, 35), nonnegative expected spike counts per bin
    
    n_train, n_bins, n_obs = train_x.shape
    _, _, n_ho = train_y.shape
    n_test = test_x.shape[0]

    assert train_y.shape == (n_train, n_bins, n_ho)
    assert test_x.shape == (n_test, n_bins, n_obs)

    # Flatten temporal and neuronal dimensions for input features of each trial
    # For each trial we have features: 35 timebins x 107 neurons = 3745
    X_train = train_x.reshape(n_train, n_bins * n_obs)
    X_test = test_x.reshape(n_test, n_bins * n_obs)

    # For each held-out neuron and target time-bin, fit a separate Ridge
    # Target for y: per trial, for each time bin, for each neuron
    preds = np.zeros((n_test, n_bins, n_ho), dtype=np.float32)
    
    # Reshape train_y to (n_train, n_bins, n_ho)
    rng = np.random.RandomState(42)
    alpha = 10.0  # Moderate regularization; can be adjusted

    for neuron in range(n_ho):
        for t in range(n_bins):
            # Target: shape (n_train,)
            ytr = train_y[:, t, neuron]
            # Train Ridge regression
            reg = Ridge(
                alpha=alpha,
                fit_intercept=True,
                random_state=42
            )
            # The feature is the whole held-in neuron activity in the trial
            reg.fit(X_train, ytr)
            # Predict for test trials
            ypr = reg.predict(X_test)
            # Ensure predictions are finite and non-negative
            ypr = np.maximum(ypr, 0.0)
            # Save to prediction array
            preds[:, t, neuron] = ypr.astype(np.float32)
    
    # check for any non-finite values (shouldn't occur)
    if not np.isfinite(preds).all():
        preds = np.nan_to_num(preds, nan=0.0, posinf=0.0, neginf=0.0)
        preds = np.maximum(preds, 0.0)
    return preds
