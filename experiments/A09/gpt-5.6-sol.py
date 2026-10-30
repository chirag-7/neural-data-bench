import gc
import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier


_OFFSETS = np.asarray([-15, -5, -1, 0, 1, 5, 15], dtype=np.float32)


def _features(x):
    x = np.array(x, dtype=np.float32, order="C", copy=True)
    np.nan_to_num(x, copy=False, nan=0.0, posinf=0.0, neginf=0.0)
    n = x.shape[0]

    # Input order is (mouse, coordinate, landmark). Convert to
    # (example, time, mouse, landmark, coordinate).
    p = x.reshape(n, 7, 2, 2, 7).transpose(0, 1, 2, 4, 3)
    del x

    # Body axes and a robust per-example scale.
    a0 = p[:, :, 0, 3] - p[:, :, 0, 6]
    a1 = p[:, :, 1, 3] - p[:, :, 1, 6]
    l0 = np.sqrt(np.sum(a0 * a0, axis=-1) + 1e-6)
    l1 = np.sqrt(np.sum(a1 * a1, axis=-1) + 1e-6)
    scale = np.median(0.5 * (l0 + l1), axis=1)
    scale = np.clip(scale, 2.0, 1000.0).astype(np.float32)

    # Orient every supplied frame by the resident tail-to-neck direction.
    safe_l0 = np.maximum(l0, 1e-3)
    ux = a0[..., 0] / safe_l0
    uy = a0[..., 1] / safe_l0
    bad = l0 < 1.0
    ux[bad] = 1.0
    uy[bad] = 0.0

    origin = p[:, :, 0, 3]
    rel = p - origin[:, :, None, None, :]
    den = scale[:, None, None, None]
    cx = (rel[..., 0] * ux[:, :, None, None] +
          rel[..., 1] * uy[:, :, None, None]) / den
    cy = (-rel[..., 0] * uy[:, :, None, None] +
          rel[..., 1] * ux[:, :, None, None]) / den
    canonical = np.stack((cx, cy), axis=-1).reshape(n, -1)

    # Global-coordinate landmark velocities, expressed in the target
    # resident's body frame and normalized by body size and elapsed frames.
    dt = np.diff(_OFFSETS)
    v = (p[:, 1:] - p[:, :-1]) / dt[None, :, None, None, None]
    tx = ux[:, 3]
    ty = uy[:, 3]
    vx = v[..., 0] * tx[:, None, None, None] + \
         v[..., 1] * ty[:, None, None, None]
    vy = -v[..., 0] * ty[:, None, None, None] + \
         v[..., 1] * tx[:, None, None, None]
    velocity = np.stack((vx, vy), axis=-1)
    velocity /= scale[:, None, None, None, None]
    velocity = velocity.reshape(n, -1)

    # All 21 within-mouse and 49 cross-mouse distances at every offset.
    ii, jj = np.triu_indices(7, 1)
    d = p[:, :, 0, :, None, :] - p[:, :, 0, None, :, :]
    d0 = np.sqrt(np.sum(d * d, axis=-1) + 1e-6)[:, :, ii, jj]
    del d
    d = p[:, :, 1, :, None, :] - p[:, :, 1, None, :, :]
    d1 = np.sqrt(np.sum(d * d, axis=-1) + 1e-6)[:, :, ii, jj]
    del d
    d = p[:, :, 0, :, None, :] - p[:, :, 1, None, :, :]
    dc = np.sqrt(np.sum(d * d, axis=-1) + 1e-6).reshape(n, 7, 49)
    del d
    geo = np.concatenate((d0, d1, dc), axis=2)
    geo /= scale[:, None, None]
    geo_now = geo[:, 3]
    geo_mean = np.mean(geo, axis=1)
    geo_std = np.std(geo, axis=1)
    geo_range = np.max(geo, axis=1) - np.min(geo, axis=1)

    # Preserve coarse arena location and resident heading/body-size history.
    absolute = p[:, 3].reshape(n, -1) / scale[:, None]
    body = np.stack((l0 / scale[:, None], l1 / scale[:, None], ux, uy),
                    axis=-1).reshape(n, -1)

    f = np.concatenate((canonical, velocity, geo_now, geo_mean,
                        geo_std, geo_range, absolute, body), axis=1)
    np.nan_to_num(f, copy=False, nan=0.0, posinf=25.0, neginf=-25.0)
    np.clip(f, -25.0, 25.0, out=f)
    return np.asarray(f, dtype=np.float32, order="C")


def fit_predict(train_x, train_y, test_x):
    y = np.asarray(train_y, dtype=np.int64).reshape(-1)
    xtr = _features(train_x)

    counts = np.bincount(y, minlength=4).astype(np.float64)
    counts = np.maximum(counts, 1.0)
    class_weight = (counts.mean() / counts) ** 0.60
    sample_weight = class_weight[y]
    sample_weight /= sample_weight.mean()

    model = HistGradientBoostingClassifier(
        loss="log_loss",
        learning_rate=0.07,
        max_iter=250,
        max_leaf_nodes=31,
        max_depth=None,
        min_samples_leaf=24,
        l2_regularization=2.0,
        max_bins=127,
        early_stopping=False,
        random_state=1729
    )
    model.fit(xtr, y, sample_weight=sample_weight)
    del xtr
    gc.collect()

    xte = _features(test_x)
    pred = model.predict(xte)
    return np.asarray(pred, dtype=np.int64).reshape(-1)
