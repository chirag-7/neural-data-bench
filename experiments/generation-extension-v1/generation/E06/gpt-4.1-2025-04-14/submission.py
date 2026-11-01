import numpy as np

def fit_predict(train_x, train_y, test_x, train_groups):
    """
    Implements the analytic NLinear-like forecast: fits a ridge-regularized temporal mapping (64→32)
    across all neuron/window pairs in training, with explicit last-frame subtraction and restore.
    Args:
        train_x (np.ndarray): (N_windows, 64, 256), input history
        train_y (np.ndarray): (N_windows, 32, 256), future targets
        test_x (np.ndarray): (N_test_windows, 64, 256), input history for test
        train_groups (ignored): always None
    Returns:
        np.ndarray: predictions (N_test_windows, 32, 256)
    """
    np.random.seed(0)  # deterministic behavior for any stochastic step (not used, but explicit)
    Nw, T_in, Nn = train_x.shape  # (272,64,256)
    _, T_out, _ = train_y.shape  # (272,32,256)
    Nt = len(test_x)  # variable test set size

    # Reshape: stack all neuron/window pairs as samples for batch fit
    # For every (window,neuron): input (64,), output (32,)
    X = train_x.transpose(0,2,1).reshape(-1, T_in)  # (Nw*Nn, 64)
    Y = train_y.transpose(0,2,1).reshape(-1, T_out)  # (Nw*Nn, 32)
    # Compute last context frame per sample (used for both fitting and transformation)
    last_ctx = X[:,-1].reshape(-1,1)  # (Nw*Nn,1)

    # Subtract last context frame from both input and output (broadcast)
    Xc = X - last_ctx  # center each row
    Yc = Y - last_ctx  # target as delta from last context

    # Closed-form ridge regression: fit W,b to minimize
    # sum_i ||Yc[i] - (Xc[i] @ W.T + b)||^2 + alpha*||W||^2
    alpha = 1.0  # regularization strength (matches reference)
    n_samples = Xc.shape[0]
    # Fit on large batch: Xc shape (Nw*Nn,64), Yc (Nw*Nn,32)

    # Add bias: center Xc to have mean zero for easy bias fit (fit b after W)
    Xc_mean = Xc.mean(axis=0, keepdims=True)
    Yc_mean = Yc.mean(axis=0, keepdims=True)
    # Fit W via regularized normal equations for multi-target regression
    XX = Xc.T @ Xc + alpha*np.eye(T_in)
    XY = Xc.T @ Yc
    W = np.linalg.solve(XX, XY)  # shape (64,32)
    b = (Yc_mean - Xc_mean @ W).ravel()  # shape (32,)

    # Predict on test
    pred = np.empty((Nt, T_out, Nn), dtype=np.float64)
    for i in range(Nn):
        Xi = test_x[:, :, i]  # shape (Nt, 64)
        # Subtract last frame of each context
        last_ctx_test = Xi[:, -1][:, np.newaxis]  # (Nt,1)
        Xc_test = Xi - last_ctx_test
        # Predict delta
        Yc_pred = Xc_test @ W + b  # (Nt,32)
        # Restore last context frame
        pred[:,:,i] = Yc_pred + last_ctx_test
    return pred
