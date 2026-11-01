import numpy as np
from scipy.optimize import minimize

# Stable log-sigmoid
def _log_sigmoid(z):
    # log(sigmoid(z)) computed stably
    # = -softplus(-z) = -log(1+exp(-z)) with stability
    az = np.abs(z)
    return -np.log1p(np.exp(-az)) - np.maximum(-z, 0.0)

# Negative log-likelihood for a single agent under Q-learning
def _nll_q(params, choices, rewards, valid_idx):
    a = float(params[0])
    b = float(params[1])
    # Enforce bounds softly in case optimizer steps out slightly
    if not (0.01 <= a <= 0.99 and 0.1 <= b <= 10.0):
        # Large penalty outside bounds
        return 1e9 + (max(0.01 - a, 0, a - 0.99) + max(0.1 - b, 0, b - 10.0)) * 1e6

    Q0 = 0.5
    Q1 = 0.5
    ll = 0.0
    for t in valid_idx:
        c = choices[t]
        r = rewards[t]
        # compute choice probability
        z = b * (Q1 - Q0)
        if c == 1:
            ll += _log_sigmoid(z)
            Q1 += a * (r - Q1)
        else:  # c == 0
            ll += _log_sigmoid(-z)
            Q0 += a * (r - Q0)
    return -ll

def _prepare_valid_idx(choices_row, rewards_row):
    # Valid trials: choices in {0,1} and rewards finite (0/1 expected)
    c = choices_row
    r = rewards_row
    if c.dtype.kind in ('f', 'c'):
        c_valid = np.isfinite(c) & ((c == 0) | (c == 1))
    else:
        c_valid = (c == 0) | (c == 1)
    r_valid = np.isfinite(r)
    valid = np.where(c_valid & r_valid)[0]
    return valid

def _fit_agent(choices_row, rewards_row):
    valid_idx = _prepare_valid_idx(choices_row, rewards_row)
    # If no valid trials, return mid-range defaults
    if valid_idx.size == 0:
        return np.array([0.5, 1.0], dtype=float)

    # Coarse grid search for robust starts
    alpha_grid = np.array([0.02, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.98])
    beta_grid = np.logspace(-1, 1, 12)  # 0.1 .. 10

    best_vals = []  # list of (nll, alpha, beta)
    best_nll = np.inf
    best_ab = (0.5, 1.0)

    for a in alpha_grid:
        for b in beta_grid:
            nll = _nll_q((a, b), choices_row, rewards_row, valid_idx)
            if nll < best_nll:
                best_nll = nll
                best_ab = (a, b)
            best_vals.append((nll, a, b))

    # Take up to K best grid points for local refinement
    best_vals.sort(key=lambda x: x[0])
    starts = best_vals[:3]

    bounds = [(0.01, 0.99), (0.1, 10.0)]
    final_best = best_nll
    final_params = np.array(best_ab, dtype=float)

    for nll0, a0, b0 in starts:
        x0 = np.array([a0, b0], dtype=float)
        res = minimize(
            _nll_q,
            x0,
            args=(choices_row, rewards_row, valid_idx),
            method='L-BFGS-B',
            bounds=bounds,
            options={'maxiter': 200, 'ftol': 1e-9}
        )
        if res.success and res.fun < final_best:
            final_best = res.fun
            final_params = res.x

    # Clip to bounds exactly
    final_params[0] = float(np.clip(final_params[0], 0.01, 0.99))
    final_params[1] = float(np.clip(final_params[1], 0.1, 10.0))
    return final_params


def estimate(choices, rewards):
    """Estimate alpha and beta per agent.

    Parameters:
        choices: ndarray shape (N, T) with binary choices {0,1}
        rewards: ndarray shape (N, T) with binary rewards {0,1}

    Returns:
        ndarray shape (N, 2): columns are [alpha, beta]
    """
    c = np.asarray(choices)
    r = np.asarray(rewards)
    if c.ndim == 1:
        c = c[None, :]
        r = r[None, :]
    N, T = c.shape
    assert r.shape == (N, T), "choices and rewards must have the same shape"

    est = np.zeros((N, 2), dtype=float)
    for i in range(N):
        est[i, :] = _fit_agent(c[i], r[i])
    return est
