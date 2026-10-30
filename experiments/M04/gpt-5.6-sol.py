import numpy as np


def _posterior_median(grid, density):
    """Median of a piecewise-linearly interpolated one-dimensional density."""
    density = np.asarray(density, dtype=float)
    dx = np.diff(grid)
    areas = 0.5 * (density[:-1] + density[1:]) * dx
    total = float(np.sum(areas))
    if not np.isfinite(total) or total <= 0.0:
        return float(grid[len(grid) // 2])

    target = 0.5 * total
    cumulative = np.cumsum(areas)
    j = int(np.searchsorted(cumulative, target, side="left"))
    j = min(j, len(grid) - 2)
    previous = 0.0 if j == 0 else float(cumulative[j - 1])
    remaining = target - previous
    h = float(dx[j])
    p0 = float(density[j])
    delta = float(density[j + 1] - p0)
    scaled = remaining / h

    if abs(delta) <= 1e-14 * max(1.0, abs(p0)):
        u = scaled / p0 if p0 > 0.0 else 0.5
    else:
        disc = max(0.0, p0 * p0 + 2.0 * delta * scaled)
        denom = p0 + np.sqrt(disc)
        u = 2.0 * scaled / denom if denom > 0.0 else 0.5
    u = min(1.0, max(0.0, u))
    return float(grid[j] + h * u)


def _agent_estimate(choice, reward, alpha_grid, beta_grid):
    na = alpha_grid.size
    nt = choice.size

    # Simultaneously construct Q trajectories for every candidate alpha.
    q0 = np.full(na, 0.5, dtype=float)
    q1 = np.full(na, 0.5, dtype=float)
    differences = np.empty((na, nt), dtype=float)
    for t in range(nt):
        differences[:, t] = q1 - q0
        r = float(reward[t])
        if choice[t] == 0:
            q0 += alpha_grid * (r - q0)
        else:
            q1 += alpha_grid * (r - q1)

    # log p(choice | preceding Q), evaluated in beta blocks to limit memory.
    chosen_linear_term = differences @ choice.astype(float)
    log_likelihood = np.empty((na, beta_grid.size), dtype=float)
    block = 64
    for start in range(0, beta_grid.size, block):
        stop = min(start + block, beta_grid.size)
        betas = beta_grid[start:stop]
        softplus = differences[:, :, None] * betas[None, None, :]
        np.logaddexp(0.0, softplus, out=softplus)
        log_likelihood[:, start:stop] = (
            chosen_linear_term[:, None] * betas[None, :]
            - np.sum(softplus, axis=1)
        )

    # Uniform continuous priors over the stated bounds. Integrating the joint
    # grid gives marginal densities; their medians minimize posterior absolute loss.
    log_likelihood -= np.max(log_likelihood)
    posterior = np.exp(log_likelihood)
    alpha_weights = np.ones(na, dtype=float)
    beta_weights = np.ones(beta_grid.size, dtype=float)
    alpha_weights[[0, -1]] = 0.5
    beta_weights[[0, -1]] = 0.5
    marginal_alpha = posterior @ beta_weights
    marginal_beta = alpha_weights @ posterior

    return (_posterior_median(alpha_grid, marginal_alpha),
            _posterior_median(beta_grid, marginal_beta))


def estimate(choices, rewards):
    choices = np.asarray(choices)
    rewards = np.asarray(rewards)
    if choices.ndim != 2 or rewards.shape != choices.shape:
        raise ValueError("choices and rewards must have the same two-dimensional shape")

    # These spacings are fine relative to the sampling uncertainty at T about 240.
    alpha_grid = np.linspace(0.01, 0.99, 181)
    beta_grid = np.linspace(0.1, 10.0, 241)
    result = np.empty((choices.shape[0], 2), dtype=float)
    for agent in range(choices.shape[0]):
        result[agent] = _agent_estimate(
            choices[agent], rewards[agent], alpha_grid, beta_grid
        )
    return result
