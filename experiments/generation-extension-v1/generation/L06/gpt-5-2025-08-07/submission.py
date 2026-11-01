import numpy as np
from scipy.special import expit
from scipy.linalg import cho_solve, solve_triangular

# ----------------- helpers -----------------

def _logpost_and_grad(beta, X, y, Q):
    u = X @ beta
    s = expit(u)
    ll = float(y @ u) - np.sum(np.logaddexp(0.0, u))
    Qb = Q @ beta
    grad = X.T @ (y - s) - Qb
    lp = ll - 0.5 * float(beta @ Qb)
    return lp, grad


def _newton_map(X, y, Q, max_iter=50):
    p = X.shape[1]
    b = np.zeros(p, dtype=np.float64)
    lp, g = _logpost_and_grad(b, X, y, Q)
    for _ in range(max_iter):
        u = X @ b
        s = expit(u)
        W = s * (1.0 - s)
        WX = W[:, None] * X
        H = X.T @ WX + Q
        # Solve H delta = g using Cholesky with small jitter if needed
        jitter = 0.0
        for _try in range(3):
            try:
                c = np.linalg.cholesky(H + jitter * np.eye(p))
                y1 = solve_triangular(c, g, lower=True, check_finite=False)
                delta = solve_triangular(c.T, y1, lower=False, check_finite=False)
                break
            except np.linalg.LinAlgError:
                jitter = 1e-8 if jitter == 0.0 else jitter * 10.0
        # Backtracking line search
        step = 1.0
        g_dot_delta = float(g @ delta)
        improved = False
        while step > 1e-8:
            b_new = b + step * delta
            lp_new, g_new = _logpost_and_grad(b_new, X, y, Q)
            if np.isfinite(lp_new) and lp_new >= lp + 1e-4 * step * g_dot_delta:
                b, lp, g = b_new, lp_new, g_new
                improved = True
                break
            step *= 0.5
        if not improved or np.linalg.norm(step * delta) < 1e-6 * (1.0 + np.linalg.norm(b)):
            break
    # Final Hessian at mode
    u = X @ b
    s = expit(u)
    W = s * (1.0 - s)
    WX = W[:, None] * X
    H = X.T @ WX + Q
    return b, H


def _mala_sampler(b0, Sigma, L, logdetM, X, y, Q, n_samples, rng, burn=800):
    p = X.shape[1]
    const_prop = -0.5 * (p * np.log(2.0 * np.pi) + logdetM)

    def log_q(x, m, eps):
        v = solve_triangular(L, x - m, lower=True, check_finite=False)
        return const_prop - p * np.log(eps) - 0.5 * float(v @ v) / (eps ** 2)

    def lp_grad(b):
        return _logpost_and_grad(b, X, y, Q)

    cur = np.array(b0, dtype=np.float64, copy=True)
    lp_cur, g_cur = lp_grad(cur)
    mg_cur = Sigma @ g_cur

    log_eps = np.log(1.0)
    target = 0.57

    draws = np.empty((n_samples, p), dtype=np.float64)
    total_steps = burn + n_samples

    for t in range(total_steps):
        eps = float(np.exp(log_eps))
        mu = cur + 0.5 * (eps ** 2) * mg_cur
        z = rng.standard_normal(p)
        prop = mu + eps * (L @ z)

        lp_prop, g_prop = lp_grad(prop)
        mg_prop = Sigma @ g_prop
        mu_rev = prop + 0.5 * (eps ** 2) * mg_prop

        logq_fwd = log_q(prop, mu, eps)
        logq_rev = log_q(cur, mu_rev, eps)
        log_alpha = (lp_prop - lp_cur) + (logq_rev - logq_fwd)

        if np.log(rng.random()) < log_alpha:
            cur = prop
            lp_cur = lp_prop
            g_cur = g_prop
            mg_cur = mg_prop
            accepted = 1.0
        else:
            accepted = 0.0

        if t < burn:
            a = 1.0 / np.sqrt(t + 1.0)
            log_eps += a * (accepted - target)
            # keep within reasonable bounds
            log_eps = float(np.clip(log_eps, np.log(1e-3), np.log(3.0)))
        else:
            draws[t - burn, :] = cur

    return draws


# ----------------- main API -----------------

def sample_posterior(design_matrix, spike_trains, prior_precision, n_samples, seed):
    X = np.asarray(design_matrix, dtype=np.float64)
    Q = np.asarray(prior_precision, dtype=np.float64)
    Y = np.asarray(spike_trains, dtype=np.float64)

    rng = np.random.default_rng(int(seed))
    n_obs = Y.shape[0]
    p = X.shape[1]
    out = np.empty((n_obs, int(n_samples), p), dtype=np.float64)

    I = np.eye(p, dtype=np.float64)

    for i in range(n_obs):
        y = Y[i]
        b_map, H = _newton_map(X, y, Q)
        # Invert H for Sigma and get its Cholesky
        cH = np.linalg.cholesky(H)
        Sigma = cho_solve((cH, True), I)
        Sigma = 0.5 * (Sigma + Sigma.T)  # symmetrize
        L = np.linalg.cholesky(Sigma)
        logdetM = 2.0 * np.sum(np.log(np.diag(L)))
        burn = max(600, min(1200, int(n_samples) // 8))
        draws = _mala_sampler(b_map, Sigma, L, logdetM, X, y, Q, int(n_samples), rng, burn=burn)
        out[i, :, :] = draws

    return out
