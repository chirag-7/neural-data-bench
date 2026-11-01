import numpy as np
from sklearn.linear_model import Ridge

def fit_predict(train_x, train_y, test_x):
    """
    EEG artifact repair via frequency-domain ridge regression filtering.
    Args:
      train_x: (n_train, n_samples) noisy (mixture) segments, float32
      train_y: (n_train, n_samples) clean matching segments, float32
      test_x: (n_test, n_samples) noisy (mixture) segments, float32 (to denoise)
    Returns:
      denoised: (n_test, n_samples), np.ndarray(float32)
    """
    # Consistent FFT setup
    n_freq = train_x.shape[1] // 2 + 1  # for rFFT

    # rFFT along last axis for each segment
    X_fft = np.fft.rfft(train_x, axis=1)  # (n_train, n_freq), complex
    Y_fft = np.fft.rfft(train_y, axis=1)  # (n_train, n_freq), complex
    T_fft = np.fft.rfft(test_x, axis=1)   # (n_test, n_freq), complex

    # For each frequency bin, learn a linear complex mapping (via real regression over real/imag)
    denoised_fft = np.zeros_like(T_fft, dtype=np.complex128)
    alpha = 0.05  # Ridge strength

    for f in range(n_freq):
        # Regress both real/imag parts as 2-D target
        # Each: shape (n_train,)
        X_feat = np.vstack([
            X_fft[:,f].real,  # (n_train,)
            X_fft[:,f].imag
        ]).T  # shape: (n_train, 2)
        Y_feat = np.vstack([
            Y_fft[:,f].real,
            Y_fft[:,f].imag
        ]).T # shape: (n_train, 2)

        # Regression: simple mapping, Ridge is stable
        model = Ridge(alpha=alpha, fit_intercept=True, random_state=42)
        model.fit(X_feat, Y_feat)

        # Prepare test feature
        T_feat = np.vstack([
            T_fft[:,f].real,
            T_fft[:,f].imag
        ]).T  # (n_test, 2)
        pred = model.predict(T_feat) # (n_test, 2)
        denoised_fft[:,f] = pred[:,0] + 1j*pred[:,1]

    # Inverse rFFT per segment
    denoised = np.fft.irfft(denoised_fft, n=train_x.shape[1], axis=1)
    # Final shape and dtype
    denoised = denoised.astype(np.float32)
    return denoised
