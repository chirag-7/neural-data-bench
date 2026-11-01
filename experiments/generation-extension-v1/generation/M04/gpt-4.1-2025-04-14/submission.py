import numpy as np
from scipy.optimize import minimize
from scipy.special import expit as sigmoid

def _negloglike(params, choices, rewards):
    """
    Negative log-likelihood for single agent.
    params: [alpha, beta]
    choices: (T,) array in {0,1}
    rewards: (T,) array in {0,1}
    """
    alpha, beta = params
    Q = np.array([0.5, 0.5], dtype=np.float64)
    nll = 0.0
    for t, (a, r) in enumerate(zip(choices, rewards)):
        delta_Q = Q[1] - Q[0]
        p1 = sigmoid(beta * delta_Q)
        p = p1 if a == 1 else 1 - p1
        # Avoid log(0) with proper clipping
        p = np.clip(p, 1e-8, 1. - 1e-8)
        nll -= np.log(p)
        # Q update
        Q[a] += alpha * (r - Q[a])
    return nll

def _fit_agent(choices, rewards, n_restarts=5):
    bounds = [(0.01, 0.99), (0.1, 10)]
    best_loss = np.inf
    best_params = None
    T = len(choices)
    # Different starting guesses covering range, plus central value
    startparams = [
        [0.2, 0.5],
        [0.5, 2.0],
        [0.8, 5.0],
        [0.05, 9.0],
        [0.95, 0.12]
    ]
    # if n_restarts > hardcoded starts:
    rng = np.random.RandomState(0)
    while len(startparams) < n_restarts:
        startparams.append([
            rng.uniform(0.01, 0.99),
            rng.uniform(0.1, 10),
        ])
    for x0 in startparams[:n_restarts]:
        res = minimize(
            _negloglike,
            x0,
            args=(choices, rewards),
            method='L-BFGS-B',
            bounds=bounds,
            options={'ftol': 1e-9, 'gtol':1e-7, 'disp': False, 'maxiter': 400}
        )
        if res.success and res.fun < best_loss:
            best_loss = res.fun
            best_params = res.x
    # fallback: if optimizer failed, fall back to midrange values
    if best_params is None:
        best_params = np.array([0.5, 2.0])
    return best_params

def estimate(choices, rewards):
    """
    Estimate Q-learning alpha and beta for each agent.
    choices: (N,T) int array, values 0 or 1
    rewards: (N,T) int array, 0 or 1
    Returns: (N,2) array: estimated [alpha, beta] per agent
    """
    choices = np.asarray(choices)
    rewards = np.asarray(rewards)
    N, T = choices.shape
    est = np.zeros((N, 2), dtype=np.float64)
    for i in range(N):
        est[i] = _fit_agent(choices[i], rewards[i], n_restarts=7)
    return est
