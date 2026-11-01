import numpy as np

# For reproducibility
class SplitRandom:
    def __init__(self, seed):
        # Split master seed deterministically for each chain
        self.base_seed = seed
        self.ct = 0
    def next(self):
        res = np.random.default_rng(self.base_seed + self.ct)
        self.ct += 1
        return res

def log_bernoulli_glm_posterior(beta, X, y, Q):
    # beta: (d,), X: (n,d), y: (n,)
    xb = X @ beta
    llik = np.dot(y, xb) - np.sum(np.logaddexp(0, xb))
    lprior = -0.5 * beta @ Q @ beta
    return llik + lprior

# Elliptical slice sampling for non-conjugate, correlated Gaussian-prior posteriors
def elliptical_slice_sampler(init, cov_chol, logpost, X, y, Q, n_samples, burnin, rng):
    d = len(init)
    samples = np.zeros((n_samples + burnin, d), dtype=np.float64)
    beta = np.array(init, dtype=np.float64)
    for i in range(n_samples + burnin):
        # Propose from the prior
        nu = cov_chol @ rng.standard_normal(d)
        # Evaluate log posterior at current
        cur_logpost = logpost(beta, X, y, Q)
        # Draw threshold log-uniformly
        logy = cur_logpost + np.log(rng.uniform())
        # Draw a bracket for theta
        theta = rng.uniform(0, 2*np.pi)
        theta_min = theta - 2*np.pi
        theta_max = theta
        while True:
            proposal = beta * np.cos(theta) + nu * np.sin(theta)
            proposal_logpost = logpost(proposal, X, y, Q)
            if proposal_logpost > logy:
                beta = proposal
                break
            else:
                # Shrink bracket and resample
                if theta < 0:
                    theta_min = theta
                else:
                    theta_max = theta
                theta = rng.uniform(theta_min, theta_max)
        samples[i] = beta
    return samples[burnin:]  # discard burnin

def sample_posterior(design_matrix, spike_trains, prior_precision, n_samples, seed):
    """
    design_matrix: (100,10)
    spike_trains: (10,100), rows are y for 10 observations
    prior_precision: (10,10) symmetric positive-definite
    n_samples: int, e.g. 10000
    seed: int
    Returns: (10, n_samples, 10) samples
    """
    num_obs = spike_trains.shape[0]
    d = design_matrix.shape[1]

    # Cholesky decomposition of prior covariance
    cov = np.linalg.inv(prior_precision)
    cov_chol = np.linalg.cholesky(cov)

    master_rng = SplitRandom(seed)

    # Number of burn-in samples
    burnin = 2000

    all_samples = np.zeros((num_obs, n_samples, d), dtype=np.float64)

    # Starting point: MAP estimate via Newton's method (optional, here use zeros)
    init = np.zeros(d, dtype=np.float64)

    for i in range(num_obs):
        y = spike_trains[i]  # (100,)
        rng = master_rng.next()
        samples = elliptical_slice_sampler(
            init=init,
            cov_chol=cov_chol,
            logpost=log_bernoulli_glm_posterior,
            X=design_matrix,
            y=y,
            Q=prior_precision,
            n_samples=n_samples,
            burnin=burnin,
            rng=rng
        )
        all_samples[i] = samples
    return all_samples
