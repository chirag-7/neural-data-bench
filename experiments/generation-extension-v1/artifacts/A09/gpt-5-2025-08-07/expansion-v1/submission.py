import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.utils.class_weight import compute_class_weight


def fit_predict(train_x, train_y, test_x):
    # Deterministic behavior
    rng_seed = 1337
    np.random.seed(rng_seed)

    Xtr = np.asarray(train_x, dtype=np.float32)
    Xte = np.asarray(test_x, dtype=np.float32)
    y = np.asarray(train_y, dtype=np.int64)

    def impute_per_example_timewise(X):
        # Fill NaN/inf per example by mean across its 7 offsets for each coordinate.
        Xf = X.astype(np.float32, copy=True)
        Xf[~np.isfinite(Xf)] = np.nan
        means = np.nanmean(Xf, axis=1, keepdims=True)  # (N,1,28)
        means_rep = np.repeat(means, Xf.shape[1], axis=1)
        mask = np.isnan(Xf)
        Xf[mask] = means_rep[mask]
        # If a whole coordinate is NaN across time for a sample, fall back to 0
        Xf[np.isnan(Xf)] = 0.0
        return Xf

    Xtr = impute_per_example_timewise(Xtr)
    Xte = impute_per_example_timewise(Xte)

    def build_features(X):
        # X: (N, 7, 28) in order [res_x[7], res_y[7], int_x[7], int_y[7]] per offset
        N, T, F = X.shape
        eps = 1e-6
        # Reshape to [N, T, 4, 7]: (res_x, res_y, int_x, int_y)
        Xg = X.reshape(N, T, 4, 7)
        rx, ry, ix, iy = Xg[:, :, 0, :], Xg[:, :, 1, :], Xg[:, :, 2, :], Xg[:, :, 3, :]
        idxm15, idxm5, idxm1, idx0, idxp1, idxp5, idxp15 = 0, 1, 2, 3, 4, 5, 6

        def dist(ax, ay, bx, by):
            return np.sqrt((ax - bx) ** 2 + (ay - by) ** 2 + eps)

        # t0 slices
        rx0, ry0 = rx[:, idx0, :], ry[:, idx0, :]
        ix0, iy0 = ix[:, idx0, :], iy[:, idx0, :]

        # Body lengths (nose to tail base)
        r_len = dist(rx0[:, 0], ry0[:, 0], rx0[:, 6], ry0[:, 6])
        i_len = dist(ix0[:, 0], iy0[:, 0], ix0[:, 6], iy0[:, 6])
        scale = np.sqrt(r_len * i_len)
        scale = np.maximum(scale, 1.0)

        # Centers (mean of neck, L/R hips, tail base)
        r_cx0 = np.mean(rx0[:, [3, 4, 5, 6]], axis=1)
        r_cy0 = np.mean(ry0[:, [3, 4, 5, 6]], axis=1)
        i_cx0 = np.mean(ix0[:, [3, 4, 5, 6]], axis=1)
        i_cy0 = np.mean(iy0[:, [3, 4, 5, 6]], axis=1)

        # Head and body-axis vectors at t0
        r_hx, r_hy = rx0[:, 0] - rx0[:, 3], ry0[:, 0] - ry0[:, 3]
        i_hx, i_hy = ix0[:, 0] - ix0[:, 3], iy0[:, 0] - iy0[:, 3]
        r_bx, r_by = rx0[:, 3] - rx0[:, 6], ry0[:, 3] - ry0[:, 6]
        i_bx, i_by = ix0[:, 3] - ix0[:, 6], iy0[:, 3] - iy0[:, 6]

        # Relative vector resident->intruder at t0 (nose positions)
        r_nx0, r_ny0 = rx0[:, 0], ry0[:, 0]
        i_nx0, i_ny0 = ix0[:, 0], iy0[:, 0]
        r2i_x, r2i_y = i_nx0 - r_nx0, i_ny0 - r_ny0
        d_nn0 = np.sqrt(r2i_x ** 2 + r2i_y ** 2 + eps)
        u_x, u_y = r2i_x / (d_nn0 + eps), r2i_y / (d_nn0 + eps)
        u_perp_x, u_perp_y = -u_y, u_x

        # Intra-animal shape features normalized by own length
        def shape_feats(x0, y0, L):
            ear_gap = dist(x0[:, 1], y0[:, 1], x0[:, 2], y0[:, 2]) / (L + eps)
            hip_gap = dist(x0[:, 4], y0[:, 4], x0[:, 5], y0[:, 5]) / (L + eps)
            neck_tail = dist(x0[:, 3], y0[:, 3], x0[:, 6], y0[:, 6]) / (L + eps)
            nose_tail = dist(x0[:, 0], y0[:, 0], x0[:, 6], y0[:, 6]) / (L + eps)
            nose_center = dist(x0[:, 0], y0[:, 0], np.mean(x0[:, [3, 4, 5, 6]], axis=1),
                                np.mean(y0[:, [3, 4, 5, 6]], axis=1)) / (L + eps)
            return [ear_gap, hip_gap, neck_tail, nose_tail, nose_center]

        r_shape = shape_feats(rx0, ry0, r_len)
        i_shape = shape_feats(ix0, iy0, i_len)
        ratio_len = r_len / (i_len + eps)

        def cos_pair(ax, ay, bx, by):
            denom = (np.sqrt(ax * ax + ay * ay) * np.sqrt(bx * bx + by * by) + eps)
            return (ax * bx + ay * by) / denom

        cos_head_head = cos_pair(r_hx, r_hy, i_hx, i_hy)
        cos_body_body = cos_pair(r_bx, r_by, i_bx, i_by)

        def proj_to_u(ax, ay, ux, uy):
            return (ax * ux + ay * uy) / (np.sqrt(ax * ax + ay * ay) + eps)

        cos_rhead_to_i = proj_to_u(r_hx, r_hy, u_x, u_y)
        cos_ihead_to_r = proj_to_u(i_hx, i_hy, -u_x, -u_y)
        cos_rbody_to_i = proj_to_u(r_bx, r_by, u_x, u_y)
        cos_ibody_to_r = proj_to_u(i_bx, i_by, -u_x, -u_y)

        # Distances at each time offset (nose-nose, center-center, min landmark distance)
        d_nn_ts, d_cc_ts, d_min_ts = [], [], []
        for tidx in range(7):
            rxs, rys = rx[:, tidx, :], ry[:, tidx, :]
            ixs, iys = ix[:, tidx, :], iy[:, tidx, :]
            d_nn = dist(rxs[:, 0], rys[:, 0], ixs[:, 0], iys[:, 0])
            r_cx = np.mean(rxs[:, [3, 4, 5, 6]], axis=1)
            r_cy = np.mean(rys[:, [3, 4, 5, 6]], axis=1)
            i_cx = np.mean(ixs[:, [3, 4, 5, 6]], axis=1)
            i_cy = np.mean(iys[:, [3, 4, 5, 6]], axis=1)
            d_cc = dist(r_cx, r_cy, i_cx, i_cy)
            dx = rxs[:, :, None] - ixs[:, None, :]
            dy = rys[:, :, None] - iys[:, None, :]
            dists = np.sqrt(dx * dx + dy * dy + eps)
            d_min = dists.reshape(N, -1).min(axis=1)
            d_nn_ts.append(d_nn / scale)
            d_cc_ts.append(d_cc / scale)
            d_min_ts.append(d_min / scale)

        # Approach speed and individual nose speeds over different time deltas
        def approach(idxm, idxp):
            vrx = rx[:, idxp, 0] - rx[:, idxm, 0]
            vry = ry[:, idxp, 0] - ry[:, idxm, 0]
            vix = ix[:, idxp, 0] - ix[:, idxm, 0]
            viy = iy[:, idxp, 0] - iy[:, idxm, 0]
            vrelx, vrely = vrx - vix, vry - viy
            appr = -(vrelx * u_x + vrely * u_y) / (scale + eps)
            sp_r = np.sqrt(vrx * vrx + vry * vry + eps) / (scale + eps)
            sp_i = np.sqrt(vix * vix + viy * viy + eps) / (scale + eps)
            return appr, sp_r, sp_i

        appr1, sp_r1, sp_i1 = approach(idxm1, idxp1)
        appr5, sp_r5, sp_i5 = approach(idxm5, idxp5)
        appr15, sp_r15, sp_i15 = approach(idxm15, idxp15)

        # Separation change
        def dchange(idxm, idxp):
            dm = dist(rx[:, idxm, 0], ry[:, idxm, 0], ix[:, idxm, 0], iy[:, idxm, 0])
            dp = dist(rx[:, idxp, 0], ry[:, idxp, 0], ix[:, idxp, 0], iy[:, idxp, 0])
            return (dp - dm) / (scale + eps)

        dd1, dd5, dd15 = dchange(idxm1, idxp1), dchange(idxm5, idxp5), dchange(idxm15, idxp15)

        # Center projections along inter-animal axis at t0
        dx_c, dy_c = i_cx0 - r_cx0, i_cy0 - r_cy0
        cen_longi = (dx_c * u_x + dy_c * u_y) / (scale + eps)
        pair_cx0 = 0.5 * (r_cx0 + i_cx0)
        pair_cy0 = 0.5 * (r_cy0 + i_cy0)
        r_longi = ((r_nx0 - pair_cx0) * u_x + (r_ny0 - pair_cy0) * u_y) / (scale + eps)
        i_longi = ((i_nx0 - pair_cx0) * u_x + (i_ny0 - pair_cy0) * u_y) / (scale + eps)

        # Head turning (cosine of change) over ±1 and ±5
        def head_turn(idxm, idxp):
            rhx1, rhy1 = rx[:, idxp, 0] - rx[:, idxp, 3], ry[:, idxp, 0] - ry[:, idxp, 3]
            rhx2, rhy2 = rx[:, idxm, 0] - rx[:, idxm, 3], ry[:, idxm, 0] - ry[:, idxm, 3]
            ihx1, ihy1 = ix[:, idxp, 0] - ix[:, idxp, 3], iy[:, idxp, 0] - iy[:, idxp, 3]
            ihx2, ihy2 = ix[:, idxm, 0] - ix[:, idxm, 3], iy[:, idxm, 0] - iy[:, idxm, 3]
            def coschg(ax1, ay1, ax2, ay2):
                return (ax1 * ax2 + ay1 * ay2) / (np.sqrt(ax1 * ax1 + ay1 * ay1) * np.sqrt(ax2 * ax2 + ay2 * ay2) + eps)
            return coschg(rhx1, rhy1, rhx2, rhy2), coschg(ihx1, ihy1, ihx2, ihy2)

        r_turn1, i_turn1 = head_turn(idxm1, idxp1)
        r_turn5, i_turn5 = head_turn(idxm5, idxp5)

        # Contact-like distances at t0
        d_rnose_i_tail = dist(r_nx0, r_ny0, ix0[:, 6], iy0[:, 6]) / (scale + eps)
        d_inose_r_tail = dist(i_nx0, i_ny0, rx0[:, 6], ry0[:, 6]) / (scale + eps)
        d_rnose_i_neck = dist(r_nx0, r_ny0, ix0[:, 3], iy0[:, 3]) / (scale + eps)
        d_inose_r_neck = dist(i_nx0, i_ny0, rx0[:, 3], ry0[:, 3]) / (scale + eps)
        d_center_center0 = dist(r_cx0, r_cy0, i_cx0, i_cy0) / (scale + eps)

        feats = []
        feats += d_nn_ts
        feats += d_cc_ts
        feats += d_min_ts
        feats += [appr1, appr5, appr15, sp_r1, sp_i1, sp_r5, sp_i5, sp_r15, sp_i15, dd1, dd5, dd15]
        feats += [cos_head_head, cos_body_body, cos_rhead_to_i, cos_ihead_to_r, cos_rbody_to_i, cos_ibody_to_r]
        feats += r_shape + i_shape + [ratio_len]
        feats += [d_rnose_i_tail, d_inose_r_tail, d_rnose_i_neck, d_inose_r_neck, d_center_center0, cen_longi, r_longi, i_longi]
        feats += [r_turn1, i_turn1, r_turn5, i_turn5]

        Feat = np.stack(feats, axis=1).astype(np.float32)
        Feat = np.nan_to_num(Feat, nan=0.0, posinf=1e6, neginf=-1e6)
        return Feat

    Ftr = build_features(Xtr)
    Fte = build_features(Xte)

    # Class-balanced training
    classes = np.unique(y)
    class_w = compute_class_weight(class_weight='balanced', classes=classes, y=y)
    # Map weights to samples via indexing
    idx = np.searchsorted(classes, y)
    sample_w = class_w[idx].astype(np.float32)

    clf = HistGradientBoostingClassifier(
        loss='log_loss',
        max_iter=220,
        learning_rate=0.08,
        max_leaf_nodes=31,
        min_samples_leaf=25,
        l2_regularization=0.0,
        early_stopping=False,
        random_state=rng_seed,
    )

    clf.fit(Ftr, y, sample_weight=sample_w)
    y_pred = clf.predict(Fte)
    return y_pred.astype(int)
