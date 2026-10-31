def fit_predict(train_x, train_y, test_x, train_groups):
    import numpy as np
    from sklearn.svm import LinearSVC

    NCLASS = 7
    C_GRID = (0.003, 0.015, 0.075)
    GAMMA_GRID = (0.0, 0.15, -0.15, 0.30)

    def dense32(x):
        if hasattr(x, "toarray"):
            x = x.toarray()
        return np.asarray(x, dtype=np.float32)

    # Every added quantity is calculated independently for each spot.
    def augment(x):
        x = dense32(x)
        mean = np.mean(x, axis=1, dtype=np.float64).astype(np.float32)
        std = np.std(x, axis=1, dtype=np.float64).astype(np.float32)
        zero = np.mean(x <= 0.0, axis=1, dtype=np.float64).astype(np.float32)
        maximum = np.max(x, axis=1).astype(np.float32)
        return np.column_stack((x, mean, std, zero, maximum)).astype(
            np.float32, copy=False
        )

    def fit_scaler(x):
        mu = np.mean(x, axis=0, dtype=np.float64).astype(np.float32)
        sd = np.std(x, axis=0, dtype=np.float64).astype(np.float32)
        sd[sd < 1e-5] = 1.0
        return mu, sd

    def transform(x, mu, sd):
        z = (x - mu) / sd
        np.clip(z, -8.0, 8.0, out=z)
        return np.ascontiguousarray(z, dtype=np.float32)

    def weights_and_prior(y):
        counts = np.bincount(y, minlength=NCLASS).astype(np.float64)
        present = counts > 0
        k = int(np.sum(present))
        raw = np.ones(NCLASS, dtype=np.float64)
        raw[present] = np.sqrt(float(y.size) / (k * counts[present]))
        norm = np.sum(counts[present] * raw[present]) / float(y.size)
        raw[present] /= norm
        cw = {int(c): float(raw[c]) for c in np.flatnonzero(present)}
        prior = counts / float(y.size)
        return cw, prior

    def fit_svc(x, y, c_value):
        classes = np.unique(y)
        if classes.size == 1:
            return (None, classes)
        cw, _ = weights_and_prior(y)
        model = LinearSVC(
            C=float(c_value),
            class_weight=cw,
            loss="squared_hinge",
            penalty="l2",
            dual=False,
            tol=2e-4,
            max_iter=4000,
            random_state=1729,
        )
        model.fit(x, y)
        return (model, model.classes_.astype(np.int64, copy=False))

    def aligned_scores(fitted, x):
        model, classes = fitted
        out = np.full((x.shape[0], NCLASS), -1e6, dtype=np.float64)
        if model is None:
            out[:, int(classes[0])] = 0.0
            return out
        score = model.decision_function(x)
        if np.ndim(score) == 1:
            score = np.asarray(score, dtype=np.float64)
            out[:, int(classes[0])] = -score
            out[:, int(classes[1])] = score
        else:
            out[:, classes] = np.asarray(score, dtype=np.float64)
        return out

    def adjust(scores, prior, gamma):
        offsets = np.zeros(NCLASS, dtype=np.float64)
        present = prior > 0
        offsets[present] = -float(gamma) * np.log(prior[present])
        return scores + offsets

    def macro_f1(y, pred):
        total = 0.0
        for c in range(NCLASS):
            yt = y == c
            yp = pred == c
            tp = np.count_nonzero(yt & yp)
            fp = np.count_nonzero((~yt) & yp)
            fn = np.count_nonzero(yt & (~yp))
            den = 2 * tp + fp + fn
            if den:
                total += (2.0 * tp) / den
        return total / NCLASS

    x_all = augment(train_x)
    x_test = augment(test_x)
    y_all = np.asarray(train_y, dtype=np.int64).reshape(-1)
    groups = np.asarray(train_groups).reshape(-1)
    unique_groups = np.unique(groups)

    fold_cache = {c: [] for c in C_GRID}
    for held_out in unique_groups:
        va = groups == held_out
        tr = ~va
        ytr = y_all[tr]
        mu, sd = fit_scaler(x_all[tr])
        ztr = transform(x_all[tr], mu, sd)
        zva = transform(x_all[va], mu, sd)
        _, prior = weights_and_prior(ytr)
        for c_value in C_GRID:
            fitted = fit_svc(ztr, ytr, c_value)
            scores = aligned_scores(fitted, zva)
            fold_cache[c_value].append((y_all[va], scores, prior))
        del ztr, zva

    best_score = -1.0
    best_c = C_GRID[0]
    best_gamma = GAMMA_GRID[0]
    for c_value in C_GRID:
        for gamma in GAMMA_GRID:
            values = []
            for yva, scores, prior in fold_cache[c_value]:
                pred = np.argmax(adjust(scores, prior, gamma), axis=1)
                values.append(macro_f1(yva, pred))
            value = float(np.mean(values))
            if value > best_score + 1e-12:
                best_score = value
                best_c = c_value
                best_gamma = gamma

    mu, sd = fit_scaler(x_all)
    ztrain = transform(x_all, mu, sd)
    ztest = transform(x_test, mu, sd)
    fitted = fit_svc(ztrain, y_all, best_c)
    _, prior = weights_and_prior(y_all)
    scores = aligned_scores(fitted, ztest)
    pred = np.argmax(adjust(scores, prior, best_gamma), axis=1)
    return pred.astype(np.int64, copy=False)