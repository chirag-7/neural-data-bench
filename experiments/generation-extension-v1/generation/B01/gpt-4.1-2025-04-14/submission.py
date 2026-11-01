import numpy as np
from scipy import linalg
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import math

# For clustering without external packages; HDBSCAN is not allowed, fallback to DBSCAN
from sklearn.cluster import DBSCAN

def sort(recording_uv, fs, channel_positions_um):
    """
    Blind, unsupervised, deterministic spike sorting with event detection, snippet extraction,
    local whitening, PCA, and DBSCAN clustering.
    Args:
      recording_uv (np.ndarray): (320000, 32) numpy array (float32)
      fs (float): 32000 sampling rate
      channel_positions_um (np.ndarray): (32, 3) channel positions, not used for clustering here
    Returns:
      events (np.ndarray): (n_events, 2) array of [sample_index, unit_id], dtype=int64
    """
    np.random.seed(0)

    n_samples, n_channels = recording_uv.shape
    refractory_samp = int(0.0008 * fs)  # 0.8 ms absolute refractory
    window_pre = int(0.001 * fs)  # 1 ms before peak
    window_post = int(0.002 * fs)  # 2 ms after peak
    snippet_len = window_pre + window_post
    thresh_factor = 4.5  # threshold in std units

    # 1. Robust std estimate per channel (MAD)
    mad = np.median(np.abs(recording_uv - np.median(recording_uv, axis=0)), axis=0)
    noise_sigma = 1.4826 * mad  # approx std
    # Set low noise channels to min nonzero sigma
    noise_sigma[noise_sigma == 0] = np.min(noise_sigma[noise_sigma > 0])

    # 2. Threshold detection (detect on max absolute channel at each time)
    # Use slightly padded border for snippet extraction
    detection_start = window_pre
    detection_end = n_samples - window_post

    thr = thresh_factor * noise_sigma
    # Joint detection mask for all channels: event occurs if any channel crosses its thr
    above_thr = np.any(np.abs(recording_uv[detection_start:detection_end, :]) > thr, axis=1)
    crossing_indices = np.flatnonzero(above_thr) + detection_start

    # 3. Local maxima (peak picking within neighborhood per channel)
    # Only keep those that are local maxima in a 0.4 ms window (typical event half-width)
    peak_window = int(0.0004 * fs)  # ~12 samples
    event_indices = []
    for ch in range(n_channels):
        signal = recording_uv[:, ch]
        ch_thr = thr[ch]
        ch_crossings = np.flatnonzero(np.abs(signal[detection_start:detection_end]) > ch_thr) + detection_start
        # For each crossing, keep if local maximum in window
        for idx in ch_crossings:
            start = max(idx - peak_window, 0)
            end = min(idx + peak_window + 1, n_samples)
            if np.abs(signal[idx]) == np.max(np.abs(signal[start:end])):
                event_indices.append(idx)
    # Unique events
    event_indices = np.unique(event_indices)

    # Enforce refractory period globally
    if len(event_indices) > 0:
        event_indices = np.sort(event_indices)
        keep_inds = [event_indices[0]]
        for idx in event_indices[1:]:
            if idx - keep_inds[-1] > refractory_samp:
                keep_inds.append(idx)
        event_indices = np.array(keep_inds, dtype=int)
    else:
        return np.empty((0,2), dtype=np.int64)

    # 4. Extract and whiten snippets
    snippets = []
    keep_idx_mask = []  # final kept event indices (exclude near edges)
    for idx in event_indices:
        # Check if valid window
        if (idx - window_pre >= 0) and (idx + window_post <= n_samples):
            snippet = recording_uv[idx - window_pre: idx + window_post, :]
            snippets.append(snippet)
            keep_idx_mask.append(idx)
    if len(snippets) == 0:
        return np.empty((0,2), dtype=np.int64)
    snippets = np.stack(snippets, axis=0)  # (n_events, snippet_len, n_channels)
    keep_idx_mask = np.array(keep_idx_mask, dtype=np.int64)

    # Subtract mean per channel for snippet normalization
    snippets = snippets - np.mean(snippets, axis=1, keepdims=True)
    # Whiten: collapse time x channel (whiten across all dims)
    n_ev = snippets.shape[0]
    flat_snippets = snippets.reshape((n_ev, -1))  # (n_events, snippet_len * n_channels)
    scaler = StandardScaler(copy=False)
    flat_snippets = scaler.fit_transform(flat_snippets)

    # 5. Reduce dimension (PCA)
    n_components = min(8, flat_snippets.shape[1], flat_snippets.shape[0])
    pca = PCA(n_components=n_components, random_state=0)
    pca_snippets = pca.fit_transform(flat_snippets)

    # 6. Unsupervised clustering (deterministic)
    # DBSCAN: notes
    # - eps: set conservatively; min_samples: >=10
    # DBSCAN can create -1 for 'noise', reindex after clustering
    clustering = DBSCAN(eps=1.5, min_samples=12, algorithm='auto', n_jobs=1)
    cluster_labels = clustering.fit_predict(pca_snippets)

    # Re-map -1 and nonnegative cluster IDs to sequential positive integers
    uniq_units = np.unique(cluster_labels[cluster_labels >= 0])
    cluster_map = {uid: i for i, uid in enumerate(uniq_units)}
    mapped_labels = np.full_like(cluster_labels, -1)
    for i, label in enumerate(cluster_labels):
        if label >= 0:
            mapped_labels[i] = cluster_map[label]
    # Only keep events assigned to any cluster (ignore DBSCAN noise)
    valid_mask = mapped_labels >= 0
    final_idx = keep_idx_mask[valid_mask]
    final_labels = mapped_labels[valid_mask]
    # Sort by sample index, then by unit id
    out = np.stack([final_idx, final_labels], axis=1)
    out = out[np.lexsort((out[:,1], out[:,0]))]
    return out.astype(np.int64)
