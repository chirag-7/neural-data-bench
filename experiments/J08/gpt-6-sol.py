import numpy as np
from scipy import ndimage as ndi
from scipy.optimize import linear_sum_assignment
from sklearn.ensemble import HistGradientBoostingClassifier


def _features(image):
    z = np.asarray(image, dtype=np.float32)
    a = ndi.gaussian_filter(z, 0.8)
    b = ndi.gaussian_filter(z, 1.6)
    c = ndi.gaussian_filter(z, 3.2)
    d = ndi.gaussian_filter(z, 6.0)
    gx = ndi.sobel(b, axis=0) / 8.0
    gy = ndi.sobel(b, axis=1) / 8.0
    gradient = np.sqrt(gx * gx + gy * gy)
    variance = ndi.gaussian_filter(z * z, 1.6) - b * b
    deviation = np.sqrt(np.maximum(variance, 0))
    return np.stack((z, a, b, c, d, z - b, a - c,
                     b - d, gradient, deviation), axis=-1)


def _instances(image, probability, extent, threshold, peak_size):
    mask = (probability >= threshold) & extent
    components, count = ndi.label(mask, structure=np.ones((3, 3)))
    if count == 0:
        return np.zeros(image.shape, dtype=np.int32)

    sizes = np.bincount(components.ravel())
    mask &= sizes[components] >= 4
    components, count = ndi.label(mask, structure=np.ones((3, 3)))
    if count == 0:
        return np.zeros(image.shape, dtype=np.int32)

    distance = ndi.distance_transform_edt(mask).astype(np.float32)
    smooth_image = ndi.gaussian_filter(np.asarray(image, dtype=np.float32), 1.0)
    smooth_probability = ndi.gaussian_filter(probability, 1.0)
    score = (0.55 * smooth_image + 0.35 * smooth_probability +
             0.10 * np.minimum(distance, 5.0) / 5.0)
    score[~mask] = -1.0

    peaks = (score == ndi.maximum_filter(score, size=peak_size)) & mask
    positions = np.asarray(ndi.maximum_position(
        score, labels=components, index=np.arange(1, count + 1)))
    if positions.ndim == 1:
        positions = positions.reshape(1, 2)
    peaks[positions[:, 0], positions[:, 1]] = True
    markers, _ = ndi.label(peaks, structure=np.ones((3, 3)))
    markers = markers.astype(np.int32)

    elevation = np.full(image.shape, 255, dtype=np.uint8)
    elevation[mask] = (1 + 200 * (1 - np.clip(score[mask], 0, 1))).astype(np.uint8)
    result = ndi.watershed_ift(elevation, markers,
                               structure=np.ones((3, 3))).astype(np.int32)
    result[~mask] = 0
    areas = np.bincount(result.ravel())
    result[areas[result] < 4] = 0
    return result


def _counts_for_f1(truth, prediction):
    truth = np.asarray(truth, dtype=np.int32)
    prediction = np.asarray(prediction, dtype=np.int32)
    gt_ids, gt_areas = np.unique(truth[truth > 0], return_counts=True)
    pr_ids, pr_areas = np.unique(prediction[prediction > 0], return_counts=True)
    gt_keep = gt_areas >= 4
    pr_keep = pr_areas >= 4
    gt_ids, gt_areas = gt_ids[gt_keep], gt_areas[gt_keep]
    pr_ids, pr_areas = pr_ids[pr_keep], pr_areas[pr_keep]
    ng, npred = len(gt_ids), len(pr_ids)
    if ng == 0 or npred == 0:
        return 0, ng, npred

    gt_map = np.full(int(truth.max()) + 1, -1, dtype=np.int32)
    pr_map = np.full(int(prediction.max()) + 1, -1, dtype=np.int32)
    gt_map[gt_ids] = np.arange(ng)
    pr_map[pr_ids] = np.arange(npred)
    overlap = (truth > 0) & (prediction > 0)
    gi = gt_map[truth[overlap]]
    pi = pr_map[prediction[overlap]]
    keep = (gi >= 0) & (pi >= 0)
    intersection = np.bincount(gi[keep] * npred + pi[keep],
                               minlength=ng * npred).reshape(ng, npred)
    union = gt_areas[:, None] + pr_areas[None, :] - intersection
    iou = intersection / np.maximum(union, 1)
    weight = (iou >= 0.5).astype(np.float32) + 0.001 * iou
    rows, cols = linear_sum_assignment(-weight)
    return int(np.count_nonzero(iou[rows, cols] >= 0.5)), ng, npred


def fit_predict(train_x, train_y, test_x):
    rng = np.random.default_rng(20261030)
    n = len(train_x)
    valid_pixels = (train_x[:, 1] > 0.5) & (train_y >= 0)
    positive_counts = np.count_nonzero((train_y > 0) & valid_pixels,
                                       axis=(1, 2))
    eligible = np.flatnonzero(positive_counts >= 4)
    validation_ids = set(rng.choice(eligible, size=min(40, len(eligible)),
                                    replace=False).tolist())

    samples = []
    targets = []
    for j in range(n):
        if j in validation_ids:
            continue
        valid = valid_pixels[j].ravel()
        labels = train_y[j].ravel()
        foreground = np.flatnonzero(valid & (labels > 0))
        background = np.flatnonzero(valid & (labels == 0))
        chosen = []
        if len(foreground):
            chosen.append(rng.choice(foreground, size=min(50, len(foreground)),
                                     replace=False))
        if len(background):
            chosen.append(rng.choice(background, size=min(70, len(background)),
                                     replace=False))
        if not chosen:
            continue
        indices = np.concatenate(chosen)
        features = _features(train_x[j, 0]).reshape(-1, 10)
        samples.append(features[indices])
        targets.append((labels[indices] > 0).astype(np.uint8))

    x = np.concatenate(samples, axis=0)
    y = np.concatenate(targets, axis=0)
    model = HistGradientBoostingClassifier(
        max_iter=70, max_leaf_nodes=15, min_samples_leaf=35,
        learning_rate=0.08, l2_regularization=3.0, random_state=20261030)
    model.fit(x, y)
    del x, y, samples, targets

    threshold, peak_size = 0.55, 7
    if validation_ids:
        validation = []
        for j in sorted(validation_ids):
            image = train_x[j, 0]
            features = _features(image)
            probability = model.predict_proba(features.reshape(-1, 10))[:, 1]
            probability = probability.reshape(image.shape).astype(np.float32)
            valid = valid_pixels[j]
            truth = np.where(valid, train_y[j], 0).astype(np.int32)
            validation.append((image, probability, valid, truth))

        best_f1 = -1.0
        for candidate_threshold in (0.75, 0.60, 0.45, 0.30):
            for candidate_peak_size in (9, 5):
                matched = total_gt = total_predicted = 0
                for image, probability, valid, truth in validation:
                    predicted = _instances(image, probability, valid,
                                           candidate_threshold,
                                           candidate_peak_size)
                    m, g, p = _counts_for_f1(truth, predicted)
                    matched += m
                    total_gt += g
                    total_predicted += p
                f1 = 2 * matched / max(total_gt + total_predicted, 1)
                if f1 > best_f1:
                    best_f1 = f1
                    threshold = candidate_threshold
                    peak_size = candidate_peak_size

    output = np.zeros((len(test_x), test_x.shape[2], test_x.shape[3]),
                      dtype=np.int32)
    for j in range(len(test_x)):
        extent = test_x[j, 1] > 0.5
        rows, cols = np.nonzero(extent)
        if len(rows) == 0:
            continue
        r0, r1 = int(rows.min()), int(rows.max()) + 1
        c0, c1 = int(cols.min()), int(cols.max()) + 1
        image = test_x[j, 0, r0:r1, c0:c1]
        crop_extent = extent[r0:r1, c0:c1]
        features = _features(image)
        probability = model.predict_proba(features.reshape(-1, 10))[:, 1]
        probability = probability.reshape(image.shape).astype(np.float32)
        output[j, r0:r1, c0:c1] = _instances(
            image, probability, crop_extent, threshold, peak_size)
    return output