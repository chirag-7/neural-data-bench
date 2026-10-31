import numpy as np
from scipy.special import expit


def sample_posterior(design_matrix, spike_trains, prior_precision,
                     n_samples, seed):
    X = np.asarray(design_matrix, dtype=np.float64)
    Y = np.asarray(spike_trains, dtype=np.float64)
    Q = np.asarray(prior_precision, dtype=np.float64)
    n_samples = int(n_samples)

    if X.shape != (100, 10):
        raise ValueError("design_matrix must have shape (100, 10)")
    if Y.shape != (10, 100):
        raise ValueError("spike_trains must have shape (10, 100)")
    if Q.shape != (10, 10):
        raise ValueError("prior_precision must have shape (10, 10)")
    if n_samples <= 0:
        raise ValueError("n_samples must be positive")
    if not (np.all(np.isfinite(X)) and np.all(np.isfinite(Y)) and
            np.all(np.isfinite(Q))):
        raise ValueError("inputs must be finite")

    Q = 0.5 * (Q + Q.T)
    np.linalg.cholesky(Q)
    d = X.shape[1]
    eye = np.eye(d, dtype=np.float64)
    result = np.empty((10, n_samples, d), dtype=np.float64)
    master = np.random.SeedSequence(seed)
    streams = master.spawn(10)

    def log_posterior(beta, y):
        eta = X @ beta
        return (float(y @ eta - np.logaddexp(0.0, eta).sum())
                - 0.5 * float(beta @ (Q @ beta)))

    def find_mode(y):
        beta = np.zeros(d, dtype=np.float64)
        value = log_posterior(beta, y)
        for _ in range(60):
            eta = X @ beta
            p = expit(eta)
            grad = X.T @ (y - p) - Q @ beta
            w = p * (1.0 - p)
            hess = Q + X.T @ (w[:, None] * X)
            step = np.linalg.solve(hess, grad)
            directional = float(grad @ step)
            scale = 1.0
            accepted = False
            while scale >= 2.0 ** -24:
                candidate = beta + scale * step
                candidate_value = log_posterior(candidate, y)
                if (np.isfinite(candidate_value) and
                        candidate_value >= value + 1e-4 * scale * directional):
                    beta = candidate
                    value = candidate_value
                    accepted = True
                    break
                scale *= 0.5
            if not accepted or np.max(np.abs(scale * step)) < 2e-10:
                break

        eta = X @ beta
        p = expit(eta)
        w = p * (1.0 - p)
        hess = Q + X.T @ (w[:, None] * X)
        return beta, hess

    for obs in range(10):
        y = Y[obs]
        mode, hess = find_mode(y)
        chol = np.linalg.cholesky(hess)
        transform = np.linalg.solve(chol.T, eye)
        rng = np.random.default_rng(streams[obs])

        def potential_and_grad(z):
            beta = mode + transform @ z
            eta = X @ beta
            p = expit(eta)
            logp = (float(y @ eta - np.logaddexp(0.0, eta).sum())
                    - 0.5 * float(beta @ (Q @ beta)))
            grad_beta = X.T @ (y - p) - Q @ beta
            return -logp, -(transform.T @ grad_beta)

        def transition(z, potential, grad, epsilon):
            momentum0 = rng.standard_normal(d)
            momentum = momentum0.copy()
            proposal = z.copy()
            tau = rng.uniform(1.25, 2.05)
            n_leapfrog = int(np.clip(np.rint(tau / epsilon), 1, 50))
            step = tau / n_leapfrog
            momentum -= 0.5 * step * grad
            new_potential = potential
            new_grad = grad

            valid = True
            for leap in range(n_leapfrog):
                proposal += step * momentum
                new_potential, new_grad = potential_and_grad(proposal)
                if (not np.isfinite(new_potential) or
                        not np.all(np.isfinite(new_grad))):
                    valid = False
                    break
                if leap + 1 < n_leapfrog:
                    momentum -= step * new_grad

            if valid:
                momentum -= 0.5 * step * new_grad
                old_energy = potential + 0.5 * float(momentum0 @ momentum0)
                new_energy = new_potential + 0.5 * float(momentum @ momentum)
                log_ratio = old_energy - new_energy
                if np.isfinite(log_ratio):
                    accept_prob = min(1.0, float(np.exp(min(0.0, log_ratio))))
                else:
                    accept_prob = 0.0
            else:
                accept_prob = 0.0

            if valid and np.log(rng.random()) < min(0.0, log_ratio):
                return proposal, new_potential, new_grad, accept_prob
            return z, potential, grad, accept_prob

        z = np.zeros(d, dtype=np.float64)
        potential, grad = potential_and_grad(z)
        warmup = 1200
        adapt_steps = 900
        target = 0.90
        epsilon = 0.30
        mu = np.log(10.0 * epsilon)
        log_epsilon_bar = np.log(epsilon)
        h_bar = 0.0
        gamma = 0.05
        t0 = 10.0
        kappa = 0.75

        for iteration in range(1, warmup + 1):
            z, potential, grad, accept_prob = transition(
                z, potential, grad, epsilon)
            if iteration <= adapt_steps:
                weight = 1.0 / (iteration + t0)
                h_bar = (1.0 - weight) * h_bar + weight * (target - accept_prob)
                log_epsilon = mu - np.sqrt(iteration) * h_bar / gamma
                averaging_weight = iteration ** (-kappa)
                log_epsilon_bar = (averaging_weight * log_epsilon +
                                   (1.0 - averaging_weight) * log_epsilon_bar)
                epsilon = float(np.clip(np.exp(log_epsilon), 0.025, 0.75))
                if iteration == adapt_steps:
                    epsilon = float(np.clip(np.exp(log_epsilon_bar), 0.025, 0.75))

        draws = np.empty((n_samples, d), dtype=np.float64)
        for draw in range(n_samples):
            z, potential, grad, _ = transition(z, potential, grad, epsilon)
            draws[draw] = mode + transform @ z

        draws = draws[rng.permutation(n_samples)]
        if not np.all(np.isfinite(draws)):
            raise FloatingPointError("non-finite posterior draw encountered")
        result[obs] = draws

    return result