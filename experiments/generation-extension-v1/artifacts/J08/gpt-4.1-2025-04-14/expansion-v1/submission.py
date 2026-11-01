
import numpy as np
from scipy import ndimage as ndi
from collections import deque
from functools import lru_cache
from sklearn.ensemble import RandomForestClassifier

# Helper: sliding window generator
def sliding_window(arr, window, step):
    x_max, y_max = arr.shape[-2], arr.shape[-1]
    for x in range(0, x_max - window[0] + 1, step[0]):
        for y in range(0, y_max - window[1] + 1, step[1]):
            yield x, y, arr[..., x:x+window[0], y:y+window[1]]

def rel_coords(h, w):
    yy, xx = np.meshgrid(np.arange(h), np.arange(w), indexing='ij')
    return (yy / h).astype(np.float32), (xx / w).astype(np.float32)

def extract_features(patch):
    # patch: (2, H, W), ch0 = intensity, ch1 = mask
    ch0 = patch[0]
    h, w = ch0.shape
    yy, xx = rel_coords(h, w)
    grad = ndi.gaussian_gradient_magnitude(ch0, sigma=1)
    laplace = ndi.gaussian_laplace(ch0, sigma=1)
    # Multi-scale mean/std in 9x9 window
    mean9 = ndi.uniform_filter(ch0, size=9)
    std9 = ndi.uniform_filter((ch0 - mean9) ** 2, size=9) ** 0.5
    features = np.stack([
        ch0, grad, laplace, mean9, std9, yy, xx
    ], -1)
    return features.reshape(-1, features.shape[-1])

def valid_pixels(ch1, label):
    mask = (ch1 == 1) & (label >= 0)
    return np.where(mask)

# Extract label centers given instance labels
@lru_cache(maxsize=512)
def instance_centers(label):
    ids = np.unique(label[label > 0])
    centers = []
    for inst_id in ids:
        mask = (label == inst_id)
        if np.count_nonzero(mask) >= 4:
            pts = np.argwhere(mask)
            centroid = np.round(np.mean(pts, axis=0)).astype(int)
            centers.append((centroid[0], centroid[1]))
    return centers, ids

# Watershed using greyscale seeds & valid extent mask
def instance_watershed(pred_fg, valid_mask):
    # Distance map for foreground pixels
    distance = ndi.distance_transform_edt(pred_fg * valid_mask)
    # Identify local maxima as markers (centers of objects)
    local_max = (ndi.maximum_filter(distance, size=5) == distance) & (distance > 0)
    markers, _ = ndi.label(local_max)
    lbl = ndi.watershed_ift((255 - (255 * pred_fg).astype(np.uint8)), markers.astype(np.uint8))
    lbl *= pred_fg
    # Remove small objects, ensure non-overlapping ids per image
    ids = np.unique(lbl)
    label_map = np.zeros(lbl.shape, np.int32)
    object_id = 1
    for i in ids:
        if i == 0:
            continue
        obj = (lbl == i) & valid_mask
        if np.count_nonzero(obj) >= 4:
            label_map[obj] = object_id
            object_id += 1
    return label_map

# Remove small objects < 4 px for F1-level symmetry
def filter_small_objects(bin_img):
    labeled, nlab = ndi.label(bin_img)
    output = np.zeros_like(bin_img)
    for i in range(1, nlab+1):
        obj = (labeled == i)
        if np.count_nonzero(obj) >= 4:
            output[obj] = 1
    return output

def fit_predict(train_x, train_y, test_x):
    # Prepare training feature table
    np.random.seed(0)
    n_patch, n_chan, ph, pw = train_x.shape
    feat_list, lab_list = [], []
    for i in range(n_patch):
        x_patch = train_x[i]
        y_patch = train_y[i]
        mask = (x_patch[1] == 1) & (y_patch >= 0)
        if not np.any(mask):
            continue
        feat = extract_features(x_patch)
        # Convert label: center pixels as positive, others (0) as background, ignore -1
        center_mask = np.zeros_like(y_patch, dtype=bool)
        centers, ids = instance_centers(y_patch)
        for c, inst_id in zip(centers, ids):
            pts = np.argwhere((y_patch == inst_id))
            if len(pts) < 4:
                continue
            # Mark only the centroid pixel as instance center
            center_mask[c[0], c[1]] = True
        flat_lab = np.full(y_patch.shape, 0, dtype=np.int32) # background=0
        flat_lab[center_mask] = 1 # center pixel/foreground
        flat_lab[y_patch < 0] = -1
        choose = mask & (flat_lab >= 0)
        feat_list.append(feat[choose.ravel()])
        lab_list.append(flat_lab[choose].ravel())
    X_train = np.concatenate(feat_list, 0)
    y_train = np.concatenate(lab_list, 0)
    # Train RandomForest for FG (center) vs BG
    clf = RandomForestClassifier(n_estimators=30, max_depth=9, random_state=42, n_jobs=1)
    clf.fit(X_train, y_train)

    # Threshold selection: grid search over train patches, maximizing F1 (centroid->mask)
    thresholds = np.linspace(0.25, 0.65, 9)
    best_thresh = 0.5
    best_f1 = 0.0
    for t in thresholds:
        f1s = []
        for i in range(min(80, n_patch)):
            x_patch = train_x[i]
            y_patch = train_y[i]
            mask = (x_patch[1] == 1) & (y_patch >= 0)
            fx = extract_features(x_patch)
            prob = clf.predict_proba(fx)[:,1].reshape(ph, pw)
            pred_fg = (prob > t) & mask
            pred_fg = filter_small_objects(pred_fg)
            gt_fg = (y_patch > 0) & mask
            tp = np.count_nonzero(pred_fg & gt_fg)
            fp = np.count_nonzero(pred_fg & ~gt_fg)
            fn = np.count_nonzero(~pred_fg & gt_fg)
            if tp+fp+fn > 0:
                prec = tp / (tp+fp)
                rec = tp / (tp+fn)
                if prec+rec > 0:
                    f1s.append(2*prec*rec/(prec+rec))
        if len(f1s) > 0 and np.mean(f1s) > best_f1:
            best_f1 = np.mean(f1s)
            best_thresh = t

    results = np.zeros((test_x.shape[0],) + test_x.shape[2:], dtype=np.int32)
    for ti in range(test_x.shape[0]):
        image = test_x[ti]
        valid_mask = (image[1] == 1)
        H, W = image.shape[1:]
        proba_accum = np.zeros((H, W), np.float32)
        count_accum = np.zeros((H, W), np.float32)
        # Slide window, step 64
        for x, y, crop in sliding_window(image, (128,128), (64,64)):
            feat = extract_features(crop)
            prob = clf.predict_proba(feat)[:,1].reshape(128,128)
            proba_accum[x:x+128, y:y+128] += prob
            count_accum[x:x+128, y:y+128] += 1
        mask_nonzero = count_accum > 0
        avg_proba = np.zeros_like(proba_accum)
        avg_proba[mask_nonzero] = proba_accum[mask_nonzero] / count_accum[mask_nonzero]
        pred_fg = (avg_proba > best_thresh) & valid_mask
        pred_fg = filter_small_objects(pred_fg)
        inst_map = instance_watershed(pred_fg.astype(np.uint8), valid_mask)
        inst_map[~valid_mask] = 0
        results[ti] = inst_map.astype(np.int32)
    return results
