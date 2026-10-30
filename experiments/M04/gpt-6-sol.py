import numpy as np


def _marginal_median(mass, lower, upper):
    mass = mass / mass.sum(axis=1, keepdims=True)
    cumulative = np.cumsum(mass, axis=1)
    index = np.sum(cumulative < 0.5, axis=1)
    rows = np.arange(mass.shape[0])
    previous = np.zeros(mass.shape[0], dtype=float)
    nonzero = index > 0
    previous[nonzero] = cumulative[rows[nonzero], index[nonzero] - 1]
    fraction = (0.5 - previous) / mass[rows, index]
    width = (upper - lower) / mass.shape[1]
    return lower + (index + fraction) * width


def estimate(choices, rewards):
    choices = np.asarray(choices)
    rewards = np.asarray(rewards, dtype=float)
    if choices.ndim != 2 or choices.shape != rewards.shape:
        raise ValueError('choices and rewards must have the same (N, T) shape')

    n_agents, n_trials = choices.shape
    n_alpha, n_beta = 100, 120
    alpha = (0.01 + (np.arange(n_alpha) + 0.5) * (0.98 / n_alpha))[None, :, None]
    beta = (0.1 + (np.arange(n_beta) + 0.5) * (9.9 / n_beta))[None, None, :]

    shape = (n_agents, n_alpha, n_beta)
    q0 = np.full(shape, 0.5)
    q1 = np.full(shape, 0.5)
    log_likelihood = np.zeros(shape)

    for t in range(n_trials):
        chose_one = (choices[:, t] == 1)[:, None, None]
        reward = rewards[:, t, None, None]
        log_odds = beta * (q1 - q0)
        log_likelihood -= np.logaddexp(0.0, np.where(chose_one, -log_odds, log_odds))
        q0 += np.where(chose_one, 0.0, alpha * (reward - q0))
        q1 += np.where(chose_one, alpha * (reward - q1), 0.0)

    log_likelihood -= log_likelihood.max(axis=(1, 2), keepdims=True)
    posterior = np.exp(log_likelihood)
    alpha_mass = posterior.sum(axis=2)
    beta_mass = posterior.sum(axis=1)

    alpha_est = _marginal_median(alpha_mass, 0.01, 0.99)
    beta_est = _marginal_median(beta_mass, 0.1, 10.0)
    return np.column_stack((alpha_est, beta_est))