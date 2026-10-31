def fit_predict(train_x, train_y, test_x, train_groups):
    import numpy as np
    from scipy.linalg import eigh
    from sklearn.metrics import roc_auc_score

    y = np.asarray(train_y, dtype=np.int8).reshape(-1)
    groups = np.asarray(train_groups).reshape(-1)
    people = np.unique(groups)
    alphas = np.array([0.03, 0.10, 0.25, 0.50, 0.80])

    def epochs(a):
        a = np.asarray(a)
        n = a.shape[0]
        # 31.25 ms non-overlapping averages; retain 93.75--906.25 ms.
        b = a[:, :, :128].reshape(n, 16, 32, 4).mean(axis=3)
        b = np.asarray(b[:, :, 3:29], dtype=np.float64)
        np.nan_to_num(b, copy=False, nan=0.0, posinf=120.0, neginf=-120.0)
        np.clip(b, -120.0, 120.0, out=b)
        return b

    B = epochs(train_x)
    BT = epochs(test_x)
    n, c, t = B.shape
    raw = B.reshape(n, c * t)
    raw_test = BT.reshape(BT.shape[0], c * t)

    def make_stats(X, selected):
        out = {}
        for u in selected:
            pair = {}
            ug = (groups == u)
            for cls in (0, 1):
                ix = np.flatnonzero(ug & (y == cls))
                if ix.size:
                    z = X[ix]
                    pair[cls] = (z.mean(axis=0), (z.T @ z) / float(ix.size))
            out[u] = pair
        return out

    def weights_from_stats(stats, selected):
        mus = []
        seconds = []
        for cls in (0, 1):
            mm, qq = [], []
            for u in selected:
                if cls in stats[u]:
                    mm.append(stats[u][cls][0])
                    qq.append(stats[u][cls][1])
            mu = np.mean(mm, axis=0)
            sec = np.mean(qq, axis=0)
            mus.append(mu)
            seconds.append(sec)
        cov = 0.5 * ((seconds[0] - np.outer(mus[0], mus[0])) +
                     (seconds[1] - np.outer(mus[1], mus[1])))
        cov = 0.5 * (cov + cov.T)
        diag = np.maximum(np.diag(cov), 1e-8)
        scale = np.sqrt(diag)
        corr = cov / np.outer(scale, scale)
        corr = 0.5 * (corr + corr.T)
        ev, V = np.linalg.eigh(corr)
        ev = np.maximum(ev, 0.0)
        delta = (mus[1] - mus[0]) / scale
        vd = V.T @ delta
        ans = []
        for a in alphas:
            ws = V @ (vd / ((1.0 - a) * ev + a))
            w = ws / scale
            norm = np.sqrt(max(float(w @ cov @ w), 1e-12))
            ans.append(w / norm)
        return ans

    def make_spatial_stats():
        out = {}
        for u in people:
            ug = (groups == u)
            rec = {}
            for cls in (0, 1):
                z = B[ug & (y == cls)]
                if len(z):
                    rec[cls] = z.mean(axis=0)
            z = B[ug]
            flat = z.transpose(0, 2, 1).reshape(-1, c)
            rec['noise'] = (flat.T @ flat) / float(len(flat))
            out[u] = rec
        return out

    def spatial_filters(stats, selected, k=8):
        m0 = np.mean([stats[u][0] for u in selected], axis=0)
        m1 = np.mean([stats[u][1] for u in selected], axis=0)
        d = m1 - m0
        signal = (d @ d.T) / float(t)
        noise = np.mean([stats[u]['noise'] for u in selected], axis=0)
        ridge = max(float(np.trace(noise)) / c, 1e-8) * 0.05
        noise = 0.5 * (noise + noise.T) + ridge * np.eye(c)
        _, vec = eigh(signal, noise, check_finite=False)
        return vec[:, -k:][:, ::-1].T

    def project(S, A):
        return np.einsum('kc,nct->nkt', S, A, optimize=True).reshape(len(A), -1)

    def mean_person_auc(score):
        vals = []
        for u in people:
            ix = (groups == u)
            yy = y[ix]
            if yy.min() != yy.max():
                vals.append(roc_auc_score(yy, score[ix]))
        return float(np.mean(vals))

    raw_stats = make_stats(raw, people)
    spatial_stats = make_spatial_stats()
    raw_oof = np.zeros((len(alphas), n), dtype=np.float64)
    xd_oof = np.zeros_like(raw_oof)
    nf = min(5, len(people))

    for fold in range(nf):
        held = people[fold::nf]
        selected = people[~np.isin(people, held)]
        va = np.isin(groups, held)

        rw = weights_from_stats(raw_stats, selected)
        raw_oof[:, va] = (raw[va] @ np.column_stack(rw)).T

        S = spatial_filters(spatial_stats, selected)
        xd = project(S, B)
        xd_stats = make_stats(xd, selected)
        xw = weights_from_stats(xd_stats, selected)
        xd_oof[:, va] = (xd[va] @ np.column_stack(xw)).T

    blend_grid = [0.50, 0.25, 0.75, 0.0, 1.0]
    best_value = -np.inf
    best_choice = (0, 0, 0.5)
    for ir in range(len(alphas)):
        for ix in range(len(alphas)):
            for blend in blend_grid:
                score = blend * raw_oof[ir] + (1.0 - blend) * xd_oof[ix]
                value = mean_person_auc(score)
                if value > best_value + 1e-12:
                    best_value = value
                    best_choice = (ir, ix, blend)

    ir, ix, blend = best_choice
    rw = weights_from_stats(raw_stats, people)[ir]
    raw_score = raw_test @ rw

    S = spatial_filters(spatial_stats, people)
    xd = project(S, B)
    xd_test = project(S, BT)
    xd_stats = make_stats(xd, people)
    xw = weights_from_stats(xd_stats, people)[ix]
    xd_score = xd_test @ xw

    result = blend * raw_score + (1.0 - blend) * xd_score
    return np.nan_to_num(result, nan=0.0, posinf=1e12, neginf=-1e12)
