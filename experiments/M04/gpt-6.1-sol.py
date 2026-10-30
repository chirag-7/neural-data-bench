import numpy as np


def _integration_weights(grid):
    gaps = np.diff(grid)
    weights = np.empty_like(grid)
    weights[0] = 0.5 * gaps[0]
    weights[-1] = 0.5 * gaps[-1]
    weights[1:-1] = 0.5 * (gaps[:-1] + gaps[1:])
    return weights


def _density_median(grid, density):
    widths = np.diff(grid)
    masses = 0.5 * (density[:-1] + density[1:]) * widths
    cumulative = np.cumsum(masses)
    target = 0.5 * cumulative[-1]
    j = min(int(np.searchsorted(cumulative, target)), len(widths) - 1)
    previous = cumulative[j - 1] if j else 0.0
    area = max(0.0, (target - previous) / widths[j])
    left = density[j]
    change = density[j + 1] - left
    discriminant = max(0.0, left * left + 2.0 * change * area)
    denominator = left + np.sqrt(discriminant)
    fraction = 2.0 * area / denominator if denominator > 0.0 else 0.5
    return grid[j] + widths[j] * np.clip(fraction, 0.0, 1.0)


def estimate(choices, rewards):
    choices = np.asarray(choices)
    rewards = np.asarray(rewards, dtype=np.float64)
    if choices.ndim != 2 or rewards.shape != choices.shape:
        raise ValueError('choices and rewards must have matching (N, T) shapes')
    if np.any((choices != 0) & (choices != 1)):
        raise ValueError('choices must contain only 0 and 1')
    if np.any((rewards != 0) & (rewards != 1)):
        raise ValueError('rewards must contain only 0 and 1')
    choices = choices.astype(np.int64, copy=False)
    n, trials = choices.shape
    estimates = np.empty((n, 2), dtype=np.float64)
    if n == 0:
        return estimates

    # Denser alpha coverage near both bounds resolves narrow edge posteriors.
    u = np.linspace(0.0, 1.0, 257)
    alphas = 0.01 + 0.98 * (0.5 - 0.5 * np.cos(np.pi * u))
    betas = np.linspace(0.1, 10.0, 193)
    alpha_weights = _integration_weights(alphas)
    beta_weights = _integration_weights(betas)

    q0 = np.full((n, len(alphas)), 0.5)
    q1 = np.full_like(q0, 0.5)
    signed_differences = np.empty((n, len(alphas), trials))
    learning_rates = alphas[None, :]
    for t in range(trials):
        action = choices[:, t, None]
        reward = rewards[:, t, None]
        signed_differences[:, :, t] = (q1 - q0) * (2 * action - 1)
        q0 += learning_rates * (reward - q0) * (1 - action)
        q1 += learning_rates * (reward - q1) * action

    for agent in range(n):
        losses = np.empty((len(alphas), len(betas)))
        differences = signed_differences[agent]
        # Blocking limits temporary memory while vectorizing likelihood work.
        for start in range(0, len(betas), 32):
            stop = min(start + 32, len(betas))
            terms = -differences[:, None, :] * betas[None, start:stop, None]
            np.logaddexp(0.0, terms, out=terms)
            losses[:, start:stop] = terms.sum(axis=2)
        posterior = np.exp(np.min(losses) - losses)
        alpha_density = np.sum(posterior * beta_weights[None, :], axis=1)
        beta_density = np.sum(posterior * alpha_weights[:, None], axis=0)
        estimates[agent, 0] = _density_median(alphas, alpha_density)
        estimates[agent, 1] = _density_median(betas, beta_density)
    return estimates
