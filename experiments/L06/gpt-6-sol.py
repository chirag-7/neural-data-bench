import numpy as np
from scipy.linalg import solve_triangular
from scipy.special import expit


def _logpost_batch(beta, X, Xt_y, Q):
    eta = beta @ X.T
    penalty = np.sum((beta @ Q) * beta, axis=1)
    return beta @ Xt_y - np.logaddexp(0.0, eta).sum(axis=1) - 0.5 * penalty


def _mode_and_covariance(X, y, Q):
    Xt_y = X.T @ y
    beta = np.zeros(X.shape[1], dtype=np.float64)

    def logpost_one(b):
        eta = X @ b
        return float(Xt_y @ b - np.logaddexp(0.0, eta).sum()
                     - 0.5 * b @ Q @ b)

    for _ in range(40):
        eta = X @ beta
        p = expit(eta)
        gradient = Xt_y - X.T @ p - Q @ beta
        weights = p * (1.0 - p)
        hessian = Q + X.T @ (weights[:, None] * X)
        step = np.linalg.solve(hessian, gradient)
        if np.max(np.abs(step)) < 1e-10:
            break
        base = logpost_one(beta)
        slope = float(gradient @ step)
        alpha = 1.0
        while alpha > 1e-10:
            trial = beta + alpha * step
            if logpost_one(trial) >= base + 1e-4 * alpha * slope:
                break
            alpha *= 0.5
        beta = trial

    p = expit(X @ beta)
    hessian = Q + X.T @ ((p * (1.0 - p))[:, None] * X)
    covariance = np.linalg.inv(hessian)
    covariance = 0.5 * (covariance + covariance.T)
    return beta, covariance, Xt_y


def _independent_t_chain(X, Xt_y, Q, rng, center, scale,
                         initial, n_keep, thin, burn, df=18.0):
    dim = center.size
    L = np.linalg.cholesky(scale)
    current = initial.copy()
    current_lp = _logpost_batch(current[None, :], X, Xt_y, Q)[0]
    transformed = solve_triangular(L, current - center, lower=True)
    current_lq = -0.5 * (df + dim) * np.log1p(
        float(transformed @ transformed) / df)
    output = np.empty((n_keep, dim), dtype=np.float64)
    total = burn + thin * n_keep
    position = 0
    saved = 0

    while position < total:
        size = min(1024, total - position)
        z = rng.standard_normal((size, dim))
        chi2 = rng.chisquare(df, size=size)
        multiplier = np.sqrt(df / chi2)
        proposals = center + (z @ L.T) * multiplier[:, None]
        proposal_lp = _logpost_batch(proposals, X, Xt_y, Q)
        radius2 = np.sum(z * z, axis=1) * (df / chi2)
        proposal_lq = -0.5 * (df + dim) * np.log1p(radius2 / df)
        log_uniform = np.log(rng.random(size))

        for j in range(size):
            if log_uniform[j] < (proposal_lp[j] - proposal_lq[j]
                                 - current_lp + current_lq):
                current = proposals[j]
                current_lp = proposal_lp[j]
                current_lq = proposal_lq[j]
            position += 1
            if position > burn and (position - burn) % thin == 0:
                output[saved] = current
                saved += 1

    return output, current


def sample_posterior(design_matrix, spike_trains, prior_precision,
                     n_samples, seed):
    X = np.asarray(design_matrix, dtype=np.float64)
    Y = np.asarray(spike_trains, dtype=np.float64)
    Q = np.asarray(prior_precision, dtype=np.float64)
    result = np.empty((10, n_samples, 10), dtype=np.float64)
    child_seeds = np.random.SeedSequence(seed).spawn(10)
    df = 18.0
    t_scale_factor = 1.05 * (df - 2.0) / df

    for row in range(10):
        rng = np.random.default_rng(child_seeds[row])
        mode, laplace_cov, Xt_y = _mode_and_covariance(X, Y[row], Q)
        pilot, last = _independent_t_chain(
            X, Xt_y, Q, rng, mode, t_scale_factor * laplace_cov,
            mode, 4000, 1, 1000, df)
        pilot_mean = pilot.mean(axis=0)
        pilot_cov = np.cov(pilot, rowvar=False)
        fitted_cov = 0.85 * pilot_cov + 0.15 * laplace_cov
        fitted_cov = 0.5 * (fitted_cov + fitted_cov.T)
        result[row], _ = _independent_t_chain(
            X, Xt_y, Q, rng, pilot_mean, t_scale_factor * fitted_cov,
            last, n_samples, 5, 1000, df)

    return result