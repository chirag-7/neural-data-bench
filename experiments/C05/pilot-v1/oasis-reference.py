import numpy as np
from oasis.functions import deconvolve
def fit_predict(train_calcium, train_spikes, test_calcium):
    out = np.full(test_calcium.shape, np.nan)
    for j in range(test_calcium.shape[1]):
        mask = np.isfinite(test_calcium[:,j])
        y = np.asarray(test_calcium[mask,j], dtype=float)
        c,s,b,g,lam = deconvolve(y, penalty=1)
        out[mask,j] = np.maximum(s,0)
    return out
