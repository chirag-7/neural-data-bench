import numpy as np
import scipy.linalg

def fit_predict(train_x, train_y, test_x):
    """
    Predicts voltage sweeps using a linear time-invariant filter (impulse response)
    fitted on train_x/train_y, and applies the filter to test_x.
    Args:
        train_x: (4, 500), input currents (pA), 4 sweeps
        train_y: (4, 500), output voltages (mV), 4 sweeps
        test_x: (2, 500), input currents (pA), 2 sweeps
    Returns:
        predictions: (2, 500) float64, predicted voltage deflection (mV)
    """
    n_train, T = train_x.shape
    n_test = test_x.shape[0]
    # Grid of kernel lengths to try (ms): 10, 20, ..., 100 ms = 5, 10, ..., 50 samples
    kernel_sizes = [5, 10, 15, 20, 25, 30, 40, 50]
    best_rmse = np.inf
    best_kernel = None
    best_k_size = None
    np.random.seed(42)

    for k_size in kernel_sizes:
        # Collate input/output for linear regression (all sweeps stack up)
        # Each sweep: design matrix X_i is (T-k_size+1, k_size)
        # Each row is input_current[t:t+k_size] (reversed for convolution matching)
        X_blocks = []
        y_blocks = []
        for i in range(n_train):
            Xi = np.lib.stride_tricks.sliding_window_view(train_x[i], k_size)
            X_blocks.append(Xi[::-1])  # reverse for convolution correspondence
            y_blocks.append(train_y[i][k_size-1:])
        X = np.concatenate(X_blocks, axis=0)  # shape (total_timepoints, k_size)
        y = np.concatenate(y_blocks, axis=0)  # shape (total_timepoints,)
        # Fit kernel
        kernel, _, _, _ = np.linalg.lstsq(X, y, rcond=None)

        # Leave-one-sweep-out validation
        rmses = []
        for i in range(n_train):
            idx = np.arange(n_train) != i
            # Concatenate all but i sweeps
            X_val = [np.lib.stride_tricks.sliding_window_view(train_x[j], k_size)[::-1] for j in np.where(idx)[0]]
            y_val = [train_y[j][k_size-1:] for j in np.where(idx)[0]]
            Xtr = np.concatenate(X_val, axis=0)
            ytr = np.concatenate(y_val, axis=0)
            krn, _, _, _ = np.linalg.lstsq(Xtr, ytr, rcond=None)
            # Predict on left-out sweep
            xi = np.lib.stride_tricks.sliding_window_view(train_x[i], k_size)[::-1]
            pred = xi @ krn
            tgt = train_y[i][k_size-1:]
            rmse = np.sqrt(np.mean((pred - tgt)**2))
            rmses.append(rmse)
        mean_rmse = np.mean(rmses)
        if mean_rmse < best_rmse:
            best_rmse = mean_rmse
            best_kernel = kernel.copy()
            best_k_size = k_size
    # Use best_kernel for final fit on all training data
    k_size = best_k_size
    # Refit IMPULSE RESPONSE FILTER on all training data
    X_blocks = []
    y_blocks = []
    for i in range(n_train):
        Xi = np.lib.stride_tricks.sliding_window_view(train_x[i], k_size)
        X_blocks.append(Xi[::-1])
        y_blocks.append(train_y[i][k_size-1:])
    X = np.concatenate(X_blocks, axis=0)
    y = np.concatenate(y_blocks, axis=0)
    kernel, _, _, _ = np.linalg.lstsq(X, y, rcond=None)
    # Predict on test_x sweeps
    preds = np.zeros((n_test, T))
    for j in range(n_test):
        # To preserve time alignment (output must be (500,)), produce lin. filter response
        # Pad left with zeros for convolution
        conv_full = np.convolve(test_x[j], kernel[::-1], mode='full')
        conv_resp = conv_full[:T]  # cut to 500
        preds[j] = conv_resp
    # Defensive, though not expected to need it:
    preds = np.where(np.isfinite(preds), preds, 0.)
    return preds
