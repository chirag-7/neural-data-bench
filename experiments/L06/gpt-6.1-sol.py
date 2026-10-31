import numpy as np
from scipy.special import expit
from scipy.linalg import solve_triangular
from scipy.optimize import minimize


def sample_posterior(design_matrix, spike_trains, prior_precision, n_samples, seed):
    X = np.asarray(design_matrix, dtype=np.float64)
    Y = np.asarray(spike_trains, dtype=np.float64)
    Q = np.asarray(prior_precision, dtype=np.float64)
    n_samples = int(n_samples)
    if X.shape != (100, 10) or Y.shape != (10, 100) or Q.shape != (10, 10):
        raise ValueError('Expected X=(100,10), spike_trains=(10,100), Q=(10,10).')
    if n_samples < 0:
        raise ValueError('n_samples must be nonnegative.')
    if not (np.isfinite(X).all() and np.isfinite(Y).all() and np.isfinite(Q).all()):
        raise ValueError('Inputs must be finite.')
    if not np.all((Y == 0) | (Y == 1)):
        raise ValueError('Spike trains must be binary.')
    Q = 0.5 * (Q + Q.T)
    np.linalg.cholesky(Q)
    out = np.empty((10, n_samples, 10), dtype=np.float64)
    if n_samples == 0:
        return out

    rng = np.random.default_rng(seed)
    n_obs, n_chains, dim = 10, 4, 10
    centers = np.empty((n_obs, dim))
    factors = np.empty((n_obs, dim, dim))
    eye = np.eye(dim)

    # A separate posterior mode and curvature for every observation.
    for obs in range(n_obs):
        y = Y[obs]
        signs = 2.0 * y - 1.0

        def objective(beta):
            eta = X @ beta
            value = np.logaddexp(0.0, -signs * eta).sum()
            value += 0.5 * beta @ Q @ beta
            gradient = X.T @ (expit(eta) - y) + Q @ beta
            return value, gradient

        def hessian(beta):
            probabilities = expit(X @ beta)
            weights = probabilities * (1.0 - probabilities)
            return Q + X.T @ (weights[:, None] * X)

        result = minimize(objective, np.zeros(dim), jac=True, hess=hessian,
                          method='trust-exact',
                          options={'gtol': 1e-9, 'maxiter': 100})
        mode = result.x if np.isfinite(result.x).all() else np.zeros(dim)
        centers[obs] = mode
        chol = np.linalg.cholesky(hessian(mode))
        factors[obs] = solve_triangular(chol.T, eye, lower=False)

    signs = (2.0 * Y - 1.0)[:, None, :]

    def geometry():
        transformed_X = np.matmul(X[None, :, :], factors)
        offsets = centers @ X.T
        precision = np.matmul(factors.swapaxes(1, 2),
                              np.matmul(Q[None, :, :], factors))
        precision = 0.5 * (precision + precision.swapaxes(1, 2))
        linear = np.einsum('oi,oij->oj', centers @ Q, factors)
        return transformed_X, offsets, precision, linear

    W, offsets, precision, linear = geometry()

    def evaluate(z, need_value=True):
        eta = np.matmul(z, W.swapaxes(1, 2)) + offsets[:, None, :]
        prior_gradient = np.matmul(z, precision)
        gradient = np.matmul(Y[:, None, :] - expit(eta), W)
        gradient -= prior_gradient + linear[:, None, :]
        if not need_value:
            return None, gradient
        value = -np.logaddexp(0.0, -signs * eta).sum(axis=-1)
        value -= 0.5 * np.sum(z * prior_gradient, axis=-1)
        value -= np.sum(z * linear[:, None, :], axis=-1)
        return value, gradient

    def transition(z, value, gradient, step_sizes):
        # Randomized integration avoids persistent trajectory resonances.
        step = step_sizes[:, None, None]
        step = step * rng.uniform(0.85, 1.15, (n_obs, n_chains, 1))
        initial_momentum = rng.standard_normal(z.shape)
        momentum = initial_momentum + 0.5 * step * gradient
        proposal = z.copy()
        leapfrog_steps = int(rng.integers(3, 10))
        for leap in range(leapfrog_steps):
            proposal += step * momentum
            last = leap == leapfrog_steps - 1
            proposal_value, proposal_gradient = evaluate(proposal, last)
            momentum += (0.5 if last else 1.0) * step * proposal_gradient
        log_ratio = proposal_value - value
        log_ratio += 0.5 * np.sum(initial_momentum ** 2 - momentum ** 2, axis=-1)
        log_ratio = np.where(np.isfinite(log_ratio), log_ratio, -np.inf)
        probability = np.exp(np.minimum(log_ratio, 0.0))
        accepted = rng.random((n_obs, n_chains)) < probability
        z = np.where(accepted[..., None], proposal, z)
        value = np.where(accepted, proposal_value, value)
        gradient = np.where(accepted[..., None], proposal_gradient, gradient)
        return z, value, gradient, probability.mean(axis=1)

    def warmup(z, iterations, initial_step, collect=False):
        value, gradient = evaluate(z)
        steps = np.broadcast_to(initial_step, (n_obs,)).copy()
        anchor = np.log(10.0 * steps)
        averaged_log_step = np.log(steps)
        error_average = np.zeros(n_obs)
        sum_z = np.zeros((n_obs, dim))
        sum_zz = np.zeros((n_obs, dim, dim))
        count = 0
        for iteration in range(1, iterations + 1):
            z, value, gradient, acceptance = transition(z, value, gradient, steps)
            weight = 1.0 / (iteration + 10.0)
            error_average = ((1.0 - weight) * error_average
                             + weight * (0.9 - acceptance))
            log_step = anchor - np.sqrt(iteration) * error_average / 0.05
            log_step = np.clip(log_step, np.log(0.005), np.log(1.2))
            averaging_weight = iteration ** -0.75
            averaged_log_step = (averaging_weight * log_step
                                 + (1.0 - averaging_weight) * averaged_log_step)
            steps = np.exp(log_step)
            if collect and iteration > iterations // 3:
                sum_z += z.sum(axis=1)
                sum_zz += np.matmul(z.swapaxes(1, 2), z)
                count += n_chains
        if collect:
            mean = sum_z / count
            covariance = sum_zz / count - mean[:, :, None] * mean[:, None, :]
            covariance = 0.5 * (covariance + covariance.swapaxes(1, 2))
            covariance = 0.95 * covariance + 0.05 * eye[None, :, :]
        else:
            mean, covariance = None, None
        return z, np.exp(averaged_log_step), mean, covariance

    z = rng.standard_normal((n_obs, n_chains, dim))
    z, steps, mean, covariance = warmup(z, 600, 0.25, collect=True)

    # Learn joint geometry, then stop metric adaptation before production.
    covariance_factor = np.linalg.cholesky(covariance)
    for obs in range(n_obs):
        z[obs] = solve_triangular(covariance_factor[obs],
                                  (z[obs] - mean[obs]).T, lower=True).T
    centers = centers + np.einsum('oij,oj->oi', factors, mean)
    factors = np.matmul(factors, covariance_factor)
    W, offsets, precision, linear = geometry()
    z, steps, _, _ = warmup(z, 350, steps)
    value, gradient = evaluate(z)
    for _ in range(100):
        z, value, gradient, _ = transition(z, value, gradient, steps)

    for start in range(0, n_samples, n_chains):
        for _ in range(3):
            z, value, gradient, _ = transition(z, value, gradient, steps)
        draws = centers[:, None, :] + np.matmul(z, factors.swapaxes(1, 2))
        stop = min(start + n_chains, n_samples)
        out[:, start:stop, :] = draws[:, :stop - start, :]
    return out
